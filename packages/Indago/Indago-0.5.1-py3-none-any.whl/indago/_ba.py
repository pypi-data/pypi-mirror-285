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

File content: Definition of Bat Algorithm (BA) optimizer.
Usage: from indago import BA

"""


import numpy as np
from ._optimizer import Optimizer, Candidate


class Bat(Candidate):
    """BA Bat class. A Bat is a member of a BA swarm.
    
    Attributes
    ----------
    V : ndarray
        Bat velocity.
    Freq : ndarray
        Bat frequency.    
    A : float
        Bat loudness.
    r : float
        Bat pulse rate.
         
    Returns
    -------
    agent : Bat
        Bat instance.
    """
    
    def __init__(self, optimizer: Optimizer):
        Candidate.__init__(self, optimizer)
        #super(Particle, self).__init__(optimizer) # ugly version of the above
        self.V = np.full(optimizer.dimensions, np.nan)
        self.Freq = None
        self.A = None
        self.r = None


class BA(Optimizer):
    """Bat Algorithm method class.
    
    References: [1] Yang, Xin‐She, and Amir Hossein Gandomi. Bat algorithm: a novel approach 
    for global engineering optimization. Engineering computations (2012). https://arxiv.org/pdf/1211.6663.pdf, 
    [2] Yang, Xin‐She. Nature-inspired optimization algorithms (2021).
    
    In this implementation loudness **A** and pulse rate **r** are generated for each Bat separately (initial*2*rand).
    
    Attributes
    ----------
    variant : str
        Name of the BA variant. Default: ``Vanilla``.
    params : dict
        A dictionary of BA parameters.
    _swarm : ndarray
        Array of Bat instances.
    _bests : ndarray
        Best solutions.
        
    Returns
    -------
    optimizer : BA
        BA optimizer instance.
    """

    def __init__(self):
        Optimizer.__init__(self)

        self.variant = None
 

    def _check_params(self):
        """Private method which performs some BA-specific parameter checks
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
            mandatory_params = 'pop_size loudness pulse_rate alpha gamma freq_range'.split()

            if 'pop_size' not in self.params:
                self.params['pop_size'] = max(15, self.dimensions)
                defined_params += 'pop_size'.split()
            if 'loudness' not in self.params:
                self.params['loudness'] = 1
                defined_params += 'loudness'.split()
            if 'pulse_rate' not in self.params:
                self.params['pulse_rate'] = 0.001
                defined_params += 'pulse_rate'.split()
            if 'alpha' not in self.params:
                self.params['alpha'] = 0.9
                defined_params += 'alpha'.split()
            if 'gamma' not in self.params:
                self.params['gamma'] = 0.1
                defined_params += 'gamma'.split()
            if 'freq_range' not in self.params:
                self.params['freq_range'] = [0, 1]
                defined_params += 'freq_range'.split()
        else:
            assert False, f'Unknown variant! {self.variant}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)


    def _init_method(self):
        """Private method for initializing the BA optimizer instance.
        Initializes and evaluates the swarm.

        Returns
        -------
        None
            Nothing
            
        """

        self._evaluate_initial_candidates()

        # Generate a swarm
        self._swarm = np.array([Bat(self) for c in range(self.params['pop_size'])], dtype=Bat)

        # Generate initial positions
        n0 = 0 if self._initial_candidates is None else self._initial_candidates.size
        
        self._initialize_X(self._swarm)
        for p in range(self.params['pop_size']):
                  
            # Using specified particles initial positions
            if p < n0:
                self._swarm[p] = self._initial_candidates[p].copy()
            
            # Generate velocity
            self._swarm[p].V = 0.0
            
            # Frequency
            self._swarm[p].Freq = np.random.uniform(self.params['freq_range'][0], self.params['freq_range'][1])
            
            # Loudness
            self._swarm[p].A = self.params['loudness'] * 2 * np.random.uniform()
            
            # Pulse rate
            self._swarm[p].r = self.params['pulse_rate'] * 2 * np.random.uniform()

        # Evaluate
        if n0 < self.params['pop_size']:
            self._collective_evaluation(self._swarm[n0:])

        # if all candidates are NaNs
        if np.isnan([bat.f for bat in self._swarm]).all():
            self._err_msg = 'ALL CANDIDATES FAILED TO EVALUATE'
        
        self._bests = np.array([bat.copy() for bat in self._swarm])
           
        
        self._finalize_iteration()
        

    def _run(self):
        """Main loop of BA method.

        Returns
        -------
        optimum: Bat
            Best solution found during the BA optimization.
        """

        # for EEEO
        if self._inject:
            worst = np.max(self._swarm)
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

        if 'pulse_rate' in self.params:
            r_ = self.params['pulse_rate']
        if 'alpha' in self.params:
            alpha = self.params['alpha']
        if 'gamma' in self.params:
            gamma = self.params['gamma']
        if 'freq_range' in self.params:
            freq_min = self.params['freq_range'][0]
            freq_max = self.params['freq_range'][1]

        while True:
            
            A_avg = np.mean(np.array([self._swarm[p].A for p in range(len(self._swarm))]))
            
            #Calculate new velocity and new position
            for p, bat in enumerate(self._swarm):
            
                bat.Freq = freq_min + (freq_max - freq_min)*np.random.uniform()

                bat.V = bat.V + (bat.X - self.best.X)*bat.Freq
                bat.X = bat.X + bat.V
                
                if np.random.uniform() > bat.r:
                    bat.X = self.best.X + 0.05*np.abs(self.lb - self.ub)*np.random.normal(size=self.dimensions)*A_avg
                                       
                bat.clip(self)
               
            #Evaluate swarm
            for p, bat in enumerate(self._swarm):
                # Update personal best
                if bat.f <= self._bests[p].f and np.random.uniform() < bat.A:
                    self._bests[p] = bat.copy()
                    bat.A = alpha*bat.A
                    bat.r = r_ *(1 - np.exp(-gamma*self.it))
            self._collective_evaluation(self._swarm)
            
            if self._finalize_iteration():
                break
        
        return self.best
