#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 16:04:55 2022

@author: benjamin
"""

import h5py
import numpy as np
from .dnntools import (
                        check_input_area, 
                        dnn_joint_mapping, 
                        dnn_mapping, 
                        load_mapping_model, 
                        normalization_model,
                        output_area, 
                        output_contour, 
                        reshape_input
                       )
from maedeep.signaltools import vtln

def acoustic_to_area(formants, model_directory=None, output_type="raw"):
    areas = dnn_mapping(vtln(formants), model_directory=model_directory,
                       input_space="acoustic", output_space="area")

    return output_area(areas, output_type)

def acoustic_to_articulatory(formants, model_directory=None, joint=True):
    if joint:
        return dnn_joint_mapping(vtln(formants), input_space="acoustic",
                                 output_spaces=("articulatory", "task"),
                                 model_directory=model_directory)[0]
        
    else: 
        return dnn_mapping(vtln(formants), model_directory=model_directory,
                       input_space="acoustic", output_space="articulator")

def area_to_articulatory(areas, model_directory=None, 
                         output_type="raw"):
    return dnn_mapping(check_input_area(areas), model_directory=model_directory,
                       input_space="area", output_space="articulator")
        

def task_to_articulatory(tasks, model_directory=None):
    return dnn_mapping(tasks, model_directory=model_directory,
                       input_space="task", output_space="articulator")

def contour_to_articulatory(contours, model_directory=None,
                            output_type="raw"):

    model, model_file = load_mapping_model(model_directory, "contour",
                                     "articulator")
    with h5py.File(model_file, "r") as hf:
        norms_input = hf["normalization_factors_input"][()]
        if "normalization_factors_output" in hf.keys():
            norms_output = hf["normalization_factors_output"][()]
        else:
            norms_output = hf["normalization_factors_outpur"][()]
        idx_var = hf["variance_index"][()]

    x = np.array([contour.contours for contour in contours])
    x = normalization_model(x[:, idx_var], norms_input, 0)
    return normalization_model(model.predict(x, verbose=0), (norms_output, 0), 1)

def contour_to_area(contours, model_directory=None, output_type="raw"):

    model, model_file = load_mapping_model(model_directory, "contour",
                                     "acoustic")
    with h5py.File(model_file, "r") as hf:
        norms_input = hf["normalization_factors_input"][()]
        if "normalization_factors_output" in hf.keys():
            norms_output = hf["normalization_factors_output"][()]
        else:
            norms_output = hf["normalization_factors_outpur"][()]
        idx_var = hf["variance_index"][()]

    x = np.array([contour.contours for contour in contours])
    x = normalization_model(x[:, idx_var], norms_input, 0)
    areas = normalization_model(model.predict(x, verbose=0), (norms_output, 0), 1)
    return output_area(areas, output_type)

def acoustic_to_contour(formants, model_directory=None, output_type="raw"):

    model, model_file = load_mapping_model(model_directory, "acoustic",
                                     "contour")
    with h5py.File(model_file, "r") as hf:
        norms_input = hf["normalization_factors_input"][()]
        norms_output = hf["normalization_factors_output"][()]
        idx_var = hf["variance_index"][()]
        idx_invar = hf["invariance_index"][()]
        my_full = hf["full_mean"][()]
    # nb_feat = model.get_config()["layers"][0]["config"]["batch_input_shape"][1]
    x = normalization_model(vtln(formants), norms_input, 0)
    predicted_contours = np.zeros((x.shape[0], my_full.shape[1]))
    predicted_contours[:, idx_var] = normalization_model(model.predict(x, verbose=0), norms_output, 1)
    predicted_contours[:, idx_invar] = np.repeat(my_full[:, idx_invar].reshape(1, -1),
                                                 x.shape[0], axis=0)
    return output_contour(predicted_contours, output_type)

def task_to_contour(tasks, model_directory=None, output_type="raw"):

    model, model_file = load_mapping_model(model_directory, "task",
                                     "contour")
    with h5py.File(model_file, "r") as hf:
        norms_input = hf["normalization_factors_input"][()]
        norms_output = hf["normalization_factors_output"][()]
        idx_var = hf["variance_index"][()]
        idx_invar = hf["invariance_index"][()]
        my_full = hf["full_mean"][()]
    nb_feat = model.get_config()["layers"][0]["config"]["batch_input_shape"][1]
    x = normalization_model(reshape_input(tasks, nb_feat), norms_input, 0)
    predicted_contours = np.zeros((x.shape[0], my_full.shape[1]))
    predicted_contours[:, idx_var] = normalization_model(model.predict(x, verbose=0), norms_output, 1)
    predicted_contours[:, idx_invar] = np.repeat(my_full[:, idx_invar].reshape(1, -1),
                                                 x.shape[0], axis=0)
    return output_contour(predicted_contours, output_type)

def acoustic_to_task(formants, model_directory=None, joint=True):
    if joint:
        return dnn_joint_mapping(vtln(formants), input_space="acoustic",
                                 output_spaces=("articulatory", "task"),
                                 model_directory=model_directory)[1]
    else:
        return dnn_mapping(vtln(formants), model_directory=model_directory,
                           input_space="acoustic", output_space="task")










