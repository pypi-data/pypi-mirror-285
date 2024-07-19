# -*- coding: utf-8 -*-
"""
Test the Discrepancy class in bayesvalidrox.
Tests are available for the following functions
Class Discrepancy: 
    get_sample

"""
import sys
sys.path.append("src/")
import pytest

from bayesvalidrox.bayes_inference.discrepancy import Discrepancy
from bayesvalidrox.surrogate_models.inputs import Input

#%% Test Discrepancy init

def test_discrepancy() -> None:
    """
    Construct a Discrepancy object
    """
    disc = Discrepancy()
    
#%% Test Discrepancy.get_sample

def test_get_sample_noinput() -> None:
    """
    Get discrepancy sample without input dist
    """
    disc = Discrepancy()
    with pytest.raises(AttributeError) as excinfo:
        disc.get_sample(2)
    assert str(excinfo.value) == 'Cannot create new samples, please provide input distributions'
    
def test_get_sample() -> None:
    """
    Get discrepancy sample
    """
    disc = Discrepancy()
    with pytest.raises(AttributeError) as excinfo:
        disc.get_sample(2)
    assert str(excinfo.value) == 'Cannot create new samples, please provide input distributions'
    