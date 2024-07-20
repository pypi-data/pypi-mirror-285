#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 16:01:43 2022

@author: benjamin
"""

import os
from importlib.resources import files

def get_maedeep_path():
    return files("maedeep")#.as_posix()

def get_maedeep_model():
    return os.path.join(get_maedeep_path(), "parametric", "models", 
                        "model_spec.json")

def get_maedeep_linear_model():
    return os.path.join(get_maedeep_path(), "linear", "models", 
                        "linear_model.h5")

    
  