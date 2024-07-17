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

File content: Definition of Covariance Matrix Adaptation Evolution Strategies (CMAES) optimizer.
Usage: from indago import CMAES

NOTE: Due to np.linalg.eigh() returning irreproducible results, CMAES results are not strictly reproducible across
different platforms (Windows, Linux).

"""

import numpy as np
from ._optimizer import Optimizer, Candidate


class Solution(Candidate):
    """CMAES Solution class.

    Attributes
    ----------
    Z : ndarray
        Normally distributed random vector.

    Returns
    -------
    solution : Solution
        Solution instance.
    """

    def __init__(self, optimizer: Optimizer):
        Candidate.__init__(self, optimizer)
        # super(Particle, self).__init__(optimizer) # ugly version of the above

        self.Z = np.full(optimizer.dimensions, np.nan)


class CMAES(Optimizer):
    """Covariance Matrix Adaptation Evolution Strategies class method class.

    Reference: Hansen, N. The CMA Evolution Strategy: A Tutorial, arXiv:1604.00772 [cs.LG], 2023

    Attributes
    ----------
    variant : str
        Name of the CMAES variant. Default: ``Vanilla``.
    params : dict
        A dictionary of CMAES parameters.
    _pop : ndarray
        Array of Solution instances.

    Returns
    -------
    optimizer : CMAES
        CMAES optimizer instance.
    """

    def __init__(self):
        Optimizer.__init__(self)

        self.variant = None

    def _check_params(self):
        """Private method which performs some CMAES-specific parameter checks
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

        if self.variant == 'Vanilla':
            mandatory_params += 'pop_size sigma_scale'.split()

            if 'pop_size' in self.params:
                self.params['pop_size'] = int(self.params['pop_size'])
            else:
                self.params['pop_size'] = 4 + int(3 * np.log(self.dimensions))

            if 'sigma_scale' not in self.params:
                self.params['sigma_scale'] = 0.3

            defined_params += 'pop_size sigma_scale'.split()

        else:
            assert False, f'Unknown variant! {self.variant}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)

    def _init_method(self):
        """Private method for initializing the CMAES optimizer instance.
        Initializes and evaluates the population.

        Returns
        -------
        None
            Nothing
        """

        assert self.params['pop_size'] >= 4, \
            'population size (pop_size param) should be no less than 4'

        assert 1e-15 < self.params['sigma_scale'] < 1, \
            'sigma_scale param should be between 1e-15 and 1'

        # Generate population
        self._pop = np.array([Solution(self) for _ in range(self.params['pop_size'])])
        # self._initialize_X(self._pop)

        # Special initialization
        self._sigma = self.params['sigma_scale'] * np.min(self.ub - self.lb)
        for c in self._pop:
            c.Z = np.random.normal(size=self.dimensions)
            c.X = (self.lb + self.ub) / 2 + self._sigma * c.Z
            c.clip(self)

        self._evaluate_initial_candidates()
        n0 = 0 if self._initial_candidates is None else self._initial_candidates.size
        # Using specified particles initial positions
        for p in range(np.size(self._pop)):
            if p < n0:
                self._pop[p] = self._initial_candidates[p].copy()
                self._pop[p].Z = np.random.normal(size=self.dimensions)

        # Evaluate
        if n0 < np.size(self._pop):
            self._collective_evaluation(self._pop[n0:])

        # If all candidates are NaNs
        if np.isnan([c.f for c in self._pop]).all():
            self._err_msg = 'ALL CANDIDATES FAILED TO EVALUATE'

        # aliases
        self._N = self.dimensions
        self._lambda = self.params['pop_size']
        self._mu = self._lambda // 2

        # constants
        self._Weights = np.log(self._mu + 1 / 2) - np.log(np.arange(1, self._mu + 1)).T  # needs to be array of shape (mu,1)
        self._Weights = self._Weights / np.sum(self._Weights)
        self._mueff = np.sum(self._Weights) ** 2 / np.sum(self._Weights ** 2)
        self._cc = (4 + self._mueff / self._N) / (self._N + 4 + 2 * self._mueff / self._N)
        self._cs = (self._mueff + 2) / (self._N + self._mueff + 5)
        self._c1 = 2 / ((self._N + 1.3) ** 2 + self._mueff)
        self._cmu = min(1 - self._c1, 2 * (self._mueff - 2 + 1 / self._mueff) / ((self._N + 2) ** 2 + 2 * self._mueff / 2))
        self._damps = 1 + 2 * max(0, np.sqrt((self._mueff - 1) / (self._N + 1)) - 1) + self._cs
        self._chiN = self._N ** 0.5 * (1 - 1 / (4 * self._N) + 1 / (21 * self._N ** 2))

        # method variables
        self._sigma = self.params['sigma_scale'] * np.min(self.ub - self.lb)  # originally sigma=0.5 or sigma=1
        self._Pc = np.zeros(self._N)
        self._Ps = np.zeros(self._N)
        self._B = np.eye(self._N)
        self._D = np.eye(self._N)
        self._BD = np.eye(self._N)  # B dot D
        self._C = np.eye(self._N)  # BD dot BD.T
        self._eigeneval = 0

        # for speed
        self._DiagWeights = np.diag(self._Weights.flatten())

        self._finalize_iteration()

    def _run(self):
        """Main loop of CMAES method.

        Returns
        -------
        optimum: Solution
            Best solution found during the CMAES optimization.
        """

        # for EEEO
        if self._inject:
            worst = np.max(self._pop)
            worst.X = np.copy(self._inject.X)
            worst.O = np.copy(self._inject.O)
            worst.C = np.copy(self._inject.C)
            worst.f = self._inject.f
            # # CMAES specific
            # worst.Z = np.random.normal(size=self.dimensions)

        self._check_params()

        if self.status == 'Optimization running (resumed)':
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1
        else:
            self._init_method()

        while True:

            # Sort by rank and compute weighted mean
            self._pop = np.sort(self._pop)
            X_mu = np.array([c.X for c in self._pop[:self._mu]]).T
            Xmean = np.dot(X_mu, self._Weights)
            Z_mu = np.array([c.Z for c in self._pop[:self._mu]]).T
            Zmean = np.dot(Z_mu, self._Weights)

            # Update evolution paths
            self._Ps = (1 - self._cs) * self._Ps + (np.sqrt(self._cs * (2 - self._cs) * self._mueff)) * np.dot(self._B, Zmean).flatten()
            hsig = (np.linalg.norm(self._Ps) / np.sqrt(1 - (1 - self._cs) ** (2 * self.eval / self._lambda)) / self._chiN) \
                    < (1.4 + 2 / (self._N + 1))  # alternatively (2 + 4 / (N + 1))
            hsig = int(hsig)
            self._Pc = (1 - self._cc) * self._Pc + hsig * np.sqrt(self._cc * (2 - self._cc) * self._mueff) * np.dot(self._BD, Zmean).flatten()

            # Adapt covariance matrix C
            BDZmu = np.dot(self._BD, Z_mu)
            self._C = (1 - self._c1 - self._cmu) * self._C \
                + self._c1 * (np.dot(np.array([self._Pc]).T, np.array([self._Pc])) + (1 - hsig) * self._cc * (2 - self._cc) * self._C) \
                + self._cmu * np.dot(np.dot(BDZmu, self._DiagWeights), BDZmu.T)

            # Adapt step-size sigma
            # self._sigma = self._sigma * np.exp((self._cs / self._damps) * (np.linalg.norm(self._Ps) / self._chiN - 1))  # originally
            self._sigma = self._sigma * np.exp(min(1, (self._cs / self._damps) * (np.linalg.norm(self._Ps) / self._chiN - 1)))

            # Update B and D from C
            if self.eval - self._eigeneval > self._lambda / (self._c1 + self._cmu) / self._N / 10:
                self._eigeneval = self.eval
                self._C = np.triu(self._C) + np.triu(self._C, 1).T
                self._D, self._B = np.linalg.eigh(self._C)
                self._D, self._B = np.real(self._D), np.real(self._B)  # symmetrical C should guarantee real solutions of eig, but...
                self._D = np.diag(self._D)  # needs to be a matrix

                # limit condition of C to 1e14 + 1
                if np.max(np.diag(self._D)) > 1e14 * np.min(np.diag(self._D)):
                    fix = np.max(np.diag(self._D)) / 1e14 - np.min(np.diag(self._D))
                    self._C = self._C + fix * np.eye(self._N)
                    self._D = self._D + fix * np.eye(self._N)

                self._D = np.sqrt(self._D)  # np.diag(np.sqrt(np.diag(self._D)))
                self._BD = np.dot(self._B, self._D)

            # Escape flat fitness
            if self._pop[0] == self._pop[int(0.7 * self._lambda)]:
                self._sigma = self._sigma * np.exp(0.2 + self._cs / self._damps)

            # Compute new positions
            for c in self._pop:
                c.Z = np.random.normal(size=self._N)
                c.X = Xmean.flatten() + self._sigma * np.dot(self._BD, np.array([c.Z]).T).flatten()
                c.clip(self)

            # Evaluate
            self._collective_evaluation(self._pop)

            if self._finalize_iteration():
                break

        return self.best
