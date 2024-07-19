# -*- coding: utf-8 -*-
"""
Test the MCM class of bayesvalidrox
Tests are available for the following functions
_check_ranges           - x
gelmain_rubin
_iterative_scheme
_my_ESS                 - x
Class MCMC: 
    run_sampler
    log_prior
    log_likelihood
    log_posterior
    eval_model
    train_error_model
    marginal_llk_emcee
"""
import emcee
import sys
import pandas as pd
import numpy as np

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns
from bayesvalidrox.surrogate_models.surrogate_models import MetaModel
from bayesvalidrox.pylink.pylink import PyLinkForwardModel as PL
from bayesvalidrox.surrogate_models.engine import Engine
from bayesvalidrox.bayes_inference.discrepancy import Discrepancy
from bayesvalidrox.bayes_inference.mcmc import MCMC
from bayesvalidrox.bayes_inference.bayes_inference import BayesInference
from bayesvalidrox.bayes_inference.mcmc import _check_ranges, gelman_rubin

sys.path.append("src/")
sys.path.append("../src/")


#%% Test MCMC init

def test_MCMC() -> None:
    """
    Construct an MCMC object
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}
    expdes.x_values = np.array([0])

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))

    mod = PL()
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}
    mod.Output.names = ['Z']
    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    disc = Discrepancy('')
    disc.type = 'Gaussian'
    disc.parameters = (obsData * 0.15) ** 2
    disc.opt_sigma = 'B'

    bi = BayesInference(engine)
    bi.Discrepancy = disc
    bi.inference_method = 'mcmc'
    bi.setup_inference()
    MCMC(engine, bi.mcmc_params, disc, None, 
                 None, None, None, True,
                 '', 'MCMC')


#%% Test run_sampler
if 0: # TODO: issue not resolved here, issue appears due to specific test setup, not in general
    def test_run_sampler() -> None:
        """
        Run short MCMC
    
        Returns
        -------
        None
            DESCRIPTION.
    
        """
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].dist_type = 'normal'
        inp.Marginals[0].parameters = [0, 1]
    
        expdes = ExpDesigns(inp)
        expdes.n_init_samples = 2
        expdes.n_max_samples = 4
        expdes.X = np.array([[0], [1], [0.5]])
        expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}
        expdes.x_values = np.array([0])
    
        mm = MetaModel(inp)
        mm.fit(expdes.X, expdes.Y)
        expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    
        mod = PL()
        mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}
        mod.Output.names = ['Z']
        engine = Engine(mm, mod, expdes)
    
        obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
        disc = Discrepancy('')
        disc.type = 'Gaussian'
        disc.parameters = (obsData * 0.15) ** 2
        disc.opt_sigma = 'B'
    
        bi = BayesInference(engine)
        bi.Discrepancy = disc
        bi.inference_method = 'mcmc'
        bi.setup_inference()
        total_sigma2s = {'Z': np.array([0.15])}
        bi.perform_bootstrap(total_sigma2s)
        data = bi.perturbed_data
        selected_indices = np.nonzero(data)[0]
        mcmc=MCMC(engine, bi.mcmc_params, disc, None, False, None, [],True, 'Outputs_testMCMC', 'MCMC')
        
        mcmc.nburn = 10
        mcmc.nsteps = 50
        mcmc.run_sampler(mod.observations, total_sigma2s)


#%% Test log_prior

#%% Test log_likelihood

#%% Test log_posterior

#%% Test eval_model

#%% Test train_error_model

#%% Test gelmain_rubin

def test_gelman_rubin() -> None:
    """
    Calculate gelman-rubin
    """
    chain = [[[1], [2]]]
    gelman_rubin(chain)


def test_gelman_rubin_returnvar() -> None:
    """
    Calculate gelman-rubin returning var
    """
    chain = [[[1], [2]]]
    gelman_rubin(chain, return_var=True)


#%% Test marginal_llk_emcee

#%% Test _check_ranges

def test_check_ranges() -> None:
    """
    Check to see if theta lies in expected ranges
    """
    theta = [0.5, 1.2]
    ranges = [[0, 1], [1, 2]]
    assert _check_ranges(theta, ranges) is True


def test_check_ranges_inv() -> None:
    """
    Check to see if theta lies not in expected ranges
    """
    theta = [1.5, 1.2]
    ranges = [[0, 1], [1, 2]]
    assert _check_ranges(theta, ranges) is False


#%% Main

if __name__ == '__main__':
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}
    # expdes.x_values = np.array([0]) #  Error in plots if this is not available

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))

    mod = PL()
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}
    mod.Output.names = ['Z']

    engine = Engine(mm, mod, expdes)

    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    disc = Discrepancy('')
    disc.type = 'Gaussian'
    disc.parameters = (obsData * 0.15) ** 2
    disc.opt_sigma = 'B'

    bi = BayesInference(engine)
    bi.Discrepancy = disc
    bi.inference_method = 'mcmc'
    bi.setup_inference()

    # chain = [[[1],[2]]]
    total_sigma2s = {'Z': np.array([0.15])}
    mcmc = MCMC(bi)
    mcmc.nsteps = 50
    mcmc.nburn = 10
    mcmc.run_sampler(mod.observations, total_sigma2s)
    # mcmc.gelmain_rubin(chain)

    chain = [[[1], [2]]]
    gelman_rubin(chain, return_var=True)
