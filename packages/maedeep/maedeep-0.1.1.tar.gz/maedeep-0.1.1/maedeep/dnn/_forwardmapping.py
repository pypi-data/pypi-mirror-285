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

def area_to_formant(areas, model_directory=None, model=None, norms=None):
    areas = check_input_area(areas)
    return dnn_mapping(areas, model_directory=model_directory,
                       input_space="area", output_space="acoustic",
                       model=model, norms=norms)

def articulatory_to_formant(articulatory_parameters, model_directory=None,
                            model=None, norms=None, joint=True):
    if joint:
        return dnn_joint_mapping(articulatory_parameters, 
                                 input_space="articulator",
                                 output_spaces=("acoustic", "task"),
                                 model=model, model_directory=model_directory)[0]
    else:
        return dnn_mapping(articulatory_parameters,
                           model_directory=model_directory,
                       input_space="articulator", output_space="acoustic",
                       model=model, norms=norms)

def articulatory_to_area(articulatory_parameters, model_directory=None,
                         model=None, norms=None, output_type="raw"):

    areas = dnn_mapping(articulatory_parameters, model_directory=model_directory,
                       input_space="articulator", output_space="area",
                       model=model, norms=norms)
    return output_area(areas, output_type)


def articulatory_to_task(articulatory_parameters, model_directory=None,
                         model=None, norms=None, joint=True):
    if joint:
        return dnn_joint_mapping(articulatory_parameters, 
                                 input_space="articulator",
                                 output_spaces=("acoustic", "task"),
                                 model=model, model_directory=model_directory)[1]
    else:
        return dnn_mapping(articulatory_parameters, model_directory=model_directory,
                           input_space="articulator", output_space="task",
                           model=model, norms=norms)

def articulatory_to_contour(articulatory_parameters, model_directory=None,
                            output_type="raw", model=None, norms=None):

    model, model_file = load_mapping_model(model_directory, "articulator",
                                     "contour")
    with h5py.File(model_file, "r") as hf:
        norms_input = hf["normalization_factors_input"][()]
        norms_output = hf["normalization_factors_output"][()]
        idx_var = hf["variance_index"][()]
        idx_invar = hf["invariance_index"][()]
        my_full = hf["full_mean"][()]
    nb_feat = model.get_config()["layers"][0]["config"]["batch_input_shape"][1]
    x = normalization_model(reshape_input(articulatory_parameters, nb_feat), norms_input, 0)
    predicted_contours = np.zeros((x.shape[0], my_full.shape[1]))
    predicted_contours[:, idx_var] = normalization_model(model.predict(x, verbose=0), norms_output, 1)
    predicted_contours[:, idx_invar] = np.repeat(my_full[:, idx_invar].reshape(1, -1),
                                                 x.shape[0], axis=0)

    return output_contour(predicted_contours, output_type)

def contour_to_area(contours, model_directory=None, output_type="raw",
                    model=None, norms=None):

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

def contour_to_formant(contours, model_directory=None, model=None, norms=None):

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
    return normalization_model(model.predict(x, verbose=0), norms_output, 1)

def contour_to_task(contours, model_directory=None, model=None, norms=None):

    model, model_file = load_mapping_model(model_directory, "contour",
                                     "task")
    with h5py.File(model_file, "r") as hf:
        norms_input = hf["normalization_factors_input"][()]
        if "normalization_factors_output" in hf.keys():
            norms_output = hf["normalization_factors_output"][()]
        else:
            norms_output = hf["normalization_factors_outpur"][()]
        idx_var = hf["variance_index"][()]
    x = np.array([contour.contours for contour in contours])
    x = normalization_model(x[:, idx_var], norms_input, 0)
    return normalization_model(model.predict(x, verbose=0), norms_output, 1)

def task_to_formant(task, model_directory=None, model=None, norms=None):
    return dnn_mapping(task, model_directory=model_directory,
                       input_space="task", output_space="acoustic",
                       model=model, norms=norms)










