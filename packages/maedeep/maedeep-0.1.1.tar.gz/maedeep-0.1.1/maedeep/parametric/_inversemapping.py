#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 16:04:55 2022

@author: benjamin
"""

import numpy as np
from maedeep.signaltools import (
    vtl_estimation
    )
from .modeltools import (
    check_model
    )
from .optimtools import Optimizer
import maedeep.dnn as dnn

def acoustic_to_articulatory(formants, weight=0, vtln=True, model=None,
                         init_estimate='model', verbosity=1, fixed_size=None,
                         min_area=0, threshold=0, art2ac_model=None):

    if vtln:
        length = vtl_estimation(formants)
    else: 
        length = 0.16273747
    if isinstance(init_estimate, str):
        if init_estimate == 'model':
            articulatory_params = dnn.acoustic_to_articulatory(formants)
        elif init_estimate == 'random':
            articulatory_params = np.random.uniform(-3, 3, (7, formants.shape[0]))
    else:
        articulatory_params = np.array(init_estimate)
    data = check_model(model)
    c = data["semi-polar coordinates"]["size correction"]
    x = articulatory_params.flatten().tolist()
    optim = Optimizer("vocal_model", data, "weight", weight,
                                 'verbosity', verbosity,
                                 'min_area', min_area,
                                 'threshold', threshold,
                                 'acoustic_model', art2ac_model)

    if fixed_size is not None:
        if fixed_size == 0:
            fixed_size = c / length * 0.16273747
        optim.fixed_size_factor = fixed_size
    else:
        fixed_size = c / length * 0.16273747
        x += [c / length * 0.16273747]
        optim.fixed_size_factor = None
    optim.global_optimization(formants, x0=x)
    return optim





