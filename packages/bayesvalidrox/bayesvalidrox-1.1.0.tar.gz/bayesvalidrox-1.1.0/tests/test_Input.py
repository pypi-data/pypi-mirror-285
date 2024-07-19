# -*- coding: utf-8 -*-
"""
Test the Input and associated Marginal classes in bayesvalidrox.
Tests are available for the following functions
Class Marginal contains no functions - no tests to write.
Class Input: 
    add_marginals

@author: Rebecca Kohlhaas
"""
import sys

from bayesvalidrox.surrogate_models.inputs import Input

sys.path.append("src/")


def test_addmarginals() -> None:
    """
    Tests function 'Input.add_marginals()'
    Ensure that marginals get appended
    """
    inp = Input()
    inp.add_marginals()
    assert len(inp.Marginals) == 1
