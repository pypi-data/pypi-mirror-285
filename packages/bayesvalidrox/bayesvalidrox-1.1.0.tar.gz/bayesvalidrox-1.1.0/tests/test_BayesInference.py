# -*- coding: utf-8 -*-
"""
Test the BayesInference class for bayesvalidrox

Tests are available for the following functions
    _logpdf                 - x
    _kernel_rbf             - x
class BayesInference:
    setup_inference         - x
    create_inference        - x
    perform_bootstrap       Need working model for tests without emulator
    _perturb_data           - x
    create_error_model      Error in the MetaModel
    _eval_model             Need working model to test this
    normpdf                 - x
    _corr_factor_BME_old    - removed
    _corr_factor_BME        - x
    _rejection_sampling     - x
    _posterior_predictive   - x
    plot_post_params        - x 
    plot_log_BME            - x
    _plot_max_a_posteriori  Need working model to test this
    _plot_post_predictive   - x
"""

import sys
import pytest
import numpy as np
import pandas as pd

sys.path.append("src/")
sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns
from bayesvalidrox.surrogate_models.surrogate_models import MetaModel
from bayesvalidrox.pylink.pylink import PyLinkForwardModel as PL
from bayesvalidrox.surrogate_models.engine import Engine
from bayesvalidrox.bayes_inference.discrepancy import Discrepancy
from bayesvalidrox.bayes_inference.mcmc import MCMC
from bayesvalidrox.bayes_inference.bayes_inference import BayesInference
from bayesvalidrox.bayes_inference.bayes_inference import _logpdf, _kernel_rbf



#%% Test _logpdf

def test_logpdf() -> None:
    """
    Calculate loglikelihood

    """
    _logpdf([0], [0], [1])


#%% Test _kernel_rbf

def test_kernel_rbf() -> None:
    """
    Create RBF kernel
    """
    X = [[0, 0], [1, 1.5]]
    pars = [1, 0.5, 1]
    _kernel_rbf(X, pars)


def test_kernel_rbf_lesspar() -> None:
    """
    Create RBF kernel with too few parameters
    """
    X = [[0, 0], [1, 1.5]]
    pars = [1, 2]
    with pytest.raises(AttributeError) as excinfo:
        _kernel_rbf(X, pars)
    assert str(excinfo.value) == 'Provide 3 parameters for the RBF kernel!'


#%% Test MCMC init

def test_BayesInference() -> None:
    """
    Construct a BayesInference object
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mod = PL()
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    engine = Engine(mm, mod, expdes)
    BayesInference(engine)


#%% Test create_inference
# TODO: disabled this test!
def test_create_inference() -> None:
    """
    Run inference
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
    expdes.x_values = np.array([0])  # Error in plots if this is not available

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}  # Error if x_values not given
    mod.Output.names = ['Z']

    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts  # Error if this not class 'DiscrepancyOpts' or dict(?)
    bi.bootstrap = True  # Error if this and bayes_loocv and just_analysis are all False?
    bi.plot_post_pred = False  # Remaining issue in the violinplot
    bi.create_inference()
    # Remaining issue in the violinplot in plot_post_predictive


#%% Test rejection_sampling
def test_rejection_sampling_nologlik() -> None:
    """
    Perform rejection sampling without given log likelihood
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mod = PL()
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    engine = Engine(mm, mod, expdes)
    bi = BayesInference(engine)
    bi.prior_samples = expdes.generate_samples(100, 'random')
    with pytest.raises(AttributeError) as excinfo:
        bi._rejection_sampling()
    assert str(excinfo.value) == 'No log-likelihoods available!'


def test_rejection_sampling_noprior() -> None:
    """
    Perform rejection sampling without prior samples
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mod = PL()
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    engine = Engine(mm, mod, expdes)
    bi = BayesInference(engine)
    with pytest.raises(AttributeError) as excinfo:
        bi._rejection_sampling()
    assert str(excinfo.value) == 'No prior samples available!'


def test_rejection_sampling() -> None:
    """
    Perform rejection sampling
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mod = PL()
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    engine = Engine(mm, mod, expdes)
    bi = BayesInference(engine)
    bi.prior_samples = expdes.generate_samples(100, 'random')
    bi.log_likes = np.swapaxes(np.atleast_2d(np.log(np.random.random(100) * 3)), 0, 1)
    bi._rejection_sampling()


#%% Test _perturb_data

def test_perturb_data() -> None:
    """
    Perturb data
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mod = PL()
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    engine = Engine(mm, mod, expdes)

    bi = BayesInference(engine)
    data = pd.DataFrame()
    data['Z'] = [0.45]
    bi._perturb_data(data, ['Z'])


def test_perturb_data_loocv() -> None:
    """
    Perturb data with bayes_loocv
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mod = PL()
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    engine = Engine(mm, mod, expdes)

    bi = BayesInference(engine)
    data = pd.DataFrame()
    data['Z'] = [0.45]
    bi.bayes_loocv = True
    bi._perturb_data(data, ['Z'])


#%% Test _eval_model

def test_eval_model() -> None:
    """
    Run model with descriptive key
    """
    # TODO: need functioning example model to test this
    None


#%% Test corr_factor_BME

def test_corr_factor_BME() -> None:
    """
    Calculate correction factor
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    mod = PL()
    engine = Engine(mm, mod, expdes)

    obs_data = {'Z': np.array([0.45])}
    total_sigma2s = {'Z': np.array([0.15])}
    logBME = [0, 0, 0]

    bi = BayesInference(engine)
    bi.selected_indices = {'Z': 0}
    bi._corr_factor_BME(obs_data, total_sigma2s, logBME)


def test_corr_factor_BME_selectedindices() -> None:
    """
    Calculate correction factor
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    mod = PL()
    engine = Engine(mm, mod, expdes)

    obs_data = {'Z': np.array([0.45])}
    total_sigma2s = {'Z': np.array([0.15])}
    logBME = [0, 0, 0]

    bi = BayesInference(engine)
    bi.selected_indices = {'Z': 0}
    bi._corr_factor_BME(obs_data, total_sigma2s, logBME)


#%% Test normpdf

def test_normpdf_nosigmas() -> None:
    """
    Run normpdf without any additional sigmas
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': np.array([[0.4], [0.5], [0.45]])}

    mm = MetaModel(inp)
    mod = PL()
    mod.Output.names = ['Z']
    engine = Engine(mm, mod, expdes)

    obs_data = {'Z': np.array([0.45])}
    total_sigma2s = {'Z': np.array([0.15])}

    bi = BayesInference(engine)
    bi.normpdf(expdes.Y, obs_data, total_sigma2s, sigma2=None, std=None)


def test_normpdf_sigma2() -> None:
    """
    Run normpdf with sigma2
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': np.array([[0.4], [0.5], [0.45]])}

    mm = MetaModel(inp)
    mod = PL()
    mod.Output.names = ['Z']
    engine = Engine(mm, mod, expdes)

    obs_data = {'Z': np.array([0.45])}
    total_sigma2s = {'Z': np.array([0.15])}
    sigma2 = [[0]]

    bi = BayesInference(engine)
    bi.normpdf(expdes.Y, obs_data, total_sigma2s, sigma2=sigma2, std=None)


def test_normpdf_allsigmas() -> None:
    """
    Run normpdf with all additional sigmas
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': np.array([[0.4], [0.5], [0.45]])}

    mm = MetaModel(inp)
    mod = PL()
    mod.Output.names = ['Z']
    engine = Engine(mm, mod, expdes)

    obs_data = {'Z': np.array([0.45])}
    total_sigma2s = {'Z': np.array([0.15])}
    sigma2 = [[0]]

    bi = BayesInference(engine)
    bi.normpdf(expdes.Y, obs_data, total_sigma2s, sigma2=sigma2, std=total_sigma2s)


#%% Test setup_inference

def test_setup_inference_noobservation() -> None:
    """
    Test the object setup without given observations
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))

    mod = PL()
    mod.Output.names = ['Z']

    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts
    with pytest.raises(Exception) as excinfo:
        bi.setup_inference()
    assert str(
        excinfo.value) == ('Please provide the observation data as a dictionary via observations attribute or pass the '
                           'csv-file path to MeasurementFile attribute')


def test_setup_inference() -> None:
    """
    Test the object setup with observations
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}
    mod.Output.names = ['Z']

    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts
    bi.setup_inference()


def test_setup_inference_priorsamples() -> None:
    """
    Test the object setup with prior samples set by hand
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}
    mod.Output.names = ['Z']

    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.prior_samples = np.swapaxes(np.array([np.random.normal(0, 1, 100)]), 0, 1)
    bi.Discrepancy = DiscrepancyOpts
    bi.setup_inference()


def test_setup_inference_valid() -> None:
    """
    Test the object setup for valid
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))

    mod = PL()
    mod.observations_valid = {'Z': np.array([0.45])}
    mod.observations_valid = {'Z': np.array([0.45]), 'x_values': np.array([0])}
    mod.Output.names = ['Z']

    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts
    bi.name = 'valid'
    bi.setup_inference()


def test_setup_inference_noname() -> None:
    """
    Test the object setup for an invalid inference name
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}
    mod.Output.names = ['Z']

    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts
    bi.name = ''
    with pytest.raises(Exception) as excinfo:
        bi.setup_inference()
    assert str(excinfo.value) == 'The set inference type is not known! Use either `calib` or `valid`'


#%% Test perform_bootstrap

def test_perform_bootstrap() -> None:
    """
    Do bootstrap
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
    expdes.x_values = np.array([0])  # Error in plots if this is not available

    mm = MetaModel(inp)
    mm.n_params = 1
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}  # Error if x_values not given
    mod.Output.names = ['Z']
    mod.n_obs = 1

    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts
    bi.bootstrap = True
    bi.plot_post_pred = False
    total_sigma2s = {'Z': np.array([0.15])}
    bi.setup_inference()
    bi.perform_bootstrap(total_sigma2s)


def test_perform_bootstrap_bayesloocv() -> None:
    """
    Do bootstrap
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
    expdes.x_values = np.array([0])  # Error in plots if this is not available

    mm = MetaModel(inp)
    mm.n_params = 1
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}  # Error if x_values not given
    mod.Output.names = ['Z']
    mod.n_obs = 1

    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts
    bi.bootstrap = True
    bi.plot_post_pred = False
    total_sigma2s = {'Z': np.array([0.15])}
    bi.setup_inference()
    bi.bayes_loocv = True
    bi.perform_bootstrap(total_sigma2s)


#%% Test create_error_model

def create_error_model_prior() -> None:
    """ 
    Test creating MetaModel error-model for 'prior'
    """
    # TODO: there are issues with the expected formats from the MetaModel
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}

    mm = MetaModel(inp)
    mm.n_params = 1
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}
    mod.Output.names = ['Z']
    mod.n_obs = 1

    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts
    bi.bootstrap = True
    bi.setup_inference()
    bi.bias_inputs = expdes.X
    bi.create_error_model(type_='prior', opt_sigma='B', sampler=None)


def create_error_model_posterior() -> None:
    """ 
    Test creating MetaModel error-model for 'posterior'
    """
    # TODO: there are issues with the expected formats from the MetaModel
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}

    mm = MetaModel(inp)
    mm.n_params = 1
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}
    mod.Output.names = ['Z']
    mod.n_obs = 1

    engine = Engine(mm, mod, expdes)

    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    posterior = pd.DataFrame()
    posterior[None] = [0, 1, 0.5]

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts
    bi.bootstrap = True
    bi.setup_inference()
    bi.bias_inputs = expdes.X
    bi.posterior_df = posterior
    bi.create_error_model(type_='posterior', opt_sigma='B', sampler=None)


#%% Test _posterior_predictive

def test_posterior_predictive() -> None:
    """
    Test posterior predictions
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    prior_samples = np.swapaxes(np.array([np.random.normal(0, 1, 10)]), 0, 1)

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}
    expdes.x_values = np.array([0])  # Error in plots if this is not available

    mm = MetaModel(inp)
    mm.n_params = 1
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))
    y_hat, y_std = mm.eval_metamodel(prior_samples)

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}  # Error if x_values not given
    mod.Output.names = ['Z']
    mod.n_obs = 1

    engine = Engine(mm, mod, expdes)

    total_sigma2s = {'Z': np.array([0.15])}
    posterior = pd.DataFrame()
    posterior[None] = [0, 1, 0.5]
    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts
    bi.bootstrap = True
    bi.plot_post_pred = False
    bi.posterior_df = posterior
    bi.bias_inputs = expdes.X
    bi._mean_pce_prior_pred = y_hat
    bi._std_pce_prior_pred = y_std
    bi.Discrepancy.total_sigma2 = total_sigma2s
    bi.setup_inference()
    bi._posterior_predictive()


def test_posterior_predictive_rejection() -> None:
    """
    Test posterior predictions with rejection inference
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    prior_samples = np.swapaxes(np.array([np.random.normal(0, 1, 10)]), 0, 1)

    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}
    expdes.x_values = np.array([0])  # Error in plots if this is not available

    mm = MetaModel(inp)
    mm.n_params = 1
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))
    y_hat, y_std = mm.eval_metamodel(prior_samples)

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}  # Error if x_values not given
    mod.Output.names = ['Z']
    mod.n_obs = 1

    engine = Engine(mm, mod, expdes)

    total_sigma2s = {'Z': np.array([0.15])}
    posterior = pd.DataFrame()
    posterior[None] = [0, 1, 0.5]
    obsData = pd.DataFrame(mod.observations, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts
    bi.bootstrap = True
    bi.plot_post_pred = False
    bi.posterior_df = posterior
    bi.bias_inputs = expdes.X
    bi._mean_pce_prior_pred = y_hat
    bi._std_pce_prior_pred = y_std
    bi.Discrepancy.total_sigma2 = total_sigma2s
    bi.inference_method = 'rejection'
    bi.setup_inference()
    bi._posterior_predictive()


#%% Test plot_post_params

def test_plot_post_params() -> None:
    """
    Plot posterior dist
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    mod = PL()
    engine = Engine(mm, mod, expdes)

    bi = BayesInference(engine)
    posterior = pd.DataFrame()
    posterior[None] = [0, 1, 0.5]
    bi.posterior_df = posterior
    bi.plot_post_params('B')


def test_plot_post_params_noemulator() -> None:
    """
    Plot posterior dist with emulator = False
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    mod = PL()
    engine = Engine(mm, mod, expdes)

    bi = BayesInference(engine)
    posterior = pd.DataFrame()
    posterior[None] = [0, 1, 0.5]
    bi.posterior_df = posterior
    bi.emulator = False
    bi.plot_post_params('B')


#%% Test plot_log_BME

def test_plot_log_BME() -> None:
    """
    Show the log_BME from bootstrapping
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    mod = PL()
    engine = Engine(mm, mod, expdes)

    bi = BayesInference(engine)
    bi.log_BME = np.array([0, 0.2, 0, 0.2])
    bi.n_tot_measurement = 1
    bi.plot_log_BME()


def test_plot_log_BME_noemulator() -> None:
    """
    Show the log_BME from bootstrapping with emulator = False
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    mod = PL()
    engine = Engine(mm, mod, expdes)

    bi = BayesInference(engine)
    bi.log_BME = np.array([0, 0.2, 0, 0.2])
    bi.n_tot_measurement = 1
    bi.emulator = False
    bi.plot_log_BME()


#%% Test _plot_max_a_posteriori

def test_plot_max_a_posteriori_rejection() -> None:
    """
    Plot MAP estimate for rejection
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    mod = PL()
    engine = Engine(mm, mod, expdes)

    bi = BayesInference(engine)
    bi.inference_method = 'rejection'
    bi._plot_post_predictive()


def test_plot_max_a_posteriori() -> None:
    """
    Plot MAP estimate
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    mod = PL()
    engine = Engine(mm, mod, expdes)

    bi = BayesInference(engine)
    bi._plot_post_predictive()


#%% Test _plot_post_predictive


def test_plot_post_predictive_rejection() -> None:
    """
    Plot posterior predictions for rejection
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    mod = PL()
    engine = Engine(mm, mod, expdes)

    bi = BayesInference(engine)
    bi.inference_method = 'rejection'
    bi._plot_post_predictive()


def test_plot_post_predictive() -> None:
    """
    Plot posterior predictions
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]

    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.n_init_samples = 2

    mm = MetaModel(inp)
    mm.n_params = 1
    mod = PL()
    engine = Engine(mm, mod, expdes)

    bi = BayesInference(engine)
    bi._plot_post_predictive()


#%% Main runs
if __name__ == '__main__':
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    # prior_samples = np.swapaxes(np.array([np.random.normal(0,1,10)]),0,1)

    expdes = ExpDesigns(inp)
    expdes.init_param_space(max_deg=1)
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}
    expdes.x_values = np.array([0])  # Error in plots if this is not

    mm = MetaModel(inp)
    mm.n_params = 1
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(1))
    # y_hat, y_std = mm.eval_metamodel(prior_samples)

    mod = PL()
    mod.observations = {'Z': np.array([0.45])}
    mod.observations = {'Z': np.array([0.45]), 'x_values': np.array([0])}  # Error if x_values not given
    mod.Output.names = ['Z']
    mod.n_obs = 1

    engine = Engine(mm, mod, expdes)

    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    obsData = pd.DataFrame({'Z': np.array([0.45]), 'x_values': np.array([0])}, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2
    DiscrepancyOpts.opt_sigma = 'B'

    bi = BayesInference(engine)
    bi.Discrepancy = DiscrepancyOpts  # Error if this not class 'DiscrepancyOpts' or dict(?)
    bi.bootstrap = True  # Error if this and bayes_loocv and just_analysis are all False?
    bi.plot_post_pred = False  # Remaining issue in the violinplot
    bi.error_model = False
    bi.bayes_loocv = True
    if 1:
        bi.create_inference()
    # opt_sigma = 'B'
    # total_sigma2s = {'Z':np.array([0.15])}
    # data = pd.DataFrame()
    # data['Z'] = [0.45]
    # data['x_values'] = [0.3]
    # bi.setup_inference()
    # bi.perform_bootstrap(total_sigma2s)
    posterior = pd.DataFrame()
    posterior[None] = [0, 1, 0.5]
    bi.posterior_df = posterior
    # bi.bias_inputs = expdes.X
    # bi._mean_pce_prior_pred = y_hat
    # bi._std_pce_prior_pred = y_std
    # bi.Discrepancy.total_sigma2 = total_sigma2s
    # bi.create_error_model(type_ = 'posterior', opt_sigma = 'B', sampler = None)
    # bi._posterior_predictive()
    # bi.plot_post_params('B')
    # bi.log_BME = np.array([[0,0.2],[0,0.2]])
    # bi.n_tot_measurement = 1
    # bi.plot_log_BME()
    bi.inference_method = 'rejection'
    bi._plot_max_a_posteriori()
