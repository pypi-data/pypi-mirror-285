#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import emcee
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import multiprocessing
import scipy.stats as st
from scipy import stats
import shutil
import scipy.linalg as spla
from sklearn import preprocessing
os.environ["OMP_NUM_THREADS"] = "1"


# -------------------------------------------------------------------------
def _check_ranges(theta, ranges): # TODO: this is a replica of exp_designs.check_ranges
    """
    This function checks if theta lies in the given ranges.

    Parameters
    ----------
    theta : array
        Proposed parameter set.
    ranges : nested list
        List of the praremeter ranges.

    Returns
    -------
    c : bool
        If it lies in the given range, it return True else False.

    """
    c = True
    # traverse in the list1
    for i, bounds in enumerate(ranges):
        x = theta[i]
        # condition check
        if x < bounds[0] or x > bounds[1]:
            c = False
            return c
    return c

# -------------------------------------------------------------------------
def gelman_rubin(chain, return_var=False):
    """
    The potential scale reduction factor (PSRF) defined by the variance
    within one chain, W, with the variance between chains B.
    Both variances are combined in a weighted sum to obtain an estimate of
    the variance of a parameter \\( \\theta \\).The square root of the
    ratio of this estimates variance to the within chain variance is called
    the potential scale reduction.
    For a well converged chain it should approach 1. Values greater than
    1.1 typically indicate that the chains have not yet fully converged.

    Source: http://joergdietrich.github.io/emcee-convergence.html

    https://github.com/jwalton3141/jwalton3141.github.io/blob/master/assets/posts/ESS/rwmh.py

    Parameters
    ----------
    chain : array (n_walkers, n_steps, n_params)
        The emcee ensamples.

    Returns
    -------
    R_hat : float
        The Gelman-Robin values.

    """
    chain = np.array(chain)
    m_chains, n_iters = chain.shape[:2]

    # Calculate between-chain variance
    θb = np.mean(chain, axis=1)
    θbb = np.mean(θb, axis=0)
    B_over_n = ((θbb - θb)**2).sum(axis=0)
    B_over_n /= (m_chains - 1)

    # Calculate within-chain variances
    ssq = np.var(chain, axis=1, ddof=1)
    W = np.mean(ssq, axis=0)

    # (over) estimate of variance
    var_θ = W * (n_iters - 1) / n_iters + B_over_n

    if return_var:
        return var_θ
    else:
        # The square root of the ratio of this estimates variance to the
        # within chain variance
        R_hat = np.sqrt(var_θ / W)
        return R_hat

# -------------------------------------------------------------------------
def _kernel_rbf(X, hyperparameters):
    """
    Isotropic squared exponential kernel.

    Higher l values lead to smoother functions and therefore to coarser
    approximations of the training data. Lower l values make functions
    more wiggly with wide uncertainty regions between training data points.

    sigma_f controls the marginal variance of b(x)

    Parameters
    ----------
    X : ndarray of shape (n_samples_X, n_features)

    hyperparameters : Dict
        Lambda characteristic length
        sigma_f controls the marginal variance of b(x)
        sigma_0 unresolvable error nugget term, interpreted as random
                error that cannot be attributed to measurement error.
    Returns
    -------
    var_cov_matrix : ndarray of shape (n_samples_X,n_samples_X)
        Kernel k(X, X).

    """
    from sklearn.gaussian_process.kernels import RBF
    min_max_scaler = preprocessing.MinMaxScaler()
    X_minmax = min_max_scaler.fit_transform(X)

    nparams = len(hyperparameters)
    if nparams < 3:
        raise AttributeError('Provide 3 parameters for the RBF kernel!')

    # characteristic length (0,1]
    Lambda = hyperparameters[0]
    # sigma_f controls the marginal variance of b(x)
    sigma2_f = hyperparameters[1]

    rbf = RBF(length_scale=Lambda)
    cov_matrix = sigma2_f * rbf(X_minmax)

    # (unresolvable error) nugget term that is interpreted as random
    # error that cannot be attributed to measurement error.
    sigma2_0 = hyperparameters[2:]
    for i, j in np.ndindex(cov_matrix.shape):
        cov_matrix[i, j] += np.sum(sigma2_0) if i == j else 0

    return cov_matrix


# -------------------------------------------------------------------------
def _logpdf(x, mean, cov):
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

    # Tranform into np arrays
    x = np.array(x)
    mean = np.array(mean)
    cov = np.array(cov)

    n = len(mean)
    L = spla.cholesky(cov, lower=True)
    beta = np.sum(np.log(np.diag(L)))
    dev = x - mean
    alpha = dev.dot(spla.cho_solve((L, True), dev))
    log_lik = -0.5 * alpha - beta - n / 2. * np.log(2 * np.pi)
    return log_lik


class MCMC:
    """
    A class for bayesian inference via a Markov-Chain Monte-Carlo (MCMC)
    Sampler to approximate the posterior distribution of the Bayes theorem:
    $$p(\\theta|\\mathcal{y}) = \\frac{p(\\mathcal{y}|\\theta) p(\\theta)}
                                         {p(\\mathcal{y})}.$$

    This class make inference with emcee package [1] using an Affine Invariant
    Ensemble sampler (AIES) [2].

    [1] Foreman-Mackey, D., Hogg, D.W., Lang, D. and Goodman, J., 2013.emcee:
        the MCMC hammer. Publications of the Astronomical Society of the
        Pacific, 125(925), p.306. https://emcee.readthedocs.io/en/stable/

    [2] Goodman, J. and Weare, J., 2010. Ensemble samplers with affine
        invariance. Communications in applied mathematics and computational
        science, 5(1), pp.65-80.


    Attributes
    ----------
    BayesOpts : obj
        Bayes object.
    engine :  bayesvalidrox.Engine
        Engine object that contains the surrogate, model and expdesign
    mcmc_params : dict
        Dictionary of parameters for the mcmc. Required are
        - init_samples
        - n_steps
        - n_walkers
        - n_burn
        - moves
        - multiplrocessing
        - verbose
    Discrepancy : bayesvalidrox.Discrepancy
        Discrepancy object that described the uncertainty of the data.
    bias_inputs : 
        
    error_model : 
        
    req_outputs : 
        
    selected_indices : 
        
    emulator : 
        
    out_dir : string
        Directory to write the outputs to.
    name : string
        Name of this MCMC selection (?)
    BiasInputs : 
        The default is None.
    """

    def __init__(self, engine, mcmc_params, Discrepancy, bias_inputs, 
                 error_model, req_outputs, selected_indices, emulator,
                 out_dir, name, BiasInputs = None):
        
        # TODO: maybe would be worth to make this a child class of BayesInf?
        # Inputs
        #self.BayesOpts = BayesOpts
        self.engine = engine
        self.Discrepancy = Discrepancy
        
        # Get the needed properties from the BayesInf class
        self.bias_inputs = bias_inputs
        self.error_model = error_model
        self.BiasInputs = BiasInputs
        self.selected_indices = selected_indices
        self.req_outputs = req_outputs
        self.emulator = emulator
        self.out_dir = out_dir
        self.name = name
        
        # Param inits
        self.counter = 0
        self.observation = None
        self.total_sigma2 = None
        self.error_MetaModel = None
        
        # Get MCMC parameters from BayesOpts
        self.initsamples = mcmc_params['init_samples']
        if isinstance(self.initsamples, pd.DataFrame):
            self.initsamples = self.initsamples.values
        self.nsteps = int(mcmc_params['n_steps'])
        self.nwalkers = int(mcmc_params['n_walkers'])
        self.nburn = mcmc_params['n_burn']
        self.moves = mcmc_params['moves']
        self.mp = mcmc_params['multiprocessing']
        self.verbose = mcmc_params['verbose']

    def run_sampler(self, observation, total_sigma2):
        """
        Run the MCMC sampler for the given observations and stdevs.

        Parameters
        ----------
        observation : TYPE
            DESCRIPTION.
        total_sigma2 : TYPE
            DESCRIPTION.

        Returns
        -------
        Posterior_df : TYPE
            DESCRIPTION.

        """
        # Get init values
        engine = self.engine
        Discrepancy = self.Discrepancy
        n_cpus = engine.Model.n_cpus
        ndim = engine.ExpDesign.ndim
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        # Save inputs
        self.observation = observation
        self.total_sigma2 = total_sigma2

        # Set initial samples
        np.random.seed(0)
        if self.initsamples is None:
            try:
                # Version 1 # TODO: recheck this code, it it a mix of old and new
                priorDist = self.engine.ExpDesign.JDist
                initsamples = priorDist.sample(self.nwalkers).T

#                initsamples = engine.ExpDesign.JDist.sample(self.nwalkers).T
#                initsamples = np.swapaxes(np.array([initsamples]),0,1) # TODO: test if this still works with multiple input dists
            except:
                # when aPCE selected - gaussian kernel distribution
                inputSamples = engine.ExpDesign.raw_data.T
                random_indices = np.random.choice(
                    len(inputSamples), size=self.nwalkers, replace=False
                    )
                initsamples = inputSamples[random_indices]

            # Check if ndim == 1, change to 2D vector (nwalkers, ndim)
            # ToDo: Check if it is better to change this in how the samples are taken (line 309)
            if initsamples.ndim == 1:
                initsamples = initsamples.reshape(-1, 1)

        else:
            if self.initsamples.ndim == 1:
                # When MAL is given.
                theta = self.initsamples
                initsamples = [theta + 1e-1*np.multiply(
                    np.random.randn(ndim), theta) for i in
                               range(self.nwalkers)]
            else:
                # Pick samples based on a uniform dist between min and max of
                # each dim
                initsamples = np.zeros((self.nwalkers, ndim))
                bound_tuples = []
                for idx_dim in range(ndim):
                    lower = np.min(self.initsamples[:, idx_dim])
                    upper = np.max(self.initsamples[:, idx_dim])
                    bound_tuples.append((lower, upper))
                    dist = st.uniform(loc=lower, scale=upper-lower)
                    initsamples[:, idx_dim] = dist.rvs(size=self.nwalkers)

                # Update lower and upper
                engine.ExpDesign.bound_tuples = bound_tuples

        # Check if sigma^2 needs to be inferred
        if Discrepancy.opt_sigma != 'B': # TODO: why !='B'?
            sigma2_samples = Discrepancy.get_sample(self.nwalkers)

            # Update initsamples
            initsamples = np.hstack((initsamples, sigma2_samples))
            ndim = initsamples.shape[1]

            # Discrepancy bound
            disc_bound_tuple = Discrepancy.ExpDesign.bound_tuples

            # Update bound_tuples
            engine.ExpDesign.bound_tuples += disc_bound_tuple

        print("\n>>>> Bayesian inference with MCMC for "
              f"{self.name} started. <<<<<<")

        # Set up the backend and clear it in case the file already exists
        backend = emcee.backends.HDFBackend(f"{self.out_dir}/emcee_sampler.h5")
        backend.reset(self.nwalkers, ndim)

        # Define emcee sampler
        # Here we'll set up the computation. emcee combines multiple "walkers",
        # each of which is its own MCMC chain. The number of trace results will
        # be nwalkers * nsteps.
        if self.mp:
            # Run in parallel
            if n_cpus is None:
                n_cpus = multiprocessing.cpu_count()

            with multiprocessing.Pool(n_cpus) as pool:
                sampler = emcee.EnsembleSampler(
                    self.nwalkers, ndim, self.log_posterior, moves=self.moves,
                    pool=pool, backend=backend
                    )

                # Check if a burn-in phase is needed!
                if self.initsamples is None:
                    # Burn-in
                    print("\n Burn-in period is starting:")
                    pos = sampler.run_mcmc(
                        initsamples, self.nburn, progress=True
                        )

                    # Reset sampler
                    pos = pos.coords
                    sampler.reset()
                else:
                    pos = initsamples

                # Production run
                print("\n Production run is starting:")
                pos, prob, state = sampler.run_mcmc(
                    pos, self.nsteps, progress=True
                    )

        else:
            # Run in series and monitor the convergence
            sampler = emcee.EnsembleSampler(
                self.nwalkers, ndim, self.log_posterior, moves=self.moves,
                backend=backend, vectorize=True
                )
            print(f'ndim: {ndim}')
            print(f'initsamples.shape: {initsamples.shape}')
            # Check if a burn-in phase is needed!
            if self.initsamples is None:
                # Burn-in
                print("\n Burn-in period is starting:")
                pos = sampler.run_mcmc(
                    initsamples, self.nburn, progress=True
                    )

                # Reset sampler
                sampler.reset()
                pos = pos.coords
            else:
                pos = initsamples

            # Production run
            print("\n Production run is starting:")

            # Track how the average autocorrelation time estimate changes
            autocorrIdx = 0
            autocorr = np.empty(self.nsteps)
            tauold = np.inf
            autocorreverynsteps = 50

            # sample step by step using the generator sampler.sample
            for sample in sampler.sample(pos,
                                         iterations=self.nsteps,
                                         tune=True,
                                         progress=True):

                # only check convergence every autocorreverynsteps steps
                if sampler.iteration % autocorreverynsteps:
                    continue

                # Train model discrepancy/error
                # TODO: add this back in when the error model is actually working
                #       and this is not dependent on BayesObj
                if self.error_model and not sampler.iteration % 3 * autocorreverynsteps:
                    try:
                        self.error_MetaModel = self.train_error_model(sampler)
                    except:
                        pass

                # Print the current mean acceptance fraction
                if self.verbose:
                    print("\nStep: {}".format(sampler.iteration))
                    acc_fr = np.mean(sampler.acceptance_fraction)
                    print(f"Mean acceptance fraction: {acc_fr:.3f}")

                # compute the autocorrelation time so far
                # using tol=0 means that we'll always get an estimate even if
                # it isn't trustworthy
                tau = sampler.get_autocorr_time(tol=0)
                # average over walkers
                autocorr[autocorrIdx] = np.nanmean(tau)
                autocorrIdx += 1

                # output current autocorrelation estimate
                if self.verbose:
                    print(f"Mean autocorr. time estimate: {np.nanmean(tau):.3f}")
                    list_gr = np.round(gelman_rubin(sampler.chain), 3)
                    print("Gelman-Rubin Test*: ", list_gr)

                # check convergence
                converged = np.all(tau*autocorreverynsteps < sampler.iteration)
                converged &= np.all(np.abs(tauold - tau) / tau < 0.01)
                converged &= np.all(gelman_rubin(sampler.chain) < 1.1)

                if converged:
                    break
                tauold = tau

        # Posterior diagnostics
        try:
            tau = sampler.get_autocorr_time(tol=0)
        except emcee.autocorr.AutocorrError:
            tau = 5

        if all(np.isnan(tau)):
            tau = 5

        burnin = int(2*np.nanmax(tau))
        thin = int(0.5*np.nanmin(tau)) if int(0.5*np.nanmin(tau)) != 0 else 1
        finalsamples = sampler.get_chain(discard=burnin, flat=True, thin=thin)
        acc_fr = np.nanmean(sampler.acceptance_fraction)
        list_gr = np.round(gelman_rubin(sampler.chain[:, burnin:]), 3)

        # Print summary
        print('\n')
        print('-'*15 + 'Posterior diagnostics' + '-'*15)
        print(f"Mean auto-correlation time: {np.nanmean(tau):.3f}")
        print(f"Thin: {thin}")
        print(f"Burn-in: {burnin}")
        print(f"Flat chain shape: {finalsamples.shape}")
        print(f"Mean acceptance fraction*: {acc_fr:.3f}")
        print("Gelman-Rubin Test**: ", list_gr)

        print("\n* This value must lay between 0.234 and 0.5.")
        print("** These values must be smaller than 1.1.")
        print('-'*50)

        print(f"\n>>>> Bayesian inference with MCMC for {self.name} "
              "successfully completed. <<<<<<\n")

        # Extract parameter names and their prior ranges
        par_names = engine.ExpDesign.par_names

        if Discrepancy.opt_sigma != 'B':
            for i in range(len(Discrepancy.InputDisc.Marginals)):
                par_names.append(Discrepancy.InputDisc.Marginals[i].name)

        params_range = engine.ExpDesign.bound_tuples

        # Plot traces
        if self.verbose and self.nsteps < 10000:
            pdf = PdfPages(self.out_dir+'/traceplots.pdf')
            fig = plt.figure()
            for parIdx in range(ndim):
                # Set up the axes with gridspec
                fig = plt.figure()
                grid = plt.GridSpec(4, 4, hspace=0.2, wspace=0.2)
                main_ax = fig.add_subplot(grid[:-1, :3])
                y_hist = fig.add_subplot(grid[:-1, -1], xticklabels=[],
                                         sharey=main_ax)

                for i in range(self.nwalkers):
                    samples = sampler.chain[i, :, parIdx]
                    main_ax.plot(samples, '-')

                    # histogram on the attached axes
                    y_hist.hist(samples[burnin:], 40, histtype='stepfilled',
                                orientation='horizontal', color='gray')

                main_ax.set_ylim(params_range[parIdx])
                main_ax.set_title('traceplot for ' + par_names[parIdx])
                main_ax.set_xlabel('step number')

                # save the current figure
                pdf.savefig(fig, bbox_inches='tight')

                # Destroy the current plot
                plt.clf()
            pdf.close()

        # plot development of autocorrelation estimate
        if not self.mp:
            fig1 = plt.figure()
            steps = autocorreverynsteps*np.arange(1, autocorrIdx+1)
            taus = autocorr[:autocorrIdx]
            plt.plot(steps, steps / autocorreverynsteps, "--k")
            plt.plot(steps, taus)
            plt.xlim(0, steps.max())
            plt.ylim(0, np.nanmax(taus)+0.1*(np.nanmax(taus)-np.nanmin(taus)))
            plt.xlabel("number of steps")
            plt.ylabel(r"mean $\hat{\tau}$")
            fig1.savefig(f"{self.out_dir}/autocorrelation_time.pdf",
                         bbox_inches='tight')

        Posterior_df = pd.DataFrame(finalsamples, columns=par_names)

        return Posterior_df

    # -------------------------------------------------------------------------
    def log_prior(self, theta):
        """
        Calculates the log prior likelihood \\( p(\\theta)\\) for the given
        parameter set(s) \\( \\theta \\).

        Parameters
        ----------
        theta : array of shape (n_samples, n_params)
            Parameter sets, i.e. proposals of MCMC chains.

        Returns
        -------
        logprior: float or array of shape n_samples
            Log prior likelihood. If theta has only one row, a single value is
            returned otherwise an array.

        """
        engine = self.engine
        Discrepancy = self.Discrepancy

        # Find the number of sigma2 parameters
        if Discrepancy.opt_sigma != 'B':
            disc_bound_tuples = Discrepancy.ExpDesign.bound_tuples
            disc_marginals = Discrepancy.ExpDesign.InputObj.Marginals
            disc_prior_space = Discrepancy.ExpDesign.prior_space
            n_sigma2 = len(disc_bound_tuples)
        else:
            n_sigma2 = -len(theta)
        prior_dist = engine.ExpDesign.prior_space
        params_range = engine.ExpDesign.bound_tuples
        theta = theta if theta.ndim != 1 else theta.reshape((1, -1))
        nsamples = theta.shape[0]
        logprior = -np.inf*np.ones(nsamples)

        for i in range(nsamples):
            # Check if the sample is within the parameters' range
            if _check_ranges(theta[i], params_range):
                # Check if all dists are uniform, if yes priors are equal.
                if all(engine.ExpDesign.InputObj.Marginals[i].dist_type == 'uniform'
                       for i in range(engine.ExpDesign.ndim)):
                    logprior[i] = 0.0
                else:
                    logprior[i] = np.log(
                        prior_dist.pdf(theta[i, :-n_sigma2].T)
                        )

                # Check if bias term needs to be inferred
                if Discrepancy.opt_sigma != 'B':
                    if _check_ranges(theta[i, -n_sigma2:],
                                          disc_bound_tuples):
                        if all('unif' in disc_marginals[i].dist_type for i in
                               range(Discrepancy.ExpDesign.ndim)):
                            logprior[i] = 0.0
                        else:
                            logprior[i] += np.log(
                                disc_prior_space.pdf(theta[i, -n_sigma2:])
                                )

        if nsamples == 1:
            return logprior[0]
        else:
            return logprior

    # -------------------------------------------------------------------------
    def log_likelihood(self, theta):
        """
        Computes likelihood \\( p(\\mathcal{Y}|\\theta)\\) of the performance
        of the (meta-)model in reproducing the observation data.

        Parameters
        ----------
        theta : array of shape (n_samples, n_params)
            Parameter set, i.e. proposals of the MCMC chains.

        Returns
        -------
        log_like : array of shape (n_samples)
            Log likelihood.

        """
        MetaModel = self.engine.MetaModel
        Discrepancy = self.Discrepancy

        # Find the number of sigma2 parameters
        if Discrepancy.opt_sigma != 'B':
            disc_bound_tuples = Discrepancy.ExpDesign.bound_tuples
            n_sigma2 = len(disc_bound_tuples)
            # Check if bias term should be inferred
            sigma2 = theta[:, -n_sigma2:]
            theta = theta[:, :-n_sigma2]
        else:
            n_sigma2 = -len(theta)
            sigma2 = None
        
        theta = theta if theta.ndim != 1 else theta.reshape((1, -1))

        # Evaluate Model/MetaModel at theta
        mean_pred, _std_pce_prior_pred = self.eval_model(theta)

        # Surrogate model's error using RMSE of test data
        surrError = MetaModel.rmse if hasattr(MetaModel, 'rmse') else None

        # Likelihood
        log_like = self.normpdf(
            mean_pred, self.observation, self.total_sigma2, sigma2,
            std=surrError
            )
        # TODO: give the second return argument back to BayesInf (parameter of the same name)
        return log_like, _std_pce_prior_pred 

    # -------------------------------------------------------------------------
    def log_posterior(self, theta):
        """
        Computes the posterior likelihood \\(p(\\theta| \\mathcal{Y})\\) for
        the given parameterset.

        Parameters
        ----------
        theta : array of shape (n_samples, n_params)
            Parameter set, i.e. proposals of the MCMC chains.

        Returns
        -------
        log_like : array of shape (n_samples)
            Log posterior likelihood.

        """

        nsamples = 1 if theta.ndim == 1 else theta.shape[0]

        if nsamples == 1:
            if self.log_prior(theta) == -np.inf:
                return -np.inf
            else:
                # Compute log prior
                log_prior = self.log_prior(theta)
                # Compute log Likelihood
                log_likelihood, _std_pce_prior_pred = self.log_likelihood(theta)

                return log_prior + log_likelihood
        else:
            # Compute log prior
            log_prior = self.log_prior(theta)

            # Initialize log_likelihood
            log_likelihood = -np.inf*np.ones(nsamples)

            # find the indices for -inf sets
            non_inf_idx = np.where(log_prior != -np.inf)[0]

            # Compute loLikelihoods
            if non_inf_idx.size != 0:
                log_likelihood[non_inf_idx], _std_pce_prior_pred = self.log_likelihood(
                    theta[non_inf_idx]
                    )

            return log_prior + log_likelihood

    # -------------------------------------------------------------------------
    def eval_model(self, theta):
        """
        Evaluates the (meta-) model at the given theta.

        Parameters
        ----------
        theta : array of shape (n_samples, n_params)
            Parameter set, i.e. proposals of the MCMC chains.

        Returns
        -------
        mean_pred : dict
            Mean model prediction.
        std_pred : dict
            Std of model prediction.

        """
        engine = self.engine
        Model = engine.Model

        if self.emulator:
            # Evaluate the MetaModel
            mean_pred, std_pred = engine.MetaModel.eval_metamodel(samples=theta)
        else:
            # Evaluate the origModel
            mean_pred, std_pred = dict(), dict()

            model_outs, _ = Model.run_model_parallel(
                theta, prevRun_No=self.counter,
                key_str='_MCMC', mp=False, verbose=False)

            # Save outputs in respective dicts
            for varIdx, var in enumerate(Model.Output.names):
                mean_pred[var] = model_outs[var]
                std_pred[var] = np.zeros((mean_pred[var].shape))

            # Remove the folder
            if Model.link_type.lower() != 'function':
                shutil.rmtree(f"{Model.name}_MCMC_{self.counter+1}")

            # Add one to the counter
            self.counter += 1

        if self.error_MetaModel is not None and self.error_model:
            meanPred, stdPred = self.error_MetaModel.eval_model_error(
                self.BiasInputs, mean_pred
                )

        return mean_pred, std_pred

    # -------------------------------------------------------------------------
    def train_error_model(self, sampler):
        """
        Trains an error model using a Gaussian Process Regression.

        Parameters
        ----------
        sampler : obj
            emcee sampler.

        Returns
        -------
        error_MetaModel : obj
            A error model.

        """
        MetaModel = self.engine.MetaModel

        # Prepare the poster samples
        try:
            tau = sampler.get_autocorr_time(tol=0)
        except emcee.autocorr.AutocorrError:
            tau = 5

        if all(np.isnan(tau)):
            tau = 5

        burnin = int(2*np.nanmax(tau))
        thin = int(0.5*np.nanmin(tau)) if int(0.5*np.nanmin(tau)) != 0 else 1
        finalsamples = sampler.get_chain(discard=burnin, flat=True, thin=thin)
        posterior = finalsamples[:, :MetaModel.n_params]

        # Select posterior mean as MAP
        map_theta = posterior.mean(axis=0).reshape((1, MetaModel.n_params))
        # MAP_theta = st.mode(Posterior_df,axis=0)[0]

        # Evaluate the (meta-)model at the MAP
        y_map, y_std_map = MetaModel.eval_metamodel(samples=map_theta)

        # Train a GPR meta-model using MAP
        error_MetaModel = MetaModel.create_model_error(
            self.BiasInputs, y_map, name='Calib')

        return error_MetaModel
    
    # -------------------------------------------------------------------------
    def normpdf(self, outputs, obs_data, total_sigma2s, sigma2=None, std=None):
        """
        Calculates the likelihood of simulation outputs compared with
        observation data.

        Parameters
        ----------
        outputs : dict
            A dictionary containing the simulation outputs as array of shape
            (n_samples, n_measurement) for each model output.
        obs_data : dict
            A dictionary/dataframe containing the observation data.
        total_sigma2s : dict
            A dictionary with known values of the covariance diagonal entries,
            a.k.a. sigma^2.
        sigma2 : array, optional
            An array of the sigma^2 samples, when the covariance diagonal
            entries are unknown and are being jointly inferred. The default is
            None.
        std : dict, optional
            A dictionary containing the root mean squared error as array of
            shape (n_samples, n_measurement) for each model output. The default
            is None.

        Returns
        -------
        logLik : array of shape (n_samples)
            Likelihoods.

        """
        Model = self.engine.Model
        logLik = 0.0

        # Extract the requested model outputs for likelihood calulation
        if self.req_outputs is None:
            req_outputs = Model.Output.names  # TODO: should this then be saved as self.req_outputs?
        else:
            req_outputs = list(self.req_outputs)

        # Loop over the output keys
        for idx, out in enumerate(req_outputs):

            # (Meta)Model Output
            nsamples, nout = outputs[out].shape

            # Prepare data and remove NaN
            try:
                data = obs_data[out].values[~np.isnan(obs_data[out])]
            except AttributeError:
                data = obs_data[out][~np.isnan(obs_data[out])]

            # Prepare data uncertainty / error estimation (sigma2s)
            non_nan_indices = ~np.isnan(total_sigma2s[out])
            tot_sigma2s = total_sigma2s[out][non_nan_indices][:nout]

            # Add the std of the PCE if an emulator is used
            if self.emulator:
                if std is not None:
                    tot_sigma2s += std[out] ** 2

            # Select the data points to compare
            try:
                indices = self.selected_indices[out]
            except:
                indices = list(range(nout))

            # Set up Covariance Matrix
            covMatrix = np.diag(np.diag(tot_sigma2s)[indices, indices])

            # If sigma2 is not given, use given total_sigma2s and move to next itr
            if sigma2 is None:
                logLik += stats.multivariate_normal.logpdf(
                    outputs[out][:, indices], data[indices], covMatrix)
                continue

            # Loop over each run/sample and calculate logLikelihood
            logliks = np.zeros(nsamples)
            for s_idx in range(nsamples):

                # Simulation run
                tot_outputs = outputs[out]

                # Covariance Matrix
                covMatrix = np.diag(tot_sigma2s)

                # Check the type error term
                if self.bias_inputs is not None and self.error_model is None:
                    # Infer a Bias model usig Gaussian Process Regression
                    bias_inputs = np.hstack(
                        (self.bias_inputs[out],
                         tot_outputs[s_idx].reshape(-1, 1)))

                    params = sigma2[s_idx, idx * 3:(idx + 1) * 3]
                    covMatrix = _kernel_rbf(bias_inputs, params)
                else:
                    # Infer equal sigma2s
                    try:
                        sigma_2 = sigma2[s_idx, idx]
                    except TypeError:
                        sigma_2 = 0.0

                    covMatrix += sigma_2 * np.eye(nout)
                    # covMatrix = np.diag(sigma2 * total_sigma2s)

                # Select the data points to compare
                try:
                    indices = self.selected_indices[out]
                except:
                    indices = list(range(nout))
                covMatrix = np.diag(covMatrix[indices, indices])

                # Compute loglikelihood
                logliks[s_idx] = _logpdf(
                    tot_outputs[s_idx, indices], data[indices], covMatrix
                )
            logLik += logliks
        return logLik

