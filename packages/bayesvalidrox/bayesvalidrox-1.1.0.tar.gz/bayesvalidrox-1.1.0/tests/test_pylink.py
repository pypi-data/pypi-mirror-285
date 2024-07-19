# -*- coding: utf-8 -*-
"""
Test the PyLinkForwardModel class in bayesvalidrox.
Tests are available for the following functions
    within_range *not used again in here            - x
PyLinkForwardModel:
    read_observation *not used again in here        - x
    read_mc_reference *not used again in here       - x
    read_output *used only once
    update_input_params *used only once
    run_command *used only once
    run_forwardmodel
    run_model_parallel
    _store_simulations *used only once
    zip_subdirs *used in metamodel again
OutputData:
    constructor only

"""
import sys
sys.path.append("src/")
import pandas as pd
import pytest

from bayesvalidrox.pylink.pylink import PyLinkForwardModel as PL
from bayesvalidrox.pylink.pylink import within_range

#%% Test constructor

def test_PL() -> None:
    """
    Build PyLinkForwardModel without inputs
    """
    PL()


#%% Test PyLink.within_range

def test_within_range_noarray() -> None:
    """
    Value not an array
    """
    with pytest.raises(AttributeError) as excinfo:
        within_range(1,2,3)
    assert str(excinfo.value) == 'The given values should be a 1D array, but are not'

def test_within_range_2d() -> None:
    """
    Value not an array
    """
    with pytest.raises(AttributeError) as excinfo:
        within_range([[1],[2]],2,3)
    assert str(excinfo.value) == 'The given values should be a 1D array, but are not'

def test_within_range_err() -> None:
    """
    Value not in range
    """
    assert within_range([1],2,3) == False

def test_within_range_switchbounds() -> None:
    """
    Switched min and max
    """
    with pytest.raises(ValueError) as excinfo:
        within_range([1],4,3)
    assert str(excinfo.value) == 'The lower and upper bounds do not form a valid range, they might be switched'

def test_within_range() -> None:
    """
    Value in range
    """
    assert within_range([1],0,3) == True
    
#%% Test PyLink.read_observation
# TODO: check that the shape,... of what is read in matches wha is in the files
def test_read_observation_none() -> None:
    """
    Read observation - 'calib' without anything
    """
    pl = PL()
    with pytest.raises(Exception) as excinfo:
        pl.read_observation()
    assert str(excinfo.value) == "Please provide the observation data as a dictionary via observations attribute or pass the csv-file path to MeasurementFile attribute"
    
def test_read_observation() -> None:
    """
    Read observation - 'calib' from file
    """
    pl = PL()
    pl.meas_file = 'tests/MeasuredData.csv'
    pl.read_observation()
    
def test_read_observation_datadict() -> None:
    """
    Read observation - 'calib' with given observation as dict
    """
    pl = PL()
    pl.observations = {'Z':[0.1]}
    pl.read_observation()
    
def test_read_observation_dataframe() -> None:
    """
    Read observation - 'calib' with given observation as dict
    """
    pl = PL()
    pl.observations = pd.DataFrame({'Z':[0.1]}, columns = ['Z'])
    pl.read_observation()
    
def test_read_observation_validnone() -> None:
    """
    Read observation - 'valid' without anything
    """
    pl = PL()
    with pytest.raises(AttributeError) as excinfo:
        pl.read_observation(case = 'valid')
    assert str(excinfo.value) == "Please provide the observation data as a dictionary via observations attribute or pass the csv-file path to MeasurementFile attribute"
    
def test_read_observation_valid() -> None:
    """
    Read observation - 'valid' from file
    """
    pl = PL()
    pl.meas_file_valid = 'tests/MeasuredData_Valid.csv'
    pl.read_observation(case = 'valid')
       
def test_read_observation_validdatadict() -> None:
    """
    Read observation - 'valid' with given observation as dict
    """
    pl = PL()
    pl.observations_valid = {'Z':[0.1]}
    pl.read_observation(case = 'valid')
    
def test_read_observation_validdataframe() -> None:
    """
    Read observation - 'valid' with given observation as dict
    """
    pl = PL()
    pl.observations_valid = pd.DataFrame({'Z':[0.1]}, columns = ['Z'])
    pl.read_observation(case = 'valid')
    

def test_read_observation_mc() -> None:
    """
    Read mc ref from file
    """
    pl = PL()
    pl.mc_ref_file = 'tests/MCrefs_MeanStd.csv'
    pl.read_observation(case = 'mc_ref')
    

def test_read_observation_mcdatadict() -> None:
    """
    Read mc ref from fict
    """
    pl = PL()
    pl.mc_reference = {'Mean':[0.1],'Std':[0.1]}
    pl.read_observation(case = 'mc_ref')
 
def test_read_observation_mcdataframe() -> None:
    """
    Read mc ref from dataframe
    """
    pl = PL()
    pl.observations_valid = pd.DataFrame({'Mean':[0.1],'Std':[0.1]}, columns = ['Mean', 'Std'])
    pl.read_observation(case = 'mc_ref')
    
def test_read_observation_mcnone() -> None:
    """
    Read mc ref with nothing
    """
    pl = PL()
    pl.read_observation(case = 'mc_ref')
    
#%% Test PyLink.read_output

def test_read_output() -> None:
    """
    Reads model run output
    """
    pl = PL()
    #pl.read_output()
    # TODO: create parser first to be able to test this
    
#%% Test PyLink.update_input_params

def test_update_input_params() -> None:
    """
    Updates parameters in file
    """
    pl = PL()
    # TODO: better understand what this is meant to do
    
#%% Test PyLink.run_command

def test_run_command() -> None:
    """
    Runs command and reads results
    """
    pl = PL()
    # TODO: Find command to run to then read in file
    
#%% Test PyLink.zip_subdirs
def test_zip_subdirs() -> None:
    """
    Zips specified subdirs
    """
    pl = PL()
    pl.zip_subdirs('tests\Outputs_SeqPosteriorComparison', 'Z')

#%% Test PyLink._store_simulations
def test_store_simulations() -> None:
    """
    Stores simulation results
    """
    pl = PL()
    
    
#%% Test PyLink.run_model_parallel
if 0:
    def test_run_model_parallel() -> None:
        """
        Runs model in parallel
        """
        pl = PL()
        pl.link_type = 'PyLink'
        pl.name = 'Beam9points'
        pl.input_file = "tests\test_model\SSBeam_Deflection.inp"
        pl.input_template = "tests\test_model\SSBeam_Deflection.tpl.inp"
    
        pl.shell_command = "tests\test_model\myBeam9points SSBeam_Deflection.inp"
        pl.Output.parser = 'tests\test_model\read_Beam_Deflection'
        pl.Output.names = ['Deflection [m]']
        pl.Output.file_names = ["SSBeam_Deflection.out"]
        pl.run_model_parallel([[0.1,0.25,30000e+6,1e4]])
    

if __name__ == '__main__':
    None
