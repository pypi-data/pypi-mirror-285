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

File content: Definition of Manta Ray Foraging Optimization (MRFO) optimizer.
Usage: from indago import MRFO

"""


import numpy as np
from ._optimizer import Optimizer, Candidate


class MRFO(Optimizer):
    """Manta Ray Foraging Optimization method class.
    
    Reference: Zhao, Weiguo, Zhenxing Zhang, and Liying Wang. Manta ray foraging 
    optimization: An effective bio-inspired optimizer for engineering applications.
    Engineering Applications of Artificial Intelligence 87 (2020): 103300.
    
    Attributes
    ----------
    variant : str
        Name of the MRFO variant. Default: ``Vanilla``.
    params : dict
        A dictionary of MRFO parameters.
    _mantas : ndarray
        Array of Candidate instances.
        
    Returns
    -------
    optimizer : MRFO
        MRFO optimizer instance.
        
    """

    def __init__(self):
        Optimizer.__init__(self)
        
        self.variant = None

    def _check_params(self):
        """Private method which performs some MRFO-specific parameter checks
        and prepares the parameters to be validated by Optimizer._check_params.

        Returns
        -------
        None
            Nothing
            
        """

        if not self.variant:
            self.variant = 'Vanilla'
        
        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []
        
        if 'pop_size' in self.params:
            self.params['pop_size'] = int(self.params['pop_size'])

        if self.variant == 'Vanilla':
            mandatory_params = 'pop_size f_som'.split()
            if 'pop_size' not in self.params:
                self.params['pop_size'] = max(10, self.dimensions)
                defined_params += 'pop_size'.split()
            if 'f_som' not in self.params:
                self.params['f_som'] = 2
                defined_params += 'f_som'.split()    
        else:
            assert False, f'Unknown variant! {self.variant}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)

    def _init_method(self):
        """Private method for initializing the MRFO optimizer instance.
        Initializes and evaluates the swarm.

        Returns
        -------
        None
            Nothing
            
        """
        
        assert self.max_iterations or self.max_evaluations or self.max_elapsed_time, \
            'optimizer.max_iteration, optimizer.max_evaluations, or self.max_elapsed_time should be provided for this method/variant'

        self._evaluate_initial_candidates()

        # Generate a swarm
        self._mantas = np.array([Candidate(self) for c in range(self.params['pop_size'])], dtype=Candidate)
        
        # Generate initial positions
        n0 = 0 if self._initial_candidates is None else self._initial_candidates.size
        
        self._initialize_X(self._mantas)
        
        # Using specified particles initial positions
        for p in range(self.params['pop_size']):
            if p < n0:
                self._mantas[p] = self._initial_candidates[p].copy()

        # Evaluate
        if n0 < self.params['pop_size']:
            self._collective_evaluation(self._mantas[n0:])
            
        # if all candidates are NaNs       
        if np.isnan([manta.f for manta in self._mantas]).all():
            self._err_msg = 'ALL CANDIDATES FAILED TO EVALUATE'

        self._finalize_iteration()
        
    def _run(self):
        """Main loop of MRFO method.

        Returns
        -------
        optimum: Candidate
            Best solution found during the MRFO optimization.
            
        """

        # for EEEO
        if self._inject:
            worst = np.max(self._mantas)
            worst.X = np.copy(self._inject.X)
            worst.O = np.copy(self._inject.O)
            worst.C = np.copy(self._inject.C)
            worst.f = self._inject.f

        self._check_params()

        if self.status == 'Optimization running (resumed)':
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1
        else:
            self._init_method()

        while True:
            
            X_ = np.copy(self._mantas)
            
            if np.random.uniform() < 0.5:
                
                # CYCLONE FORAGING
                r = np.random.uniform(size=self.dimensions)
                r1 = np.random.uniform(size=self.dimensions)
                # beta = 2*np.exp(r1*((self.max_iterations-self.it+1)/self.max_iterations))*np.sin(2*np.pi*r1)
                beta = 2 * np.exp(r1 * (1 - self._progress_factor())) * np.sin(2*np.pi*r1)
                
                if self._progress_factor() < np.random.uniform():
                    X_rand = np.random.uniform(self.lb, self.ub, size=self.dimensions)
                    self._mantas[0].X = X_rand + r*(X_rand - X_[0].X) + beta*(X_rand - X_[0].X)
                    for p in range(1, len(self._mantas)):
                        self._mantas[p].X = X_rand + r*(self._mantas[p-1].X - X_[p].X) + beta*(X_rand - X_[p].X)
                else:
                    self._mantas[0].X = self.best.X + r*(self.best.X - X_[0].X) + beta*(self.best.X - X_[0].X)
                    for p in range(1, len(self._mantas)):
                        self._mantas[p].X = self.best.X + r*(self._mantas[p-1].X - X_[p].X) + beta*(self.best.X - X_[p].X)
                        
            else: 
                
                # CHAIN FORAGING
                r = np.random.uniform(size=self.dimensions)
                alpha = 2*r*np.sqrt(np.abs(np.log(r)))
                self._mantas[0].X = X_[0].X + r*(self.best.X - X_[0].X) + alpha*(self.best.X - X_[0].X)
                for p in range(1, len(self._mantas)):
                    self._mantas[p].X = X_[p].X + r*(self._mantas[p-1].X - X_[p].X) + alpha*(self.best.X - X_[p].X)
            
            for manta in self._mantas:
                manta.clip(self)
            
            self._collective_evaluation(self._mantas)
                               
            # SOMERSAULT FORAGING        
            r2 = np.random.uniform(size=self.dimensions)
            r3 = np.random.uniform(size=self.dimensions)
            for p, p_ in zip(self._mantas, X_):
                p.X = p_.X + self.params['f_som']*(r2*self.best.X - r3*p_.X)
            
            for manta in self._mantas:
                manta.clip(self)
                
            self._collective_evaluation(self._mantas)
            
            if self._finalize_iteration():
                break

        return self.best
