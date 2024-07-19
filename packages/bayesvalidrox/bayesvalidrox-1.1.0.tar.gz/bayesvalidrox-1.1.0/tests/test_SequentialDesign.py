# -*- coding: utf-8 -*-
"""
Test the SequentialDesign class for bayesvalidrox

Tests are available for the following functions
    logpdf               - x
    subdomain            - x
    hellinger_distance   - x
SequentialDesign:
    start_seqdesign         
    choose_next_sample
        plotter
    tradoff_weights      - x
    run_util_func
    util_VarBasedDesign
    util_BayesianActiveDesign
    util_BayesianDesign
    dual_annealing
    util_AlphOptDesign
    _normpdf            - x    Also move outside the class?
    _corr_factor_BME           Not used again in this class
    _posteriorPlot      - x
    _BME_Calculator     - x
    _validError         - x
    _error_Mean_Std     - x 
    _select_indices


"""
import math
import numpy as np
import pandas as pd
import sys
import pytest

sys.path.append("../src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns
from bayesvalidrox.surrogate_models.sequential_design import SequentialDesign, hellinger_distance, subdomain, logpdf
from bayesvalidrox.surrogate_models.surrogate_models import MetaModel
from bayesvalidrox.pylink.pylink import PyLinkForwardModel as PL
from bayesvalidrox.surrogate_models.engine import Engine
from bayesvalidrox.bayes_inference.discrepancy import Discrepancy

#%% Test Engine.tradeoff_weights

def test_tradeoff_weights_None() -> None:
    """
    Tradeoff weights with no scheme
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    mod = PL()
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    weights = seqDes.tradeoff_weights(None, [[0], [1]], {'Z': [[0.4], [0.5]]})
    assert weights[0] == 0 and weights[1] == 1


def test_tradeoff_weights_equal() -> None:
    """
    Tradeoff weights with 'equal' scheme
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    mod = PL()
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    weights = seqDes.tradeoff_weights('equal', [[0], [1]], {'Z': [[0.4], [0.5]]})
    assert weights[0] == 0.5 and weights[1] == 0.5


def test_tradeoff_weights_epsdecr() -> None:
    """
    Tradeoff weights with 'epsilon-decreasing' scheme
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2
    expdes.n_max_samples = 3
    expdes.X = np.array([[0], [1]])
    mod = PL()
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    weights = seqDes.tradeoff_weights('epsilon-decreasing', expdes.X, {'Z': [[0.4], [0.5]]})
    assert weights[0] == 1.0 and weights[1] == 0.0


def test_tradeoff_weights_adaptive() -> None:
    """
    Tradeoff weights with 'adaptive' scheme
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    expdes = ExpDesigns(inp)
    expdes.n_init_samples = 2
    expdes.n_max_samples = 3
    expdes.X = np.array([[0], [1]])
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    weights = seqDes.tradeoff_weights('adaptive', expdes.X, {'Z': [[0.4], [0.5]]})
    assert weights[0] == 0.5 and weights[1] == 0.5


def test_tradeoff_weights_adaptiveit1() -> None:
    """
    Tradeoff weights with 'adaptive' scheme for later iteration (not the first)
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
    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes._y_hat_prev, _ = mm.eval_metamodel(samples=np.array([[0.1], [0.2], [0.6]]))
    seqDes.tradeoff_weights('adaptive', expdes.X, expdes.Y)



#%% Test Engine.choose_next_sample

def test_choose_next_sample() -> None:
    """
    Chooses new sample using all standard settings (exploration, random, space-filling,...)
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
    expdes.explore_method = 'random'
    expdes.exploit_method = 'Space-filling'
    expdes.util_func = 'Space-filling'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    x, nan = seqDes.choose_next_sample()
    assert x.shape[0] == 1 and x.shape[1] == 1


def test_choose_next_sample_da_spaceparallel() -> None:
    """
    Chooses new sample using dual-annealing and space-filling, parallel=True
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
    expdes.explore_method = 'dual-annealing'
    expdes.exploit_method = 'Space-filling'
    expdes.util_func = 'Space-filling'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    seqDes.parallel = True
    x, nan = seqDes.choose_next_sample()
    assert x.shape[0] == 1 and x.shape[1] == 1


def test_choose_next_sample_da_spacenoparallel() -> None:
    """
    Chooses new sample using dual-annealing and space-filling, parallel = False
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
    expdes.explore_method = 'dual-annealing'
    expdes.exploit_method = 'Space-filling'
    expdes.util_func = 'Space-filling'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    seqDes.parallel = False
    x, nan = seqDes.choose_next_sample()
    assert x.shape[0] == 1 and x.shape[1] == 1


def test_choose_next_sample_loo_space() -> None:
    """
    Chooses new sample using all LOO-CV and space-filling
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
    expdes.explore_method = 'LOO-CV'
    expdes.exploit_method = 'Space-filling'
    expdes.util_func = 'Space-filling'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    x, nan = seqDes.choose_next_sample()
    assert x.shape[0] == 1 and x.shape[1] == 1


def test_choose_next_sample_vor_space() -> None:
    """
    Chooses new sample using voronoi, space-filling
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
    expdes.explore_method = 'voronoi'
    expdes.exploit_method = 'Space-filling'
    expdes.util_func = 'Space-filling'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    #x, nan = seqDes.choose_next_sample()
    #assert x.shape[0] == 1 and x.shape[1] == 1


    # TODO: removed this functionality for v1.1.0
    with pytest.raises(AttributeError) as excinfo:
        x, nan = seqDes.choose_next_sample()
    assert str(excinfo.value) == ('Exploration with voronoi currently not supported!')

def test_choose_next_sample_latin_space() -> None:
    """
    Chooses new sample using all latin-hypercube, space-filling
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
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'Space-filling'
    expdes.util_func = 'Space-filling'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    x, nan = seqDes.choose_next_sample()
    assert x.shape[0] == 1 and x.shape[1] == 1


def test_choose_next_sample_latin_alphD() -> None:
    """
    Chooses new sample using all latin-hypercube, alphabetic (D)
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
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'alphabetic'
    expdes.util_func = 'D-Opt'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    x, nan = seqDes.choose_next_sample(var=expdes.util_func)
    assert x.shape[0] == 1 and x.shape[1] == 1


def test_choose_next_sample_latin_alphK() -> None:
    """
    Chooses new sample using all latin-hypercube, alphabetic (K)
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
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'alphabetic'
    expdes.util_func = 'K-Opt'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    x, nan = seqDes.choose_next_sample(var=expdes.util_func)
    assert x.shape[0] == 1 and x.shape[1] == 1


def test_choose_next_sample_latin_alphA() -> None:
    """
    Chooses new sample using all latin-hypercube, alphabetic (A)
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
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'alphabetic'
    expdes.util_func = 'A-Opt'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    x, nan = seqDes.choose_next_sample(var=expdes.util_func)
    assert x.shape[0] == 1 and x.shape[1] == 1


def test_choose_next_sample_latin_VarALM() -> None:
    """
    Chooses new sample using all latin-hypercube, VarDesign (ALM)
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
    expdes.tradeoff_scheme = 'equal'
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'VarOptDesign'
    expdes.util_func = 'ALM'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    x, nan = seqDes.choose_next_sample(var=expdes.util_func)
    assert x.shape[0] == 1 and x.shape[1] == 1


def test_choose_next_sample_latin_VarEIGF() -> None:
    """
    Chooses new sample using all latin-hypercube, VarDesign (EIGF)
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
    expdes.tradeoff_scheme = 'equal'
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'VarOptDesign'
    expdes.util_func = 'EIGF'

    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    x, nan = seqDes.choose_next_sample(var=expdes.util_func)
    assert x.shape[0] == 1 and x.shape[1] == 1


# TODO: shape mismatch for the total score
if 0:
    def test_choose_next_sample_latin_VarLOO() -> None:
        """
        Chooses new sample using all latin-hypercube, VarDesign (LOOCV)
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
        expdes.tradeoff_scheme = 'equal'
        expdes.explore_method = 'latin-hypercube'
        expdes.exploit_method = 'VarOptDesign'
        expdes.util_func = 'LOOCV'
    
        mm = MetaModel(inp)
        mm.fit(expdes.X, expdes.Y)
        expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
        mod = PL()
        
        engine = Engine(mm, mod, expdes)
        engine.start_engine()
        seqDes = SequentialDesign(mm, mod, expdes, engine)
        seqDes.out_names = ['Z']
        x, nan = seqDes.choose_next_sample(var=expdes.util_func)
        assert x.shape[0] == 1 and x.shape[1] == 1


def test_choose_next_sample_latin_BODMI() -> None:
    """
    Chooses new sample using all latin-hypercube, BayesOptDesign (MI)
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    expdes = ExpDesigns(inp)
    expdes.sampling_method = 'user'
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}
    expdes.tradeoff_scheme = 'equal'
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'BayesOptDesign'
    expdes.util_func = 'MI'
    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    seqDes.observations = {'Z': np.array([0.45])}
    # seqDes.choose_next_sample(sigma2=None, n_candidates=5, var='DKL')
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    seqDes.choose_next_sample(sigma2=sigma2Dict, var=expdes.util_func)

def test_choose_next_sample_vor_BODMI() -> None:
    """
    Chooses new sample using all voronoi, BayesOptDesign (MI)
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    expdes = ExpDesigns(inp)
    expdes.sampling_method = 'user'
    expdes.n_init_samples = 2
    expdes.n_max_samples = 4
    expdes.X = np.array([[0], [1], [0.5]])
    expdes.Y = {'Z': [[0.4], [0.5], [0.45]]}
    expdes.tradeoff_scheme = 'equal'
    expdes.explore_method = 'voronoi'
    expdes.exploit_method = 'BayesOptDesign'
    expdes.util_func = 'MI'
    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    seqDes.observations = {'Z': np.array([0.45])}
    # seqDes.choose_next_sample(sigma2=None, n_candidates=5, var='DKL')
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    
    # TODO: removed this functionality for v1.1.0
    with pytest.raises(AttributeError) as excinfo:
        seqDes.choose_next_sample(sigma2=sigma2Dict, var=expdes.util_func)
    assert str(excinfo.value) == ('Exploration with voronoi currently not supported!')



def test_choose_next_sample_latin_BODALC() -> None:
    """
    Chooses new sample using all latin-hypercube, BayesOptDesign (ALC)
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
    expdes.tradeoff_scheme = 'equal'
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'BayesOptDesign'
    expdes.util_func = 'ALC'
    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    seqDes.observations = {'Z': np.array([0.45])}
    # seqDes.choose_next_sample(sigma2=None, n_candidates=5, var='DKL')
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    seqDes.choose_next_sample(sigma2=sigma2Dict, var=expdes.util_func)


def test_choose_next_sample_latin_BODDKL() -> None:
    """
    Chooses new sample using all latin-hypercube, BayesOptDesign (DKL)
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
    expdes.tradeoff_scheme = 'equal'
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'BayesOptDesign'
    expdes.util_func = 'DKL'
    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    seqDes.observations = {'Z': np.array([0.45])}
    # seqDes.choose_next_sample(sigma2=None, n_candidates=5, var='DKL')
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    seqDes.choose_next_sample(sigma2=sigma2Dict, var=expdes.util_func)


def test_choose_next_sample_latin_BODDPP() -> None:
    """
    Chooses new sample using all latin-hypercube, BayesOptDesign (DPP)
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
    expdes.tradeoff_scheme = 'equal'
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'BayesOptDesign'
    expdes.util_func = 'DPP'
    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    seqDes.observations = {'Z': np.array([0.45])}
    # seqDes.choose_next_sample(sigma2=None, n_candidates=5, var='DKL')
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    seqDes.choose_next_sample(sigma2=sigma2Dict, var=expdes.util_func)


def test_choose_next_sample_latin_BODAPP() -> None:
    """
    Chooses new sample using all latin-hypercube, BayesOptDesign (APP)
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
    expdes.tradeoff_scheme = 'equal'
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'BayesOptDesign'
    expdes.util_func = 'APP'
    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    seqDes.observations = {'Z': np.array([0.45])}
    # seqDes.choose_next_sample(sigma2=None, n_candidates=5, var='DKL')
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    seqDes.choose_next_sample(sigma2=sigma2Dict, var=expdes.util_func)


def test_choose_next_sample_latin_BODMI_() -> None:
    """
    Chooses new sample using all latin-hypercube, BayesOptDesign (MI)
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
    expdes.tradeoff_scheme = 'equal'
    expdes.explore_method = 'latin-hypercube'
    expdes.exploit_method = 'BayesOptDesign'
    expdes.util_func = 'MI'
    mm = MetaModel(inp)
    mm.fit(expdes.X, expdes.Y)
    expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
    mod = PL()
    
    engine = Engine(mm, mod, expdes)
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)
    seqDes.out_names = ['Z']
    seqDes.observations = {'Z': np.array([0.45])}
    # seqDes.choose_next_sample(sigma2=None, n_candidates=5, var='DKL')
    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    seqDes.choose_next_sample(sigma2=sigma2Dict, var=expdes.util_func)

if 0:
    def test_choose_next_sample_latin_BADBME() -> None:
        """
        Chooses new sample using all latin-hypercube, BayesActDesign (BME)
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
        expdes.tradeoff_scheme = 'equal'
        expdes.explore_method = 'latin-hypercube'
        expdes.exploit_method = 'BayesActDesign'
        expdes.util_func = 'BME'
        mm = MetaModel(inp)
        mm.fit(expdes.X, expdes.Y)
        expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
        mod = PL()
        
        engine = Engine(mm, mod, expdes)
        engine.start_engine()
        seqDes = SequentialDesign(mm, mod, expdes, engine)
        seqDes.out_names = ['Z']
        seqDes.observations = {'Z': np.array([0.45])}
        # seqDes.choose_next_sample(sigma2=None, n_candidates=5, var='DKL')
        sigma2Dict = {'Z': np.array([0.05])}
        sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
        seqDes.n_obs = 1
        seqDes.choose_next_sample(sigma2=sigma2Dict, var=expdes.util_func)
    
    
    def test_choose_next_sample_latin_BADDKL() -> None:
        """
        Chooses new sample using all latin-hypercube, BayesActDesign (DKL)
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
        expdes.tradeoff_scheme = 'equal'
        expdes.explore_method = 'latin-hypercube'
        expdes.exploit_method = 'BayesActDesign'
        expdes.util_func = 'DKL'
        mm = MetaModel(inp)
        mm.fit(expdes.X, expdes.Y)
        expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
        mod = PL()
        
        engine = Engine(mm, mod, expdes)
        engine.start_engine()
        seqDes = SequentialDesign(mm, mod, expdes, engine)
        seqDes.out_names = ['Z']
        seqDes.observations = {'Z': np.array([0.45])}
        # seqDes.choose_next_sample(sigma2=None, n_candidates=5, var='DKL')
        sigma2Dict = {'Z': np.array([0.05])}
        sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
        seqDes.n_obs = 1
        seqDes.choose_next_sample(sigma2=sigma2Dict, var=expdes.util_func)
    
    
    def test_choose_next_sample_latin_BADinfEntropy() -> None:
        """
        Chooses new sample using all latin-hypercube, BayesActDesign (infEntropy)
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
        expdes.tradeoff_scheme = 'equal'
        expdes.explore_method = 'latin-hypercube'
        expdes.exploit_method = 'BayesActDesign'
        expdes.util_func = 'infEntropy'
        mm = MetaModel(inp)
        mm.fit(expdes.X, expdes.Y)
        expdes.generate_ED(expdes.n_init_samples, max_pce_deg=np.max(mm.pce_deg))
        mod = PL()
        
        engine = Engine(mm, mod, expdes)
        engine.start_engine()
        seqDes = SequentialDesign(mm, mod, expdes, engine)
        seqDes.out_names = ['Z']
        seqDes.observations = {'Z': np.array([0.45])}
        # seqDes.choose_next_sample(sigma2=None, n_candidates=5, var='DKL')
        sigma2Dict = {'Z': np.array([0.05])}
        sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
        seqDes.n_obs = 1
        seqDes.choose_next_sample(sigma2=sigma2Dict, var=expdes.util_func)

#%% Test hellinger_distance

def test_hellinger_distance_isnan() -> None:
    """
    Calculate Hellinger distance-nan
    """
    P = [0]
    Q = [1]
    math.isnan(hellinger_distance(P, Q))


def test_hellinger_distance_0() -> None:
    """
    Calculate Hellinger distance-0
    """
    P = [0, 1, 2]
    Q = [1, 0, 2]
    assert hellinger_distance(P, Q) == 0.0


def test_hellinger_distance_1() -> None:
    """
    Calculate Hellinger distance-1
    """
    P = [0, 1, 2]
    Q = [0, 0, 0]
    assert hellinger_distance(P, Q) == 1.0

#%% Test logpdf

def test_logpdf() -> None:
    """
    Calculate log-pdf
    """
    logpdf(np.array([0.1]), np.array([0.2]), np.array([0.1]))


#%% Test Engine._corr_factor_BME
# TODO: not used again here?

#%% Test subdomain

def test_subdomain() -> None:
    """
    Create subdomains from bounds
    """
    subdomain([(0, 1), (0, 1)], 2)


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
    engine.start_engine()
    seqDes = SequentialDesign(mm, mod, expdes, engine)

    sigma2Dict = {'Z': np.array([0.05])}
    sigma2Dict = pd.DataFrame(sigma2Dict, columns=['Z'])
    obsData = pd.DataFrame({'Z': np.array([0.45]), 'x_values': np.array([0])}, columns=mod.Output.names)
    DiscrepancyOpts = Discrepancy('')
    DiscrepancyOpts.type = 'Gaussian'
    DiscrepancyOpts.parameters = (obsData * 0.15) ** 2
    DiscrepancyOpts.opt_sigma = 'B'
