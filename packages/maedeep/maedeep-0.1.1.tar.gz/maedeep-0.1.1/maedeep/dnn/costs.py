#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 17:53:08 2022

@author: benjamin
"""

import numpy as np

def rmse(generated, observed, relative=False):    
    if relative:
        return np.mean(np.abs((generated-observed)/observed))
    else:
        return np.mean(np.abs((generated-observed)))
    
def kinetic(articulators):
    return np.mean(np.linalg.norm(np.diff(articulators, axis=0), axis=1)**2)

def potential(articulators, reference=0):
    return np.mean(np.linalg.norm(articulators - reference, axis=1)**2)
