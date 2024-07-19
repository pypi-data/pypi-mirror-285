# -*- coding: utf-8 -*-
"""
Tests the class Engine in bayesvalidrox
Tests are available for the following functions:
    hellinger_distance   - x
    logpdf               - x
    subdomain            - x
Engine:
    start_engine         - x
    train_normal
    train_sequential
    eval_metamodel
    train_seq_design
    util_VarBasedDesign
    util_BayesianActiveDesign
    util_BayesianDesign
    run_util_func
    dual_annealing
    tradoff_weights      - x
    choose_next_sample
        plotter
    util_AlphOptDesign
    _normpdf            - x    Also move outside the class?
    _corr_factor_BME           Not used again in this class
    _posteriorPlot      - x
    _BME_Calculator     - x
    _validError         - x
    _error_Mean_Std     - x 

"""
import math
import numpy as np
import pandas as pd
import pytest
import sys

sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns
from bayesvalidrox.surrogate_models.surrogate_models import MetaModel
from bayesvalidrox.pylink.pylink import PyLinkForwardModel as PL
from bayesvalidrox.surrogate_models.engine import Engine

import matplotlib as mpl
mpl.rcParams.update(mpl.rcParamsDefault)

#%% Test Engine constructor


def test_engine() -> None:
    """
    Build Engine without inputs
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mod = PL()
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    Engine(mm, mod, expdes)


#%% Test Engine.start_engine

def test_start_engine() -> None:
    """
    Build Engine without inputs
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mod = PL()
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    engine = Engine(mm, mod, expdes)
    engine.start_engine()


#%% Test Engine.train_normal
# TODO: build mock model to do this? - test again in full-length examples

#%% Test Engine._error_Mean_Std

def test__error_Mean_Std_nomc() -> None:
    """
    Compare moments of surrogate and reference without mc-reference
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.0], [1.0]], {'Z': [[0.5], [0.5]]})
    expdes = ExpDesigns(inp)
    mod = PL()
    mod.mc_reference['mean'] = [0.5]
    mod.mc_reference['std'] = [0.0]
    mod.Output.names = ['Z']
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    mean, std = engine._error_Mean_Std()
    assert mean < 0.01 and std < 0.01
    
#def test__error_Mean_Std() -> None:
#    """
#    Compare moments of surrogate and reference
#    """
#    mod = PL()
#    engine = Engine(None, mod, None)
#    engine.start_engine()
#    with pytest.raises(AttributeError) as excinfo:
#        engine._error_Mean_Std()
#    assert str(excinfo.value) == ('Model.mc_reference needs to be given to calculate the surrogate error!')

#%% Test Engine._validError

def test__validError() -> None:
    """
    Calculate validation error
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.0], [1.0]], {'Z': [[0.5], [0.5]]})
    expdes = ExpDesigns(inp)
    mod = PL()
    expdes.valid_samples = [[0.5]]
    expdes.valid_model_runs = {'Z': [[0.5]]}
    mod.Output.names = ['Z']
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    mean, std = engine._validError()
    assert mean['Z'][0] < 0.01  # and std['Z'][0] <0.01


#%% Test Engine._BME_Calculator

def test__BME_Calculator() -> None:
    """
    Calculate BME
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.0], [0.5], [1.0]], {'Z': [[0.5], [0.4], [0.5]]})
    expdes = ExpDesigns(inp)
    expdes.generate_ED(2, max_pce_deg=1)
    mod = PL()
    mod.Output.names = ['Z']
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    obs_data = {'Z': np.array([0.45])}
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    engine._BME_Calculator(obs_data, sigma2Dict)
    # Note: if error appears here it might also be due to inoptimal choice of training samples


def test__BME_Calculator_rmse() -> None:
    """
    Calculate BME with given RMSE
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.0], [0.5], [1.0]], {'Z': [[0.5], [0.4], [0.5]]})
    expdes = ExpDesigns(inp)
    expdes.generate_ED(2, max_pce_deg=1)
    mod = PL()
    mod.Output.names = ['Z']
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    obs_data = {'Z': np.array([0.45])}
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    engine._BME_Calculator(obs_data, sigma2Dict, rmse={'Z': 0.1})
    # Note: if error appears here it might also be due to inoptimal choice of training samples


def test__BME_Calculator_lik() -> None:
    """
    Calculate BME with given validation likelihood and post-snapshot
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.0], [0.5], [1.0]], {'Z': [[0.5], [0.4], [0.5]]})
    expdes = ExpDesigns(inp)
    expdes.generate_ED(2, max_pce_deg=1)
    mod = PL()
    mod.Output.names = ['Z']
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    obs_data = {'Z': np.array([0.45])}
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    expdes.post_snapshot = True

    engine.valid_likelihoods = [0.1]
    engine._BME_Calculator(obs_data, sigma2Dict)


def test__BME_Calculator_2d() -> None:
    """
    Calculate BME with given validation likelihood and post-snapshot, 2d input
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    inp.add_marginals()
    inp.Marginals[1].dist_type = 'normal'
    inp.Marginals[1].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.0, 0.0], [0.5, 0.1], [1.0, 0.9]], {'Z': [[0.5], [0.4], [0.5]]})
    expdes = ExpDesigns(inp)
    expdes.generate_ED(2, max_pce_deg=1)
    mod = PL()
    mod.n_obs = 1
    mod.Output.names = ['Z']
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    obs_data = {'Z': np.array([0.45])}
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    expdes.post_snapshot = True

    engine.valid_likelihoods = [0.1]
    engine._BME_Calculator(obs_data, sigma2Dict)

#%% Test Engine._normpdf

def test__normpdf() -> None:
    """
    Likelihoods based on gaussian dist
    """

    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    mod = PL()
    mod.Output.names = ['Z']

    y_hat_pce = {'Z': np.array([[0.12]])}
    std_pce = {'Z': np.array([[0.05]])}
    obs_data = {'Z': np.array([0.1])}
    sigma2Dict = {'Z': np.array([0.05])}
    total_sigma2s = pd.DataFrame(sigma2Dict, columns=['Z'])

    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    engine._normpdf(y_hat_pce, std_pce, obs_data, total_sigma2s)


def test__normpdf_rmse() -> None:
    """
    Likelihoods based on gaussian dist with rmse
    """

    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    mod = PL()
    mod.Output.names = ['Z']

    y_hat_pce = {'Z': np.array([[0.12]])}
    std_pce = {'Z': np.array([[0.05]])}
    obs_data = {'Z': np.array([0.1])}
    sigma2Dict = {'Z': np.array([0.05])}
    total_sigma2s = pd.DataFrame(sigma2Dict, columns=['Z'])

    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    engine._normpdf(y_hat_pce, std_pce, obs_data, total_sigma2s, rmse={'Z': 0.1})


#%% Test Engine._posteriorPlot

def test__posteriorPlot() -> None:
    """
    Plot posterior
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    expdes.generate_ED(2, max_pce_deg=1)
    mod = PL()
    posterior = np.array([[0], [0.1], [0.2]])
    engine = Engine(mm, mod, expdes)
    engine._posteriorPlot(posterior, ['i'], 'Z')


def test__posteriorPlot_2d() -> None:
    """
    Plot posterior for 2 params
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    inp.add_marginals()
    inp.Marginals[1].dist_type = 'normal'
    inp.Marginals[1].parameters = [0, 1]
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    expdes.generate_ED(2, max_pce_deg=1)
    mod = PL()
    posterior = np.array([[0, 0], [0.1, 1.0], [0.2, 0.5]])
    engine = Engine(mm, mod, expdes)
    engine._posteriorPlot(posterior, ['i', 'j'], 'Z')


