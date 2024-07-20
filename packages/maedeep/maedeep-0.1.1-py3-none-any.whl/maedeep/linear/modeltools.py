#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 09:58:38 2022

@author: benjamin
"""

import h5py
import os
from maedeep._config import get_maedeep_linear_model

def check_model(model):
    
    if model is None:
        model = get_maedeep_linear_model()
        
    if isinstance(model, str):
        if os.path.isfile(model):
            with h5py.File(model, "r") as file_id:
                return [file_id[key][()] for
                        key in ["matrix", "offset", "factor"]]
        else:
            raise ValueError(model + " is not a valid file")
    elif isinstance(model, dict):
        return model
    else:
        raise ValueError("The model is not a valid object")
    
def crop(x, lower_bound=None, upper_bound=None):
    if lower_bound is not None:
        x[x <= lower_bound] = lower_bound
    if upper_bound is not None:
        x[x >= upper_bound] = upper_bound
    return x
    
    
def normalize(x, offset, factor, direction=0):
    """ Normalization between 0 and 1"""
    if direction not in [0, 1]:
        raise ValueError("Direction not valid, please choose either 0 or 1")
    if direction == 0:
        return (x - offset)/factor
    elif direction == 1:
        return x * factor + offset
