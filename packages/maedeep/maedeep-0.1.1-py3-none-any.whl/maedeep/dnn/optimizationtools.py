#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 16:59:33 2022

@author: benjamin
"""

import numpy as np
from scipy.optimize import minimize, dual_annealing
from tqdm import tqdm

class Solution:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=pointless-string-statement

    error = None
    error_formants = None
    sparsity = None
    articulatory_params = None
    estimated_formants = None

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

def cost_function(generated, observed, x=None, lbd=0):
    
    return (np.sqrt(np.mean(((generated-observed)/observed)**2)).reshape(-1).squeeze() + 
        lbd * l12norm(x))

def initial_solution(israndm=True, nb_param=7, nb_frame=1):
    if israndm:
        x0 = np.random.randn(nb_param * nb_frame)
        while (abs(x0) > 3).any():
            x0 = np.random.randn(nb_param * nb_frame)
    else:
        x0 = np.zeros(nb_param * nb_frame)
    return x0

def l12norm(x):
    if x is not None:
        nb_row, nb_col = x.shape
        if nb_col > 1:
            s = 0
            for r in range(nb_row):
                s += np.linalg.norm(x[r, :].squeeze(), 2)
        else:
            s = np.linalg.norm(x, 1)
        return s
    else:
        return 0

def mat2vec(x, nb_param, nb_frame):
    return x.reshape((nb_param*nb_frame, 1), order="F")

def multiple_optimization(args, maxiter=200, method='nelder-mead', nb_optim=10,
                          israndm=True, disable=False, nb_param=7, 
                          verbose=False):
    solutions = []
    nb_frame = args[0].shape[1]
    for n in tqdm(range(nb_optim), disable=disable):
        solution = optimization(args, x0=initial_solution(israndm, 
                                                          nb_frame=nb_frame), 
                                maxiter=maxiter, method=method)
        solutions.append(solution)
    return solutions[np.argmin([s.error for s in solutions])]

def objective(x, *args):
    """ Objective function """
    
    nb_frame = args[0].shape[1]
    gen_formants = np.zeros_like(args[0])
    nb_param = int(len(x) / nb_frame)
    x = vec2mat(x, nb_param, nb_frame)
    x0 = np.vstack((x, np.zeros((1, nb_frame))))
    gen_formants = model_to_formants(x0).squeeze()
    verbose = False
    if len(args) == 1:
        obs_formants = args[0]
        lbd = 0
    elif len(args) == 2:
        (obs_formants, lbd) = args
    elif len(args) == 3:
        (obs_formants, lbd, verbose) = args
    E = cost_function(gen_formants, obs_formants, x, lbd)
    if verbose:
        print(E)
    return E

def optimization(args, x0=np.zeros(8), maxiter=200, method='nelder-mead'):    
    options={'maxiter': maxiter * len(x0)}
    bounds = ((((-3, 3),)*len(x0)))
    try:
        if method != "annealing":
            tmp_sol = minimize(objective, x0, args=args, 
                               method=method, options=options, bounds=bounds)
        else:
            tmp_sol = dual_annealing(objective, bounds, x0=x0, 
                                  args=args, maxiter=maxiter)        
       
        x_sol = tmp_sol["x"]
        nb_frame = args[0].shape[1]
        gen_formants = np.zeros_like(args[0])
        nb_param = int(len(x_sol) / nb_frame)
        x = vec2mat(x_sol, nb_param, nb_frame)
        x0 = np.vstack((x, np.zeros((1, nb_frame))))
        gen_formants = model_to_formants(x0).squeeze()
        if len(args) == 1:
            obs_formants = args[0]
            lbd = 0
        else:
            (obs_formants, lbd) = args
        return Solution("error", cost_function(gen_formants, obs_formants, x, lbd),
                        "articulatory_params", vec2mat(x_sol, nb_param, nb_frame),
                        "estimated_formants",  gen_formants,
                        "error_formants", cost_function(gen_formants, obs_formants, 
                                                        x, 0),
                        "sparsity", l12norm(x))
    except:
        return Solution("error", np.inf)
    
def vec2mat(x, nb_param, nb_frame):
    return x.reshape((nb_param, nb_frame), order="F")
    
