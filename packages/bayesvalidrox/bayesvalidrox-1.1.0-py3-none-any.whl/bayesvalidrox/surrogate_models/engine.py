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
from scipy import stats
from scipy.spatial import distance
from sklearn.metrics import mean_squared_error
import seaborn as sns
import sys
from tqdm import tqdm

from bayesvalidrox.bayes_inference.bayes_inference import BayesInference
from bayesvalidrox.bayes_inference.discrepancy import Discrepancy
from.surrogate_models import MetaModel as MM
from .sequential_design import SequentialDesign, hellinger_distance, logpdf


class Engine:

    def __init__(self, MetaMod, Model, ExpDes):
        self.MetaModel = MetaMod
        self.Model = Model
        self.ExpDesign = ExpDes
        self.parallel = False
        self.trained = False

        # Init other parameters
        self.bound_tuples = None
        self.errorModel = None
        self.LCerror = None
        self.n_obs = None
        self.observations = None
        self.out_names = None
        self.seqMinDist = None
        self.seqRMSEStd = None
        self.SeqKLD = None
        self.SeqDistHellinger = None
        self.SeqBME = None
        self.seqValidError = None
        self.SeqModifiedLOO = None
        self.valid_likelihoods = None
        self._y_hat_prev = None
        self.emulator = False
        self.verbose = False

    def start_engine(self) -> None:
        """
        Do all the preparations that need to be run before the actual training

        Returns
        -------
        None

        """
        self.out_names = self.Model.Output.names
        if isinstance(self.MetaModel, MM):
            self.emulator = True
            self.MetaModel.out_names = self.out_names
            if self.verbose:
                print('MetaModel has been given, `emulator` will be set to `True`')
        else:
            self.emulator = False
            if self.verbose:
                print('MetaModel has not been given, `emulator` will be set to `False`')

    def train_normal(self, parallel=False, verbose=False, save=False) -> None:
        """
        Trains surrogate on static samples only.
        Samples are taken from the experimental design and the specified 
        model is run on them.
        Alternatively the samples can be read in from a provided hdf5 file.
        

        Returns
        -------
        None

        """
        self.verbose = verbose
        self.start_engine()

        ExpDesign = self.ExpDesign
        MetaModel = self.MetaModel

        # Read ExpDesign (training and targets) from the provided hdf5
        if ExpDesign.hdf5_file is not None:
            ExpDesign.read_from_file(self.out_names)
        else:
            # Check if an old hdf5 file exists: if yes, rename it
            hdf5file = f'ExpDesign_{self.Model.name}.hdf5'
            if os.path.exists(hdf5file):
                #     os.rename(hdf5file, 'old_'+hdf5file)
                file = pathlib.Path(hdf5file)
                file.unlink()

        # Prepare X samples 
        # For training the surrogate use ExpDesign.X_tr, ExpDesign.X is for the model to run on 
        if self.emulator:
            maxdeg = np.max(MetaModel.pce_deg)
        else:
            maxdeg = 1
        ExpDesign.generate_ED(ExpDesign.n_init_samples,
                              #transform=True,
                              max_pce_deg=maxdeg)

        # Run simulations at X 
        if not hasattr(ExpDesign, 'Y') or ExpDesign.Y is None:
            print('\n Now the forward model needs to be run!\n')
            ED_Y, up_ED_X = self.Model.run_model_parallel(ExpDesign.X, mp=parallel)
            ExpDesign.Y = ED_Y
        else:
            # Check if a dict has been passed.
            if not type(ExpDesign.Y) is dict:
                raise Exception('Please provide either a dictionary or a hdf5'
                                'file to ExpDesign.hdf5_file argument.')

        # Separate output dict and x-values
        if 'x_values' in ExpDesign.Y:
            ExpDesign.x_values = ExpDesign.Y['x_values']
            del ExpDesign.Y['x_values']
        else:
            if self.verbose:
                print('No x_values are given, this might lead to issues during PostProcessing')

        # Fit the surrogate
        if self.emulator:
            MetaModel.fit(ExpDesign.X, ExpDesign.Y, parallel, verbose)

        # Save what there is to save
        if save:
            # Save surrogate
            if not os.path.exists('surrogates/'):
                os.makedirs('surrogates/')
            with open(f'surrogates/surrogate_{self.Model.name}.pk1', 'wb') as output:
                joblib.dump(MetaModel, output, 2)

            # Zip the model run directories
            if self.Model.link_type.lower() == 'pylink' and \
                    self.ExpDesign.sampling_method.lower() != 'user':
                self.Model.zip_subdirs(self.Model.name, f'{self.Model.name}_')

        # Set that training was done
        self.trained = True

    def train_sequential(self, parallel=False, verbose=False) -> None:
        """
        Train the surrogate in a sequential manner.
        First build and train evereything on the static samples, then iterate
        choosing more samples and refitting the surrogate on them.

        Returns
        -------
        None

        """
        # self.train_normal(parallel, verbose)
        self.parallel = parallel
        self.train_seq_design(parallel, verbose)

    # -------------------------------------------------------------------------
    def eval_metamodel(self, samples=None, nsamples=None,
                       sampling_method='random', return_samples=False,
                       parallel = False):
        """
        Evaluates metamodel at the requested samples. One can also generate
        nsamples.

        Parameters
        ----------
        samples : array of shape (n_samples, n_params), optional
            Samples to evaluate metamodel at. The default is None.
        nsamples : int, optional
            Number of samples to generate, if no `samples` is provided. The
            default is None.
        sampling_method : str, optional
            Type of sampling, if no `samples` is provided. The default is
            'random'.
        return_samples : bool, optional
            Retun samples, if no `samples` is provided. The default is False.
        parallel : bool, optional
            Set to true if the evaluations should be done in parallel.
            The default is False.

        Returns
        -------
        mean_pred : dict
            Mean of the predictions.
        std_pred : dict
            Standard deviatioon of the predictions.
        """
        # Generate or transform (if need be) samples
        if samples is None:
            # Generate
            samples = self.ExpDesign.generate_samples(
                nsamples,
                sampling_method
            )

        # Transformation to other space is to be done in the MetaModel
        # TODO: sort the transformations better
        if self.emulator:
            mean_pred, std_pred = self.MetaModel.eval_metamodel(samples)
        else:
            mean_pred , X = self.Model.run_model_parallel(samples, mp=parallel)

        if return_samples:
            if self.emulator:
                return mean_pred, std_pred, samples
            else:
                return mean_pred, samples
        else:
            if self.emulator:
                return mean_pred, std_pred
            else:
                return mean_pred, None
                

    # -------------------------------------------------------------------------
    def train_seq_design(self, parallel=False, verbose=False):
        """
        Starts the adaptive sequential design for refining the surrogate model
        by selecting training points in a sequential manner.

        Returns
        -------
        MetaModel : object
            Meta model object.

        """
        self.parallel = parallel

        # Initialization
        self.SeqModifiedLOO = {}
        self.seqValidError = {}
        self.SeqBME = {}
        self.SeqKLD = {}
        self.SeqDistHellinger = {}
        self.seqRMSEMean = {}
        self.seqRMSEStd = {}
        self.seqMinDist = []

        if not hasattr(self.MetaModel, 'valid_samples') or self.MetaModel.valid_samples is None:
            self.ExpDesign.valid_samples = []
            self.ExpDesign.valid_model_runs = []
            self.valid_likelihoods = []

        # validError = None

        # Determine the metamodel type
        if self.MetaModel.meta_model_type.lower() != 'gpe':
            pce = True
        else:
            pce = False
        #mc_ref = True if bool(self.Model.mc_reference) else False
        mc_ref = False
        if self.Model.mc_reference != {}:
            mc_ref = True
            self.Model.read_observation('mc_ref')

        # Get the parameters
        max_n_samples = self.ExpDesign.n_max_samples
        mod_LOO_threshold = self.ExpDesign.mod_LOO_threshold
        n_canddidate = self.ExpDesign.n_canddidate
        post_snapshot = self.ExpDesign.post_snapshot
        n_replication = self.ExpDesign.n_replication
        util_func = self.ExpDesign.util_func
        output_name = self.out_names

        # Setup the Sequential Design object
        self.SeqDes = SequentialDesign(self.MetaModel, self.Model, self.ExpDesign, self)
        self.SeqDes.out_names = self.out_names

        # Handle if only one UtilityFunctions is provided
        if not isinstance(util_func, list):
            util_func = [self.ExpDesign.util_func]

        # Read observations or MCReference
        # TODO: recheck the logic in this if statement
        if (len(self.Model.observations) != 0 or self.Model.meas_file is not None) and hasattr(self.MetaModel,
                                                                                               'Discrepancy'):
            self.observations = self.Model.read_observation()
            obs_data = self.observations
        else:
            obs_data = []
            # TODO: TotalSigma2 not defined if not in this else???
            # TODO: no self.observations if in here
            TotalSigma2 = {}

        # ---------- Initial self.MetaModel ----------
        if not self.trained:
            self.train_normal(parallel=parallel, verbose=verbose)

        initMetaModel = deepcopy(self.MetaModel)

        # Validation error if validation set is provided.
        if self.ExpDesign.valid_model_runs:
            init_rmse, init_valid_error = self._validError()  # initMetaModel)
            init_valid_error = list(init_valid_error.values())
        else:
            init_rmse = None

        # Check if discrepancy is provided
        if len(obs_data) != 0 and hasattr(self.MetaModel, 'Discrepancy'):
            TotalSigma2 = self.MetaModel.Discrepancy.parameters

            # Calculate the initial BME
            out = self._BME_Calculator(
                obs_data, TotalSigma2, init_rmse)
            init_BME, init_KLD, init_post, init_likes, init_dist_hellinger = out
            print(f"\nInitial BME: {init_BME:.2f}")
            print(f"Initial KLD: {init_KLD:.2f}")

            # Posterior snapshot (initial)
            if post_snapshot:
                parNames = self.ExpDesign.par_names
                print('Posterior snapshot (initial) is being plotted...')
                self._posteriorPlot(init_post, parNames, 'SeqPosterior_init')

        # Check the convergence of the Mean & Std
        if mc_ref and pce:
            init_rmse_mean, init_rmse_std = self._error_Mean_Std()
            print(f"Initial Mean and Std error: {init_rmse_mean:.2f},"
                  f" {init_rmse_std:.2f}")

        # Read the initial experimental design
        Xinit = self.ExpDesign.X
        init_n_samples = len(self.ExpDesign.X)
        initYprev = self.ExpDesign.Y  # initMetaModel.ModelOutputDict
        # self.MetaModel.ModelOutputDict = self.ExpDesign.Y
        initLCerror = initMetaModel.LCerror
        n_itrs = max_n_samples - init_n_samples

        # Get some initial statistics
        # Read the initial ModifiedLOO
        init_mod_LOO = []
        if pce:
            Scores_all, varExpDesignY = [], []
            for out_name in output_name:
                y = self.ExpDesign.Y[out_name]
                Scores_all.append(list(
                    self.MetaModel.score_dict['b_1'][out_name].values()))
                if self.MetaModel.dim_red_method.lower() == 'pca':
                    pca = self.MetaModel.pca['b_1'][out_name]
                    components = pca.transform(y)
                    varExpDesignY.append(np.var(components, axis=0))
                else:
                    varExpDesignY.append(np.var(y, axis=0))

            Scores = [item for sublist in Scores_all for item in sublist]
            weights = [item for sublist in varExpDesignY for item in sublist]
            init_mod_LOO = [np.average([1 - score for score in Scores],
                                       weights=weights)]

        prevMetaModel_dict = {}
        # prevExpDesign_dict = {}
        # Can run sequential design multiple times for comparison
        for repIdx in range(n_replication):
            print(f'\n>>>> Replication: {repIdx + 1}<<<<')

            # util_func: the function to use inside the type of exploitation
            for util_f in util_func:
                print(f'\n>>>> Utility Function: {util_f} <<<<')
                # To avoid changes ub original aPCE object
                self.ExpDesign.X = Xinit
                self.ExpDesign.Y = initYprev
                self.ExpDesign.LCerror = initLCerror

                # Set the experimental design
                Xprev = Xinit
                total_n_samples = init_n_samples
                Yprev = initYprev

                Xfull = []

                # Store the initial ModifiedLOO
                if pce:
                    print("\nInitial ModifiedLOO:", init_mod_LOO)
                    SeqModifiedLOO = np.array(init_mod_LOO)

                if len(self.ExpDesign.valid_model_runs) != 0:
                    SeqValidError = np.array(init_valid_error)

                # Check if data is provided
                if len(obs_data) != 0 and hasattr(self.MetaModel, 'Discrepancy'):
                    SeqBME = np.array([init_BME])
                    SeqKLD = np.array([init_KLD])
                    SeqDistHellinger = np.array([init_dist_hellinger])

                if mc_ref and pce:
                    seqRMSEMean = np.array([init_rmse_mean])
                    seqRMSEStd = np.array([init_rmse_std])

                # ------- Start Sequential Experimental Design -------
                postcnt = 1
                for itr_no in range(1, n_itrs + 1):
                    print(f'\n>>>> Iteration number {itr_no} <<<<')

                    # Save the metamodel prediction before updating
                    prevMetaModel_dict[itr_no] = deepcopy(self.MetaModel)
                    # prevExpDesign_dict[itr_no] = deepcopy(self.ExpDesign)
                    # TODO: recheck that the iteration numbers here match what it should do!
                    if itr_no > 1:
                        pc_model = prevMetaModel_dict[itr_no - 1]
                        self.SeqDes._y_hat_prev, _ = pc_model.eval_metamodel(
                            samples=Xfull[-1].reshape(1, -1))
                        del prevMetaModel_dict[itr_no - 1]
                    if itr_no == 1 and self.ExpDesign.tradeoff_scheme == 'adaptive':
                        # TODO: this was added just as a fix, needs to be reworked
                        # Changes: itr_no-1 -> itr_no
                        #          Xfull[-1] -> Xprev
                        #print(Xprev.shape)
                        pc_model = prevMetaModel_dict[itr_no]
                        self.SeqDes._y_hat_prev, _ = pc_model.eval_metamodel(
                            samples=Xprev)

                    # Optimal Bayesian Design
                    # self.MetaModel.ExpDesignFlag = 'sequential'
                    Xnew, updatedPrior = self.SeqDes.choose_next_sample(TotalSigma2,
                                                                 n_canddidate,
                                                                 util_f)

#                    Xnew, updatedPrior = self.choose_next_sample(TotalSigma2,
#                                                                 n_canddidate,
#                                                                 util_f)
                    S = np.min(distance.cdist(Xinit, Xnew, 'euclidean'))
                    self.seqMinDist.append(S)
                    print(f"\nmin Dist from OldExpDesign: {S:2f}")
                    print("\n")

                    # Evaluate the full model response at the new sample
                    Ynew, _ = self.Model.run_model_parallel(
                        Xnew, prevRun_No=total_n_samples
                    )
                    total_n_samples += Xnew.shape[0]

                    # ------ Plot the surrogate model vs Origninal Model ------
                    if self.ExpDesign.adapt_verbose:
                        from .adaptPlot import adaptPlot
                        y_hat, std_hat = self.MetaModel.eval_metamodel(
                            samples=Xnew
                        )
                        adaptPlot(
                            self.MetaModel, Ynew, y_hat, std_hat,
                            plotED=False
                        )

                    # -------- Retrain the surrogate model -------
                    # Extend new experimental design
                    Xfull = np.vstack((Xprev, Xnew))

                    # Updating experimental design Y
                    for out_name in output_name:
                        Yfull = np.vstack((Yprev[out_name], Ynew[out_name]))
                        self.ExpDesign.Y[out_name] = Yfull

                    # Pass new design to the metamodel object
                    self.ExpDesign.sampling_method = 'user'
                    self.ExpDesign.X = Xfull
                    # self.ExpDesign.Y = self.MetaModel.ModelOutputDict

                    # Save the Experimental Design for next iteration
                    Xprev = Xfull
                    Yprev = self.ExpDesign.Y

                    # Pass the new prior as the input
                    # TODO: another look at this - no difference apc to pce to gpe?
                    self.MetaModel.input_obj.poly_coeffs_flag = False
                    if updatedPrior is not None:
                        self.MetaModel.input_obj.poly_coeffs_flag = True
                        print("updatedPrior:", updatedPrior.shape)
                        # Arbitrary polynomial chaos
                        for i in range(updatedPrior.shape[1]):
                            self.MetaModel.input_obj.Marginals[i].dist_type = None
                            x = updatedPrior[:, i]
                            self.MetaModel.input_obj.Marginals[i].raw_data = x

                    # Train the surrogate model for new ExpDesign
                    self.train_normal(parallel=False)

                    # -------- Evaluate the retrained surrogate model -------
                    # Extract Modified LOO from Output
                    if pce:
                        Scores_all, varExpDesignY = [], []
                        for out_name in output_name:
                            y = self.ExpDesign.Y[out_name]
                            Scores_all.append(list(
                                self.MetaModel.score_dict['b_1'][out_name].values()))
                            if self.MetaModel.dim_red_method.lower() == 'pca':
                                pca = self.MetaModel.pca['b_1'][out_name]
                                components = pca.transform(y)
                                varExpDesignY.append(np.var(components,
                                                            axis=0))
                            else:
                                varExpDesignY.append(np.var(y, axis=0))
                        Scores = [item for sublist in Scores_all for item
                                  in sublist]
                        weights = [item for sublist in varExpDesignY for item
                                   in sublist]
                        ModifiedLOO = [np.average(
                            [1 - score for score in Scores], weights=weights)]

                        print('\n')
                        print(f"Updated ModifiedLOO {util_f}:\n", ModifiedLOO)
                        print('\n')

                    # Compute the validation error
                    if self.ExpDesign.valid_model_runs:
                        rmse, validError = self._validError()  # self.MetaModel)
                        ValidError = list(validError.values())
                    else:
                        rmse = None

                    # Store updated ModifiedLOO
                    if pce:
                        SeqModifiedLOO = np.vstack(
                            (SeqModifiedLOO, ModifiedLOO))
                        if len(self.ExpDesign.valid_model_runs) != 0:
                            SeqValidError = np.vstack(
                                (SeqValidError, ValidError))
                    # -------- Caclulation of BME as accuracy metric -------
                    # Check if data is provided
                    if len(obs_data) != 0:
                        # Calculate the initial BME
                        out = self._BME_Calculator(obs_data, TotalSigma2, rmse)
                        BME, KLD, Posterior, likes, DistHellinger = out
                        print('\n')
                        print(f"Updated BME: {BME:.2f}")
                        print(f"Updated KLD: {KLD:.2f}")
                        print('\n')

                        # Plot some snapshots of the posterior
                        step_snapshot = self.ExpDesign.step_snapshot
                        if post_snapshot and postcnt % step_snapshot == 0:
                            parNames = self.ExpDesign.par_names
                            print('Posterior snapshot is being plotted...')
                            self._posteriorPlot(Posterior, parNames,
                                                f'SeqPosterior_{postcnt}')
                        postcnt += 1

                    # Check the convergence of the Mean&Std
                    if mc_ref and pce:
                        print('\n')
                        RMSE_Mean, RMSE_std = self._error_Mean_Std()
                        print(f"Updated Mean and Std error: {RMSE_Mean:.2f}, "
                              f"{RMSE_std:.2f}")
                        print('\n')

                    # Store the updated BME & KLD
                    # Check if data is provided
                    if len(obs_data) != 0:
                        SeqBME = np.vstack((SeqBME, BME))
                        SeqKLD = np.vstack((SeqKLD, KLD))
                        SeqDistHellinger = np.vstack((SeqDistHellinger,
                                                      DistHellinger))
                    if mc_ref and pce:
                        seqRMSEMean = np.vstack((seqRMSEMean, RMSE_Mean))
                        seqRMSEStd = np.vstack((seqRMSEStd, RMSE_std))

                    if pce and any(LOO < mod_LOO_threshold
                                   for LOO in ModifiedLOO):
                        break

                    # Clean up
                    if len(obs_data) != 0:
                        del out
                    print()
                    print('-' * 50)
                    print()

                # Store updated ModifiedLOO and BME in dictonary
                strKey = f'{util_f}_rep_{repIdx + 1}'
                if pce:
                    self.SeqModifiedLOO[strKey] = SeqModifiedLOO
                if len(self.ExpDesign.valid_model_runs) != 0:
                    self.seqValidError[strKey] = SeqValidError

                # Check if data is provided
                if len(obs_data) != 0:
                    self.SeqBME[strKey] = SeqBME
                    self.SeqKLD[strKey] = SeqKLD
                if hasattr(self.MetaModel, 'valid_likelihoods') and \
                        self.valid_likelihoods:
                    self.SeqDistHellinger[strKey] = SeqDistHellinger
                if mc_ref and pce:
                    self.seqRMSEMean[strKey] = seqRMSEMean
                    self.seqRMSEStd[strKey] = seqRMSEStd


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
    def _posteriorPlot(self, posterior, par_names, key):
        """
        Plot the posterior of a specific key as a corner plot

        Parameters
        ----------
        posterior : 2d np.array
            Samples of the posterior.
        par_names : list of strings
            List of the parameter names.
        key : string
            Output key that this posterior belongs to.

        Returns
        -------
        figPosterior : corner.corner
            Plot of the posterior.

        """

        # Initialization
        newpath = r'Outputs_SeqPosteriorComparison/posterior'
        os.makedirs(newpath, exist_ok=True)

        bound_tuples = self.ExpDesign.bound_tuples
        n_params = len(par_names)
        font_size = 40
        if n_params == 2:

            figPosterior, ax = plt.subplots(figsize=(15, 15))

            sns.kdeplot(x=posterior[:, 0], y=posterior[:, 1],
                        fill=True, ax=ax, cmap=plt.cm.jet,
                        clip=bound_tuples)
            # Axis labels
            plt.xlabel(par_names[0], fontsize=font_size)
            plt.ylabel(par_names[1], fontsize=font_size)

            # Set axis limit
            plt.xlim(bound_tuples[0])
            plt.ylim(bound_tuples[1])

            # Increase font size
            plt.xticks(fontsize=font_size)
            plt.yticks(fontsize=font_size)

            # Switch off the grids
            plt.grid(False)

        else:
            import corner
            figPosterior = corner.corner(posterior, labels=par_names,
                                         title_fmt='.2e', show_titles=True,
                                         title_kwargs={"fontsize": 12})

        figPosterior.savefig(f'./{newpath}/{key}.pdf', bbox_inches='tight')
        plt.close()

        # Save the posterior as .npy
        np.save(f'./{newpath}/{key}.npy', posterior)

        return figPosterior

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
        if self.Model.mc_reference == {}:
            raise AttributeError('Model.mc_reference needs to be given to calculate the surrogate error!')
        # Compute the mean and std based on the MetaModel
        pce_means, pce_stds = self.MetaModel._compute_pce_moments()

        # Compute the root mean squared error
        for output in self.out_names:
            # Compute the error between mean and std of MetaModel and OrigModel
            # TODO: write test that checks if mc_reference exists
            RMSE_Mean = mean_squared_error(
                self.Model.mc_reference['mean'], pce_means[output], squared=False
            )
            RMSE_std = mean_squared_error(
                self.Model.mc_reference['std'], pce_stds[output], squared=False
            )

        return RMSE_Mean, RMSE_std
