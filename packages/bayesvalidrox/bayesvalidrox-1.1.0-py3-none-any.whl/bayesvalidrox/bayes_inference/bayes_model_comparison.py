#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import emcee
import numpy as np
import os
from scipy import stats
import seaborn as sns
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import matplotlib.pylab as plt
import pandas as pd
from .bayes_inference import BayesInference

# Load the mplstyle
plt.style.use(os.path.join(os.path.split(__file__)[0],
                           '../', 'bayesvalidrox.mplstyle'))


class BayesModelComparison:
    """
    A class to perform Bayesian Analysis.


    Attributes
    ----------
    justifiability : bool, optional
        Whether to perform the justifiability analysis. The default is
        `True`.
    perturbed_data : array of shape (n_bootstrap_itrs, n_obs), optional
        User defined perturbed data. The default is `None`.
    n_bootstrap : int
        Number of bootstrap iteration. The default is `1000`.
    data_noise_level : float
        A noise level to perturb the data set. The default is `0.01`.

    """

    def __init__(self, justifiability=True, perturbed_data=None,
                 n_bootstrap=1000, data_noise_level=0.01,
                 use_Bayes_settings = True, emulator = True, out_dir = 'Outputs_Comparison/'):

        # TODO: check valid ranges of the parameters
        
        self.justifiability = justifiability
        self.perturbed_data = perturbed_data
        self.n_bootstrap = n_bootstrap
        self.data_noise_level = data_noise_level
        self.use_Bayes_settings = use_Bayes_settings
        self.emulator = emulator
        self.out_dir = out_dir
        
        # Other parameters
        self.n_meas = None
        self.BF_data = None
        self.just_data = None
        self.BME_dict = None
        self.set_up = False
        self.dtype = None
        self.bayes_dict = None
        self.just_bayes_dict = None
        self.model_weights = None
        self.model_weights_dict = None
        self.just_model_weights_dict = None
        
        
    # --------------------------------------------------------------------------
    def setup(self, model_dict):
        """
        Initialize parameters that are needed for all types of model comparison

        Returns
        -------
        None.

        """
        
        if not isinstance(model_dict, dict):
            raise Exception("To run model comparsion, you need to pass a "
                            "dictionary of models.")

        # Extract model names
        self.model_names = [*model_dict]

        # Compute total number of the measurement points
        # TODO: there could be a different option for this here
        Engine = list(model_dict.items())[0][1]
        Engine.Model.read_observation()
        self.n_meas = Engine.Model.n_obs

        # Find n_bootstrap
        if self.perturbed_data is not None:
            self.n_bootstrap = self.perturbed_data.shape[0]
            
        # Output directory
        os.makedirs(self.out_dir, exist_ok=True)

        # System settings
        if os.name == 'nt':
            print('')
            print('WARNING: Performing the inference on windows can lead to reduced accuracy!')
            print('')
            self.dtype=np.longdouble
        else:
            self.dtype=np.float128


    # --------------------------------------------------------------------------
    def model_comparison_all(self, model_dict, opts_dict):
        """
        Perform all three types of model comparison: 
            * Bayes Factors
            * Model weights
            * Justifiability analysis

        Parameters
        ----------
        model_dict : dict
            A dictionary including the metamodels.
        opts_dict : dict
            A dictionary given the `BayesInference` options.

        Returns
        -------
        results : dict
            A dictionary that contains the calculated BME values, model weights
            and confusion matrix

        """
        self.calc_bayes_factors(model_dict, opts_dict)
        self.calc_model_weights(model_dict, opts_dict)
        self.calc_justifiability_analysis(model_dict, opts_dict)
        
        results = {'BME': self.BME_dict, 'Model weights': self.model_weights_dict,
                   'Confusion matrix': self.confusion_matrix}
        return results
    

    # --------------------------------------------------------------------------
    def calc_bayes_factors(self, model_dict, opts_dict):
        """
        Calculate the BayesFactors for each pair of models in the model_dict
        with respect to given data.

        Parameters
        ----------
        model_dict : dict
            A dictionary including the metamodels.
        opts_dict : dict
            A dictionary given the `BayesInference` options.

        Returns
        -------
        None.

        """
        # Do the setup
        if self.n_meas is None:
            self.setup(model_dict)
        
        # ----- Generate data -----
        # Create dataset
        self.BF_data = self.generate_dataset(
            model_dict, False, n_bootstrap=self.n_bootstrap)

        # Run create Interface for each model
        self.bayes_dict = {}
        for model in model_dict.keys():
            print("-"*20)
            print("Bayesian inference of {}.\n".format(model))
            BayesOpts = BayesInference(model_dict[model])
                
            # Set BayesInference options
            for key, value in opts_dict.items():
                if key in BayesOpts.__dict__.keys():
                    if key == "Discrepancy" and isinstance(value, dict):
                        setattr(BayesOpts, key, value[model])
                    else:
                        setattr(BayesOpts, key, value)

            # Pass justifiability data as perturbed data
            BayesOpts.bmc = True
            BayesOpts.emulator= self.emulator
            BayesOpts.just_analysis = False
            BayesOpts.perturbed_data = self.BF_data

            self.bayes_dict[model] = BayesOpts.create_inference()
            print("-"*20)

        # Accumulate the BMEs
        self.BME_dict = dict()
        for modelName, bayesObj in self.bayes_dict.items():
            self.BME_dict[modelName] = np.exp(bayesObj.log_BME, dtype=self.dtype)

        # TODO: move the calculation of the Bayes Factors out of the plots to here!
        # Create kde plot for bayes factors
        self.plot_bayes_factor(self.BME_dict, 'kde_plot')
        
        
    def calc_model_weights(self, model_dict, opts_dict):
        """
        Calculate the model weights from BME evaluations for Bayes factors.

        Parameters
        ----------
        model_dict : TYPE
            DESCRIPTION.
        opts_dict : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # Get BMEs via Bayes Factors if not already done so
        if self.BME_dict is None:
            self.calc_bayes_factors(model_dict, opts_dict)
        
        # Calculate the model weights
        self.model_weights = self.cal_model_weight(
            self.BME_dict, False, n_bootstrap=self.n_bootstrap)

        # Create box plot for model weights
        self.plot_model_weights(self.model_weights, 'model_weights')


    # -------------------------------------------------------------------------    
    def calc_justifiability_analysis(self, model_dict, opts_dict):
        """
        Perform justifiability analysis by calculating the confusion matrix
        
        Parameters
        ----------
        model_dict : dict
            A dictionary including the metamodels.
        opts_dict : dict
            A dictionary given the `BayesInference` options.
        
        Returns
        -------
        confusion_matrix: dict
            The averaged confusion matrix
        
        """
        # Do setup
        if self.n_meas is None:
            self.setup(model_dict)
            
        # Extend model names
        model_names = self.model_names
        if model_names[0]!= 'Observation':
            model_names.insert(0, 'Observation')
        
        # Generate data
        # TODO: generate the datset only if it does not exist yet
        # TODO: shape of this is still ok
        self.just_data = self.generate_dataset(
            model_dict, True, n_bootstrap=self.n_bootstrap)

        # Run inference for each model if this is not available
        #if self.just_bayes_dict is None:
        self.just_bayes_dict = {}
        for model in model_dict.keys():
            print("-"*20)
            print("Bayesian inference of {}.\n".format(model))
            BayesOpts = BayesInference(model_dict[model])
                
            # Set BayesInference options
            for key, value in opts_dict.items():
                if key in BayesOpts.__dict__.keys():
                    if key == "Discrepancy" and isinstance(value, dict):
                        setattr(BayesOpts, key, value[model])
                    else:
                        setattr(BayesOpts, key, value)

            # Pass justifiability data as perturbed data
            BayesOpts.bmc = True
            BayesOpts.emulator= self.emulator
            BayesOpts.just_analysis = True
            BayesOpts.perturbed_data = self.just_data

            self.just_bayes_dict[model] = BayesOpts.create_inference()
            print("-"*20)

        # Compute model weights
        # TODO: shape of this now ok as well
        self.BME_dict = dict()
        for modelName, bayesObj in self.just_bayes_dict.items():
            self.BME_dict[modelName] = np.exp(bayesObj.log_BME, dtype=self.dtype)

        # BME correction in BayesInference class
        just_model_weights = self.cal_model_weight(
            self.BME_dict, True, n_bootstrap=self.n_bootstrap)

        # Split the model weights and save in a dict
        list_ModelWeights = np.split(
            just_model_weights, just_model_weights.shape[1]/self.n_meas, axis=1)
        self.just_model_weights_dict = {key: weights for key, weights in
                              zip(model_names, list_ModelWeights)}
        
        # Confusion matrix over all measurement points
        cf_m = pd.DataFrame()
        cf_m['Generated by'] = model_names
        for i in range(len(model_names)):
            # Ignore 'Observation', this not in the model_weights_dict
            # TODO: how to change the code so that it is included as well?
            if i==0:
                continue
            avg = []
            for n in model_names:
                avg.append(np.sum(self.just_model_weights_dict[n][i-1]))
                
            # Norm to sum to 1 for each 'Generated by' row
            cf_m[model_names[i]] = avg/self.n_meas
        self.confusion_matrix = cf_m
            
        # Plot model weights
        self.plot_just_analysis()


    # -------------------------------------------------------------------------
    def generate_dataset(self, model_dict, justifiability=False,
                         n_bootstrap=1):
        """
        Generates the perturbed data set for the Bayes factor calculations and
        the data set for the justifiability analysis.

        Parameters
        ----------
        model_dict : dict
            A dictionary including the metamodels.
        bool, optional
            Whether to perform the justifiability analysis. The default is
            `False`.
        n_bootstrap : int, optional
            Number of bootstrap iterations. The default is `1`.

        Returns
        -------
        all_just_data: array
            Created data set.

        """
        # Compute some variables
        all_just_data = []
        Engine = list(model_dict.items())[0][1]
        out_names = Engine.Model.Output.names

        # Perturb observations for Bayes Factor
        if self.perturbed_data is None:
            self.perturbed_data = self.__perturb_data(
                    Engine.Model.observations, out_names, n_bootstrap,
                    noise_level=self.data_noise_level)

        # Only for Bayes Factor
        if not justifiability:
            return self.perturbed_data # TODO: why return this as self... and the other one not? Is this used again?

        # Evaluate metamodel
        runs = {}
        for key, engine in model_dict.items(): # TODO: add check for emulator vs model
            y_hat, _ = engine.eval_metamodel(nsamples=n_bootstrap)
            runs[key] = y_hat

        # Generate data
        for i in range(n_bootstrap):
            y_data = self.perturbed_data[i].reshape(1, -1)# makes every entry in self.perturbed_data 2D by adding one dim outside
            justData = np.tril(np.repeat(y_data, y_data.shape[1], axis=0)) # Lower triangle matrix from repeats of y_data
            # TODO: why triangle matrix here?
            # Use surrogate runs for data-generating process
            for key, metaModel in model_dict.items():
                model_data = np.array(
                    [runs[key][out][i] for out in out_names]).reshape(y_data.shape) # reshapes model runs to match y_data
                justData = np.vstack((
                    justData,
                    np.tril(np.repeat(model_data, model_data.shape[1], axis=0))
                    ))
            # Save in a list
            all_just_data.append(justData)

        # Squeeze the array
        all_just_data = np.array(all_just_data).transpose(1, 0, 2).reshape(
            -1, np.array(all_just_data).shape[2]
            )

        return all_just_data

    # -------------------------------------------------------------------------
    def __perturb_data(self, data, output_names, n_bootstrap, noise_level):
        """
        Returns an array with n_bootstrap_itrs rows of perturbed data.
        The first row includes the original observation data.
        If `self.bayes_loocv` is True, a 2d-array will be returned with
        repeated rows and zero diagonal entries.

        Parameters
        ----------
        data : pandas DataFrame
            Observation data.
        output_names : list
            List of the output names.

        Returns
        -------
        final_data : array
            Perturbed data set.

        """
        obs_data = data[output_names].values
        n_measurement, n_outs = obs_data.shape
        n_tot_measurement = obs_data[~np.isnan(obs_data)].shape[0]
        final_data = np.zeros(
            (n_bootstrap, n_tot_measurement)
            )
        final_data[0] = obs_data.T[~np.isnan(obs_data.T)]
        for itrIdx in range(1, n_bootstrap):
            data = np.zeros((n_measurement, n_outs))
            for idx in range(len(output_names)):
                std = np.nanstd(obs_data[:, idx])
                if std == 0:
                    std = 0.001
                noise = std * noise_level
                data[:, idx] = np.add(
                    obs_data[:, idx],
                    np.random.normal(0, 1, obs_data.shape[0]) * noise,
                )

            final_data[itrIdx] = data.T[~np.isnan(data.T)]

        return final_data

    # -------------------------------------------------------------------------
    def cal_model_weight(self, BME_dict, justifiability=False, n_bootstrap=1):
        """
        Normalize the BME (Asumption: Model Prior weights are equal for models)

        Parameters
        ----------
        BME_dict : dict
            A dictionary containing the BME values.

        Returns
        -------
        model_weights : array
            Model weights.

        """
        # Stack the BME values for all models
        all_BME = np.vstack(list(BME_dict.values()))

        if justifiability:
            # Compute expected log_BME for justifiabiliy analysis
            all_BME = all_BME.reshape(
                all_BME.shape[0], -1, n_bootstrap).mean(axis=2)

        # Model weights
        model_weights = np.divide(all_BME, np.nansum(all_BME, axis=0))

        return model_weights

    # -------------------------------------------------------------------------
    def plot_just_analysis(self):
        """
        Visualizes the confusion matrix and the model wights for the
        justifiability analysis.

        Parameters
        ----------
        model_weights_dict : dict
            Model weights.

        Returns
        -------
        None.

        """
        model_weights_dict = self.just_model_weights_dict
        Color = [*mcolors.TABLEAU_COLORS]
        names = [*model_weights_dict]

        # Plot weights for each 'Generated by'
        model_names = [model.replace('_', '$-$') for model in self.model_names]
        for name in names:
            fig, ax = plt.subplots()
            for i, model in enumerate(model_names[1:]):
                plt.plot(list(range(1, self.n_meas+1)),
                         model_weights_dict[name][i],
                         color=Color[i], marker='o',
                         ms=10, linewidth=2, label=model
                         )

            plt.title(f"Data generated by: {name.replace('_', '$-$')}")
            plt.ylabel("Weights")
            plt.xlabel("No. of measurement points")
            ax.set_xticks(list(range(1, self.n_meas+1)))
            plt.legend(loc="best")
            fig.savefig(
                f'{self.out_dir}modelWeights_{name}.svg', bbox_inches='tight'
                )
            plt.close()

        # Confusion matrix for each measurement point
        for index in range(0, self.n_meas):
            weights = np.array(
                [model_weights_dict[key][:, index] for key in model_weights_dict]
                )
            g = sns.heatmap(
                weights.T, annot=True, cmap='Blues', xticklabels=model_names,
                yticklabels=model_names[1:], annot_kws={"size": 24}
                )

            # x axis on top
            g.xaxis.tick_top()
            g.xaxis.set_label_position('top')
            g.set_xlabel(r"\textbf{Data generated by:}", labelpad=15)
            g.set_ylabel(r"\textbf{Model weight for:}", labelpad=15)
            g.figure.savefig(
                f"{self.out_dir}confusionMatrix_ND_{index+1}.pdf",
                bbox_inches='tight'
                )
            plt.close()
                
        # Plot the averaged confusion matrix
        out_names = names[1:]
        cf = self.confusion_matrix[out_names].to_numpy()
        g = sns.heatmap(cf.T, annot=True, cmap='Blues', xticklabels=model_names,
        yticklabels=model_names[1:], annot_kws={"size": 24})
        g.xaxis.tick_top()
        g.xaxis.set_label_position('top')
        g.set_xlabel(r"\textbf{Data generated by:}", labelpad=15)
        g.set_ylabel(r"\textbf{Model weight for:}", labelpad=15)
        g.figure.savefig(
            f"{self.out_dir}confusionMatrix_full.pdf",
            bbox_inches='tight'
            )
        plt.close()
        

    # -------------------------------------------------------------------------
    def plot_model_weights(self, model_weights, plot_name):
        """
        Visualizes the model weights resulting from BMS via the observation
        data.

        Parameters
        ----------
        model_weights : array
            Model weights.
        plot_name : str
            Plot name.

        Returns
        -------
        None.

        """
        # Create figure
        fig, ax = plt.subplots()
        font_size = 40

        # Filter data using np.isnan
        mask = ~np.isnan(model_weights.T)
        filtered_data = [d[m] for d, m in zip(model_weights, mask.T)]

        # Create the boxplot
        bp = ax.boxplot(filtered_data, patch_artist=True, showfliers=False)

        # change outline color, fill color and linewidth of the boxes
        for box in bp['boxes']:
            # change outline color
            box.set(color='#7570b3', linewidth=4)
            # change fill color
            box.set(facecolor='#1b9e77')

        # change color and linewidth of the whiskers
        for whisker in bp['whiskers']:
            whisker.set(color='#7570b3', linewidth=2)

        # change color and linewidth of the caps
        for cap in bp['caps']:
            cap.set(color='#7570b3', linewidth=2)

        # change color and linewidth of the medians
        for median in bp['medians']:
            median.set(color='#b2df8a', linewidth=2)

        # Customize the axes
        model_names = [model.replace('_', '$-$') for model in self.model_names]
        ax.set_xticklabels(model_names)
        ax.set_ylabel('Weight', fontsize=font_size)
        ax.set_ylim((-0.05, 1.05))
        for t in ax.get_xticklabels():
            t.set_fontsize(font_size)
        for t in ax.get_yticklabels():
            t.set_fontsize(font_size)

        # Title
        plt.title('Posterior Model Weights')
        
        # Save the figure
        fig.savefig(
            f'./{self.out_dir}{plot_name}.pdf', bbox_inches='tight'
            )

        plt.close()

    # -------------------------------------------------------------------------
    def plot_bayes_factor(self, BME_dict, plot_name=''):
        """
        Plots the Bayes factor distibutions in a :math:`N_m \\times N_m`
        matrix, where :math:`N_m` is the number of the models.

        Parameters
        ----------
        BME_dict : dict
            A dictionary containing the BME values of the models.
        plot_name : str, optional
            Plot name. The default is ''.

        Returns
        -------
        None.

        """
        # Plot setup
        font_size = 40
        Colors = ["blue", "green", "gray", "brown"]

        model_names = list(BME_dict.keys())
        nModels = len(model_names)

        # Plots
        fig, axes = plt.subplots(
            nrows=nModels, ncols=nModels, sharex=True, sharey=True
            )

        for i, key_i in enumerate(model_names):

            for j, key_j in enumerate(model_names):
                ax = axes[i, j]
                # Set size of the ticks
                for t in ax.get_xticklabels():
                    t.set_fontsize(font_size)
                for t in ax.get_yticklabels():
                    t.set_fontsize(font_size)

                if j != i:

                    # Null hypothesis: key_j is the better model
                    BayesFactor = np.log10(
                        np.divide(BME_dict[key_i], BME_dict[key_j])
                        )

                    # sns.kdeplot(BayesFactor, ax=ax, color=Colors[i], shade=True)
                    # sns.histplot(BayesFactor, ax=ax, stat="probability",
                    #              kde=True, element='step',
                    #              color=Colors[j])

                    # taken from seaborn's source code (utils.py and
                    # distributions.py)
                    def seaborn_kde_support(data, bw, gridsize, cut, clip):
                        if clip is None:
                            clip = (-np.inf, np.inf)
                        support_min = max(data.min() - bw * cut, clip[0])
                        support_max = min(data.max() + bw * cut, clip[1])
                        return np.linspace(support_min, support_max, gridsize)

                    kde_estim = stats.gaussian_kde(
                        BayesFactor, bw_method='scott'
                        )

                    # manual linearization of data
                    # linearized = np.linspace(
                    #     quotient.min(), quotient.max(), num=500)

                    # or better: mimic seaborn's internal stuff
                    bw = kde_estim.scotts_factor() * np.std(BayesFactor)
                    linearized = seaborn_kde_support(
                        BayesFactor, bw, 100, 3, None)

                    # computes values of the estimated function on the
                    # estimated linearized inputs
                    Z = kde_estim.evaluate(linearized)

                    # https://stackoverflow.com/questions/29661574/normalize-
                    # numpy-array-columns-in-python
                    def normalize(x):
                        return (x - x.min(0)) / x.ptp(0)

                    # normalize so it is between 0;1
                    Z2 = normalize(Z)
                    ax.plot(linearized, Z2, "-", color=Colors[i], linewidth=4)
                    ax.fill_between(
                        linearized, 0, Z2, color=Colors[i], alpha=0.25
                        )

                    # Draw BF significant levels according to Jeffreys 1961
                    # Strong evidence for both models
                    ax.axvline(
                        x=np.log10(3), ymin=0, linewidth=4, color='dimgrey'
                        )
                    # Strong evidence for one model
                    ax.axvline(
                        x=np.log10(10), ymin=0, linewidth=4, color='orange'
                        )
                    # Decisive evidence for one model
                    ax.axvline(
                        x=np.log10(100), ymin=0, linewidth=4, color='r'
                        )

                    # legend
                    BF_label = key_i.replace('_', '$-$') + \
                        '/' + key_j.replace('_', '$-$')
                    legend_elements = [
                        patches.Patch(facecolor=Colors[i], edgecolor=Colors[i],
                                      label=f'BF({BF_label})')
                        ]
                    ax.legend(
                        loc='upper left', handles=legend_elements,
                        fontsize=font_size-(nModels+1)*5
                        )

                elif j == i:
                    # build a rectangle in axes coords
                    left, width = 0, 1
                    bottom, height = 0, 1

                    # axes coordinates are 0,0 is bottom left and 1,1 is upper
                    # right
                    p = patches.Rectangle(
                        (left, bottom), width, height, color='white',
                        fill=True, transform=ax.transAxes, clip_on=False
                        )
                    ax.grid(False)
                    ax.add_patch(p)
                    # ax.text(0.5*(left+right), 0.5*(bottom+top), key_i,
                    fsize = font_size+20 if nModels < 4 else font_size
                    ax.text(0.5, 0.5, key_i.replace('_', '$-$'),
                            horizontalalignment='center',
                            verticalalignment='center',
                            fontsize=fsize, color=Colors[i],
                            transform=ax.transAxes)

        # Customize axes
        custom_ylim = (0, 1.05)
        plt.setp(axes, ylim=custom_ylim)

        # set labels
        for i in range(nModels):
            axes[-1, i].set_xlabel('log$_{10}$(BF)', fontsize=font_size)
            axes[i, 0].set_ylabel('Probability', fontsize=font_size)

        # Adjust subplots
        plt.subplots_adjust(wspace=0.2, hspace=0.1)

        plt.savefig(
            f'./{self.out_dir}Bayes_Factor{plot_name}.pdf', bbox_inches='tight'
            )

        plt.close()
