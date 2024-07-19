#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inputs and related marginal distributions
"""


class Input:
    """
    A class to define the uncertain input parameters.

    Attributes
    ----------
    Marginals : obj
        Marginal objects. See `inputs.Marginal`.
    Rosenblatt : bool
        If Rossenblatt transformation is required for the dependent input
        parameters.

    Examples
    -------
    Marginals can be defined as following:

    >>> inputs = Inputs()
    >>> inputs.add_marginals()
    >>> inputs.Marginals[0].name = 'X_1'
    >>> inputs.Marginals[0].dist_type = 'uniform'
    >>> inputs.Marginals[0].parameters = [-5, 5]

    If there is no common data is avaliable, the input data can be given
    as following:

    >>> inputs.add_marginals()
    >>> inputs.Marginals[0].name = 'X_1'
    >>> inputs.Marginals[0].input_data = [0,0,1,0]
    """
    poly_coeffs_flag = True

    def __init__(self):
        self.Marginals = []
        self.Rosenblatt = False

    def add_marginals(self):
        """
        Adds a new Marginal object to the input object.

        Returns
        -------
        None.

        """
        self.Marginals.append(Marginal())


# Nested class
class Marginal:
    """
    An object containing the specifications of the marginals for each uncertain
    parameter.

    Attributes
    ----------
    name : string
        Name of the parameter. The default is `'$x_1$'`.
    dist_type : string
        Name of the distribution. The default is `None`.
    parameters : list
        Parameters corresponding to the distribution type. The
        default is `None`.
    input_data : array
        Available input data. The default is `[]`.
    moments : list
        Moments of the distribution. The default is `None`.
    """

    def __init__(self):
        self.name = '$x_1$'
        self.dist_type = None
        self.parameters = None
        self.input_data = []
        self.moments = None
