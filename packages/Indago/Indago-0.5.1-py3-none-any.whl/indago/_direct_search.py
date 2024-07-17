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

File content: Definition of direct search optimizers: Nelder-Mead (NM) and Multi Scale Grid Search (MSGS).
Usage: from indago import NM, MSGS

"""


from ._optimizer import Optimizer, Candidate
import numpy as np


class NM(Optimizer):
    """Nelder-Mead method class.
    
    Reference: Gao, F., Han, L. Implementing the Nelder-Mead simplex algorithm 
    with adaptive parameters. Comput Optim Appl 51, 259–277 (2012). 
    https://doi.org/10.1007/s10589-010-9329-3

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
    optimizer : NM
        Nelder-Mead optimizer instance.

    """

    def __init__(self):
        """Private method which prepares the parameters to be validated by Optimizer._check_params.

        Returns
        -------
        None
            Nothing
            
        """
        
        Optimizer.__init__(self)

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
            self.variant = 'GaoHan'

        defined_params = list(self.params.keys())
        mandatory_params, optional_params = [], []

        if self.variant == 'Vanilla':         
            mandatory_params = 'init_step alpha gamma rho sigma'.split()
            if 'init_step' not in self.params:
                self.params['init_step'] = 0.4
                defined_params += 'init_step'.split()
            if 'alpha' not in self.params:
                self.params['alpha'] = 1.0
                defined_params += 'alpha'.split()                
            if 'gamma' not in self.params:
                self.params['gamma'] = 2.0
                defined_params += 'gamma'.split()
            if 'rho' not in self.params:
                self.params['rho'] = 0.5
                defined_params += 'rho'.split()
            if 'sigma' not in self.params:
                self.params['sigma'] = 0.5
                defined_params += 'sigma'.split()
        elif self.variant == 'GaoHan':
            mandatory_params = 'init_step'.split()
            if 'init_step' not in self.params:
                self.params['init_step'] = 0.4
                defined_params += 'init_step'.split()

        else:
            assert False, f'Unknown variant! {self.variant}'

        for param in mandatory_params:
            # if param not in defined_params:
            #    print('Missing parameter (%s)' % param)
            assert param in defined_params, f'Missing parameter {param}'

        for param in defined_params:
            if param not in mandatory_params and param not in optional_params:
                self._log(f'Warning: Excessive parameter {param}')

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
        self._candidates = np.array([Candidate(self) for _ in range(self.dimensions + 1)], \
                            dtype=Candidate)

        # Generate initial positions
        self._candidates[0] = self._initial_candidates[0].copy()

        for p in range(1, self.dimensions + 1):

            # Random position
            dx = np.zeros([self.dimensions])
            dx[p - 1] = self.params['init_step']
            self._candidates[p].X = self._candidates[0].X + dx * (self.ub - self.lb)
            self._candidates[p].X = np.clip(self._candidates[p].X, self.lb, self.ub)

        # Evaluate
        self._collective_evaluation(self._candidates[1:])
        
        # if all candidates are NaNs       
        if np.isnan([c.f for c in self._candidates]).all():
            self._err_msg = 'ALL CANDIDATES FAILED TO EVALUATE'
        
        self._finalize_iteration()

    def _run(self):
        """Main loop of NelderMead method.

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
        
        # Prepare parameters
        if self.variant == 'Vanilla':
            alpha = self.params['alpha']
            gamma = self.params['gamma']
            rho = self.params['rho']
            sigma = self.params['sigma']
        elif self.variant == 'GaoHan':
            alpha = 1.0
            gamma = 1 + 2 / self.dimensions
            rho = 0.75 - 1 / 2 / self.dimensions
            sigma = 1 - 1 / self.dimensions

        while True:
            self._candidates = np.sort(self._candidates)
            reduction = False

            self._progress_log()

            # # Check stopping conditions
            # if self._stopping_criteria():
            #     break

            # Center
            X0 = np.zeros(self.dimensions)
            for p in range(self.dimensions):
                X0 += self._candidates[p].X
            X0 /= self.dimensions

            dX = X0 - self._candidates[-1].X

            # Reflection
            Xr = X0 + alpha * dX
            Xr = np.clip(Xr, self.lb, self.ub)
            cR = Candidate(self)
            cR.X = Xr

            self._collective_evaluation([cR])

            if self._candidates[0] <= cR <= self._candidates[-2]:
                self._candidates[-1] = cR.copy()

            elif cR < self._candidates[0]:
                # Expansion
                Xe = X0 + gamma * dX
                Xe = np.clip(Xe, self.lb, self.ub)
                cE = Candidate(self)
                cE.X = Xe

                self._collective_evaluation([cE])

                if cE < cR:
                    self._candidates[-1] = cE.copy()
                else:
                    self._candidates[-1] = cR.copy()

            elif cR < self._candidates[-1]:
                # Contraction
                Xc = X0 + rho * dX
                Xc = np.clip(Xc, self.lb, self.ub)
                cC = Candidate(self)
                cC.X = Xc

                self._collective_evaluation([cC])

                if cC < self._candidates[-1]:
                    self._candidates[-1] = cC.copy()
                else:
                    reduction = True

            else:
                # Internal contraction
                Xc = X0 - rho * dX
                Xc = np.clip(Xc, self.lb, self.ub)
                cC = Candidate(self)
                cC.X = Xc

                self._collective_evaluation([cC])

                if cC < self._candidates[-1]:
                    self._candidates[-1] = cC.copy()
                else:
                    reduction = True

            # Reduction
            if reduction:
                for p in range(1, self.dimensions + 1):
                    self._candidates[p].X = self._candidates[0].X + sigma * (self._candidates[p].X - self._candidates[0].X)
                    # self._candidates[p].evaluate()
                self._collective_evaluation(self._candidates[1:])

            if self._finalize_iteration():
                break

        return self.best


class MSGS(Optimizer):
    """Multi Scale Grid Search class.

    Parameters
    ----------
    variant : str
        Name of the MSGS variant. Default: ``Vanilla``.
    _x : Candidate
        Candidate for current point.
    _y : ndarray of int
        The search grid indices for current point.

    Attributes
    ----------
    X0 : ???
        ???
    _scale : int
        Scale.
    _n : int
        Number of points in the grid.
    _I : ndarray
        Point index span.
    _point_x : Candidate
        Starting point.
    _X_map : list
        Map of points.
    _H : list
        ???
        
    """

    def __init__(self):
        Optimizer.__init__(self)
        
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
        
        if 'n' in defined_params:
            self.params['n'] = int(self.params['n'])

        if self.variant == 'Vanilla':
            mandatory_params = 'n zoom_in zoom_out'.split()
            if 'n' not in self.params:
                self.params['n'] = 20
                defined_params += 'n'.split()
            if 'zoom_in' not in self.params:
                self.params['zoom_in'] = 4
                defined_params.append('zoom_in')
            if 'zoom_out' not in self.params:
                self.params['zoom_out'] = 2
                defined_params.append('zoom_out')

        else:
            assert False, f'Unknown variant! {self.variant}'

        for param in mandatory_params:
            # if param not in defined_params:
            #    print('Missing parameter (%s)' % param)
            assert param in defined_params, f'Missing parameter {param}'

        for param in defined_params:
            if param not in mandatory_params and param not in optional_params:
                self._log(f'Warning: Excessive parameter {param}')

        Optimizer._check_params(self, mandatory_params, optional_params, defined_params)

    def _init_method(self):
        """Private method for initializing the MSGS optimizer instance.
        Evaluates given initial candidates, selects starting point, constructs and deforms 
        (if needed) initial grid, initializes grid search history.

        Returns
        -------
        None
            Nothing
            
        """
        
        self._evaluate_initial_candidates()

        self._scale = 1
        self._n = self.params['n']
        self._I = np.arange(-self._n, self._n + 1)
        self._point_x = self._initial_candidates[0].copy()

        # The initial mesh always fills entire domain and initial point is snapped tzo the grid
        # self._center = 0.5 * (self.lb + self.ub)
        center = self._point_x.X.copy()
        self._X_map = [self._I for i in range(self.dimensions)]
        self._reinit_grid(center, self._scale, 'Initial grid')
        self._point_x = self._y_to_x(self.point_y)

        # self._collective_evaluation([self._x])
        self._H.append(list(self.point_y))
        self._log('Initial point: [' + ', '.join([f'{x}' for x in self._point_x.X]) + ']')

        self._finalize_iteration()

    def _reinit_grid(self, center, scale, grid_action):
        """(Re)creates the search grid according to given center of the grid and grid scale. Grid action is only
        informative argument and it does not influence the generation of the search grid. If current point
        (``MSGS._x``) is not on the grid, only the closest discrete values are adjusted to the current point resulting
        with locally deformed search grid.

        Parameters
        ----------
        center : ndarray
            The center of the search grid. Grid is initially constructed using ``n`` divisions before and after the
            center (2n + 1 divisions). If needed, due to bounds, center is automatically shifted and adjusted in order to ensure the search
            mesh is inside the bounds.

        scale: int
            The scale of the search grid. The initial grid is generated using ``scale=1`` which covers entire domain.
            The discretization step for each optimization variable is defined as
            ``dx = (self.ub - self.lb) / (2 * self._n * scale)``.

        grid_action: string
            Information about the reason why the search grid reinitialization is being conducted. Possible values are:
            ``none``, ``scale_up``, ``scale_down`` or ``shift``.
            
        """

        # Calculate the mesh size
        dx = (self.ub - self.lb) / (2 * self._n * scale)

        # Chck if the mesh is changed due to the scaling
        mesh_changed = scale != self._scale
        self._scale = scale

        new_center = center.copy()

        if scale == 1:
            for i in range(self.dimensions):
                self._X_map[i] = np.linspace(self.lb[i], self.ub[i], 2 * self._n + 1)
                i_c = np.argmin(np.abs(self._X_map[i] - center[i]))
                self._X_map[i][i_c] = center[i]

        else:
            for i in range(self.dimensions):
                # Check if new mesh is within the bounds
                xi = new_center[i] + self._I * dx[i]
                dil = int(np.sum(xi < self.lb[i]))
                new_center[i] += dx[i] * dil
                diu = int(np.sum(xi > self.ub[i]))
                new_center[i] -= dx[i] * diu

                # self._log(f'{dil=}, {diu=}')
                if dil > 0 and diu > 0:
                    assert False, 'Major fail, cannot crate the grid!'

                # Check if mesh is changed due to the within bounds adjustment
                if dil > 0 or diu > 0:
                    mesh_changed = True

                # Create X-map for new mesh
                self._X_map[i] = new_center[i] + self._I * dx[i]

        # self._X_map = [new_center[i] + self._I * dx[i] for i in range(self.dimensions)]
        self.point_y = self._x_to_y(self._point_x)
        self._H = [list(self.point_y)]

        self._log(f'Grid reinitialization {scale=}, {grid_action=}, {mesh_changed=}')
        # self._log(f'{np.min(self._X_map)} - {np.max(self._X_map)}')
        # self._log(f'{center=}')
        # self._log(f'{dx=}')
        return mesh_changed

    def _x_to_y(self, x: Candidate):
        """Converts the candidate defined with coordinates in the search space to indices of candidates location on the
        search grid.

        Parameters
        ----------
        x : Candidate
            The candidate state you want to transform.

        Returns
        -------
        y : ndarray of int
            The indices of the search grid where point x is located.
        """

        y = np.zeros(self.dimensions, dtype=int)
        for i in range(self.dimensions):
            y[i] = np.argmin(np.abs(x.X[i] - self._X_map[i])) - self._n
        return y

    def _y_to_x(self, y: np.ndarray):
        """Converts the indices of the search grid to a candidate.

        Parameters
        ----------
        y : ndarray of int
            The indices of the search grid where point x is located.

        Returns
        -------
        x : Candidate
            The candidate state you want to transform.
        """

        x = Candidate(self)
        for i in range(self.dimensions):
            x.X[i] = self._X_map[i][y[i] + self._n]
        return x

    def _find_dir(self, y, dy=None):
        """Finds a search direction based on finite difference approximation of a gradiend using points on the search
        grid. It utilizes a 2-point or 3-point gradient calculation, if existing direction ``dy`` is given or not,
        respectively.

        Parameters
        ----------
        y : ndarray of int
            The coordinates of current point defined using indices of the search grid.
        dy : ndarray of int
            A step utilized in previous step of the method defined as an array of possible directions ``[-1, 0, 1]``
            for each dimension.

        Returns
        -------
        new_direction : ndarray of int
            New direction in terms of steps (one of ``[-1, 0, 1]``) on the search grid for each dimension.
        """

        # self._log(f'{y=}')
        # self._log(f'{self._x.X=}')
        new_dy = np.zeros_like(y, dtype=int)
        eval_map = np.full(self.dimensions * 2, -1, dtype=int)
        C = np.array([], dtype=Candidate)
        cnt = 0

        for i in range(self.dimensions):
            _dy = np.zeros(self.dimensions, dtype=int)
            _dy[i] = -1
            yn = y + _dy
            _dy[i] = 1
            yp = y + _dy

            calc_n = True
            calc_p = True
            if dy is not None:
                if dy[i] == 1:
                    calc_p = False
                if dy[i] == -1:
                    calc_n = False

            if np.abs(yn[i]) <= self._n and calc_n:
                C = np.append(C, np.array([self._y_to_x(yn)]))
                eval_map[2 * i + 0] = cnt
                cnt += 1

            if np.abs(yp[i]) <= self._n and calc_p:
                C = np.append(C, np.array([self._y_to_x(yp)]))
                eval_map[2 * i + 1] = cnt
                cnt += 1

        if C.size > 0:
            self._collective_evaluation(C)

        for i in range(self.dimensions):
            c0 = self._point_x

            if eval_map[2 * 1 + 0] >= 0:
                cn = C[eval_map[2 * i + 0]]
            else:
                cn = None

            if eval_map[2 * 1 + 1] >= 0:
                cp = C[eval_map[2 * i + 1]]
            else:
                cp = None

            if cp and cn:
                new_dy[i] = np.argmin([cn, c0, cp]) - 1
            elif cp:
                new_dy[i] = np.argmin([c0, cp])
            elif cn:
                new_dy[i] = np.argmin([cn, c0]) - 1
            else:
                new_dy[i] = 0

        # self._log(f'{new_dy=}')
        return new_dy

    def _run(self):
        """Main loop of MSGS method.

        Returns
        -------
        optimum: Candidate
            Best solution found during the MSGS optimization.
        """

        self._check_params()

        if self.status == 'Optimization running (resumed)':
            if self._stopping_criteria():
                return self.best
            # TODO inspect why this is necessary for resume to work:
            self.it += 1
        else:
            self._init_method()

        k, k_max = 0, 2
        d = self.dimensions

        scale = self._scale
        grid_action = 'none'
        action = 'find_dir_3p'
        shift_count = 0

        while True:

            self._update_history()  # Adding history record allows iterations without evaluation

            if grid_action == 'shift':
                if shift_count >= 2 and scale >= 2:
                    scale = int(scale / self.params['zoom_out'])
                    shift_count = 0
                    self._log('scale_down (3rd consecutive shift)')

                if self._reinit_grid(self._point_x.X, scale, grid_action):
                    # Center is changed
                    grid_action = 'none'
                    shift_count += 1
                    self._log(f'shift ({shift_count=})')
                else:
                    # Center is not changed
                    scale = scale * self.params['zoom_in']
                    self._reinit_grid(self.best.X, scale, 'scale_up (shift failed)')
                    action = 'find_dir_3p'
                    grid_action = 'none'

            elif grid_action == 'scale_up':
                scale *= self.params['zoom_in']
                if scale > 10e15:
                    self.status = 'Optimization terminated: maximum number xtol precision reached'
                    break
                self._reinit_grid(self._point_x.X, scale, grid_action)
                action = 'find_dir_3p'
                grid_action = 'none'
                shift_count = 0

            elif grid_action == 'scale_down':
                if scale >= self.params['zoom_out']:
                    scale /= self.params['zoom_out']
                self._reinit_grid(self._point_x.X, scale)
                action = 'find_dir_3p'
                grid_action = 'none'
                shift_count = 0

            elif grid_action == 'none':
                pass
            else:
                assert False, f'Unknown {grid_action=}'

            if action == 'find_dir_3p':
                # Finding a new direction based on the full gradient calculation
                dy = self._find_dir(self.point_y)
                action = 'check_dir'

            elif action == 'find_dir_2p':
                # Finding a new direction based on one-side gradient calculation
                dy = self._find_dir(self.point_y, dy)
                action = 'check_dir'
                k += 1

            elif action == 'check_dir':
                # self._log(f'{dy=}')

                if np.all(dy == 0):
                    # None of x_next's neighbouring points are better
                    if self._point_x == self.best:
                        # x_next is the best, hence convergence is finished
                        action = 'converged'
                    else:
                        action = 'move_to_best'

                else:
                    # Moving in dy direction
                    new_y = self.point_y + dy

                    # Check bounds
                    # outside_y = new_y != np.clip(new_y, -self._n, self._n, dtype=int)
                    outside_y = np.logical_or(new_y < -self._n, new_y > self._n)
                    if not np.any(outside_y):
                        # New point is inside the mesh
                        # dy = new_y - self._y
                        action = 'move'
                    else:
                        # self._log(f'bounds problem {dy=}')
                        # New point is outside the mesh
                        # Calculate x coordinates of the new point
                        dx = (self.ub - self.lb) / (2 * self._n * scale)
                        new_x = self._y_to_x(self.point_y).X + dy * dx

                        outside_x = np.logical_or(new_x < self.lb, new_x > self.ub)

                        # Correct the step
                        dy[outside_x] = 0
                        # self._log(f'corrected step {dy=}')
                        if np.any(np.abs(dy) > 0):
                            action = 'move'
                        else:
                            action == 'converged'

                        if np.any(np.logical_and(np.abs(dy) > 0, np.logical_and(outside_y, np.logical_not(outside_x)))):
                            grid_action = 'shift'

            elif action == 'move_to_best':
                # Switching to the best point
                self.point_y = self._x_to_y(self.best)
                self._point_x = self.best.copy()
                action = 'find_dir_3p'
                k = 0

            elif action == 'move':
                # Moving in dy direction
                self.point_y = self.point_y + dy
                self.point_y = np.clip(self.point_y, -self._n, self._n, dtype=int)

                if list(self.point_y) in self._H:
                    action = 'move_to_best'
                else:
                    # Calculate x_next
                    x_last = self._point_x.copy()
                    self._point_x = self._y_to_x(self.point_y)
                    # Evaluate x_next
                    self._collective_evaluation([self._point_x])
                    self._H.append(list(self.point_y))

                # Set finding new direction if there is no improvement in new point
                if self._point_x <= x_last:
                    action = 'check_dir'
                elif k < k_max:
                    action = 'find_dir_2p'
                else:
                    action = 'move_to_best'

            elif action == 'converged':
                self._point_x = self.best
                rel_err = 1 / (2 * self._n * scale)
                # print(f'{dx=}')
                # if np.all(rel_err < self.params['xtol']):
                #     self._log(f'Relative precision reached for all optimization variables.')
                #     break
                grid_action = 'scale_up'

            else:
                assert False, f'Unknown action {action=}'

            if self._finalize_iteration():
                break

        return self.best
