#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Experimental design with associated sampling methods
"""

import itertools
import math

import chaospy
import h5py
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns

from .apoly_construction import apoly_construction
from .input_space import InputSpace


# -------------------------------------------------------------------------
def check_ranges(theta, ranges):
    """
    This function checks if theta lies in the given ranges.

    Parameters
    ----------
    theta : array
        Proposed parameter set.
    ranges : nested list
        The parameter ranges.

    Returns
    -------
    c : bool
        If it lies in the given range, it returns True else False.

    """
    c = True
    # traverse in the list1
    for i, bounds in enumerate(ranges):
        x = theta[i]
        # condition check
        if x < bounds[0] or x > bounds[1]:
            c = False
            return c
    return c


class ExpDesigns(InputSpace):
    """
    This class generates samples from the prescribed marginals for the model
    parameters using the `Input` object.

    Attributes
    ----------
    input_object : obj
        Input object containing the parameter marginals, i.e. name,
        distribution type and distribution parameters or available raw data.
    meta_Model_type : str
        Type of the meta_Model_type.
    sampling_method : str
        Name of the sampling method for the experimental design. The following
        sampling method are supported:

        * random
        * latin_hypercube
        * sobol
        * halton
        * hammersley
        * chebyshev(FT)
        * grid(FT)
        * user
    hdf5_file : str
        Name of the hdf5 file that contains the experimental design.
    n_new_samples : int
        Number of (initial) training points.
    n_max_samples : int
        Number of maximum training points.
    mod_LOO_threshold : float
        The modified leave-one-out cross validation threshold where the
        sequential design stops.
    tradeoff_scheme : str
        Trade-off scheme to assign weights to the exploration and exploitation
        scores in the sequential design.
    n_canddidate : int
        Number of candidate training sets to calculate the scores for.
    explore_method : str
        Type of the exploration method for the sequential design. The following
        methods are supported:

        * Voronoi
        * random
        * latin_hypercube
        * LOOCV
        * dual annealing
    exploit_method : str
        Type of the exploitation method for the sequential design. The
        following methods are supported:

        * BayesOptDesign
        * BayesActDesign
        * VarOptDesign
        * alphabetic
        * Space-filling
    util_func : str or list
        The utility function to be specified for the `exploit_method`. For the
        available utility functions see Note section.
    n_cand_groups : int
        Number of candidate groups. Each group of candidate training sets will
        be evaulated separately in parallel.
    n_replication : int
        Number of replications. Only for comparison. The default is 1.
    post_snapshot : int
        Whether to plot the posterior in the sequential design. The default is
        `True`.
    step_snapshot : int
        The number of steps to plot the posterior in the sequential design. The
        default is 1.
    max_a_post : list or array
        Maximum a posteriori of the posterior distribution, if known. The
        default is `[]`.
    adapt_verbose : bool
        Whether to plot the model response vs that of metamodel for the new
        trining point in the sequential design.

    Note
    ----------
    The following utiliy functions for the **exploitation** methods are
    supported:

    #### BayesOptDesign (when data is available)
    - DKL (Kullback-Leibler Divergence)
    - DPP (D-Posterior-percision)
    - APP (A-Posterior-percision)

    #### VarBasedOptDesign -> when data is not available
    - Entropy (Entropy/MMSE/active learning)
    - EIGF (Expected Improvement for Global fit)
    - LOOCV (Leave-one-out Cross Validation)

    #### alphabetic
    - D-Opt (D-Optimality)
    - A-Opt (A-Optimality)
    - K-Opt (K-Optimality)
    """

    def __init__(self, input_object, meta_Model_type='pce', sampling_method='random', hdf5_file=None,
                 n_new_samples=1, n_max_samples=None, mod_LOO_threshold=1e-16, tradeoff_scheme=None, n_canddidate=1,
                 explore_method='random', exploit_method='Space-filling', util_func='Space-filling', n_cand_groups=4,
                 n_replication=1, post_snapshot=False, step_snapshot=1, max_a_post=None, adapt_verbose=False,
                 max_func_itr=1, out_dir = ''):

        super().__init__(input_object, meta_Model_type)
        if max_a_post is None:
            max_a_post = []

        self.InputObj = input_object
        self.meta_Model_type = meta_Model_type
        self.sampling_method = sampling_method
        self.hdf5_file = hdf5_file
        self.n_new_samples = n_new_samples
        self.n_max_samples = n_max_samples
        self.mod_LOO_threshold = mod_LOO_threshold
        self.explore_method = explore_method
        self.exploit_method = exploit_method
        self.util_func = util_func
        self.tradeoff_scheme = tradeoff_scheme
        self.n_canddidate = n_canddidate
        self.n_cand_groups = n_cand_groups
        self.n_replication = n_replication
        self.post_snapshot = post_snapshot
        self.step_snapshot = step_snapshot
        self.max_a_post = max_a_post
        self.adapt_verbose = adapt_verbose
        self.max_func_itr = max_func_itr
        self.out_dir = out_dir

        # Other 
        self.apce = None
        self.n_init_samples = None
        self.n_samples = None
        self.ndim = None
        self.X = None
        self.Y = None

        # Init 
        self.check_valid_inputs()
        if self.out_dir == '':
            self.out_dir = f'Outputs_Priors/'
        

    # -------------------------------------------------------------------------
    def generate_samples(self, n_samples, sampling_method='random'):
        """
        Generates samples with given sampling method

        Parameters
        ----------
        n_samples : int
            Number of requested samples.
        sampling_method : str, optional
            Sampling method. The default is `'random'`.

        Returns
        -------
        samples: array of shape (n_samples, n_params)
            Generated samples from defined model input object.

        """
        try:
            samples = chaospy.generate_samples(
                int(n_samples), domain=self.origJDist, rule=sampling_method
            )
        except:
            samples = self.random_sampler(int(n_samples)).T

        return samples.T

    # -------------------------------------------------------------------------
    def generate_ED(self, n_samples, max_pce_deg=1):
        """
        Generates experimental designs (training set) with the given method.

        Parameters
        ----------
        n_samples : int
            Number of requested training points.
        max_pce_deg : int, optional
            Maximum PCE polynomial degree. The default is 1.
            
        Returns
        -------
        None

        """
        if n_samples < 0:
            raise ValueError('A negative number of samples cannot be created. Please provide positive n_samples')
        n_samples = int(n_samples)

        if self.n_init_samples is None:
            self.n_init_samples = n_samples

        # Generate the samples based on requested method
        self.init_param_space(max_pce_deg)

        samples = None
        sampling_method = self.sampling_method
        # Pass user-defined samples as ED
        if sampling_method == 'user':
            if self.X is None:
                raise AttributeError('User-defined sampling cannot proceed as no samples provided. Please add them to '
                                     'this class as attribute X')
            if not self.X.ndim == 2:
                raise AttributeError('The provided samples shuld have 2 dimensions')
            samples = self.X
            self.n_samples = len(samples)
            return

        if sampling_method == 'latin-hypercube' and max_pce_deg is None:
            raise AttributeError('Please set `max_pce_deg` for the experimental design!')

        # Sample the distribution of parameters
        elif self.input_data_given:
            # Case II: Input values are directly given by the user.

            if sampling_method == 'random':
                samples = self.random_sampler(n_samples)

            elif sampling_method == 'PCM' or \
                    sampling_method == 'LSCM':
                samples = self.pcm_sampler(n_samples, max_pce_deg)

            else:
                # Create ExpDesign in the actual space using chaospy
                try:
                    samples = chaospy.generate_samples(n_samples,
                                                       domain=self.JDist,
                                                       rule=sampling_method).T
                except:
                    samples = self.JDist.resample(n_samples).T

        elif not self.input_data_given:
            # Case I = User passed known distributions
            samples = chaospy.generate_samples(n_samples, domain=self.JDist,
                                               rule=sampling_method).T

        self.X = samples

    def read_from_file(self, out_names):
        """
        Reads in the ExpDesign from a provided h5py file and saves the results.

        Parameters
        ----------
        out_names : list of strings
            The keys that are in the outputs (y) saved in the provided file.

        Returns
        -------
        None.

        """
        if self.hdf5_file is None:
            raise AttributeError('ExpDesign cannot be read in, please provide hdf5 file first')

        # Read hdf5 file
        f = h5py.File(self.hdf5_file, 'r+')

        # Read EDX and pass it to ExpDesign object
        try:
            self.X = np.array(f["EDX/New_init_"])
        except KeyError:
            self.X = np.array(f["EDX/init_"])

        # Update number of initial samples
        self.n_init_samples = self.X.shape[0]

        # Read EDX and pass it to ExpDesign object
        self.Y = {}

        # Extract x values
        try:
            self.Y["x_values"] = dict()
            for varIdx, var in enumerate(out_names):
                x = np.array(f[f"x_values/{var}"])
                self.Y["x_values"][var] = x
        except KeyError:
            self.Y["x_values"] = np.array(f["x_values"])

        # Store the output
        for varIdx, var in enumerate(out_names):
            try:
                y = np.array(f[f"EDY/{var}/New_init_"])
            except KeyError:
                y = np.array(f[f"EDY/{var}/init_"])
            self.Y[var] = y
        f.close()
        print(f'Experimental Design is read in from file {self.hdf5_file}')
        print('')

    # -------------------------------------------------------------------------
    def random_sampler(self, n_samples, max_deg=1):
        """
        Samples the given raw data randomly.

        Parameters
        ----------
        n_samples : int
            Number of requested samples.
            
        max_deg : int, optional
            Maximum degree. The default is 1.
            This will be used to run init_param_space, if it has not been done
            until now.

        Returns
        -------
        samples: array of shape (n_samples, n_params)
            The sampling locations in the input space.

        """
        if self.raw_data is None:
            self.init_param_space(max_deg)
        else:
            if np.array(self.raw_data).ndim != 2:
                raise AttributeError('The given raw data for sampling should have two dimensions')
        samples = np.zeros((n_samples, self.ndim))
        sample_size = self.raw_data.shape[1]

        # Use a combination of raw data
        if n_samples < sample_size:
            for pa_idx in range(self.ndim):
                # draw random indices
                rand_idx = np.random.randint(0, sample_size, n_samples)
                # store the raw data with given random indices
                samples[:, pa_idx] = self.raw_data[pa_idx, rand_idx]
        else:
            if self.JDist is None:
                raise AttributeError('Sampling cannot proceed, build ExpDesign with max_deg != 0 to create JDist!')
            try:
                # Use resample if JDist is of type gaussian_kde
                samples = self.JDist.resample(int(n_samples)).T
            except AttributeError:
                # Use sample if JDist is of type chaospy.J
                samples = self.JDist.sample(int(n_samples)).T
            # If there is only one input transform the samples
            if self.ndim == 1:
                samples = np.swapaxes(np.atleast_2d(samples), 0, 1)

            # Check if all samples are in the bound_tuples
            for idx, param_set in enumerate(samples):
                if not check_ranges(param_set, self.bound_tuples):
                    try:
                        proposed_sample = chaospy.generate_samples(
                            1, domain=self.JDist, rule='random').T[0]
                    except:
                        proposed_sample = self.JDist.resample(1).T[0]
                    while not check_ranges(proposed_sample,
                                           self.bound_tuples):
                        try:
                            proposed_sample = chaospy.generate_samples(
                                1, domain=self.JDist, rule='random').T[0]
                        except:
                            proposed_sample = self.JDist.resample(1).T[0]
                    samples[idx] = proposed_sample

        return samples

    # -------------------------------------------------------------------------
    def pcm_sampler(self, n_samples, max_deg):
        """
        Generates collocation points based on the root of the polynomial
        degrees.

        Parameters
        ----------
        n_samples : int
            Number of requested samples.
        max_deg : int
            Maximum degree defined by user. Will also be used to run 
            init_param_space if that has not been done beforehand.

        Returns
        -------
        opt_col_points: array of shape (n_samples, n_params)
            Collocation points.

        """

        if self.raw_data is None:
            self.init_param_space(max_deg)

        raw_data = self.raw_data

        # Guess the closest degree to self.n_samples
        def M_uptoMax(deg):
            """
            ??
            Parameters
            ----------
            deg : int
                Degree.

            Returns
            -------
            list of ..?
            """
            result = []
            for d in range(1, deg + 1):
                result.append(math.factorial(self.ndim + d) //
                              (math.factorial(self.ndim) * math.factorial(d)))
            return np.array(result)
        guess_Deg = np.where(M_uptoMax(max_deg) > n_samples)[0][0]

        c_points = np.zeros((guess_Deg + 1, self.ndim))

        def PolynomialPa(parIdx):
            """
            ???
            Parameters
            ----------
            parIdx

            Returns
            -------

            """
            return apoly_construction(self.raw_data[parIdx], max_deg)

        for i in range(self.ndim):
            poly_coeffs = PolynomialPa(i)[guess_Deg + 1][::-1]
            c_points[:, i] = np.trim_zeros(np.roots(poly_coeffs))

        #  Construction of optimal integration points
        Prod = itertools.product(np.arange(1, guess_Deg + 2), repeat=self.ndim)
        sort_dig_unique_combos = np.array(list(filter(lambda x: x, Prod)))

        # Ranking relatively mean
        Temp = np.empty(shape=[0, guess_Deg + 1])
        for j in range(self.ndim):
            s = abs(c_points[:, j] - np.mean(raw_data[j]))
            Temp = np.append(Temp, [s], axis=0)
        temp = Temp.T

        index_CP = np.sort(temp, axis=0)
        sort_cpoints = np.empty((0, guess_Deg + 1))

        for j in range(self.ndim):
            sort_cp = c_points[index_CP[:, j], j]
            sort_cpoints = np.vstack((sort_cpoints, sort_cp))

        # Mapping of Combination to Cpoint Combination
        sort_unique_combos = np.empty(shape=[0, self.ndim])
        for i in range(len(sort_dig_unique_combos)):
            sort_un_comb = []
            sort_uni_comb = None
            for j in range(self.ndim):
                SortUC = sort_cpoints[j, sort_dig_unique_combos[i, j] - 1]
                sort_un_comb.append(SortUC)
                sort_uni_comb = np.asarray(sort_un_comb)
            sort_unique_combos = np.vstack((sort_unique_combos, sort_uni_comb))

        # Output the collocation points
        if self.sampling_method.lower() == 'lscm':
            opt_col_points = sort_unique_combos
        else:
            opt_col_points = sort_unique_combos[0:self.n_samples]

        return opt_col_points

    def plot_samples(self, samples):
        """
        Visualizes generated samples over their given distributions.

        Parameters
        ----------
        samples : array
            The samples to visualize.

        Returns
        -------
        None.

        """
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        # Settings for the plot
        b=50
        for l in range(len(self.par_names)):
            # Get the marginal
            marg = self.InputObj.Marginals[l].input_data
            if marg != []:
                prior = marg
            else:
                prior = np.swapaxes(self.generate_samples(1000000, 'random'),0,1)[l]
                
            # TODO: The dists are only cut off at the edges, not actually correct here
            fig, ax = plt.subplots()
            sns.distplot(prior, bins=b, ax=ax, norm_hist=True,
                         color='grey', label='prior', 
                         kde_kws={'clip': (self.bound_tuples[l][0], self.bound_tuples[l][1])})
            sns.kdeplot(samples[:, l], ax=ax, color='green',
                        label='training samples', 
                        clip=(self.bound_tuples[l][0], self.bound_tuples[l][1]))
            sns.rugplot(data=samples[:, l], ax=ax, height=.1, color='green')
            plt.xlabel(self.par_names[l])
            plt.legend()
            plt.yticks([])
            plt.savefig(f'{self.out_dir}/prior_{self.par_names[l]}.png')
            plt.close()