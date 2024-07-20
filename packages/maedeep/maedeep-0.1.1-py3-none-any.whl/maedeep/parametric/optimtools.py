# -*- coding: utf-8 -*-
"""
Created on Tue May 30 10:52:13 2023

@author: belie
"""

from ._forwardmapping import articulatory_to_formant
import copy
import numpy as np
import os
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error
import tensorflow as tf


class Optimizer:
    name = None
    vocal_model = None
    weight = None
    threshold = 0
    nb_attempts = 3
    verbosity = True
    parallel = 1
    repetitions = 1
    maxiter = 200
    solution = None
    fixed_size_factor = None
    optimal_cost = None
    min_area = 0
    acoustic_model = None

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def copy(self):
        return copy.deepcopy(self)

    def global_optimization(self, refs, x0=None):
        """ Performs global optimization """

        if x0 is not None:
            global_min_cost = objective(x0, self, refs)
            global_min_x = [x for x in x0]
        else:
            global_min_cost = np.inf
            global_min_x = None

        if self.parallel <= 1 or self.repetitions <= 1:
            for k in range(self.repetitions):
                local_min_cost, local_min_x = self.repetition(x0,
                                                         global_min_cost, k,
                                                         refs)

                global_checks = check_global_optimization(local_min_cost,
                                                          local_min_x,
                                                          global_min_cost, 
                                                          global_min_x)
                global_min_cost, global_min_x = global_checks
        else:
            from joblib import Parallel, delayed
            if os.name == "nt":
                backend = "threading"
            else:
                backend = "loky"
            solutions = Parallel(n_jobs=self.parallel, backend=backend,
                             prefer="processes")(delayed(self.repetition)(x0,
                                                                      None, k,
                                                                      refs) for
                                                     k in range(self.repetitions))
            for solution in solutions:
                local_min_cost, local_min_x = solution
                global_checks = check_global_optimization(local_min_cost,
                                                          local_min_x,
                                              global_min_cost, global_min_x)
                global_min_cost, global_min_x = global_checks

        if self.verbosity:
            print("Optimization completed", flush=True)
            print("Global minimum: ", global_min_cost, flush=True)

        self.solution = global_min_x
        self.optimal_cost = global_min_cost
        return global_min_x

    def local_optimization(self, x0, refs):
        options = {'maxiter': self.maxiter * len(x0)}
        if self.fixed_size_factor is None:
            bounds = ((-3, 3), ) * (len(x0) - 1) + ((0, 2), )
        else:
            bounds = ((-3, 3), ) * len(x0)
        args = (self, refs)
        result = minimize(objective, x0, args=args, method="nelder-mead",
                              options=options, bounds=bounds)
        return result["x"], result["fun"]

    def repetition(self, x0_start, global_min_cost, k, refs):

        """ Perform one otpimization run """
        nb_f = refs.shape[1]
        if x0_start is not None:
            min_x = [xx for xx in x0_start]
        else:
            min_x = (6*np.random.rand(7*nb_f)-3).tolist() # + [1]
            if self.fixed_size_factor is None:
                min_x += [1]

        rem_attempts = self.nb_attempts
        local_min_cost = objective(min_x, self, refs)
        isContinue = True

        while isContinue:
            new_x, new_cost = self.local_optimization(min_x, refs=refs)
            (min_x, rem_attempts,
             local_min_cost, isContinue) = check_local_optimization(new_x,
                                            new_cost, local_min_cost,
                                         self.nb_attempts, min_x,
                                         self.threshold, rem_attempts)

            if self.verbosity >= 1 and global_min_cost is not None:
                print("Current repetition: ", k+1, " /",
                      self.repetitions, flush=True)
                print("Global cost function ", global_min_cost, flush=True)
                print("Local cost function: ", local_min_cost, flush=True)
                print("New cost :", new_cost, flush=True)
                print("Number of remaining attempts :",
                      rem_attempts, flush=True)

        return local_min_cost, min_x

def check_global_optimization(local_min_cost, local_min_x,
                              global_min_cost, global_min_x):
    """ Check whether the local minimum in the local loop
    is temporary a global one """
    if local_min_cost < global_min_cost:
        global_min_x = local_min_x
        global_min_cost = local_min_cost

    return global_min_cost, global_min_x

def check_local_optimization(new_x, new_cost, local_min_cost,
                             nb_attempts, min_x, threshold, rem_attempts):
    """ Check whether the local minimum is temporary a global one """

    isContinue = True
    gain = np.abs((new_cost - local_min_cost) / local_min_cost)
    if new_cost < local_min_cost:
        local_min_cost = new_cost
        min_x = new_x

        if gain > threshold:
            rem_attempts = nb_attempts
        else:
            rem_attempts -= 1
            if rem_attempts == 0:
                isContinue = False
    else:
        rem_attempts -= 1
        if rem_attempts == 0:
            isContinue = False
    return min_x, rem_attempts, local_min_cost, isContinue

def formant_cost(ref, est):
    return mean_squared_error(ref.flatten()/ref.flatten(), 
                              est.flatten()/ref.flatten(), squared=False)

def get_formants_model(x, acoustic_model):
    x_scaled = acoustic_model[1][0].transform(np.array(x).reshape(1,-1))
    x_scaled = tf.convert_to_tensor(x_scaled, dtype=tf.float32)
    f = acoustic_model[0](x_scaled).numpy()    
    return acoustic_model[1][1].inverse_transform(f)


def reshape_solution(x, size_correction=True):
    if size_correction:
        return np.reshape(x[:-1], (7, -1))
    else:
        return np.reshape(x, (7, -1))

def objective(x, *args):
    optim, refs = args
    return solution_to_cost(x, optim, refs)

def solution_to_cost(x, optim, formants_ref):
    if optim.fixed_size_factor is None:
        p = reshape_solution(x, size_correction=True)
        c = x[-1]
    else:
        p = reshape_solution(x, size_correction=False)
        c = optim.fixed_size_factor
    formants_estimated = np.nan_to_num(solution_2_formants(p, c,
                                                       optim.vocal_model,
                                                       optim.min_area, 
                                                       optim.acoustic_model),
                                       0)
    acoustic_cost = formant_cost(formants_ref, formants_estimated)
    if optim.weight != 0:
        var_p = solution_2_var(p)
        total_cost = acoustic_cost + optim.weight * var_p
    else:
        total_cost =  acoustic_cost
    if optim.verbosity == 2:
        print("Cost function is", total_cost, flush=True)
    return total_cost

def solution_2_formants(p, sc, model, min_area=0, ac_model=None):
    if ac_model is None:
        return articulatory_to_formant(p, model, 
                                       size_correction=sc, min_area=min_area)
    else:
        return get_formants_model(p, ac_model)

def solution_2_var(p):
    return np.linalg.norm(np.std(p, axis=1))**2
