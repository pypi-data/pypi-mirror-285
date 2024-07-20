#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 09:32:12 2020

@author: benjamin
"""

import copy
import numpy as np
import scipy.interpolate as scintp

class AreaFunction:
    """class for manipulating area fucntions"""
    area = None
    length = None
    parent = None
    total_length = None
    constriction_area = None
    constriction_location = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            
        if self.area is not None and self.length is not None:
            _, _, _ = self.characteristics()

    def copy(self):
        """returns a deep copy of the instance"""
        return copy.deepcopy(self)

    def interpolate(self, num_tubes):
        """interpolates area function into a vector y_out of N_out evenly spaced area function."""
        
        af = self.area
        lf = self.length
        if len(af.shape) == 1:
            af = af.reshape(-1, 1)
            lf = lf.reshape(-1, 1)

        cumx_in = np.cumsum(lf, 0)
        x_out = np.zeros((num_tubes, af.shape[1]))
        y_out = np.zeros((num_tubes, af.shape[1]))
        for kframe in range(af.shape[1]):
            y_in = af[:, kframe]
            x_in = cumx_in[:, kframe]

            x_out1 = np.arange(1, num_tubes+1)*x_in[-1]/num_tubes
            f1 = scintp.interp1d(x_in, y_in,
                                 kind='linear', fill_value='extrapolate')
            y_out[:, kframe] = f1(x_out1)
            x_out[:, kframe] = np.append(x_out1[0], np.diff(x_out1))

        self.area = y_out
        self.length = x_out
        return x_out, y_out
    
    def characteristics(self):
        """returns the characteristics of the area function"""
        
        self.total_length = np.sum(self.length, 0)
        self.constriction_area = np.min(self.area, 0)
        self.constriction_location = np.argmin(self.area, 0)
        
        return self.total_length, self.constriction_area, self.constriction_location
    
    def extend(self, nb_frame):
        """ Extends area function to a specified number of frames """
        if len(self.area.squeeze().shape) > 1:
            raise ValueError("Area function should contain only one frame")
            
        self.area = np.tile(self.area.squeeze().reshape(-1,1), 
                            (1, nb_frame))
        self.length = np.tile(self.length.squeeze().reshape(-1,1), 
                              (1, nb_frame))

def minimal_area(vt):
    
    lf, af = (vt[:,0], vt[:, 1])
    lf[lf<=0] = 1e-11
    af[af<=0] = 1e-11
    return af, lf

