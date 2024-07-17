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

File content: Definition of Simulated Annealing (SA) optimizer.
Usage: from indago import SA

NOTE: WORK IN PROGRESS

"""



import numpy as np
from ._optimizer import Optimizer, Candidate
import random as rnd


Agent = Candidate

class SA(Optimizer):
    """Simulated Annealing method class

    Attributes
    ----------
    _candidates : ndarray
        Array of Candidate instances.
    _bests : ndarray
        Best solutions.
    
    Returns
    -------
    optimizer : SA
        SA optimizer instance.

    """

    def __init__(self):
        """Initialization"""
        Optimizer.__init__(self)

        self.variant = 'Vanilla'


    def _check_params(self):
        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []

        if self.variant == 'Vanilla':
            mandatory_params = 'pop T0'.split()

            if 'pop' not in self.params:
                self.params['pop'] = 1 #just 1 agent, might experiment with a population
                defined_params += 'pop'.split()

            if 'T0' not in self.params:
                self.params['T0'] = self.dimensions #initial temperature
                defined_params += 'T0'.split()
        else:
            assert False, f'Unknown variant! {self.variant}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)


    def _init_method(self):

        self._evaluate_initial_candidates()

        # Generate agents
        self._candidates = np.array([Agent(self) for c in range(self.params['pop'])], dtype=Agent)

        # Generate initial points
        n0 = 0 if self._initial_candidates is None else self._initial_candidates.size
        
        self._initialize_X(self._candidates)
        
        # Using specified initial positions
        for p in range(self.params['pop']):
            if p < n0:
                self._candidates[p] = self._initial_candidates[p].copy()

        # Evaluate
        if n0 < self.params['pop']:
            self._collective_evaluation(self._candidates[n0:])

        # if all candidates are NaNs       
        if np.isnan([c.f for c in self._candidates]).all():
            self._err_msg = 'ALL CANDIDATES FAILED TO EVALUATE'
        
        self._bests = np.array([c.copy() for c in self._candidates], dtype=Candidate)

        self._finalize_iteration()

    def _run(self):

        self._check_params()

        if self.status == 'Optimization running (resumed)':
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1
        else:
            self._init_method()

        while True:
            
            epsilon = []
            for i in range(len(self.lb)):
                rand_ = np.random.normal(np.mean(np.linspace(self.lb[i],self.ub[i])),np.std(np.linspace(self.lb[i],self.ub[i]))) #random gaussian walk in each dimension
                epsilon.append(rand_)

            for c in self._candidates:
                c.X = c.X + epsilon
                c.clip()

            cS_old = np.copy(self._candidates)

            # Evaluate agent
            self._collective_evaluation(self._candidates)

            T = self.params['T0'] / float(self.it + 1)


            for p, c in enumerate(self._candidates):
                if self._candidates[p].f < cS_old[p].f:
                    self._candidates[p].f = np.copy(cS_old[p].f)
                    self._candidates[p].X = np.copy(cS_old[p].X)
                else:
                    r = np.random.uniform(0,1)
                    p_ = np.exp((-1*(self._candidates[p].f - cS_old[p].f))/T)
                    if p_ > r:
                        self._candidates[p].f = np.copy(cS_old[p].f)
                        self._candidates[p].X = np.copy(cS_old[p].X)

            if self._finalize_iteration():
                break
        
        return self.best

