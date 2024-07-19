# -*- coding: utf-8 -*-
"""
Test the ExpDesigns class in bayesvalidrox.
Tests are available for the following functions:
    _check_ranges       - x
    fit_dist            - x
    
Class ExpDesigns: 
    generate_samples
    generate_ED
    read_from_file
    random_sampler
    pcm_sampler
Other function tests to be found in parent class 'InputSpace'

"""
import sys
sys.path.append("src/")
import pytest
import numpy as np

from bayesvalidrox.surrogate_models.inputs import Input
import bayesvalidrox.surrogate_models.exp_designs as exp
from bayesvalidrox.surrogate_models.exp_designs import ExpDesigns

#%% Test check_ranges

def test_check_ranges() -> None:
    """
    Check to see if theta lies in expected ranges
    """
    theta = [0.5,1.2]
    ranges = [[0,1],[1,2]]
    assert exp.check_ranges(theta, ranges) == True
    
def test_check_ranges_inv() -> None:
    """
    Check to see if theta lies not in expected ranges
    """
    theta = [1.5,1.2]
    ranges = [[0,1],[1,2]]
    assert exp.check_ranges(theta, ranges) == False
 
#%% Test ExpDesign.pcm_sampler

# TODO: these all have what looks like pcm-sampler issues
if 0:
    def test_pcm_sampler_noinit() -> None:
        """
        Sample via pcm without init_param_space
        """
        x = np.random.uniform(0,1,1000)
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].input_data = x
        exp = ExpDesigns(inp)
        exp.pcm_sampler(4,2)
        
    def test_pcm_sampler_lowdeg() -> None:
        """
        Sample via pcm with init_param_space and small max_deg
        """
        x = np.random.uniform(0,1,1000)
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].input_data = x
        exp = ExpDesigns(inp)
        exp.init_param_space(2)
        exp.pcm_sampler(4,2)
        
    def test_pcm_sampler_highdeg() -> None:
        """
        Sample via pcm with init_param_space and high max_deg
        """
        x = np.random.uniform(0,1,1000)
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].input_data = x
        exp = ExpDesigns(inp)
        exp.init_param_space(30)
        exp.pcm_sampler(4,4)
        
    def test_pcm_sampler_lscm() -> None:
        """
        Sample via pcm with init_param_space and samplin gmethod 'lscm'
        """
        x = np.random.uniform(0,1,1000)
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].input_data = x
        exp = ExpDesigns(inp)
        exp.init_param_space(1)
        exp.sampling_method = 'lscm'
        exp.pcm_sampler(4,4)
        
    def test_pcm_sampler_rawdata_1d() -> None:
        """
        Sample via pcm, init_param_space implicitly, has raw data
        """
        x = np.random.uniform(0,1,(1,1000))
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].input_data = x
        exp = ExpDesigns(inp)
        exp.raw_data = np.random.uniform(0,1,1000)
        exp.pcm_sampler(4,4)   
    
    
def test_pcm_sampler_rawdata() -> None:
    """
    Sample via pcm, init_param_space implicitly, has raw data
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.raw_data = np.random.uniform(0,1,1000)
    with pytest.raises(AttributeError) as excinfo:
        exp.pcm_sampler(4,4)   
    assert str(excinfo.value) == 'Data should be a 1D array'

    
    
#%% Test ExpDesign.random_sampler

def test_random_sampler() -> None:
    """
    Sample randomly, init_param_space implicitly
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.random_sampler(4)
    
def test_random_sampler_largedataJDist0() -> None:
    """
    Sample randomly, init_param_space implicitly, more samples wanted than given, 
    JDist available, priors given via samples
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.init_param_space(max_deg = 1)
    exp.random_sampler(100000) 
    
def test_random_sampler_largedataJDist1() -> None:
    """
    Sample randomly, init_param_space implicitly, more samples wanted than given, 
    JDist available, prior distributions given
    """
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].dist_type = 'normal'
    inp.Marginals[0].parameters = [0,1]
    exp = ExpDesigns(inp)
    exp.init_param_space(max_deg = 1)
    exp.random_sampler(100000) 
     
        
        
def test_random_sampler_rawdata() -> None:
    """
    Sample randomly, init_param_space implicitly, has 2d raw data
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.raw_data = np.random.uniform(0,1,(1,1000))
    exp.random_sampler(4)   
 
def test_random_sampler_rawdata1d() -> None:
    """
    Sample randomly, init_param_space implicitly, has raw data, but only 1d
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.raw_data = np.random.uniform(0,1,1000)
    with pytest.raises(AttributeError) as excinfo:
        exp.random_sampler(4) 
    assert str(excinfo.value) == 'The given raw data for sampling should have two dimensions'
    

def test_random_sampler_fewdata() -> None:
    """
    Sample randomly, init_param_space implicitly, has few 2d raw datapoints
    """
    x = np.random.uniform(0,1,5)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.raw_data = np.random.uniform(0,1,(1,1000))
    exp.random_sampler(7)   
 
    
#%% Test ExpDesign.generate_samples

def test_generate_samples() -> None:
    """
    Generate samples according to chosen scheme
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.generate_samples(4)


#%% Test ExpDesign.generate_ED

def test_generate_ED() -> None:
    """
    Generate ED as is
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp)
    exp.generate_ED(4)
    
def test_generate_ED_negsamplenum():
    """
    Generate ED for neg number of samples
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method = 'user')   
    with pytest.raises(ValueError) as excinfo:
        exp.generate_ED(-1)
    assert str(excinfo.value) == 'A negative number of samples cannot be created. Please provide positive n_samples'
    
    

def test_generate_ED_usernoX() -> None:
    """
    User-defined ED without samples
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method = 'user')
    with pytest.raises(AttributeError) as excinfo:
        exp.generate_ED(4)
    assert str(excinfo.value) == 'User-defined sampling cannot proceed as no samples provided. Please add them to this class as attribute X'

def test_generate_ED_userXdimerr() -> None:
    """
    User-defined ED with wrong shape of samples
    """
    x = np.random.uniform(0,1,1000)
    X = np.random.uniform(0,1,(2,1,1000))
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method = 'user')
    exp.X = X
    with pytest.raises(AttributeError) as excinfo:
        exp.generate_ED(4)
    assert str(excinfo.value) == 'The provided samples shuld have 2 dimensions'
    
if 0: # TODO: JDist not created?
    def test_generate_ED_userX() -> None:
        """
        User-defined ED with wrong shape of samples
        """
        x = np.random.uniform(0,1,1000)
        X = np.random.uniform(0,1,(3,1000))
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].input_data = x
        exp = ExpDesigns(inp, sampling_method = 'user')
        exp.X = X
        exp.generate_ED(4)
    
# TODO: this looks like a pcm-sampler issue
if 0:
    def test_generate_ED_PCM() -> None:
        """
        PCM-defined ED 
        """
        x = np.random.uniform(0,1,1000)
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].input_data = x
        exp = ExpDesigns(inp, sampling_method = 'PCM')
        exp.generate_ED(4)
    
def test_generate_ED_random() -> None:
    """
    Random-defined ED 
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method = 'random')
    exp.generate_ED(4)

if 0: # TODO: JDist not created?
    def test_generate_ED_usertrafo() -> None:
        """
        User-defined ED 
        """
        x = np.random.uniform(0,1,1000)
        X = np.random.uniform(0,1,(1,1000))
        inp = Input()
        inp.add_marginals()
        inp.Marginals[0].input_data = x
        exp = ExpDesigns(inp, sampling_method = 'user')
        exp.meta_Model_type = 'gpe'
        exp.X = X
        exp.generate_ED(4)
    
def test_generate_ED_randomtrafo() -> None:
    """
    User-defined ED 
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method = 'random')
    exp.generate_ED(4)
    
def test_generate_ED_latin() -> None:
    """
    latin-hypercube-defined ED 
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method = 'latin-hypercube')
    exp.generate_ED(4,1)
    
    
#%% Test ExpDesign.read_from_file

def test_read_from_file_nofile():
    """
    No file given to read in
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method = 'user')
    with pytest.raises(AttributeError) as excinfo:
        exp.read_from_file(['Out'])
    assert str(excinfo.value) == 'ExpDesign cannot be read in, please provide hdf5 file first'
    
def test_read_from_file_wrongcomp():
    """
    Correct file, incorrect output name
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method = 'user')
    exp.hdf5_file = 'tests/ExpDesign_testfile.hdf5'
    with pytest.raises(KeyError) as excinfo:
        exp.read_from_file(['Out'])
    assert str(excinfo.value) == "'Unable to open object (component not found)'"
    
def test_read_from_file():
    """
    Read from testfile
    """
    x = np.random.uniform(0,1,1000)
    inp = Input()
    inp.add_marginals()
    inp.Marginals[0].input_data = x
    exp = ExpDesigns(inp, sampling_method = 'user')
    exp.hdf5_file = 'tests/ExpDesign_testfile.hdf5'
    exp.read_from_file(['Z'])
