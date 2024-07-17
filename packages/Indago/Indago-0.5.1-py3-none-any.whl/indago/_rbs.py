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

File content: Definition of the experimental Random Boundary Search (RBS) optimizer.
Usage: from indago import RBS

"""


import numpy as np
import scipy.stats.qmc as qmc
from ._optimizer import Optimizer, Candidate


class RBS(Optimizer):
    """Random Boundary Search method class.
    
    Attributes
    ----------
    variant : str
        Name of the RBS variant. Default (and the only available option): ``Vanilla``.
    params : dict
        A dictionary of RBS parameters.
    _candidates : ndarray
        Array of Candidate instances.
        
    Returns
    -------
    optimizer : RBS
        RBS optimizer instance.
    """
    

    def __init__(self):
        Optimizer.__init__(self)

        self.variant = 'Vanilla'


    def _check_params(self):
        """Private method which performs some RS-specific parameter checks
        and prepares the parameters to be validated by Optimizer._check_params.

        Returns
        -------
        None
            Nothing
            
        """
        
        
        defined_params = list(self.params.keys())
        mandatory_params, optional_params = ['batch_size'], []
        
        if 'batch_size' in self.params:
            self.params['batch_size'] = int(self.params['batch_size'])
            assert self.params['batch_size'] > 0, \
                "batch_size parameter should be positive integer"
        else:
            self.params['batch_size'] = self.dimensions
        defined_params += 'batch_size'.split()

        if self.variant == 'Vanilla':
            pass
    
        else:
            assert False, f'Unknown variant! {self.variant}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)


    def _init_method(self):
        """Private method for initializing the RBS optimizer instance.
        Initializes and evaluates optimizer.max_evaluations number of candidates.

        Returns
        -------
        None
            Nothing
            
        """
        
        self._evaluate_initial_candidates()

        # Generate all candidates
        n0 = 0 if self._initial_candidates is None else self._initial_candidates.size
        self._candidates = np.array([Candidate(self) for _ in range(self.params['batch_size'] - n0)], dtype=Candidate)
        self._initialize_X(self._candidates[n0:])
        
        # Using specified particles initial positions
        for p in range(np.size(self._candidates)):
            if p < n0:
                self._candidates[p] = self._initial_candidates[p].copy()
            
        # Evaluate
        if n0 < self.params['batch_size']:
            self._collective_evaluation(self._candidates[n0:])

        # if all candidates are NaNs
        if np.isnan([c.f for c in self._candidates]).all():
            self._err_msg = 'ALL CANDIDATES FAILED TO EVALUATE'

        self._finalize_iteration()
    
        
    def _run(self):
        """Run procedure for the RS method. 

        Returns
        -------
        optimum: Candidate
            Best solution found during the RS optimization.
            
        """

        self._check_params()

        if self.status == 'Optimization running (resumed)':
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1
        else:
            self._init_method()

        while True:

            #works for uniform lower and upper boundary arrays 
            #should rescale the boundaries if you want this to work for all lb/ub
            #test only on problems like that (for now)
            
            rng1 = np.random.uniform(self.lb[0], self.ub[0])
            rng2 = np.random.uniform(rng1, self.ub[0])
            
            lb = np.ones(self.dimensions)*rng1
            ub = np.ones(self.dimensions)*rng2
            
            n = int(self.params['batch_size'])
            d = self.dimensions
            sampler = qmc.Sobol(d=d)
            samples = sampler.random(n=n)
            sample_set = qmc.scale(samples, lb, ub)
                        
            for s in range(len(sample_set)):
                self._candidates[s].X = sample_set[s]
            
            

            self._collective_evaluation(self._candidates)

            if self._finalize_iteration():
                break

        return self.best
