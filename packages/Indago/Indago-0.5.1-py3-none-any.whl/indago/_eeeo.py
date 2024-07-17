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

File content: Definition of Elite-Exchanging Ensemble Optimization (EEEO) optimizer.
Usage: from indago import EEEO

"""


import indago
import numpy as np
from ._optimizer import Optimizer, Candidate


class EEEO(Optimizer):
    """Elite-Exchanging Ensemble Optimization method class.

    Elite-Exchanging Ensemble Optimization (EEEO) runs a selection of optimizers in
    parallel and after each iteration injects the overall-best found solution into
    the employed optimizers.
    
    Attributes
    ----------
    variant : str
        Name of the EEEO variant. Default: ``Vanilla``.
    methods : dict
        Indago methods (variant, params) to use. Default: ``{'PSO': (None, None),
        'FWA': (None, None)}``. ``None`` values for variant and params will activate the
        corresponding default variant and params.
    _optimizers : list of Optimizer subclass objects
        Private list of optimizers used in EEEO.
        
    Returns
    -------
    optimizer : EEEO
        EEEO optimizer instance.
    """

    def __init__(self):
        Optimizer.__init__(self)

        self.variant = None
        self.methods = None


    def _check_params(self):
        """Private method which performs some EEEO-specific parameter checks
        and prepares the parameters to be validated by Optimizer._check_params.

        Returns
        -------
        None
            Nothing
        """

        if not self.variant:
            self.variant = 'Vanilla'

        if not self.methods:
            self.methods = {'PSO': (None, None),
                            'FWA': (None, None)}

        assert len(self.methods) >= 2, \
            'optimizer.methods should provide at least 2 optimization methods'

        for method in self.methods:
            assert method in 'ABC BA CMAES DE NM MSGS EFO FWA GD GWO MRFO PSO RS SSA'.split(), \
                'EEEO does not support {method} at this time'
        
        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []

        if self.variant == 'Vanilla':
            pass

        else:
            assert False, f'Unknown variant! {self.variant}'

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)


    def _init_method(self):
        """Private method for initializing the EEEO optimizer instance.
        
        Returns
        -------
        None
            Nothing
        """

        # Prepare optimizers
        self._optimizers = []
        for opt_name, (variant, params) in self.methods.items():
            opt = indago.optimizers_dict[opt_name]()
            opt.variant = variant
            opt.params = params if params else {}

            # parallel evaluation
            opt.processes = max(1, self.processes // len(self.methods))

            # pass parameters
            opt.evaluation_function = self.evaluation_function
            opt.lb = self.lb
            opt.ub = self.ub

            # pass progress information
            opt._progress_factor = lambda: self._progress_factor()

            self._optimizers.append(opt)

        # Initialize EEEO best
        self.best = None


    def _run(self):
        """Main loop of EEEO method.

        Returns
        -------
        optimum: Candidate
            Best solution found during the EEEO optimization.
            
        """

        self._check_params()

        if self.status == 'Optimization running (resumed)':
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1
        else:
            self._init_method()

        evals = [0] * len(self.methods)

        while True:

            resume = True if self.it > 0 else False

            bests = []
            for i, opt in enumerate(self._optimizers):
                opt.max_iterations = self.it + 1
                opt.optimize(resume=resume,
                             inject=self.best if not self.best == opt.best else None,
                             seed=self._seed)
                bests.append(opt.best)
                self.eval += opt.eval - evals[i]
                evals[i] = opt.eval

            self.best = np.min(bests)

            if self._finalize_iteration():
                break

        return self.best
