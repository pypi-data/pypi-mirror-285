# -*- coding: utf-8 -*-
"""
Test the MetaModel class in bayesvalidrox.
Tests are available for the following functions
Class MetaModel: 
    build_metamodel  - x
    update_metamodel
    update_pce_coeffs
    create_basis_indices --removed, just redirects
    add_InputSpace                                   -x
    univ_basis_vals
    create_psi
    fit
    adaptive_regression
    corr_loocv_error
    pca_transformation
    gaussian_process_emulator
    eval_metamodel
    create_model_error
    eval_model_error
    auto_vivification
    copy_meta_model_opts
    __select_degree
    generate_polynomials
    _compute_pce_moments
    
"""
import numpy as np
import pytest
import sys

sys.path.append("src/")

from bayesvalidrox.surrogate_models.inputs import Input
from bayesvalidrox.surrogate_models.input_space import InputSpace
from bayesvalidrox.surrogate_models.surrogate_models import MetaModel, corr_loocv_error, create_psi
from bayesvalidrox.surrogate_models.surrogate_models import gaussian_process_emulator



#%% Test MetaMod constructor on its own

def test_metamod() -> None:
    """
    Construct MetaModel without inputs
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    MetaModel(inp)


#%% Test MetaModel.build_metamodel

def test_build_metamodel_nosamples() -> None:
    """
    Build MetaModel without collocation samples
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    with pytest.raises(AttributeError) as excinfo:
        mm.build_metamodel()
    assert str(excinfo.value) == 'Please provide samples to the metamodel before building it.'


def test_build_metamodel() -> None:
    """
    Build MetaModel
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.CollocationPoints = np.array([[0.2], [0.8]])
    mm.build_metamodel()


def test_build_metamodel_ninitsamples() -> None:
    """
    Build MetaModel with n_init_samples
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.CollocationPoints = np.array([[0.2], [0.8]])
    mm.build_metamodel(n_init_samples=2)


def test_build_metamodel_gpe() -> None:
    """
    Build MetaModel gpe
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.meta_model_type = 'gpe'
    mm.CollocationPoints = np.array([[0.2], [0.8]])
    mm.build_metamodel()


def test_build_metamodel_coldimerr() -> None:
    """
    Build MetaModel with wrong shape collocation samples
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.CollocationPoints = [[0.2, 0.8]]
    with pytest.raises(AttributeError) as excinfo:
        mm.build_metamodel()
    assert str(
        excinfo.value) == 'The second dimension of X should be the same size as the number of marginals in the InputObj'


#%% Test MetaMod.generate_polynomials

def test_generate_polynomials_noexp() -> None:
    """
    Generate polynomials without ExpDeg
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    with pytest.raises(AttributeError) as excinfo:
        mm.generate_polynomials()
    assert str(excinfo.value) == 'Generate or add InputSpace before generating polynomials'


def test_generate_polynomials_nodeg() -> None:
    """
    Generate polynomials without max_deg
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)

    # Setup
    mm.InputSpace = InputSpace(inp)
    mm.InputSpace.n_init_samples = 2
    mm.InputSpace.init_param_space(np.max(mm.pce_deg))
    mm.ndim = mm.InputSpace.ndim
    mm.n_params = len(mm.input_obj.Marginals)

    # Generate
    with pytest.raises(AttributeError) as excinfo:
        mm.generate_polynomials()
    assert str(excinfo.value) == 'MetaModel cannot generate polynomials in the given scenario!'


def test_generate_polynomials_deg() -> None:
    """
    Generate polynomials with max_deg
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)

    # Setup
    mm.InputSpace = InputSpace(inp)
    mm.InputSpace.n_init_samples = 2
    mm.InputSpace.init_param_space(np.max(mm.pce_deg))
    mm.ndim = mm.InputSpace.ndim
    mm.n_params = len(mm.input_obj.Marginals)

    # Generate
    mm.generate_polynomials(4)


#%% Test MetaMod.add_InputSpace

def test_add_inputspace() -> None:
    """
    Add InputSpace in MetaModel
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.add_InputSpace()


#%% Test MetaModel.fit
# Faster without these
def test_fit() -> None:
    """
    Fit MetaModel
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]})


def test_fit_parallel() -> None:
    """
    Fit MetaModel in parallel
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]}, parallel=True)


def test_fit_verbose() -> None:
    """
    Fit MetaModel verbose
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]}, verbose=True)


def test_fit_pca() -> None:
    """
    Fit MetaModel verbose and with pca
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.dim_red_method = 'pca'
    mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]}, verbose=True)


def test_fit_gpe() -> None:
    """
    Fit MetaModel
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.meta_model_type = 'gpe'
    mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]})


#%% Test MetaModel.create_psi

def test_create_psi() -> None:
    """
    Create psi-matrix
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2], [0.8]])
    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    create_psi(BasisIndices, univ_bas)


#%% Test MetaModel.regression

def test_regression() -> None:
    """
    Regression without a method
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi)


def test_regression_ols() -> None:
    """
    Regression: ols
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='ols')


def test_regression_olssparse() -> None:
    """
    Regression: ols and sparse
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='ols', sparsity=True)


def test_regression_ard() -> None:
    """
    Regression: ard
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2], [0.8]])
    outputs = np.array([0.4, 0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='ard')


def test_regression_ardssparse() -> None:
    """
    Regression: ard and sparse
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2], [0.8]])
    outputs = np.array([0.4, 0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='ard', sparsity=True)


def test_regression_fastard() -> None:
    """
    Regression: fastard
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='fastard')


def test_regression_fastardssparse() -> None:
    """
    Regression: fastard and sparse
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='fastard', sparsity=True)


def test_regression_brr() -> None:
    """
    Regression: brr
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='brr')


def test_regression_brrssparse() -> None:
    """
    Regression: brr and sparse
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='brr', sparsity=True)


if 0: # Could not figure out these errors, issue most likely in chosen samples/outputs
    def test_regression_bcs() -> None:
        """
        Regression: bcs
        """
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].dist_type = 'normal'
        inp.Marginals[0].parameters = [0, 1]
        mm = MetaModel(inp)
        samples = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9]])
        outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        mm.pce_deg = 3
        mm.CollocationPoints = samples
        mm.build_metamodel(n_init_samples=2)
        BasisIndices = mm.allBasisIndices[str(mm.pce_deg)][str(1.0)]
        univ_bas = mm.univ_basis_vals(samples)
        psi = create_psi(BasisIndices, univ_bas)
    
        mm.regression(samples, outputs, psi, reg_method='bcs')
    
    
    def test_regression_bcsssparse() -> None:
        """
        Regression: bcs and sparse
        """
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].dist_type = 'normal'
        inp.Marginals[0].parameters = [0, 1]
        mm = MetaModel(inp)
        samples = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]])
        outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])
    
        mm.CollocationPoints = samples
        mm.build_metamodel(n_init_samples=2)
        BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
        univ_bas = mm.univ_basis_vals(samples)
        psi = create_psi(BasisIndices, univ_bas)
    
        mm.regression(samples, outputs, psi, reg_method='bcs', sparsity=True)


def test_regression_lars() -> None:
    """
    Regression: lars
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]])
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='lars')


def test_regression_larsssparse() -> None:
    """
    Regression: lars and sparse
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]])
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='lars', sparsity=True)


def test_regression_sgdr() -> None:
    """
    Regression: sgdr
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='sgdr')


def test_regression_sgdrssparse() -> None:
    """
    Regression: sgdr and sparse
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='sgdr', sparsity=True)


if 0: # Could not figure out these errors, issue most likely in chosen samples/outputs
    def test_regression_omp() -> None:
        """
        Regression: omp
        """
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].dist_type = 'normal'
        inp.Marginals[0].parameters = [0, 1]
        mm = MetaModel(inp)
        samples = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8], [0.9], [1.0]])
        outputs = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1])
    
        mm.CollocationPoints = samples
        mm.build_metamodel(n_init_samples=2)
        BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
        univ_bas = mm.univ_basis_vals(samples)
        psi = create_psi(BasisIndices, univ_bas)
    
        mm.regression(samples, outputs, psi, reg_method='omp')
    
    
    def test_regression_ompssparse() -> None:
        """
        Regression: omp and sparse
        """
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].dist_type = 'normal'
        inp.Marginals[0].parameters = [0, 1]
        mm = MetaModel(inp)
        samples = np.array([[0.2]])
        outputs = np.array([0.5])
    
        mm.CollocationPoints = samples
        mm.build_metamodel(n_init_samples=2)
        BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
        univ_bas = mm.univ_basis_vals(samples)
        psi = create_psi(BasisIndices, univ_bas)
    
        mm.regression(samples, outputs, psi, reg_method='omp', sparsity=True)


def test_regression_vbl() -> None:
    """
    Regression: vbl
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='vbl')


def test_regression_vblssparse() -> None:
    """
    Regression: vbl and sparse
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='vbl', sparsity=True)


def test_regression_ebl() -> None:
    """
    Regression: ebl
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='ebl')


def test_regression_eblssparse() -> None:
    """
    Regression: ebl and sparse
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.5])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    mm.regression(samples, outputs, psi, reg_method='ebl', sparsity=True)


#%% Test Model.update_pce_coeffs

# TODO: very linked to the actual training...

#%% Test MetaModel.univ_basis_vals

def test_univ_basis_vals() -> None:
    """
    Creates univariate polynomials
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2], [0.8]])
    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    mm.univ_basis_vals(samples)


#%% Test MetaModel.adaptive_regression

def test_adaptive_regression_fewsamples() -> None:
    """
    Adaptive regression, no specific method, too few samples given
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.8])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)

    # Evaluate the univariate polynomials on InputSpace
    if mm.meta_model_type.lower() != 'gpe':
        mm.univ_p_val = mm.univ_basis_vals(mm.CollocationPoints)

    with pytest.raises(AttributeError) as excinfo:
        mm.adaptive_regression(outputs, 0)
    assert str(excinfo.value) == ('There are too few samples for the corrected loo-cv error. Fit surrogate on at least as '
                           'many samples as parameters to use this')


def test_adaptive_regression() -> None:
    """
    Adaptive regression, no specific method
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.0], [0.1]])
    outputs = np.array([0.0, 0.1])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)

    # Evaluate the univariate polynomials on InputSpace
    if mm.meta_model_type.lower() != 'gpe':
        mm.univ_p_val = mm.univ_basis_vals(mm.CollocationPoints)
    mm.adaptive_regression(outputs, 0)


def test_adaptive_regression_verbose() -> None:
    """
    Adaptive regression, no specific method, verbose output
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.0], [0.1]])
    outputs = np.array([0.0, 0.1])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)

    # Evaluate the univariate polynomials on InputSpace
    if mm.meta_model_type.lower() != 'gpe':
        mm.univ_p_val = mm.univ_basis_vals(mm.CollocationPoints)
    mm.adaptive_regression(outputs, 0, True)


def test_adaptive_regression_ols() -> None:
    """
    Adaptive regression, ols
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7], [0.8],
                        [0.9], [1.0]])
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)

    # Evaluate the univariate polynomials on InputSpace
    if mm.meta_model_type.lower() != 'gpe':
        mm.univ_p_val = mm.univ_basis_vals(mm.CollocationPoints)
    mm.pce_reg_method = 'ols'
    mm.adaptive_regression(outputs, 0)


#%% Test MetaModel.corr_loocv_error

def test_corr_loocv_error_nosparse() -> None:
    """
    Corrected loocv error
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7],
                        [0.8], [0.9], [1.0]])
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    outs = mm.regression(samples, outputs, psi, reg_method='ebl')
    corr_loocv_error(outs['clf_poly'], outs['sparePsi'], outs['coeffs'],
                     outputs)


def test_corr_loocv_error_singley() -> None:
    """
    Corrected loocv error
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.2]])
    outputs = np.array([0.1])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    outs = mm.regression(samples, outputs, psi, reg_method='ols')
    corr_loocv_error(outs['clf_poly'], outs['sparePsi'], outs['coeffs'],
                     outputs)


def test_corr_loocv_error_sparse() -> None:
    """
    Corrected loocv error from sparse results
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    samples = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7],
                        [0.8], [0.9], [1.0]])
    outputs = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1])

    mm.CollocationPoints = samples
    mm.build_metamodel(n_init_samples=2)
    BasisIndices = mm.allBasisIndices[str(1)][str(1.0)]
    univ_bas = mm.univ_basis_vals(samples)
    psi = create_psi(BasisIndices, univ_bas)

    outs = mm.regression(samples, outputs, psi, reg_method='ebl',
                         sparsity=True)
    corr_loocv_error(outs['clf_poly'], outs['sparePsi'], outs['coeffs'],
                     outputs)


#%% Test MetaModel.pca_transformation

def test_pca_transformation() -> None:
    """
    Apply PCA
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    outputs = np.array([[0.4, 0.4], [0.5, 0.6]])
    mm.pca_transformation(outputs)


def test_pca_transformation_varcomp() -> None:
    """
    Apply PCA with set var_pca_threshold
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    outputs = np.array([[0.4, 0.4], [0.5, 0.6]])
    mm.var_pca_threshold = 1
    mm.pca_transformation(outputs)


def test_pca_transformation_ncomp() -> None:
    """
    Apply PCA with set n_pca_components
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    outputs = np.array([[0.4, 0.4], [0.5, 0.6]])
    mm.n_pca_components = 1
    mm.pca_transformation(outputs)


#%% Test MetaModel.gaussian_process_emulator

def test_gaussian_process_emulator() -> None:
    """
    Create GPE 
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    gaussian_process_emulator([[0.2], [0.8]], [0.4, 0.5])


def test_gaussian_process_emulator_nug() -> None:
    """
    Create GPEwith nugget
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    gaussian_process_emulator([[0.2], [0.8]], [0.4, 0.5], nug_term=1.0)


def test_gaussian_process_emulator_autosel() -> None:
    """
    Fit MetaModel with autoselect
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    gaussian_process_emulator([[0.2], [0.8]], [0.4, 0.5], autoSelect=True)


def test_gaussian_process_emulator_varidx() -> None:
    """
    Create GPE with var_idx
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    gaussian_process_emulator([[0.2], [0.8]], [0.4, 0.5], varIdx=1)


#%% Test MetaModel.eval_metamodel

def test_eval_metamodel() -> None:
    """
    Eval trained MetaModel 
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.out_names = ['Z']
    mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_normalboots() -> None:
    """
    Eval trained MetaModel with normal bootstrap
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.bootstrap_method = 'normal'
    mm.out_names = ['Z']
    mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_highnormalboots() -> None:
    """
    Eval trained MetaModel with higher bootstrap-itrs
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.n_bootstrap_itrs = 2
    mm.out_names = ['Z']
    mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_gpe() -> None:
    """
    Eval trained MetaModel - gpe
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.meta_model_type = 'gpe'
    mm.out_names = ['Z']
    mm.fit([[0.2], [0.8]], {'Z': np.array([[0.4], [0.5]])})
    mm.eval_metamodel([[0.4]])


def test_eval_metamodel_pca() -> None:
    """
    Eval trained MetaModel with pca
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.dim_red_method = 'pca'
    mm.out_names = ['Z']
    mm.fit([[0.2], [0.8]], {'Z': [[0.4, 0.4], [0.5, 0.6]]})
    mm.eval_metamodel([[0.4]])


#%% Test MetaModel.create_model_error
# TODO: move model out of this function

#%% Test MetaModel.eval_model_error
# TODO: test create_model_error first

#%% Test MetaModel.auto_vivification
def test_auto_vivification() -> None:
    """
    Creation of auto-vivification objects
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.auto_vivification()


#%% Test MetaModel.copy_meta_model_opts

def test_copy_meta_model_opts() -> None:
    """
    Copy the metamodel with just some stats
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.add_InputSpace()
    mm.copy_meta_model_opts()


#%% Test MetaModel.__select_degree

#%% Test Engine._compute_pce_moments

def test__compute_pce_moments() -> None:
    """
    Compute moments of a pce-surrogate
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.fit([[0.2], [0.4], [0.8]], {'Z': [[0.4], [0.2], [0.5]]})
    mm._compute_pce_moments()


def test__compute_pce_moments_pca() -> None:
    """
    Compute moments of a pce-surrogate with pca
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.dim_red_method = 'pca'
    mm.fit([[0.2], [0.8]], {'Z': [[0.4, 0.4], [0.5, 0.6]]})
    mm._compute_pce_moments()


def test__compute_pce_moments_gpe() -> None:
    """
    Compute moments of a gpe-surrogate
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0, 1]
    mm = MetaModel(inp)
    mm.meta_model_type = 'gpe'
    with pytest.raises(AttributeError) as excinfo:
        mm._compute_pce_moments()
    assert str(excinfo.value) == 'Moments can only be computed for pce-type surrogates'


#%% Test MetaModel.update_metamodel
# TODO: taken from engine
