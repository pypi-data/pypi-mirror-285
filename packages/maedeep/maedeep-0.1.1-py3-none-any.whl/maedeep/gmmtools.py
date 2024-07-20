#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 09:46:46 2022

@author: benjamin
"""

from sklearn.mixture import GaussianMixture
import h5py
import numpy as np

def open_matlab_gmm_model(gmm_file):
    
    keys = ["mean", "covariance", "weights", 
            "converged", "iters", "nb_var", "covariance_type"]
    with h5py.File(gmm_file, "r") as hf:
        data = [hf[key][()] for key in keys]
        
    means, covars, weights, convs, nb_iter, nb_var, covar_type = data
    nb_components = len(weights)
    gm = GaussianMixture(n_components=nb_components, covariance_type="full")
    gm.means_ = means.T
    gm.weights_ = weights.squeeze()
    gm.covariances_ = covars
    gm.precisions_ = np.linalg.inv(covars)
    gm.precisions_cholesky_ = np.linalg.cholesky(np.linalg.inv(covars))
    gm.converged_ = convs
    gm.n_features_in_ = nb_var
    gm.n_iter_ = nb_iter
    
    return gm