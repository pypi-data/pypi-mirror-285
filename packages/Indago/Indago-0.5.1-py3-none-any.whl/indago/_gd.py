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

File content: Gradient Descent (GD) optimizer.
Usage: from indago import GD

NOTE: WORK IN PROGRESS

"""


from ._optimizer import Optimizer, Candidate
import numpy as np


class GD(Optimizer):
    """Gradient descent method class.

    Attributes
    ----------
    variant : str
        Name of the NM variant (``Vanilla`` or ``GaoHan``). Default: ``GaoHan``.
    X0 : ???
        ???
    _candidates : ndarray
        Array of Candidate instances.

    Returns
    -------
    optimizer : GD
        Gradient descent optimizer instance.
    """

    def __init__(self):
        """Private method which prepares the parameters to be validated by Optimizer._check_params.

        Returns
        -------
        None
            Nothing
            
        """
        
        Optimizer.__init__(self)

        # self.X = None
        self.X0 = 1
        self.variant = None


    def _check_params(self):
        """Private method which prepares the parameters to be validated by Optimizer._check_params.

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
            mandatory_params = 'dx'.split()

            if 'dx' not in self.params:
                self.params['dx'] = 1e-6
                defined_params += 'dx'.split()

        else:
            assert False, f'Unknown variant! {self.variant}'

        for param in mandatory_params:
            # if param not in defined_params:
            #    print('Missing parameter (%s)' % param)
            assert param in defined_params, f'Missing parameter {param}'

        for param in defined_params:
            if param not in mandatory_params and param not in optional_params:
                self.log(f'Warning: Excessive parameter {param}')

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)

    def _init_method(self):
        """Private method for initializing the NelderMead optimizer instance.
        Evaluates given initial candidates, selects starting point, constructs initial polytope/simplex.

        Returns
        -------
        None
            Nothing
            
        """

        self._evaluate_initial_candidates()

        # Generate set of points
        self._candidates = np.array([Candidate(self) for _ in range(self.dimensions + 1)],
                           dtype=Candidate)

        n0 = 0 if self._initial_candidates is None else self._initial_candidates.size
        self.log(f'{n0=}')
        # Generate initial positions
        self._candidates[0] = self._initial_candidates[0].copy()

        # Evaluate
        #self._collective_evaluation(self._candidates[:1])

        # if all candidates are NaNs       
        if np.isnan([c.f for c in self._candidates]).all():
            self._err_msg = 'ALL CANDIDATES FAILED TO EVALUATE'

        self._finalize_iteration()

    def _run(self):
        """Main loop of GD method.

        Returns
        -------
        optimum: Candidate
            Best solution found during the NelderMead optimization.
            
        """

        self._check_params()

        if self.status == 'Optimization running (resumed)':
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1
        else:
            self._init_method()

        dx = np.full(self.dimensions, self.params['dx'])
        DX = np.diag(dx)
        alpha = 1e-6
        delta = 1e1

        hist_x = np.full((2, self.dimensions), np.nan)
        hist_grad = np.full((2, self.dimensions), np.nan)
        grad = np.full(self.dimensions, np.nan)

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 10))

        while True:

            ax.plot(self._candidates[0].X[0], self._candidates[0].X[1], 'b+')
            for p in range(self.dimensions):
                # Random position
                self._candidates[p + 1].X = self._candidates[0].X + DX[p, :]
                self._candidates[p + 1].X = np.clip(self._candidates[p + 1].X, self.lb, self.ub)
                ax.plot(self._candidates[0].X[0], self._candidates[0].X[1], '.', c='grey')

            self._collective_evaluation(self._candidates[1:])

            for p in range(0, self.dimensions):
                grad[p] = (self._candidates[p + 1].f - self._candidates[0].f) / dx[p]
            if np.linalg.norm(grad) == 0:
                self.log('Zero gradient')
                break

            hist_x[-2, :] = hist_x[-1, :]
            hist_x[-1, :] = self._candidates[0].X.copy()
            hist_grad[-2, :] = hist_grad[-1, :]
            hist_grad[-1, :] = grad.copy()

            if self.it > 1:
                s = hist_x[-1, :] - hist_x[-2, :]
                y = hist_grad[-1, :] - hist_grad[-2, :]
                ss = np.dot(s, s)
                sy = np.dot(s, y)
                alpha = ss / sy

                if alpha <= 0 or np.isnan(alpha):
                    # eq 4.2
                    # Although the paper says this correction for nonconvex
                    # problems depends on sk for the current iteration,
                    # it's not available up to this point. Will use k-1
                    # regardless
                    alpha = np.linalg.norm(s) / np.linalg.norm(y)

                alpha = np.min([alpha, delta / np.linalg.norm(grad)])

                self.log(f'x={self._candidates[0].X}')
                self.log(f'{grad=}')
                # self.log(f'{s=}')
                # self.log(f'{y=}')
                # self.log(f'{alpha=}')


            self._candidates[0].X -= alpha * grad
            self._candidates[0].X = np.clip(self._candidates[0].X, self.lb, self.ub)
            self._collective_evaluation(self._candidates[:1])

            if self._finalize_iteration():
                break

        ax.plot(self._candidates[0].X[0], self._candidates[0].X[1], 'ro')
        ax.axis('equal')
        plt.savefig('gd.png')
        plt.close(fig)

        return self.best
