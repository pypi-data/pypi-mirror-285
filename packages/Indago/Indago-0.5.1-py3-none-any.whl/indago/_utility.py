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

File content: Definition of Indago utility functions.
Usage: from indago import minimize, minimize_exhaustive, inspect, inspect_optimizers, unconstrain, read_evals_db

"""


import indago
import numpy as np
import time
from rich.table import Table
from rich.console import Console
from copy import deepcopy
import os


def minimize(evaluation_function, 
             lb=None, 
             ub=None, 
             optimizer_name='PSO', 
             optimize_seed=None,
             **kwargs):
    """Shorthand one-line utility function for running an optimization.
        
        Parameters
        ----------
        evaluation_function : callable
            Evaluation function. Takes a design vector (ndarray) and returns fitness value (float), 
            or in case of multiobjective and/or constrainted optimization a tuple with 
            objectives (float) and constraints (float).
        lb : list or ndarray or float or None
            Lower bounds. If ``None`` lower bounds will be taken from **evaluation_function.lb**.
        ub : list or ndarray or float or None
            Upper bounds. If ``None`` upper bounds will be taken from **evaluation_function.ub**.
        optimizer_name : str
            Name (abbreviation) of the optimization method used. Default value is ``'PSO'``.
        optimize_seed : int or None
            A random seed. Use the same value for reproducing identical stochastic procedures.
        **kwargs : kwarg
            Keyword arguments passed to the Optimizer object correspoding to the **optimizer_name**.

        Returns
        -------
        (X, f) or (X, f, O, C) : tuple
            Results of the optimization, comprising the design vector **X** (ndarray) 
            and the corresponding minimum fitness **f** (float).
            In case of more than one objective and/or defined constraints, results also include
            objectives **O** (ndarray), and constraints **C** (ndarray).
    """
    
    assert optimizer_name in indago.optimizers_name_list, \
        f'Unknown optimizer name "{optimizer_name}". Use one of the following names: {", ".join(indago.optimizers_name_list)}.'

    # initialize optimizer
    opt = indago.optimizers_dict[optimizer_name]()
    
    # pass parameters
    opt.evaluation_function = evaluation_function
    opt.lb = lb
    opt.ub = ub
    for kw, val in kwargs.items():
        setattr(opt, kw, val)
        # print(f'{kw=}: {val=}')
    
    # run
    result = opt.optimize(seed=optimize_seed)
    
    # return
    if opt.objectives == 1 and opt.constraints == 0:
        return result.X, result.f
    else:
        return result.X, result.f, result.O, result.C


def minimize_exhaustive(evaluation_function, 
                        lb=None, 
                        ub=None, 
                        optimizer_name='PSO', 
                        params_ranges_dict=None,
                        hyper_optimizer_name='FWA',
                        runs=50, # optimizer runs
                        hyper_evaluations=1000, # hyper-optimizer evaluations
                        optimize_seed=None,
                        **kwargs):
    """Utility function for exhaustive optimization with meta-optimizing optimizer parameters.
       The defined meta-optimizer (``hyper_optimizer_name``) will be used for meta-optimizing
       the defined optimizer (``optimizer_name``), namely its default variant. The meta-optimization 
       will be conducted for a number of evaluations (``hyper_evaluations``). Each evaluation 
       in the meta-optimization will return a median result of multiple runs (``runs``) of 
       the optimizer used (``optimizer_name``). After the meta-optimization is conducted, 
       a final round of multiple runs (``runs``) of optimization with the defined optimizer 
       (``optimizer_name``) and optimal method parameters is performed, and the overall best result 
       is returned together with the optimal method parameters.
    
       Parameters
       ----------
       evaluation_function : callable
           Evaluation function. Takes a design vector (ndarray) and returns fitness value (float), 
           or in case of multiobjective and/or constrainted optimization a tuple with 
           objectives (float) and constraints (float).
       lb : list or ndarray or float or None
           Lower bounds. If ``None`` lower bounds will be taken from **evaluation_function.lb**.
       ub : list or ndarray or float or None
           Upper bounds. If ``None`` upper bounds will be taken from **evaluation_function.ub**.
       optimizer_name : str
           Name (abbreviation) of the optimization method used. Default value is ``'PSO'``.
       params_ranges_dict : dict or None
           A dict with method parameter names as dict keys and lists of minimum and maximum values of the
           parameter in question as dict values (e.g. ``params_ranges_dict={'param_name': [min, max], ...}``).
           If ``None`` given as range value, the default range will be used.
           If ``None``, all available parameters are used with default value minimums and maximums.
       hyper_optimizer_name : str
           Name (abbreviation) of the optimization method used for meta-optimizing the optimizer defined 
           with **optimizer_name**.
       runs : int
           Number of optimizer runs.
       hyper_evaluations : int
           Number of evaluations used by the meta-optimizer (as defined by **hyper_optimizer_name**).            
       optimize_seed : int or None
           A random seed. Use the same value for reproducing identical stochastic procedures.
       **kwargs : kwarg
           Keyword arguments passed to the Optimizer object correspoding to the **optimizer_name**.

       Returns
       -------
       (best_result, optimal_params) : tuple
           Results of the procedure, comprising overall best result (dict) in the form (X, f) or (X, f, O, C),
           as returned by the minimize utility function, and optimal method parameters (dict) 
           found through meta-optimization.
    """

    assert optimizer_name in indago.optimizers_name_list, \
        f'Unknown optimizer name "{optimizer_name}". Use one of the following names: {", ".join(indago.optimizers_name_list)}.'

    assert hyper_optimizer_name in indago.optimizers_name_list, \
        f'Unknown hyper-optimizer name "{hyper_optimizer_name}". Use one of the following names: {", ".join(indago.optimizers_name_list)}.'
    
    # defaults for params_ranges_dict
    if optimizer_name == 'PSO':
        params_ranges_dict_default = {'swarm_size': [5, 100],
                                      'inertia': [0.5, 1],
                                      'cognitive_rate': [0, 2],
                                      'social_rate': [0, 2]}
    
    elif optimizer_name == 'FWA':
        params_ranges_dict_default = {'n': [5, 100],
                                      'm1': [3, 50],
                                      'm2': [3, 50]}
    
    elif optimizer_name == 'SSA':
        params_ranges_dict_default = {'pop_size': [5, 100],
                                      'ata': [0, 1]}
    
    elif optimizer_name == 'DE':
        params_ranges_dict_default = {'pop_init': [20, 1000],
                                      'f_archive': [1, 5],
                                      'hist_size': [3, 10],
                                      'p_mutation': [0.05, 0.3]}
    
    elif optimizer_name == 'BA':
        params_ranges_dict_default = {'pop_size': [5, 100],
                                      'loudness': [0.1, 1],
                                      'pulse_rate': [0.1, 1],
                                      'alpha': [0.1, 1],
                                      'gamma': [0.1, 1]}
    
    elif optimizer_name == 'EFO':
        params_ranges_dict_default = {'pop_size': [5, 100],
                                      'R_rate': [0.1, 4],
                                      'Ps_rate': [0.1, 4],
                                      'P_field': [0.05, 0.1],
                                      'N_field': [0.4, 0.5]}
    
    elif optimizer_name == 'MRFO':
        params_ranges_dict_default = {'pop_size': [5, 100]}
    
    elif optimizer_name == 'ABC':
        params_ranges_dict_default = {'pop_size': [5, 100],
                                      'trial_limit': [10, 500]}
        
    elif optimizer_name == 'GWO':
        params_ranges_dict_default = {'pop_size': [5, 100]}

    elif optimizer_name == 'CMAES':
        params_ranges_dict_default = {'pop_size': [4, 40]}
        
    else:
        assert False, f'Unknown optimizer {optimizer_name}'
        
    # check params_ranges_dict and load defaults if needed
    if params_ranges_dict is None:
        params_ranges_dict = params_ranges_dict_default
    while True:
        for key in params_ranges_dict:
            if key not in params_ranges_dict_default:
                print(f"Warning: param '{key}' in params_ranges_dict not available for tuning, ignoring.")
                break
        else:
            break
        params_ranges_dict.pop(key)
    for key, val in params_ranges_dict.items():
        if val is None:
            params_ranges_dict[key] = params_ranges_dict_default[key]
    
    # monitoring the inner optimization makes no sense
    kwargs_inner = kwargs.copy()
    if 'monitoring' in kwargs_inner:
        kwargs_inner.pop('monitoring')
    
    def hyper_evaluation_function(params_values):
        params = {key: val for (key, val) \
                  in zip(params_ranges_dict.keys(), params_values)}
        fs = np.empty(runs)
        for r in range(runs):
            res = indago.minimize(evaluation_function,
                                  lb,
                                  ub,
                                  optimizer_name,
                                  optimize_seed=optimize_seed,
                                  params=params,
                                  **kwargs_inner)
            fs[r] = res[1]
        return np.median(fs)
    
    # hyper-optimize
    best_param_values, _ = \
        indago.minimize(hyper_evaluation_function,
                        [val[0] for val in params_ranges_dict.values()],
                        [val[1] for val in params_ranges_dict.values()],
                        hyper_optimizer_name,
                        optimize_seed=optimize_seed,
                        dimensions=1 if len(params_ranges_dict)==1 else None,
                        monitoring=kwargs['monitoring'] if 'monitoring' in kwargs else 'none',
                        max_evaluations=hyper_evaluations)

    # final optimization
    best_res = (None, np.inf)
    optimal_params = {key: val for (key, val) \
                      in zip(params_ranges_dict.keys(), best_param_values)}
    for r in range(runs):
        res = indago.minimize(evaluation_function,
                              lb,
                              ub,
                              optimizer_name,
                              optimize_seed=optimize_seed,
                              params=optimal_params,
                              **kwargs_inner)
        if res[1] < best_res[1]:
            best_res = res
    
    return best_res, optimal_params


def inspect(evaluation_function, 
            lb=None, 
            ub=None, 
            objectives=1,
            constraints=0,
            evaluations=None, 
            optimizers_name_list=None, 
            runs=10,
            xtol=1e-4,
            processes=1,
            printout=True):
    """Utility function for benchmarking default-set methods on a goal function.
       The methods defined in ``optimizers_name_list`` will be used for optimizing the evaluation function
       given in ``evaluation_function``. Each optimization will be conducted on multiple runs (``runs``).
       Unique optima (defined with mutual relative distance of ``xtol``) are counted and reported.
    
       Parameters
       ----------
       evaluation_function : callable
           Evaluation function. Takes a design vector (ndarray) and returns fitness value (float), 
           or in case of multiobjective and/or constrainted optimization a tuple with 
           objectives (float) and constraints (float).
       lb : list or ndarray or float or None
           Lower bounds. If ``None`` lower bounds will be taken from **evaluation_function.lb**.
       ub : list or ndarray or float or None
           Upper bounds. If ``None`` upper bounds will be taken from **evaluation_function.ub**.
       objectives : int
           Number of objectives.
       constraints : int
           Number of constraints.
       optimizer_name_list : list of str
           A list of names (abbreviations) of the used Indago methods. If ``None`` then ``indago.optimizers_name_list`` is used.
       runs : int
           Number of optimizer runs.
       xtol : float
           Relative tolerance for calculating distance between found optima. 
           If ``(np.abs(Xnew - Xold)) / (ub - lb) < xtol).all() == True`` then ``Xnew`` is considered non-unique.
       processes : int
           Number of processes for parallel evaluation.
       printout : bool
           If ``True`` a console printout of a tabular summary of the benchmarking results is produced.

       Returns
       -------
       (TABLE, X_best) : tuple
           Results of the benchmarking procedure. **TABLE** (dict) contains results as they
           are given in the printout. **X_best** (ndarray) is the best design vector found
           throughout the benchmarking.
    """

    if not evaluations:
        evaluations = 1000 * max(np.size(lb), np.size(ub))
    if not optimizers_name_list:
        optimizers_name_list = indago.optimizers_name_list
        
    TABLE = {}
    
    f_best_min = np.inf
    opt_f_best_min = None
    f_avg_min = np.inf
    opt_f_avg_min = None
    
    X_best = None
    
    for opt_name in optimizers_name_list:
        
        f_best = np.inf
        O_best = None
        C_best = None
        fs = np.empty(runs)
        times = []
        unique_X_list = []
        
        for r in range(runs):
            
            time_start = time.time()
            
            res = indago.minimize(evaluation_function,
                                  lb,
                                  ub,
                                  opt_name,
                                  objectives=objectives,
                                  constraints=constraints,
                                  max_evaluations=evaluations,
                                  processes=processes)
            
            O, C = None, None
            if objectives == 1 and constraints == 0:
                X, fs[r] = res
            else:
                X, fs[r], O, C = res
            
            times.append(time.time() - time_start)
            
            if fs[r] < f_best:
                f_best = fs[r]
                if O is not None:
                    O_best = O
                if C is not None:
                    C_best = C
                X_best = np.copy(X)
            
            unique = True
            for unique_X in unique_X_list:
                if ((np.abs(X - unique_X)) / (ub - lb) < xtol).all():
                    unique = False
            if unique:
                unique_X_list.append(np.copy(X))
            
        TABLE[opt_name] = {'time_avg': np.average(times), 
                           'f_avg': np.average(fs), 
                           'f_std': np.std(fs),
                           'f_best': f_best}
        if O is not None:
            TABLE[opt_name]['O_best'] = O_best
        if C is not None:
            TABLE[opt_name]['C_best'] = C_best
        TABLE[opt_name]['unique_X_share'] = len(unique_X_list) / runs
        
        if np.average(fs) < f_avg_min:
            f_avg_min = np.average(fs)
            opt_f_avg_min = opt_name
        
        if f_best < f_best_min:
            f_best_min = f_best
            opt_f_best_min = opt_name
    
    if printout:    
    
        table = Table(title=f'Indago inspect results ({runs} runs of {evaluations} evaluations)')
        
        table.add_column('Method', justify='left', style='magenta')
        table.add_column('Avg run time (s)', justify='left', style='cyan')
        table.add_column('Fitness (avg +/- std)', justify='left', style='cyan')
        table.add_column('Best fitness', justify='left', style='cyan')       
        if not (objectives == 1 and constraints == 0):
            table.add_column('Best objectives', justify='left', style='cyan')
            table.add_column('Best constraints', justify='left', style='cyan')
        table.add_column('Unique X share (%)', justify='left', style='cyan')    
        
        for opt_name, data in TABLE.items():
            if objectives == 1 and constraints == 0:
                table.add_row(opt_name, f"{data['time_avg']:.2}", 
                              f"{data['f_avg']:e} +/- {data['f_std']:e}",
                              f"{data['f_best']:e}", 
                              f"{data['unique_X_share']:.0%}",
                              style='bold' if opt_name in (opt_f_avg_min, opt_f_best_min) else None)
            else:
                table.add_row(opt_name, f"{data['time_avg']:.2}", 
                              f"{data['f_avg']:e} +/- {data['f_std']:e}",
                              f"{data['f_best']:e}", 
                              f"{data['O_best']}", f"{data['C_best']}",
                              f"{data['unique_X_share']:.0%}",
                              style='bold' if opt_name in (opt_f_avg_min, opt_f_best_min) else None)
        
        Console().print(table)
        Console().print(f'[bold][magenta]Best X: [cyan]{X_best}')
    
    return TABLE, X_best
    

def inspect_optimizers(prepared_optimizers_dict, 
                       runs=10, 
                       xtol=1e-4,
                       printout=True):
    """Utility function for benchmarking fully prepared Indago optimizers.
       The optimizer objects in ``prepared_optimizers_dict`` will be run multiple times (``runs``).
       Unique optima (defined with mutual relative distance of ``xtol``) are counted and reported.
    
       Parameters
       ----------
       prepared_optimizers_dict : dict
           A dict of fully prepared optimizer objects in the form ``{'opt1 description': opt1, 'opt2 description': opt2, ...}``.
       runs : int
           Number of optimizer runs.
       xtol : float
           Relative tolerance for calculating distance between found optima. 
           If ``(np.abs(Xnew - Xold)) / (ub - lb) < xtol).all() == True`` then ``Xnew`` is considered non-unique.
       printout : bool
           If ``True`` a console printout of a tabular summary of the benchmarking results is produced.

       Returns
       -------
       (TABLE, X_best) : tuple
           Results of the benchmarking procedure. **TABLE** (dict) contains results as they
           are given in the printout. **X_best** (ndarray) is the best design vector found
           throughout the benchmarking.
    """
     
    TABLE = {}
    
    f_best_min = np.inf
    opt_f_best_min = None
    f_avg_min = np.inf
    opt_f_avg_min = None
    
    X_best = None
    
    for opt_desc, opt_original in prepared_optimizers_dict.items():
        
        f_best = np.inf
        O_best = None
        C_best = None
        fs = np.empty(runs)
        times = []
        unique_X_list = []
        
        for r in range(runs):
            
            time_start = time.time()
            
            opt = deepcopy(opt_original)
            res = opt.optimize()
            fs[r] = res.f
            
            times.append(time.time() - time_start)
            
            if fs[r] < f_best:
                f_best = fs[r]
                if opt.objectives > 1:
                    O_best = res.O
                if opt.constraints != 0:
                    C_best = res.C
                X_best = np.copy(res.X)
                
            unique = True
            for unique_X in unique_X_list:
                if ((np.abs(res.X - unique_X)) / (opt.ub - opt.lb) < xtol).all():
                    unique = False
            if unique:
                unique_X_list.append(np.copy(res.X))
        
        TABLE[opt_desc] = {'time_avg': np.average(times), 
                           'f_avg': np.average(fs), 
                           'f_std': np.std(fs),
                           'f_best': f_best, 
                           'O_best': O_best,
                           'C_best': C_best,
                           'unique_X_share': len(unique_X_list) / runs}
        
        if np.average(fs) < f_avg_min:
            f_avg_min = np.average(fs)
            opt_f_avg_min = opt_desc
        
        if f_best < f_best_min:
            f_best_min = f_best
            opt_f_best_min = opt_desc
            
    if printout:    
        
        table = Table(title=f'Indago inspect_optimizers results ({runs} runs)')
        
        table.add_column('Optimizer', justify='left', style='magenta')
        table.add_column('Avg run time (s)', justify='left', style='cyan')
        table.add_column('Fitness (avg +/- std)', justify='left', style='cyan')
        table.add_column('Best fitness', justify='left', style='cyan')
        table.add_column('Best objectives', justify='left', style='cyan')
        table.add_column('Best constraints', justify='left', style='cyan')
        table.add_column('Unique X share (%)', justify='left', style='cyan')      
        
        for opt_desc, data in TABLE.items():
            table.add_row(opt_desc, f"{data['time_avg']:.2}", 
                          f"{data['f_avg']:e} +/- {data['f_std']:e}",
                          f"{data['f_best']:e}", 
                          f"{data['O_best']}", f"{data['C_best']}",
                          f"{data['unique_X_share']:.0%}",
                          style='bold' if opt_desc in (opt_f_avg_min, opt_f_best_min) else None)
        
        Console().print(table) 
        Console().print(f'[bold][magenta]Best X: [cyan]{X_best}')
        
    return TABLE, X_best


def unconstrain(f, f0, p0=0.1):
    """
    Utility function (decorator) for creating unconstrained version of a 
    single-objective constrained evaluation function.
    
    Parameters
    ----------
    f : callable
        Evaluation function for which the unconstrained penalty-based version 
        is to be created.
    f0 : float
        Reference value of function minimum.
    p0 : float
        Relative size of penalty step. Penalty for each constrain (c) is 
        computed as **f0** * **p0** + c
    
    Returns
    -------
    f_penalty : callable
        Penalty-based single-objective evaluation function.
    """
     
    def f_penalty(x, *args, **kwargs):
        
        fit, *constr = f(x, *args, **kwargs)

        penalty = 0
        for c in constr:
            penalty += 0 if c <= 0 else np.abs(f0*p0) + c 
         
        return fit + penalty
     
    # append doc
    f_penalty.__doc__ = f.__doc__+' (unconstrained)'
    
    return f_penalty


def _round_smooth(x, true_round=False):
    """
    Private utility function for producing smooth piecewise-constant (rounded) values 
    by use of sigmoid function. Useful for rounding variables for the purpose
    of converting discrete or mixed variables optimization problems into 
    continuous variable problems. Can do true (not smoothed) rounding if needed.
    
    Parameters
    ----------
    x : ndarray
        Design vector to smoothly round.
    true_round : bool
        If **True**, normal rounding is performed.
    
    Returns
    -------
    x : ndarray
        Smoothly rounded values.
    
    """
    
    if true_round:
        x = np.round(x)      
    else:
        decimals = x - np.floor(x)
        x_sigmoid = decimals - 0.5
        y_sigmoid = 1 / (1 + np.exp(-100*(x_sigmoid)))
        x = np.floor(x) + y_sigmoid
    
    return x


def read_evals_db(db_filename):
    """
    A helper function for reading evaluation database (**evals_db**).

    Parameters
    ----------
    db_filename : str
        File name of the evaluation database.

    Returns
    -------
    out : ndarray
        Contents of the **db_filename** file in a ndarray.

    """
    
    with open(db_filename, 'rb') as f:
        fsz = os.fstat(f.fileno()).st_size
        out = np.load(f)
        while f.tell() < fsz:
            out = np.vstack((out, np.load(f)))
        return out