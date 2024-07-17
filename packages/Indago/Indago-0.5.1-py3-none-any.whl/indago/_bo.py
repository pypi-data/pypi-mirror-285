#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Indago
Python framework for numerical optimization
https://indago.readthedocs.io/
https://pypi.org/project/Indago/

Description: Indago contains several modern methods for real fitness function optimization over a real parameter domain
and supports multiple objectives and constraints. It was developed at the University of Rijeka, Faculty of Engineering.
Authors: Stefan Ivić, Siniša Družeta, Luka Grbčić
Contact: stefan.ivic@riteh.uniri.hr
License: MIT

File content: Definition of Bayesian Optimization (BO) optimizer.
Usage: from indago import BO

"""


import numpy as np
from ._optimizer import Optimizer, Candidate

from scipy.stats import norm
from indago import PSO
import scipy.optimize as opt
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import *
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.model_selection import train_test_split
import scipy.stats.qmc as qmc


import sys
import os
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")
    os.environ["PYTHONWARNINGS"] = "ignore" # Also affect subprocesses

    
class BO(Optimizer):
    """Bayesian Optimization method class.
    
    Attributes
    ----------
    variant : str
        Name of the BO variant. Default (and the only available option): ``Vanilla``.
    params : dict
        A dictionary of BO parameters.
    _candidates : ndarray
        Array of solution candidates.
        
    Returns
    -------
    optimizer : BO
        BO optimizer instance.
    """
    

    def __init__(self):
        Optimizer.__init__(self)

        self.variant = 'Vanilla'


    def _check_params(self):
        """Private method which performs some BO-specific parameter checks
        and prepares the parameters to be validated by Optimizer._check_params.

        Returns
        -------
        None
            Nothing
            
        """
        
        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []
        

        if self.variant == 'Vanilla':
            mandatory_params = 'init_size batch_size model_type acquisition_function opt_cycles optimizer xi kappa tune'.split()
            if 'init_size' not in self.params: 
                self.params['init_size'] = 5
                defined_params += 'init_size'.split()
            if 'batch_size' not in self.params:
                self.params['batch_size'] = 1
                defined_params += 'batch_size'.split()  
            if 'model_type' not in self.params:
                self.params['model_type'] = 'GP'
                defined_params += 'model_type'.split()                
            if 'acquisition_function' not in self.params:
                self.params['acquisition_function'] = 'EI'
                defined_params += 'acquisition_function'.split()    
            if 'opt_cycles' not in self.params:
                self.params['opt_cycles'] = 10
                defined_params += 'opt_cycles'.split() 
            if 'optimizer' not in self.params:
                self.params['optimizer'] = 'LBFGSB'
                defined_params += 'optimizer'.split()    
            if 'xi' not in self.params:
                self.params['xi'] = 0.01
                defined_params += 'xi'.split()  
            if 'kappa' not in self.params:
                self.params['kappa'] = 1.96
                defined_params += 'kappa'.split()  
            if 'tune' not in self.params:
                self.params['tune'] = True
                defined_params += 'tune'.split()           
        else:
            assert False, f'Unknown variant! {self.variant}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)


    def _init_method(self):
        """Private method for initializing the BO optimizer instance.
        Initializes and evaluates optimizer.max_evaluations number of candidates.

        Returns
        -------
        None
            Nothing
            
        """
        
        self._evaluate_initial_candidates()

        # Generate all candidates
        n0 = 0 if self._initial_candidates is None else self._initial_candidates.size
        self._candidates = np.array([Candidate(self) for _ in range(self.params['init_size'] - n0)], dtype=Candidate)
        self._initialize_X(self._candidates[n0:])
        
        # Using specified particles initial positions
        for p in range(np.size(self._candidates)):
            if p < n0:
                self._candidates[p] = self._initial_candidates[p].copy()
            
        # Evaluate
        if n0 < self.params['batch_size']:
            self._collective_evaluation(self._candidates[n0:])

        # if all candidates are NaNs
        if np.isnan([candidate.f for candidate in self._candidates]).all():
            self._err_msg = 'ALL CANDIDATES FAILED TO EVALUATE'

        self._finalize_iteration()
    
    
    def _EI(self, model, x, x_samples, best, xi):
        
        """
        Expected improvement acquisition function
        """
        if self.params['model_type'] == 'GP': 
            mu, sigma = model.predict([x], return_std=True)
        else:
            all_tree_predictions = np.array([tree.predict([x]) for tree in model.estimators_])
            mu = np.mean(all_tree_predictions)
            sigma = np.std(all_tree_predictions).reshape(-1,1)
        
        mu_best = best
        Z = (mu_best - mu - xi) / sigma
        ei = (mu_best - mu - xi) * norm.cdf(Z) + sigma * norm.pdf(Z)
        ei[sigma == 0] = 0 
        
        return ei

    def _POI(self, model, x, x_samples, best, xi):
        
        """
        Probability of improvement acquisition function
        """
        if self.params['model_type'] == 'GP': 
            mu, sigma = model.predict([x], return_std=True)
        else:
            all_tree_predictions = np.array([tree.predict([x]) for tree in model.estimators_])
            mu = np.mean(all_tree_predictions)
            sigma = np.std(all_tree_predictions).reshape(-1,1)
        mu_best = best
        Z = (mu_best - mu - xi) / sigma

        poi = norm.cdf(Z)
        
        return poi
    
    def _LCB(self, model, x, x_samples, kappa):
        
        """
        Lower confidence bound acquisition function
        """
        if self.params['model_type'] == 'GP': 
            mu, sigma = model.predict([x], return_std=True)
        else:
            all_tree_predictions = np.array([tree.predict([x]) for tree in model.estimators_])
            mu = np.mean(all_tree_predictions)
            sigma = np.std(all_tree_predictions)
        
        return mu - kappa*sigma

    def _TS(self, model):
        """
        Thompson Sampling acquisition function
        """

        sampler = qmc.LatinHypercube(d=self.dimensions)
        samples = sampler.random(n=1000)
        x_samples = qmc.scale(samples, self.lb, self.ub)
        
        if self.params['model_type'] == 'GP':
            
            samples = model.sample_y(x_samples, n_samples=self.params['batch_size'])
            samples = np.mean(samples, axis=1)
            samples = samples.reshape(-1)
        else:
            
            predictions = np.array([tree.predict(x_samples) for tree in model.estimators_])
            mean_predictions = predictions.mean(axis=0)
            std_predictions = predictions.std(axis=0)
            samples = np.random.normal(mean_predictions, std_predictions)
            # selected_action = np.argmax(draws)  


        min_sample_index = np.argsort(samples)[:self.params['batch_size']]
        
        return x_samples[min_sample_index]

    def _find_samples(self, x_, model, best):
        
        x_batch = []
        if self.params['acquisition_function'] == 'EI' or self.params['acquisition_function'] == 'POI' or self.params['acquisition_function'] == 'LCB':
            for i in range(self.params['batch_size']):     
                          
                dim = self.dimensions
                f_min = np.inf
                x_min = None
                if self.params['batch_size'] > 1:
                    xi = np.random.uniform(0.01, 0.2)
                    kappa = np.random.uniform(1, 2.5)
                else:
                    xi = self.params['xi']
                    kappa = self.params['kappa']
    
                def acq(x):
                    
                    if self.params['acquisition_function'] == 'EI':
                        return -1*self._EI(model, x, x_, best, xi)
                    elif self.params['acquisition_function'] == 'POI':
                        return -1*self._POI(model, x, x_, best, xi)
                    elif self.params['acquisition_function'] == 'LCB':
                        return self._LCB(model, x, x_, kappa)
                
                if self.params['optimizer'] == 'PSO':
                    
                    pso = PSO()
                    pso.evaluation_function = acq
                    pso.lb = self.lb
                    pso.ub = self.ub
                    pso.max_evaluations = self.params['opt_cycles']
                    result = pso.optimize()
                    x_batch.append(result.X)

                else:
                    def generate_initial_guess_within_bounds(lower_bounds, upper_bounds):
                        return np.random.uniform(lower_bounds, upper_bounds)
                    
                    for _ in range(self.params['opt_cycles']):                
                                           
                        x0 = generate_initial_guess_within_bounds(self.lb, self.ub)
                        bounds = list(zip(self.lb, self.ub))
                        res = opt.minimize(acq, x0, method='L-BFGS-B', bounds=bounds, tol=1e-10)
                        if res.fun < f_min:
                            f_min = res.fun
                            x_min = res.x
                        
                    x_batch.append(x_min)
                
        elif self.params['acquisition_function'] == 'TS':

            x_batch = self._TS(model)

        return np.array(x_batch)

    
    def _update_model(self, x, y):

        if self.params['tune'] == True:
            if self.params['model_type'] == 'GP': 
                X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
                kernel = Matern()
                gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5)
                
                param_grid = {
                    # "kernel__length_scale": np.logspace(-10, 10, 10),  # Extended downwards
                    "kernel__nu": [0.5, 1.5, 2.5, np.inf, 3.5, 4.5, 5.5],  # Slightly extended
                    "alpha": [1e-12, 1e-10, 1e-8, 1e-6, 0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000]

                }
                
                grid_search = RandomizedSearchCV(gpr, param_grid, cv=2, n_jobs=-1, scoring='neg_mean_squared_error')
                grid_search.fit(X_train, y_train)          
                hyperparameters = grid_search.best_params_
                            
                kernel = Matern(length_scale=np.ones(self.dimensions), nu=hyperparameters['kernel__nu'])
                model = GaussianProcessRegressor(kernel=kernel, alpha=hyperparameters['alpha'], normalize_y=True, n_restarts_optimizer=5)
                model.fit(x, y)

            else:
    
                X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
                kernel = Matern()
                rf = RandomForestRegressor()
                param_grid = {
                    'n_estimators': np.arange(10, 300, 50),
                    'max_features': ['auto', 'sqrt', 'log2'],
                    'max_depth': np.arange(1, 20, 3),
                }
                grid_search = RandomizedSearchCV(rf, param_grid, cv=3, n_jobs=-1, scoring='neg_mean_squared_error')
                grid_search.fit(X_train, y_train)          
                hyperparameters = grid_search.best_params_
                
                model = RandomForestRegressor(n_estimators=hyperparameters['n_estimators'],
                                              max_features=hyperparameters['max_features'],
                                              max_depth=hyperparameters['max_depth'])
                model.fit(x, y)
        
        else:

            if self.params['model_type'] == 'GP': 
                               
                # kernel = Matern(length_scale=[1, 1, 1], nu=2.5)
                m52 = ConstantKernel(1.0) * Matern(length_scale=1.0, nu=2.5)
                model = GaussianProcessRegressor(kernel=m52, alpha=1)
                # model = GaussianProcessRegressor(kernel=kernel, alpha=1, normalize_y=True)
                model.fit(x, y)
            else:
    
                model = RandomForestRegressor(n_estimators=50,
                                              max_features='auto',
                                              max_depth=5)
                model.fit(x, y)
        
        
        return model
    
    def _run(self):
        """Run procedure for the BO method. 

        Returns
        -------
        optimum: Candidate
            Best solution found during the BO optimization.
            
        """

        self._check_params()

        if self.status == 'Optimization running (resumed)':
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1

        else:
            self._init_method()
        
            x_ = np.array([self._candidates[p].X for p in range(len(self._candidates))])
            y_ = np.array([self._candidates[p].f for p in range(len(self._candidates))]).reshape(-1,1)        
            self.x_eval = np.array([Candidate(self) for _ in range(self.params['batch_size'])], dtype=Candidate)
            
            best = np.min(y_)

            model = self._update_model(x_, y_)

        while True:
            

            x_new = self._find_samples(x_, model, best)
            x_ = np.vstack((x_, x_new))
            
            for p in range(len(self.x_eval)):
                self.x_eval[p].X = x_new[p]
                
            self._collective_evaluation(self.x_eval)
            
            y_new = np.array([self.x_eval[p].f for p in range(len(self.x_eval))])
            
            y_ = np.vstack((y_, y_new.reshape(-1,1)))
            
            best = np.min(y_)
            
            model = self._update_model(x_, y_, )

            if self._finalize_iteration():
                break

        return self.best
