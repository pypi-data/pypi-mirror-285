# -*- coding: utf-8 -*-
"""
Engine to train the surrogate

"""
from copy import deepcopy, copy
import joblib
from joblib import Parallel, delayed
import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
import os
import pandas as pd
import pathlib
import scipy.optimize as opt
from scipy import stats, signal, linalg, sparse
from scipy.spatial import distance
from sklearn.metrics import mean_squared_error
import seaborn as sns
import sys
from tqdm import tqdm

from bayesvalidrox.bayes_inference.bayes_inference import BayesInference
from bayesvalidrox.bayes_inference.discrepancy import Discrepancy
from .exploration import Exploration
from .surrogate_models import create_psi

def hellinger_distance(P, Q):
    """
    Hellinger distance between two continuous distributions.

    The maximum distance 1 is achieved when P assigns probability zero to
    every set to which Q assigns a positive probability, and vice versa.
    0 (identical) and 1 (maximally different)

    Parameters
    ----------
    P : array
        Reference likelihood.
    Q : array
        Estimated likelihood.

    Returns
    -------
    float
        Hellinger distance of two distributions.

    """
    P = np.array(P)
    Q = np.array(Q)

    mu1 = P.mean()
    Sigma1 = np.std(P)

    mu2 = Q.mean()
    Sigma2 = np.std(Q)

    term1 = np.sqrt(2 * Sigma1 * Sigma2 / (Sigma1 ** 2 + Sigma2 ** 2))

    term2 = np.exp(-.25 * (mu1 - mu2) ** 2 / (Sigma1 ** 2 + Sigma2 ** 2))

    H_squared = 1 - term1 * term2

    return np.sqrt(H_squared)


def logpdf(x, mean, cov):
    """
    Computes the likelihood based on a multivariate normal distribution.

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.
    mean : array_like
        Observation data.
    cov : 2d array
        Covariance matrix of the distribution.

    Returns
    -------
    log_lik : float
        Log likelihood.

    """
    n = len(mean)
    L = linalg.cholesky(cov, lower=True)
    beta = np.sum(np.log(np.diag(L)))
    dev = x - mean
    alpha = dev.dot(linalg.cho_solve((L, True), dev))
    log_lik = -0.5 * alpha - beta - n / 2. * np.log(2 * np.pi)

    return log_lik


def subdomain(Bounds, n_new_samples):
    """
    Divides a domain defined by Bounds into subdomains.

    Parameters
    ----------
    Bounds : list of tuples
        List of lower and upper bounds.
    n_new_samples : int
        Number of samples to divide the domain for.

    Returns
    -------
    Subdomains : List of tuples of tuples
        Each tuple of tuples divides one set of bounds into n_new_samples parts.

    """
    n_params = len(Bounds)
    n_subdomains = n_new_samples + 1
    LinSpace = np.zeros((n_params, n_subdomains))

    for i in range(n_params):
        LinSpace[i] = np.linspace(start=Bounds[i][0], stop=Bounds[i][1],
                                  num=n_subdomains)
    Subdomains = []
    for k in range(n_subdomains - 1):
        mylist = []
        for i in range(n_params):
            mylist.append((LinSpace[i, k + 0], LinSpace[i, k + 1]))
        Subdomains.append(tuple(mylist))

    return Subdomains


class SequentialDesign:
    """
    Contains options for choosing the next training sample iteratively.

    """

    def __init__(self, MetaMod, Model, ExpDes, engine, parallel=False):
        self.MetaModel = MetaMod # Surrogate should be trained
        self.Model = Model
        self.ExpDesign = ExpDes
        self.parallel = parallel
        self.engine = engine

        # Init other parameters
        self._y_hat_prev = None

    def start_seqdesign(self) -> None:
        """
        Do all the preparations that need to be run before the actual training

        Returns
        -------
        None

        """
        None


    # -------------------------------------------------------------------------
    def choose_next_sample(self, sigma2=None, n_candidates=5, var='DKL'):
        """
        Runs optimal sequential design.

        Parameters
        ----------
        sigma2 : dict, optional
            A dictionary containing the measurement errors (sigma^2). The
            default is None.
        n_candidates : int, optional
            Number of candidate samples. The default is 5.
        var : string, optional
            Utility function. The default is None. # TODO: default is set to DKL, not none

        Raises
        ------
        NameError
            Wrong utility function.

        Returns
        -------
        Xnew : array (n_samples, n_params)
            Selected new training point(s).
        """

        # Initialization
        Bounds = self.ExpDesign.bound_tuples
        n_new_samples = self.ExpDesign.n_new_samples
        explore_method = self.ExpDesign.explore_method
        exploit_method = self.ExpDesign.exploit_method
        n_cand_groups = self.ExpDesign.n_cand_groups
        tradeoff_scheme = self.ExpDesign.tradeoff_scheme

        old_EDX = self.ExpDesign.X
        old_EDY = self.ExpDesign.Y.copy()
        ndim = self.ExpDesign.X.shape[1]
        OutputNames = self.out_names

        # -----------------------------------------
        # ----------- CUSTOMIZED METHODS ----------
        # -----------------------------------------
        # Utility function exploit_method provided by user
        if exploit_method.lower() == 'user':
            # TODO: is the exploit_method meant here?
            if not hasattr(self.ExpDesign, 'ExploitFunction') or self.ExpDesign.ExploitFunction is None:
                raise AttributeError(
                    'Function `ExploitFunction` not given to the ExpDesign, thus cannor run user-defined sequential'
                    'scheme')
            # TODO: syntax does not fully match the rest - can test this??
            Xnew, filteredSamples = self.ExpDesign.ExploitFunction(self)

            print("\n")
            print("\nXnew:\n", Xnew)

            return Xnew, filteredSamples

        # Dual-Annealing works differently from the rest, so deal with this first
        # Here exploration and exploitation are performed simulataneously
        if explore_method.lower() == 'dual annealing':
            # ------- EXPLORATION: OPTIMIZATION -------
            import time
            start_time = time.time()

            # Divide the domain to subdomains
            subdomains = subdomain(Bounds, n_new_samples)

            # Multiprocessing
            if self.parallel:
                args = []
                for i in range(n_new_samples):
                    args.append((exploit_method, subdomains[i], sigma2, var, i))
                pool = multiprocessing.Pool(multiprocessing.cpu_count())

                # With Pool.starmap_async()
                results = pool.starmap_async(self.dual_annealing, args).get()

                # Close the pool
                pool.close()
            # Without multiprocessing
            else:
                results = []
                for i in range(n_new_samples):
                    results.append(self.dual_annealing(exploit_method, subdomains[i], sigma2, var, i))

            # New sample
            Xnew = np.array([results[i][1] for i in range(n_new_samples)])
            print("\nXnew:\n", Xnew)

            # Computational cost
            elapsed_time = time.time() - start_time
            print("\n")
            print(f"Elapsed_time: {round(elapsed_time, 2)} sec.")
            print('-' * 20)

            return Xnew, None

        # ------- Calculate Exploration weight -------
        # Compute exploration weight based on trade off scheme
        explore_w, exploit_w = self.tradeoff_weights(tradeoff_scheme,
                                                     old_EDX,
                                                     old_EDY)
        print(f"\n Exploration weight={explore_w:0.3f} "
              f"Exploitation weight={exploit_w:0.3f}\n")

        # Generate the candidate samples
        # TODO: here use the sampling method provided by the expdesign?
        # sampling_method = self.ExpDesign.sampling_method

        # TODO: changed this from 'random' for LOOCV
        # TODO: these are commented out as they are not used !?
        # if explore_method == 'LOOCV':
        # allCandidates = self.ExpDesign.generate_samples(n_candidates,
        #                                                     sampling_method)
        # else:
        #     allCandidates, scoreExploration = explore.get_exploration_samples()

        # -----------------------------------------
        # ---------- EXPLORATION METHODS ----------
        # -----------------------------------------
        # ToDo: Move this if/else into its own function called "do_exploration", which should select the
        #       exploration samples, and assign exploration scores. We should send it explore_score, for if/else stmts
        # ToDo: Check if explore_scores can be nan, and remove them from any score normalization
        if explore_method.lower() == 'voronoi':
            raise AttributeError('Exploration with voronoi currently not supported!')
            #print('WARNING: Exploration with Voronoi ')
        if explore_method.lower() == 'loocv':
            # -----------------------------------------------------------------
            # TODO: LOOCV model construnction based on Feng et al. (2020)
            # 'LOOCV':
            # Initilize the ExploitScore array

            # Generate random samples
            allCandidates = self.ExpDesign.generate_samples(n_candidates,
                                                            'random')

            # Construct error model based on LCerror
            errorModel = self.MetaModel.create_ModelError(old_EDX, self.LCerror)
            self.errorModel.append(copy(errorModel))

            # Evaluate the error models for allCandidates
            eLCAllCands, _ = errorModel.eval_errormodel(allCandidates)
            # Select the maximum as the representative error
            eLCAllCands = np.dstack(eLCAllCands.values())
            eLCAllCandidates = np.max(eLCAllCands, axis=1)[:, 0]

            # Normalize the error w.r.t the maximum error
            scoreExploration = eLCAllCandidates / np.sum(eLCAllCandidates)

        else:
            # ------- EXPLORATION: SPACE-FILLING DESIGN -------
            # ToDo: Remove Exploration class and merge the functions into SequentialDesign class
            # Generate candidate samples from Exploration class
            explore = Exploration(self.ExpDesign, n_candidates)
            explore.w = 100  # * ndim #500   # TODO: where does this value come from?
            # Select criterion (mc-intersite-proj-th, mc-intersite-proj)
            explore.mc_criterion = 'mc-intersite-proj'
            allCandidates, scoreExploration = explore.get_exploration_samples()

            # Temp: ---- Plot all candidates -----
            # ToDo: Make its own function, called inside of the select_exploration_samples function.
            if ndim == 2:
                def plotter(points, allCandidates, Method,
                            scoreExploration=None):
                    """
                    unknown

                    Parameters
                    ----------
                    points
                    allCandidates
                    Method
                    scoreExploration

                    Returns
                    -------

                    """
                    if Method.lower() == 'voronoi':
                        from scipy.spatial import Voronoi, voronoi_plot_2d
                        vor = Voronoi(points)
                        fig = voronoi_plot_2d(vor)
                        ax1 = fig.axes[0]
                    else:
                        fig = plt.figure()
                        ax1 = fig.add_subplot(111)
                    ax1.scatter(points[:, 0], points[:, 1], s=10, c='r',
                                marker="s", label='Old Design Points')
                    ax1.scatter(allCandidates[:, 0], allCandidates[:, 1], s=10,
                                c='b', marker="o", label='Design candidates')
                    for i in range(points.shape[0]):
                        txt = 'p' + str(i + 1)
                        ax1.annotate(txt, (points[i, 0], points[i, 1]))
                    if scoreExploration is not None:
                        for i in range(allCandidates.shape[0]):
                            txt = str(round(scoreExploration[i], 5))
                            ax1.annotate(txt, (allCandidates[i, 0],
                                               allCandidates[i, 1]))

                    plt.xlim(self.bound_tuples[0])
                    plt.ylim(self.bound_tuples[1])
                    # plt.show()
                    plt.legend(loc='upper left')

        # -----------------------------------------
        # --------- EXPLOITATION METHODS ----------
        # -----------------------------------------
        if exploit_method.lower() == 'bayesoptdesign' or \
                exploit_method.lower() == 'bayesactdesign':

            # ------- EXPLOITATION: BayesOptDesign & ActiveLearning -------
            if explore_w != 1.0:
                # Check if all needed properties are set
                if not hasattr(self.ExpDesign, 'max_func_itr'):
                    raise AttributeError('max_func_itr not given to the experimental design')


                # Create a sample pool for rejection sampling
                # ToDo: remove from here, add only to BayesOptDesign option
                MCsize = 15000
                X_MC = self.ExpDesign.generate_samples(MCsize, 'random')

                # Split the candidates in groups for multiprocessing
                split_cand = np.array_split(
                    allCandidates, n_cand_groups, axis=0
                )
                if self.parallel:
                    results = Parallel(n_jobs=-1, backend='multiprocessing')(
                        delayed(self.run_util_func)(
                            exploit_method, split_cand[i], i, sigma2, var, X_MC)
                        for i in range(n_cand_groups))
                else:
                    results = []
                    for i in range(n_cand_groups):
                        results.append(self.run_util_func(exploit_method, split_cand[i], i, sigma2, var, X_MC))

                # Retrieve the results and append them
                # ToDo: Rename U_J_D (here and everyhwere) to something more representative
                self.results = results
                U_J_d = np.concatenate([results[NofE][1] for NofE in
                                        range(n_cand_groups)])

                # Check if all scores are inf
                if np.isinf(U_J_d).all() or np.isnan(U_J_d).all():
                    U_J_d = np.ones(len(U_J_d))

                # Get the expected value (mean) of the Utility score
                # for each cell
                if explore_method.lower() == 'voronoi':
                    U_J_d = np.mean(U_J_d.reshape(-1, n_candidates), axis=1)

                # Normalize U_J_d
                # norm_U_J_D = U_J_d / np.nansum(np.abs(U_J_d))  # Possible solution
                norm_scoreExploitation = U_J_d / np.sum(U_J_d)

            else:
                norm_scoreExploitation = np.zeros((len(scoreExploration)))

            # temp: Plot
            # dim = self.ExpDesign.X.shape[1]
            # if dim == 2:
            #     plotter(self.ExpDesign.X, allCandidates, explore_method)
            opt_type = 'maximization'

        elif exploit_method.lower() == 'varoptdesign':
            # ------- EXPLOITATION: VarOptDesign -------
            UtilMethod = var

            # ------- Calculate Exoploration weight -------
            # Compute exploration weight based on trade off scheme
            explore_w, exploit_w = self.tradeoff_weights(tradeoff_scheme,
                                                         old_EDX,
                                                         old_EDY)
            print(f"\nweightExploration={explore_w:0.3f} "
                  f"weightExploitation={exploit_w:0.3f}")

            # Generate candidate samples from Exploration class
            nMeasurement = old_EDY[OutputNames[0]].shape[1]

            # Find sensitive region
            if UtilMethod.lower() == 'loocv':
                # TODO: why is this not inside the VarOptDesign function?
                LCerror = self.MetaModel.LCerror
                allModifiedLOO = np.zeros((len(old_EDX), len(OutputNames),
                                           nMeasurement))
                for y_idx, y_key in enumerate(OutputNames):
                    for idx, key in enumerate(LCerror[y_key].keys()):
                        allModifiedLOO[:, y_idx, idx] = abs(
                            LCerror[y_key][key])

                ExploitScore = np.max(np.max(allModifiedLOO, axis=1), axis=1)

            elif UtilMethod in ['EIGF', 'ALM']:
                # ToDo: Check the methods it actually can receive (ALC is missing from conditional list and code)
                # ----- All other in  ['EIGF', 'ALM'] -----

                # Split the candidates in groups for multiprocessing
                if explore_method.lower() != 'voronoi':
                    split_cand = np.array_split(allCandidates,
                                                n_cand_groups,
                                                axis=0)
                    goodSampleIdx = range(n_cand_groups)
                else:
                    # Find indices of the Vornoi cells with samples
                    goodSampleIdx = []
                    for idx in range(len(explore.closest_points)):
                        if len(explore.closest_points[idx]) != 0:
                            goodSampleIdx.append(idx)
                    split_cand = explore.closest_points

                # Split the candidates in groups for multiprocessing
                args = []
                for index in goodSampleIdx:
                    args.append((exploit_method, split_cand[index], index,
                                 sigma2, var))

                # Multiprocessing
                pool = multiprocessing.Pool(multiprocessing.cpu_count())
                # With Pool.starmap_async()
                results = pool.starmap_async(self.run_util_func, args).get()

                # Close the pool
                pool.close()

                # Retrieve the results and append them
                if explore_method.lower() == 'voronoi':
                    ExploitScore = [np.mean(results[k][1]) for k in
                                    range(len(goodSampleIdx))]
                else:
                    ExploitScore = np.concatenate(
                        [results[k][1] for k in range(len(goodSampleIdx))])

            else:
                raise NameError('The requested utility function is not '
                                'available.')
                
            # Total score - Normalize U_J_d
            norm_scoreExploitation = ExploitScore / np.sum(ExploitScore)            
            opt_type = 'maximization'

        elif exploit_method.lower() == 'alphabetic':
            # ToDo: Check function to see what it does for scores/how it chooses points, so it gives as an output the
            #       scores. See how it works with exploration_scores.
            # TODO: Rethink the final accumulation of scores for this function
            #       Should this be reworked to maximization as well?
            # ------- EXPLOITATION: ALPHABETIC -------
            norm_scoreExploitation = self.util_AlphOptDesign(allCandidates, var)
            opt_type = 'minimization'

        elif exploit_method.lower() == 'space-filling':
            # ------- EXPLOITATION: SPACE-FILLING -------
            norm_scoreExploitation = scoreExploration
            exploit_w = 0
            opt_type = 'maximization'
            
        else:
            raise NameError('The requested design method is not available.')
            
        # Accumulate all candidates and scores
        # TODO: recheck if this line holds true for all combinations of methods
        # TODO: for the combination none, voronoi, BOD+MI the exploration scores contain 10*more values than the exploitation scores
        #       This seems to be an issue resulting from the voronoi sampling, not BODMI
        #print('Shapes of components of the weights')
        #print(f'Exploration: {explore_w} * {scoreExploration.shape}')
        #print(f'Exploitation: {exploit_w} * {norm_scoreExploitation.shape}')
        finalCandidates = allCandidates
        totalScore = exploit_w * norm_scoreExploitation + explore_w * scoreExploration
            
        # Choose the new training samples
        # If the total weights should be maximized
        if opt_type == 'maximization':
            
            # ------- Select the best candidate -------
            # find an optimal point subset to add to the initial design by
            # maximization of the utility score and taking care of NaN values
            temp = totalScore.copy()
            temp[np.isnan(totalScore)] = -np.inf                # Since we are maximizing
            sorted_idxtotalScore = np.argsort(temp)[::-1]
            bestIdx = sorted_idxtotalScore[:n_new_samples]
            if type(bestIdx) is int:
                bestIdx = [bestIdx]

            # select the requested number of samples
            if explore_method.lower() == 'voronoi':
                Xnew = np.zeros((n_new_samples, ndim))
                for i, idx in enumerate(bestIdx):
                    X_can = explore.closestPoints[idx]

                    # Calculate the maxmin score for the region of interest
                    newSamples, maxminScore = explore.get_mc_samples(X_can) # TODO: Understand this line!

                    # select the requested number of samples
                    Xnew[i] = newSamples[np.argmax(maxminScore)]
            else:
                # Changed this from allCandiates to full set of candidates
                # TODO: still not changed for e.g. 'Voronoi'
                Xnew = finalCandidates[sorted_idxtotalScore[:n_new_samples]]
               
        # If the total weights should be maximized
        elif opt_type == 'minimization':
            # find an optimal point subset to add to the initial design
            # by minimization of the Phi
            sorted_idxtotalScore = np.argsort(totalScore)

            # select the requested number of samples
            Xnew = finalCandidates[sorted_idxtotalScore[:n_new_samples]]
            

        print("\n")
        print("\nRun No. {}:".format(old_EDX.shape[0] + 1))
        print("Xnew:\n", Xnew)

        # TODO: why does it also return None?
        return Xnew, None

    # -------------------------------------------------------------------------
    def tradeoff_weights(self, tradeoff_scheme, old_EDX, old_EDY):
        """
        Calculates weights for exploration scores based on the requested
        scheme: `None`, `equal`, `epsilon-decreasing` and `adaptive`.

        `None`: No exploration.
        `equal`: Same weights for exploration and exploitation scores.
        `epsilon-decreasing`: Start with more exploration and increase the
            influence of exploitation along the way with an exponential decay
            function
        `adaptive`: An adaptive method based on:
            Liu, Haitao, Jianfei Cai, and Yew-Soon Ong. "An adaptive sampling
            approach for Kriging metamodeling by maximizing expected prediction
            error." Computers & Chemical Engineering 106 (2017): 171-182.

        Parameters
        ----------
        tradeoff_scheme : string
            Trade-off scheme for exloration and exploitation scores.
        old_EDX : array (n_samples, n_params)
            Old experimental design (training points).
        old_EDY : dict
            Old model responses (targets).

        Returns
        -------
        exploration_weight : float
            Exploration weight.
        exploitation_weight: float
            Exploitation weight.

        """
        exploration_weight = None

        if tradeoff_scheme is None:
            exploration_weight = 0

        elif tradeoff_scheme.lower() == 'equal':
            exploration_weight = 0.5

        elif tradeoff_scheme.lower() == 'epsilon-decreasing':
            # epsilon-decreasing scheme
            # Start with more exploration and increase the influence of
            # exploitation along the way with an exponential decay function
            initNSamples = self.ExpDesign.n_init_samples
            n_max_samples = self.ExpDesign.n_max_samples

            itrNumber = (self.ExpDesign.X.shape[0] - initNSamples)
            itrNumber //= self.ExpDesign.n_new_samples

            tau2 = -(n_max_samples - initNSamples - 1) / np.log(1e-8)
            exploration_weight = signal.windows.exponential(n_max_samples - initNSamples,
                                                    0, tau2, False)[itrNumber]

        elif tradeoff_scheme.lower() == 'adaptive':

            # Extract itrNumber
            initNSamples = self.ExpDesign.n_init_samples
            # n_max_samples = self.ExpDesign.n_max_samples
            itrNumber = (self.ExpDesign.X.shape[0] - initNSamples)
            itrNumber //= self.ExpDesign.n_new_samples

            if itrNumber == 0:
                exploration_weight = 0.5
            else:
                # New adaptive trade-off according to Liu et al. (2017)
                # Mean squared error for last design point
                last_EDX = old_EDX[-1].reshape(1, -1)
                lastPCEY, _ = self.MetaModel.eval_metamodel(samples=last_EDX)
                pce_y = np.array(list(lastPCEY.values()))[:, 0]
                y = np.array(list(old_EDY.values()))[:, -1, :]
                mseError = mean_squared_error(pce_y, y)

                # Mean squared CV - error for last design point
                pce_y_prev = np.array(list(self._y_hat_prev.values()))[:, 0]
                mseCVError = mean_squared_error(pce_y_prev, y)

                exploration_weight = min([0.5 * mseError / mseCVError, 1])

        # Exploitation weight
        exploitation_weight = 1 - exploration_weight

        return exploration_weight, exploitation_weight

    # -------------------------------------------------------------------------
    def run_util_func(self, method, candidates, index, sigma2Dict=None,
                      var=None, X_MC=None):
        """
        Runs the utility function based on the given method.

        Parameters
        ----------
        method : string
            Exploitation method: `VarOptDesign`, `BayesActDesign` and
            `BayesOptDesign`.
        candidates : array of shape (n_samples, n_params)
            All candidate parameter sets.
        index : int
            ExpDesign index.
        sigma2Dict : dict, optional
            A dictionary containing the measurement errors (sigma^2). The
            default is None.
        var : string, optional
            Utility function. The default is None.
        X_MC : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        index : TYPE
            DESCRIPTION.
        List
            Scores.

        """

        if method.lower() == 'varoptdesign':
            # U_J_d = self.util_VarBasedDesign(candidates, index, var)
            U_J_d = np.zeros((candidates.shape[0]))
            for idx, X_can in tqdm(enumerate(candidates), ascii=True,
                                   desc="varoptdesign"):
                U_J_d[idx] = self.util_VarBasedDesign(X_can, index, var)

        elif method.lower() == 'bayesactdesign':
            NCandidate = candidates.shape[0]
            U_J_d = np.zeros(NCandidate)
            # Evaluate all candidates
            y_can, std_can = self.MetaModel.eval_metamodel(samples=candidates)
            # loop through candidates
            for idx, X_can in tqdm(enumerate(candidates), ascii=True,
                                   desc="BAL Design"):
                y_hat = {key: items[idx] for key, items in y_can.items()}
                std = {key: items[idx] for key, items in std_can.items()}

                U_J_d[idx] = self.util_BayesianActiveDesign(
                    y_hat, std, sigma2Dict, var)

        elif method.lower() == 'bayesoptdesign':
            # ToDo: Create X_MC here, since it is not used in the other active learning approaches.
            NCandidate = candidates.shape[0]
            U_J_d = np.zeros(NCandidate)
            for idx, X_can in tqdm(enumerate(candidates), ascii=True,
                                   desc="OptBayesianDesign"):
                U_J_d[idx] = self.util_BayesianDesign(X_can, X_MC, sigma2Dict,
                                                      var)
        return index, -1 * U_J_d


    # -------------------------------------------------------------------------
    def util_VarBasedDesign(self, X_can, index, util_func='Entropy'):
        """
        Computes the exploitation scores based on:
        active learning MacKay(ALM) and active learning Cohn (ALC)
        Paper: Sequential Design with Mutual Information for Computer
        Experiments (MICE): Emulation of a Tsunami Model by Beck and Guillas
        (2016)

        Parameters
        ----------
        X_can : array of shape (n_samples, n_params)
            Candidate samples.
        index : int
            Model output index.
        util_func : string, optional
            Exploitation utility function. The default is 'Entropy'.

        Returns
        -------
        float
            Score.

        """
        MetaModel = self.MetaModel
        ED_X = self.ExpDesign.X
        out_dict_y = self.ExpDesign.Y
        out_names = self.out_names

        # Run the Metamodel for the candidate
        X_can = X_can.reshape(1, -1)
        Y_PC_can, std_PC_can = MetaModel.eval_metamodel(samples=X_can)

        score = None
        if util_func.lower() == 'alm':
            # ----- Entropy/MMSE/active learning MacKay(ALM)  -----
            # Compute perdiction variance of the old model
            canPredVar = {key: std_PC_can[key] ** 2 for key in out_names}

            varPCE = np.zeros((len(out_names), X_can.shape[0]))
            for KeyIdx, key in enumerate(out_names):
                varPCE[KeyIdx] = np.max(canPredVar[key], axis=1)
            score = np.max(varPCE, axis=0)

        elif util_func.lower() == 'eigf':
            # ----- Expected Improvement for Global fit -----
            # Find closest EDX to the candidate
            distances = distance.cdist(ED_X, X_can, 'euclidean')
            index = np.argmin(distances)

            # Compute perdiction error and variance of the old model
            predError = {key: Y_PC_can[key] for key in out_names}
            canPredVar = {key: std_PC_can[key] ** 2 for key in out_names}

            # Compute perdiction error and variance of the old model
            # Eq (5) from Liu et al.(2018)
            EIGF_PCE = np.zeros((len(out_names), X_can.shape[0]))
            for KeyIdx, key in enumerate(out_names):
                residual = predError[key] - out_dict_y[key][int(index)]
                var = canPredVar[key]
                EIGF_PCE[KeyIdx] = np.max(residual ** 2 + var, axis=1)
            score = np.max(EIGF_PCE, axis=0)

        return -1 * score  # -1 is for minimization instead of maximization

    # -------------------------------------------------------------------------
    def util_BayesianActiveDesign(self, y_hat, std, sigma2Dict, var='DKL'):
        """
        Computes scores based on Bayesian active design criterion (var).

        It is based on the following paper:
        Oladyshkin, Sergey, Farid Mohammadi, Ilja Kroeker, and Wolfgang Nowak.
        "Bayesian3 active learning for the gaussian process emulator using
        information theory." Entropy 22, no. 8 (2020): 890.

        Parameters
        ----------
        y_hat : unknown
        std : unknown
        sigma2Dict : dict
            A dictionary containing the measurement errors (sigma^2).
        var : string, optional
            BAL design criterion. The default is 'DKL'.

        Returns
        -------
        float
            Score.

        """

        # Get the data
        obs_data = self.Model.observations
        # TODO: this should be optimizable to be calculated explicitly
        if hasattr(self.Model, 'n_obs'):
            n_obs = self.Model.n_obs
        else:
            n_obs = self.n_obs
        mc_size = 10000

        # Sample a distribution for a normal dist
        # with Y_mean_can as the mean and Y_std_can as std.
        Y_MC, std_MC = {}, {}
        logPriorLikelihoods = np.zeros(mc_size)
        for key in list(y_hat):
            cov = np.diag(std[key] ** 2)
            # Allow for singular matrices
            rv = stats.multivariate_normal(mean=y_hat[key], cov=cov, allow_singular=True)
            Y_MC[key] = rv.rvs(size=mc_size)
            logPriorLikelihoods += rv.logpdf(Y_MC[key])
            std_MC[key] = np.zeros((mc_size, y_hat[key].shape[0]))

        #  Likelihood computation (Comparison of data and simulation
        #  results via PCE with candidate design)
        likelihoods = self._normpdf(Y_MC, std_MC, obs_data, sigma2Dict)

        # Rejection Step
        # Random numbers between 0 and 1
        unif = np.random.rand(1, mc_size)[0]

        # Reject the poorly performed prior
        accepted = (likelihoods / np.max(likelihoods)) >= unif

        # Prior-based estimation of BME
        logBME = np.log(np.nanmean(likelihoods), dtype=np.longdouble)  # float128)

        # Posterior-based expectation of likelihoods
        postLikelihoods = likelihoods[accepted]
        postExpLikelihoods = np.mean(np.log(postLikelihoods))

        # Posterior-based expectation of prior densities
        postExpPrior = np.mean(logPriorLikelihoods[accepted])

        # Utility function Eq.2 in Ref. (2)
        # Posterior covariance matrix after observing data y
        # Kullback-Leibler Divergence (Sergey's paper)
        U_J_d = None
        if var.lower() == 'dkl':

            # TODO: Calculate the correction factor for BME
            # BMECorrFactor = self.BME_Corr_Weight(PCE_SparseBayes_can,
            #                                      ObservationData, sigma2Dict)
            # BME += BMECorrFactor
            # Haun et al implementation
            # U_J_d = np.mean(np.log(Likelihoods[Likelihoods!=0])- logBME)
            U_J_d = postExpLikelihoods - logBME

        # Marginal log likelihood
        elif var.lower() == 'bme':
            U_J_d = np.nanmean(likelihoods)

        # Entropy-based information gain
        elif var.lower() == 'infentropy':
            logBME = np.log(np.nanmean(likelihoods))
            infEntropy = logBME - postExpPrior - postExpLikelihoods
            U_J_d = infEntropy * -1  # -1 for minimization

        # Bayesian information criterion
        elif var.lower() == 'bic':
            coeffs = self.MetaModel.coeffs_dict.values()
            nModelParams = max(len(v) for val in coeffs for v in val.values())
            maxL = np.nanmax(likelihoods)
            U_J_d = -2 * np.log(maxL) + np.log(n_obs) * nModelParams

        # Akaike information criterion
        elif var.lower() == 'aic':
            coeffs = self.MetaModel.coeffs_dict.values()
            nModelParams = max(len(v) for val in coeffs for v in val.values())
            maxlogL = np.log(np.nanmax(likelihoods))
            AIC = -2 * maxlogL + 2 * nModelParams
            # 2 * nModelParams * (nModelParams+1) / (n_obs-nModelParams-1)
            penTerm = 0
            U_J_d = 1 * (AIC + penTerm)

        # Deviance information criterion
        elif var.lower() == 'dic':
            # D_theta_bar = np.mean(-2 * Likelihoods)
            N_star_p = 0.5 * np.var(np.log(likelihoods[likelihoods != 0]))
            Likelihoods_theta_mean = self._normpdf(
                y_hat, std, obs_data, sigma2Dict
            )
            DIC = -2 * np.log(Likelihoods_theta_mean) + 2 * N_star_p

            U_J_d = DIC

        else:
            print('The algorithm you requested has not been implemented yet!')

        # Handle inf and NaN (replace by zero)
        if np.isnan(U_J_d) or U_J_d == -np.inf or U_J_d == np.inf:
            U_J_d = 0.0

        # Clear memory
        del likelihoods
        del Y_MC
        del std_MC

        return -1 * U_J_d  # -1 is for minimization instead of maximization

    # -------------------------------------------------------------------------
    def util_BayesianDesign(self, X_can, X_MC, sigma2Dict, var='DKL'):
        """
        Computes scores based on Bayesian sequential design criterion (var).

        Parameters
        ----------
        X_can : array of shape (n_samples, n_params)
            Candidate samples.
        X_MC : unknown
        sigma2Dict : dict
            A dictionary containing the measurement errors (sigma^2).
        var : string, optional
            Bayesian design criterion. The default is 'DKL'.

        Returns
        -------
        float
            Score.

        """

        # To avoid changes ub original aPCE object
        MetaModel = self.MetaModel
        out_names = self.out_names
        if X_can.ndim == 1:
            X_can = X_can.reshape(1, -1)

        # Compute the mean and std based on the MetaModel
        # pce_means, pce_stds = self._compute_pce_moments(MetaModel)
        if var.lower() == 'alc':
            Y_MC, Y_MC_std = MetaModel.eval_metamodel(samples=X_MC)

        # Old Experimental design
        oldExpDesignX = self.ExpDesign.X
        oldExpDesignY = self.ExpDesign.Y

        # Evaluate the PCE metamodels at that location ???
        Y_PC_can, Y_std_can = MetaModel.eval_metamodel(samples=X_can)
        PCE_Model_can = deepcopy(MetaModel)
        # TODO: this is really not clean, create a workaround for this issue!
        engine_can = deepcopy(self.engine)
        # Add the candidate to the ExpDesign
        NewExpDesignX = np.vstack((oldExpDesignX, X_can))

        NewExpDesignY = {}
        for key in oldExpDesignY.keys():
            NewExpDesignY[key] = np.vstack(
                (oldExpDesignY[key], Y_PC_can[key])
            )

        engine_can.ExpDesign.sampling_method = 'user'
        engine_can.ExpDesign.X = NewExpDesignX
        # engine_can.ModelOutputDict = NewExpDesignY
        engine_can.ExpDesign.Y = NewExpDesignY

        # Train the model for the observed data using x_can
        engine_can.MetaModel.input_obj.poly_coeffs_flag = False
        engine_can.start_engine()
        engine_can.train_normal(parallel=False)
        engine_can.MetaModel.fit(NewExpDesignX, NewExpDesignY)
        #        engine_can.train_norm_design(parallel=False)

        # Set the ExpDesign to its original values
        engine_can.ExpDesign.X = oldExpDesignX
        engine_can.ModelOutputDict = oldExpDesignY
        engine_can.ExpDesign.Y = oldExpDesignY

        if var.lower() == 'mi':
            # Mutual information based on Krause et al.
            # Adapted from Beck & Guillas (MICE) paper
            _, std_PC_can = engine_can.MetaModel.eval_metamodel(samples=X_can)
            std_can = {key: std_PC_can[key] for key in out_names}

            std_old = {key: Y_std_can[key] for key in out_names}

            varPCE = np.zeros((len(out_names)))
            for i, key in enumerate(out_names):
                varPCE[i] = np.mean(std_old[key] ** 2 / std_can[key] ** 2)
            score = np.mean(varPCE)

            return -1 * score

        elif var.lower() == 'alc':
            # Active learning based on Gramyc and Lee
            # Adaptive design and analysis of supercomputer experiments Techno-
            # metrics, 51 (2009), pp. 130–145.

            # Evaluate the MetaModel at the given samples
            Y_MC_can, Y_MC_std_can = engine_can.MetaModel.eval_metamodel(samples=X_MC)

            # Compute the score
            score = []
            for i, key in enumerate(out_names):
                pce_var = Y_MC_std_can[key] ** 2
                pce_var_can = Y_MC_std[key] ** 2
                score.append(np.mean(pce_var - pce_var_can, axis=0))
            score = np.mean(score)

            return -1 * score

        # ---------- Inner MC simulation for computing Utility Value ----------
        # Estimation of the integral via Monte Varlo integration
        MCsize = X_MC.shape[0]
        ESS = 0

        likelihoods = None
        while (ESS > MCsize) or (ESS < 1):

            # Enriching Monte Carlo samples if need be
            if ESS != 0:
                X_MC = self.ExpDesign.generate_samples(
                    MCsize, 'random'
                )

            # Evaluate the MetaModel at the given samples
            Y_MC, std_MC = PCE_Model_can.eval_metamodel(samples=X_MC)

            # Likelihood computation (Comparison of data and simulation
            # results via PCE with candidate design)
            likelihoods = self._normpdf(
                Y_MC, std_MC, self.observations, sigma2Dict
            )

            # Check the Effective Sample Size (1<ESS<MCsize)
            ESS = 1 / np.sum(np.square(likelihoods / np.sum(likelihoods)))

            # Enlarge sample size if it doesn't fulfill the criteria
            if (ESS > MCsize) or (ESS < 1):
                print("--- increasing MC size---")
                MCsize *= 10
                ESS = 0

        # Rejection Step
        # Random numbers between 0 and 1
        unif = np.random.rand(1, MCsize)[0]

        # Reject the poorly performed prior
        accepted = (likelihoods / np.max(likelihoods)) >= unif

        # -------------------- Utility functions --------------------
        # Utility function Eq.2 in Ref. (2)
        # Kullback-Leibler Divergence (Sergey's paper)
        U_J_d = None
        if var.lower() == 'dkl':

            # Prior-based estimation of BME
            logBME = np.log(np.nanmean(likelihoods, dtype=np.longdouble))  # float128))

            # Posterior-based expectation of likelihoods
            # postLikelihoods = likelihoods[accepted]
            # postExpLikelihoods = np.mean(np.log(postLikelihoods))

            # Haun et al implementation
            U_J_d = np.mean(np.log(likelihoods[likelihoods != 0]) - logBME)

            # U_J_d = np.sum(G_n_m_all)
            # Ryan et al (2014) implementation
            # importanceWeights = Likelihoods[Likelihoods!=0]/np.sum(Likelihoods[Likelihoods!=0])
            # U_J_d = np.mean(importanceWeights*np.log(Likelihoods[Likelihoods!=0])) - logBME

            # U_J_d = postExpLikelihoods - logBME

        # Marginal likelihood
        elif var.lower() == 'bme':

            # Prior-based estimation of BME
            logBME = np.log(np.nanmean(likelihoods))
            U_J_d = logBME

        # Bayes risk likelihood
        elif var.lower() == 'bayesrisk':

            U_J_d = -1 * np.var(likelihoods)

        # Entropy-based information gain
        elif var.lower() == 'infentropy':
            # Prior-based estimation of BME
            logBME = np.log(np.nanmean(likelihoods))

            # Posterior-based expectation of likelihoods
            postLikelihoods = likelihoods[accepted]
            postLikelihoods /= np.nansum(likelihoods[accepted])
            postExpLikelihoods = np.mean(np.log(postLikelihoods))

            # Posterior-based expectation of prior densities
            logPriorLikelihoods = []
            logPriorLikelihoods[accepted] = None  # TODO: this is not defined here, just a fix
            postExpPrior = np.mean(logPriorLikelihoods[accepted])

            infEntropy = logBME - postExpPrior - postExpLikelihoods

            U_J_d = infEntropy * -1  # -1 for minimization

        # D-Posterior-precision
        elif var.lower() == 'dpp':
            X_Posterior = X_MC[accepted]
            # covariance of the posterior parameters
            U_J_d = -np.log(np.linalg.det(np.cov(X_Posterior)))

        # A-Posterior-precision
        elif var.lower() == 'app':
            X_Posterior = X_MC[accepted]
            # trace of the posterior parameters
            U_J_d = -np.log(np.trace(np.cov(X_Posterior)))

        else:
            print('The algorithm you requested has not been implemented yet!')

        # Clear memory
        del likelihoods
        del Y_MC
        del std_MC

        return -1 * U_J_d  # -1 is for minimization instead of maximization

    # -------------------------------------------------------------------------
    def dual_annealing(self, method, Bounds, sigma2Dict, var, Run_No,
                       verbose=False):
        """
        Exploration algorithm to find the optimum parameter space.

        Parameters
        ----------
        method : string
            Exploitation method: `VarOptDesign`, `BayesActDesign` and
            `BayesOptDesign`.
        # TODO: BayesActDesign has no corresponding function call in this function!
        Bounds : list of tuples
            List of lower and upper boundaries of parameters.
        sigma2Dict : dict
            A dictionary containing the measurement errors (sigma^2).
        var : unknown
        Run_No : int
            Run number.
        verbose : bool, optional
            Print out a summary. The default is False.

        Returns
        -------
        Run_No : int
            Run number.
        array
            Optimial candidate.

        """

        Model = self.Model
        max_func_itr = self.ExpDesign.max_func_itr

        Res_Global = None
        if method.lower() == 'varoptdesign':
            Res_Global = opt.dual_annealing(self.util_VarBasedDesign,
                                            bounds=Bounds,
                                            args=(Model, var),
                                            maxfun=max_func_itr)

        elif method.lower() == 'bayesoptdesign':
            Res_Global = opt.dual_annealing(self.util_BayesianDesign,
                                            bounds=Bounds,
                                            args=(Model, sigma2Dict, var),
                                            maxfun=max_func_itr)

        if verbose:
            print(f"Global minimum: xmin = {Res_Global.x}, "
                  f"f(xmin) = {Res_Global.fun:.6f}, nfev = {Res_Global.nfev}")

        return Run_No, Res_Global.x

    # -------------------------------------------------------------------------
    def util_AlphOptDesign(self, candidates, var='D-Opt'):
        """
        Enriches the Experimental design with the requested alphabetic
        criterion based on exploring the space with number of sampling points.

        Ref: Hadigol, M., & Doostan, A. (2018). Least squares polynomial chaos
        expansion: A review of sampling strategies., Computer Methods in
        Applied Mechanics and Engineering, 332, 382-407.

        Arguments
        ---------
        candidates : int?
            Number of candidate points to be searched

        var : string
            Alphabetic optimality criterion

        Returns
        -------
        X_new : array of shape (1, n_params)
            The new sampling location in the input space.
        """
        MetaModelOrig = self  # TODO: this doesn't fully seem correct?
        n_new_samples = MetaModelOrig.ExpDesign.n_new_samples
        NCandidate = candidates.shape[0]

        # TODO: Loop over outputs
        OutputName = self.out_names[0]

        # To avoid changes ub original aPCE object
        # MetaModel = deepcopy(MetaModelOrig)

        # Old Experimental design
        oldExpDesignX = self.ExpDesign.X

        # TODO: Only one psi can be selected.
        # Suggestion: Go for the one with the highest LOO error
        # TODO: this is just a patch, need to look at again!
        Scores = list(self.MetaModel.score_dict['b_1'][OutputName].values())
        ModifiedLOO = [1 - score for score in Scores]
        outIdx = np.argmax(ModifiedLOO)

        # Initialize Phi to save the criterion's values
        Phi = np.zeros(NCandidate)

        # TODO: also patched here
        BasisIndices = self.MetaModel.basis_dict['b_1'][OutputName]["y_" + str(outIdx + 1)]
        P = len(BasisIndices)

        # ------ Old Psi ------------
        univ_p_val = self.MetaModel.univ_basis_vals(oldExpDesignX)
        Psi = create_psi(BasisIndices, univ_p_val)

        # ------ New candidates (Psi_c) ------------
        # Assemble Psi_c
        univ_p_val_c = self.MetaModel.univ_basis_vals(candidates)
        Psi_c = create_psi(BasisIndices, univ_p_val_c)

        for idx in range(NCandidate):

            # Include the new row to the original Psi
            Psi_cand = np.vstack((Psi, Psi_c[idx]))

            # Information matrix
            PsiTPsi = np.dot(Psi_cand.T, Psi_cand)
            M = PsiTPsi / (len(oldExpDesignX) + 1)

            if 1e-12 < np.linalg.cond(PsiTPsi) < 1 / sys.float_info.epsilon:
                # faster
                invM = linalg.solve(M, sparse.eye(PsiTPsi.shape[0]).toarray())
            else:
                # stabler
                invM = np.linalg.pinv(M)

            # ---------- Calculate optimality criterion ----------
            # Optimality criteria according to Section 4.5.1 in Ref.

            # D-Opt
            if var.lower() == 'd-opt':
                Phi[idx] = (np.linalg.det(invM)) ** (1 / P)

            # A-Opt
            elif var.lower() == 'a-opt':
                Phi[idx] = np.trace(invM)

            # K-Opt
            elif var.lower() == 'k-opt':
                Phi[idx] = np.linalg.cond(M)

            else:
                raise Exception('The optimality criterion you requested has '
                                'not been implemented yet!')


        return Phi

    # -------------------------------------------------------------------------
    def _normpdf(self, y_hat_pce, std_pce, obs_data, total_sigma2s,
                 rmse=None):
        """
        Calculated gaussian likelihood for given y+std based on given obs+sigma
        # TODO: is this understanding correct?
        
        Parameters
        ----------
        y_hat_pce : dict of 2d np arrays
            Mean output of the surrogate.
        std_pce : dict of 2d np arrays
            Standard deviation output of the surrogate.
        obs_data : dict of 1d np arrays
            Observed data.
        total_sigma2s : pandas dataframe, matches obs_data
            Estimated uncertainty for the observed data.
        rmse : dict, optional
            RMSE values from validation of the surrogate. The default is None.

        Returns
        -------
        likelihoods : dict of float
            The likelihood for each surrogate eval in y_hat_pce compared to the
            observations (?).

        """

        likelihoods = 1.0

        # Loop over the outputs
        for idx, out in enumerate(self.out_names):

            # (Meta)Model Output
            nsamples, nout = y_hat_pce[out].shape

            # Prepare data and remove NaN
            try:
                data = obs_data[out].values[~np.isnan(obs_data[out])]
            except AttributeError:
                data = obs_data[out][~np.isnan(obs_data[out])]

            # Prepare sigma2s
            non_nan_indices = ~np.isnan(total_sigma2s[out])
            tot_sigma2s = total_sigma2s[out][non_nan_indices][:nout].values

            # Surrogate error if valid dataset is given.
            if rmse is not None:
                tot_sigma2s += rmse[out] ** 2
            else:
                tot_sigma2s += np.mean(std_pce[out]) ** 2

            likelihoods *= stats.multivariate_normal.pdf(
                y_hat_pce[out], data, np.diag(tot_sigma2s),
                allow_singular=True)

        # TODO: remove this here
        self.Likelihoods = likelihoods

        return likelihoods

    # -------------------------------------------------------------------------
    def _corr_factor_BME(self, obs_data, total_sigma2s, logBME):
        """
        Calculates the correction factor for BMEs.
        """
        MetaModel = self.MetaModel
        samples = self.ExpDesign.X  # valid_samples
        model_outputs = self.ExpDesign.Y  # valid_model_runs
        n_samples = samples.shape[0]

        # Extract the requested model outputs for likelihood calulation
        output_names = self.out_names

        # TODO: Evaluate MetaModel on the experimental design and ValidSet
        OutputRS, stdOutputRS = MetaModel.eval_metamodel(samples=samples)

        logLik_data = np.zeros(n_samples)
        logLik_model = np.zeros(n_samples)
        # Loop over the outputs
        for idx, out in enumerate(output_names):

            # (Meta)Model Output
            nsamples, nout = model_outputs[out].shape

            # Prepare data and remove NaN
            try:
                data = obs_data[out].values[~np.isnan(obs_data[out])]
            except AttributeError:
                data = obs_data[out][~np.isnan(obs_data[out])]

            # Prepare sigma2s
            non_nan_indices = ~np.isnan(total_sigma2s[out])
            tot_sigma2s = total_sigma2s[out][non_nan_indices][:nout]

            # Covariance Matrix
            covMatrix_data = np.diag(tot_sigma2s)

            for i, sample in enumerate(samples):
                # Simulation run
                y_m = model_outputs[out][i]

                # Surrogate prediction
                y_m_hat = OutputRS[out][i]

                # CovMatrix with the surrogate error
                # covMatrix = np.diag(stdOutputRS[out][i]**2)
                # covMatrix = np.diag((y_m - y_m_hat) ** 2)
                covMatrix = np.diag(
                    np.mean((model_outputs[out] - OutputRS[out]), axis=0) ** 2
                )

                # Compute likelilhood output vs data
                logLik_data[i] += logpdf(
                    y_m_hat, data, covMatrix_data
                )

                # Compute likelilhood output vs surrogate
                logLik_model[i] += logpdf(y_m_hat, y_m, covMatrix)

        # Weight
        logLik_data -= logBME
        weights = np.exp(logLik_model + logLik_data)

        return np.log(np.mean(weights))

    # -------------------------------------------------------------------------
    def _BME_Calculator(self, obs_data, sigma2Dict, rmse=None):
        """
        This function computes the Bayesian model evidence (BME) via Monte
        Carlo integration.

        Parameters
        ----------
        obs_data : dict of 1d np arrays
            Observed data.
        sigma2Dict : pandas dataframe, matches obs_data
            Estimated uncertainty for the observed data.
        rmse : dict of floats, optional
            RMSE values for each output-key. The dafault is None.

        Returns
        -------
        (logBME, KLD, X_Posterior, Likelihoods, distHellinger)
        
        """
        # Initializations
        # TODO: this just does not make sense, recheck from old commits
        if self.valid_likelihoods is not None:
            valid_likelihoods = self.valid_likelihoods
        else:
            valid_likelihoods = []
        valid_likelihoods = np.array(valid_likelihoods)

        post_snapshot = self.ExpDesign.post_snapshot
        if post_snapshot or valid_likelihoods.shape[0] != 0:
            newpath = r'Outputs_SeqPosteriorComparison/likelihood_vs_ref'
            os.makedirs(newpath, exist_ok=True)

        SamplingMethod = 'random'
        MCsize = 10000
        ESS = 0

        # Estimation of the integral via Monte Varlo integration
        while (ESS > MCsize) or (ESS < 1):

            # Generate samples for Monte Carlo simulation
            X_MC = self.ExpDesign.generate_samples(
                MCsize, SamplingMethod
            )

            # Monte Carlo simulation for the candidate design
            Y_MC, std_MC = self.MetaModel.eval_metamodel(samples=X_MC)

            # Likelihood computation (Comparison of data and
            # simulation results via PCE with candidate design)
            Likelihoods = self._normpdf(
                Y_MC, std_MC, obs_data, sigma2Dict, rmse
            )

            # Check the Effective Sample Size (1000<ESS<MCsize)
            ESS = 1 / np.sum(np.square(Likelihoods / np.sum(Likelihoods)))

            # Enlarge sample size if it doesn't fulfill the criteria
            if (ESS > MCsize) or (ESS < 1):
                print(f'ESS={ESS} MC size should be larger.')
                MCsize *= 10
                ESS = 0

        # Rejection Step
        # Random numbers between 0 and 1
        unif = np.random.rand(1, MCsize)[0]

        # Reject the poorly performed prior
        accepted = (Likelihoods / np.max(Likelihoods)) >= unif
        X_Posterior = X_MC[accepted]

        # ------------------------------------------------------------
        # --- Kullback-Leibler Divergence & Information Entropy ------
        # ------------------------------------------------------------
        # Prior-based estimation of BME
        logBME = np.log(np.nanmean(Likelihoods))

        # TODO: Correction factor
        # log_weight = self.__corr_factor_BME(obs_data, sigma2Dict, logBME)

        # Posterior-based expectation of likelihoods
        postExpLikelihoods = np.mean(np.log(Likelihoods[accepted]))

        # Posterior-based expectation of prior densities
        # TODO: this is commented out, as it is not used again
        # postExpPrior = np.mean(
        #     np.log(self.ExpDesign.JDist.pdf(X_Posterior.T))
        # )

        # Calculate Kullback-Leibler Divergence
        # KLD = np.mean(np.log(Likelihoods[Likelihoods!=0])- logBME)
        KLD = postExpLikelihoods - logBME

        # Information Entropy based on Entropy paper Eq. 38
        # infEntropy = logBME - postExpPrior - postExpLikelihoods

        # If post_snapshot is True, plot likelihood vs refrence
        if post_snapshot or valid_likelihoods:
            # Hellinger distance
            valid_likelihoods = np.array(valid_likelihoods)
            ref_like = np.log(valid_likelihoods[(valid_likelihoods > 0)])
            est_like = np.log(Likelihoods[Likelihoods > 0])
            distHellinger = hellinger_distance(ref_like, est_like)

            idx = len([name for name in os.listdir(newpath) if 'Likelihoods_'
                       in name and os.path.isfile(os.path.join(newpath, name))])

            fig, ax = plt.subplots()
            try:
                sns.kdeplot(np.log(valid_likelihoods[valid_likelihoods > 0]),
                            shade=True, color="g", label='Ref. Likelihood')
                sns.kdeplot(np.log(Likelihoods[Likelihoods > 0]), shade=True,
                            color="b", label='Likelihood with PCE')
            except:
                pass

            text = f"Hellinger Dist.={distHellinger:.3f}\n logBME={logBME:.3f}"
            "\n DKL={KLD:.3f}"

            plt.text(0.05, 0.75, text, bbox=dict(facecolor='wheat',
                                                 edgecolor='black',
                                                 boxstyle='round,pad=1'),
                     transform=ax.transAxes)

            fig.savefig(f'./{newpath}/Likelihoods_{idx}.pdf',
                        bbox_inches='tight')
            plt.close()

        else:
            distHellinger = 0.0

        # Bayesian inference with Emulator only for 2D problem
        if post_snapshot and self.MetaModel.n_params == 2 and not idx % 5:
            BayesOpts = BayesInference(self)

            BayesOpts.emulator = True
            BayesOpts.plot_post_pred = False

            # Select the inference method
            import emcee
            BayesOpts.inference_method = "MCMC"
            # Set the MCMC parameters passed to self.mcmc_params
            BayesOpts.mcmc_params = {
                'n_steps': 1e5,
                'n_walkers': 30,
                'moves': emcee.moves.KDEMove(),
                'verbose': False
            }

            # ----- Define the discrepancy model -------
            # TODO: check with Farid if this first line is how it should be
            BayesOpts.measured_data = obs_data
            obs_data = pd.DataFrame(obs_data, columns=self.out_names)
            BayesOpts.measurement_error = obs_data
            # TODO: shouldn't the uncertainty be sigma2Dict instead of obs_data?

            # # -- (Option B) --
            DiscrepancyOpts = Discrepancy('')
            DiscrepancyOpts.type = 'Gaussian'
            DiscrepancyOpts.parameters = obs_data ** 2
            BayesOpts.Discrepancy = DiscrepancyOpts
            # Start the calibration/inference
            Bayes_PCE = BayesOpts.create_inference()
            X_Posterior = Bayes_PCE.posterior_df.values

        return logBME, KLD, X_Posterior, Likelihoods, distHellinger

    # -------------------------------------------------------------------------
    def _validError(self):
        """
        Evaluate the metamodel on the validation samples and calculate the
        error against the corresponding model runs

        Returns
        -------
        rms_error : dict
            RMSE for each validation run.
        valid_error : dict
            Normed (?)RMSE for each validation run.

        """
        # Extract the original model with the generated samples
        valid_model_runs = self.ExpDesign.valid_model_runs

        # Run the PCE model with the generated samples
        valid_PCE_runs, _ = self.MetaModel.eval_metamodel(samples=self.ExpDesign.valid_samples)

        rms_error = {}
        valid_error = {}
        # Loop over the keys and compute RMSE error.
        for key in self.out_names:
            rms_error[key] = mean_squared_error(
                valid_model_runs[key], valid_PCE_runs[key],
                multioutput='raw_values',
                sample_weight=None,
                squared=False)
            # Validation error
            valid_error[key] = (rms_error[key] ** 2)
            valid_error[key] /= np.var(valid_model_runs[key], ddof=1, axis=0)

            # Print a report table
            print("\n>>>>> Updated Errors of {} <<<<<".format(key))
            print("\nIndex  |  RMSE   |  Validation Error")
            print('-' * 35)
            print('\n'.join(f'{i + 1}  |  {k:.3e}  |  {j:.3e}' for i, (k, j)
                            in enumerate(zip(rms_error[key],
                                             valid_error[key]))))

        return rms_error, valid_error

    # -------------------------------------------------------------------------
    def _error_Mean_Std(self):
        """
        Calculates the error in the overall mean and std approximation of the
        surrogate against the mc-reference provided to the model.
        This can only be applied to metamodels of polynomial type

        Returns
        -------
        RMSE_Mean : float
            RMSE of the means 
        RMSE_std : float
            RMSE of the standard deviations

        """
        # Compute the mean and std based on the MetaModel
        pce_means, pce_stds = self.MetaModel._compute_pce_moments()

        # Compute the root mean squared error
        for output in self.out_names:
            # Compute the error between mean and std of MetaModel and OrigModel
            RMSE_Mean = mean_squared_error(
                self.Model.mc_reference['mean'], pce_means[output], squared=False
            )
            RMSE_std = mean_squared_error(
                self.Model.mc_reference['std'], pce_stds[output], squared=False
            )

        return RMSE_Mean, RMSE_std

    def _select_indexes(self, prior_samples, collocation_points):
        """
        ToDo: This function will be used to check the user-input exploration samples, remove training points that
        were already used, and select the first mc_size samples that have not yet been used for training. It should also
        assign an exploration score of 0 to all samples.
        Args:
            prior_samples: array [mc_size, n_params]
                Pre-defined samples from the parameter space, out of which the sample sets should be extracted.
            collocation_points: [tp_size, n_params]
                array with training points which were already used to train the surrogate model, and should therefore
                not be re-explored.

        Returns: array[self.mc_size,]
            With indexes of the new candidate parameter sets, to be read from the prior_samples array

        """
        n_tp = collocation_points.shape[0]
        # a) get index of elements that have already been used
        aux1_ = np.where((prior_samples[:self.mc_samples + n_tp, :] == collocation_points[:, None]).all(-1))[1]
        # b) give each element in the prior a True if it has not been used before
        aux2_ = np.invert(np.in1d(np.arange(prior_samples[:self.mc_samples + n_tp, :].shape[0]), aux1_))
        # c) Select the first d_size_bal elements in prior_sample that have not been used before
        al_unique_index = np.arange(prior_samples[:self.mc_samples + n_tp, :].shape[0])[aux2_]
        al_unique_index = al_unique_index[:self.mc_samples]

        return al_unique_index