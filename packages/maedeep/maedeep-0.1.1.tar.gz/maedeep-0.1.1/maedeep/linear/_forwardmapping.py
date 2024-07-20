#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 16:04:55 2022

@author: benjamin
"""

from .modeltools import check_model, normalize, crop

def articulatory_to_task(articulatory_parameters, model=None):
    linear_mapping_matrix, offset, factor = check_model(model)    
    p = normalize(articulatory_parameters, -3, 6, 0)
    t = (linear_mapping_matrix @ p.T).T
    t = crop(t, lower_bound=0, upper_bound = 1)
    
    t = normalize((linear_mapping_matrix @ p.T).T, offset, factor, direction=1)
    return crop(t, lower_bound=0)

    


        
    
    
    

