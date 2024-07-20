#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 12:42:13 2022

@author: benjamin
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import keras
from keras import layers, models, regularizers
# import tensorflow as tf
# tf.compat.v1.disable_eager_execution()
import h5py
import numpy as np
from tqdm import tqdm
from maedeep._config import get_maedeep_path
from maedeep._areafunction import AreaFunction
from maedeep._contour import Contour
import pickle
import warnings

def build_model(input_layer_size, hidden_layer_size,
                encoding_function="relu",
                decoding_function="relu",
                sparsity=0,
                loss="mean_squared_error"):

    input_art = keras.Input(shape=(input_layer_size,))
    if sparsity > 0:
        encoded = layers.Dense(hidden_layer_size, 
                               activation=encoding_function,
                               activity_regularizer=regularizers.l1(sparsity))(input_art)
    else:
        encoded = layers.Dense(hidden_layer_size, 
                               activation=encoding_function)(input_art)
    # decoded = layers.Dense(input_layer_size, 
    #                        activation=decoding_function)(encoded)
    # autoencoder = keras.Model(input_art, decoded)

    encoder = keras.Model(input_art, encoded)
    # encoded_input = keras.Input(shape=(input_layer_size,))
    # decoder_layer = autoencoder.layers[-1]
    # decoder = keras.Model(encoded_input, decoder_layer(encoded_input))
    encoder.compile(optimizer='adam', loss=loss)
    # for m in [autoencoder, encoder, decoder]:
    #     m.compile(optimizer='adam', loss='mean_squared_error')

    return encoder#, decoder, autoencoder

def build_dnn_model(nb_feat_input, nb_feat_output, 
                    hidden_layer_size=(40, 80, 40), 
                    activation_function="sigmoid",
                    loss_function="mean_squared_error"):
    
    encoding_function = activation_function
    
    input_art = keras.Input(shape=(nb_feat_input,))
    nb_layers = len(hidden_layer_size)
    
    hidden_layers = [layers.Dense(hidden_layer_size[0], 
                                activation=activation_function)(input_art)]
    for n in range(1, nb_layers):
        hidden_layers.append(layers.Dense(hidden_layer_size[n], 
                                activation=encoding_function)(hidden_layers[n-1]))
    # hidden_2 = layers.Dense(hidden_layer_size[2], 
    #                         activation=encoding_function)(hidden_1)
    decoded = layers.Dense(nb_feat_output, 
                            activation=encoding_function)(hidden_layers[-1])
    encoder = keras.Model(input_art, decoded)
    
    encoder.compile(optimizer='adam', loss=loss_function)
    return encoder


def check_input_area(area):
    if hasattr(area, "area") and hasattr(area, "length"):
        af, lf = [getattr(area, key) for key in ["area", "length"]]
        return np.vstack((af, lf))
    else:
        return area

def concat_data(x, y):
    if x is None:
        return y
    else:
        return np.hstack((x, y))
  
def dnn_joint_mapping(x, input_space, output_spaces, model_directory=None, 
                model=None):
    if model is None:
        model, scaler = load_mapping_joint_model(model_directory, input_space,
                                   output_spaces)
    nb_feat = model.get_config()["layers"][0]["config"]["batch_input_shape"][1]
    x = scaler[0].transform(reshape_input(x, nb_feat))
    y = model.predict(x, verbose=False)
    return [scaler[n+1].inverse_transform(y[n]) for n in range(len(y))]

def dnn_mapping(x, input_space, output_space, model_directory=None, 
                model=None, norms=None):
    
    if model is None:
        model, model_file = load_mapping_model(model_directory, input_space,
                                   output_space)
    nb_feat = model.get_config()["layers"][0]["config"]["batch_input_shape"][1]
    
    if norms is None:
        with h5py.File(model_file, "r") as hf:
            norms_input = hf["normalization_factors_input"][()]
            norms_output = hf["normalization_factors_output"][()]
    else:
        norms_input, norms_output = norms
    x = normalization_model(reshape_input(x, nb_feat), norms_input, 0)
    return normalization_model(model.predict(x, verbose=0), norms_output, 1).T
    
def load_data(file):
    keys = ["train_input", "output_train",
            "test_input", "test_output"]
    with h5py.File(file, "r") as hf:
        data = [hf[key][()] for key in keys]
    return data

def load_model(file):
    return models.load_model(file)

def load_mapping_joint_model(model_directory, input_space, output_spaces):
    if model_directory is None:
        model_directory = os.path.join(get_maedeep_path(), "dnn", "models")
    model_prefix = "_".join([input_space, "to", output_spaces[0], "and", 
                             output_spaces[1]])
    model_file = os.path.join(model_directory, model_prefix + ".h5")
    scaler_file = os.path.join(model_directory, model_prefix + ".scl")
    
    return load_model(model_file), load_scaler_file(scaler_file)

def load_mapping_model(model_directory, input_space, output_space):
    if model_directory is None:
        model_directory = os.path.join(get_maedeep_path(), "dnn", "models")
    file = os.path.join(model_directory, 
                        input_space + "_to_" + output_space + ".h5")
    scaler_file = os.path.join(model_directory, 
                        input_space + "_to_" + output_space + ".scl")
    return load_model(file), file

def load_scaler_file(scaler_file):
    with open(scaler_file, 'rb') as f:
        return pickle.load(f)

def make_data_notrain(training_path, input_vars="articulators", 
              output_vars="tract", disable=False):

    list_files = [os.path.join(training_path, x) for x in os.listdir(training_path)
                  if ".h5" in x]
    x_train = None
    y_train = None
    for l in tqdm(list_files, disable=disable):
        with h5py.File(l, "r") as hf:
            x = hf[input_vars][()]
            y = hf[output_vars][()]
            rejected = hf["rejection"][()]

        if len(rejected) > 0:
            x, y = remove_rejected(x, y, rejected)
        x_train = concat_data(x_train, x)
        y_train = concat_data(y_train, y)
        
    return x_train, y_train

def make_data(training_path, input_vars="articulators", 
              output_vars="tract", prop=10, save=None, disable=False):

    list_files = [os.path.join(training_path, x) for x in os.listdir(training_path)
                  if ".h5" in x]
    x_train = None
    y_train = None
    for l in tqdm(list_files, disable=disable):
        with h5py.File(l, "r") as hf:
            x = hf[input_vars][()]
            y = hf[output_vars][()]
            rejected = hf["rejection"][()]

        if len(rejected) > 0:
            x, y = remove_rejected(x, y, rejected)
        x_train = concat_data(x_train, x)
        y_train = concat_data(y_train, y)
        
    x_train, y_train = make_data_notrain(training_path, input_vars=input_vars, 
                  output_vars=output_vars, disable=disable)
        
    x_train, y_train, x_test, y_test = make_test(x_train, y_train, prop=prop)
    if save is not None:
        save_data([x_train, y_train, x_test, y_test], save)
    return x_train, y_train, x_test, y_test

def make_test(x_train, y_train, prop_test=5, prop_valid=5):
    
    x_train, y_train, x_test, y_test = pick_random_sample(x_train, 
                                                          y_train, 
                                                          prop_test)  
    x_train, y_train, x_valid, y_valid = pick_random_sample(x_train, 
                                                          y_train, 
                                                          prop_valid) 
    
    return x_train.T, y_train.T, x_test.T, y_test.T, x_valid.T, y_valid.T
            
def mapping(x, input_space, output_space, model_dir="./"):
    
    model_file = os.path.join(model_dir, input_space + "_to_" + 
                              output_space + ".h5")
    
    model = load_model(model_file)
    with h5py.File(model_file, "r") as hf:
        norms_input = hf["normalization_factors_input"][()]
        norms_output = hf["normalization_factors_output"][()]

    x = normalization_model(x, norms_input, 0)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        return normalization_model(model.predict(x, verbose=0), norms_output, 1)    

def normalization_model(x, norms, direction):
    if isinstance(norms, np.int64):
        add_norm = 0
        mult_norm = norms
    elif len(norms) == 1:
        add_norm = 0
        mult_norm = norms[0]
    else:            
        add_norm = norms[1]
        mult_norm = norms[0]
    if direction == 0:
        return (x - add_norm) / mult_norm
    else:
        return x * mult_norm + add_norm

def normalization(x, axis=0):
    return (x - np.mean(x, axis=axis, keepdims=True))/ np.std(x, axis=axis, keepdims=True)

def normalization_max(x, axis=0):
    
    minx = np.min(x, axis=axis, keepdims=True)
    mx = np.max(x - minx, axis=axis, keepdims=True)
    return (x - minx) / mx, mx, minx

def normalization_tmp(x, axis=0):
    mx = np.mean(x, axis=axis, keepdims=True)
    stdx = np.std(x, axis=axis, keepdims=True)
    return (x - mx)/ stdx, mx, stdx

def normalized_data(x_train, y_train, x_test, y_test):
    return (normalization(x_train, axis=0), normalization(y_train, axis=0),
            normalization(x_test, axis=0), normalization(y_test, axis=0))

def output_area(areas, output_type):
    
    if output_type == "raw":
        return areas
    else:
        af, lf = [areas[n*40:(n+1)*40,:] for n in range(2)]
        if output_type == "separate":
            return af, lf
        elif output_type == "area_function":
            return AreaFunction("area", af, "length", lf)
        else:
            raise ValueError(output_type + """ is not a valid output type. 
                             Choose between 'raw', 'separate', 
                             and 'area_function'""")
                             
def output_contour(predicted_contours, output_type):
    
    if output_type == "raw":
        return predicted_contours.T
    else:
        low_x, low_y, up_x, up_y = [predicted_contours.T[n*29:(n+1)*29,:] for n in range(4)]
        if output_type == "separate":
            return low_x, low_y, up_x, up_y
        elif output_type == "contour":
            return [Contour("contours", [low_x[:,i], low_y[:,i],
                                        up_x[:,i], up_y[:,i]]) for i in range(low_x.shape[1])]
        else:
            raise ValueError(output_type + """ is not a valid output type. 
                             Choose between 'raw', 'separate', 
                             and 'contour'""")

def pick_random_sample(x, y, prop):
    
    nb_smpl = x.shape[1]
    nb_test = int(prop/100*nb_smpl)
    idx = np.random.randint(low=0, high=nb_smpl, size=nb_test)
    x_test = x[:, np.unique(idx)]
    y_test = y[:, np.unique(idx)]    
    
    return (np.delete(x, np.unique(idx), axis=1),
            np.delete(y, np.unique(idx), axis=1),
            x_test,
            y_test)

def remove_invariants(train, test):
    
    values = None
    idx = [x for x in range(train.shape[1]) if np.std(train[:,x]) == 0]
    if len(idx) > 0:
        values = train[0, idx]
        train = np.delete(train, idx, axis=1)
        test = np.delete(test, idx, axis=1)
        
    return train, test, (idx, values)

def remove_rejected(art_params, tract_vars, rejected):
    return (np.delete(art_params, rejected, axis=1),
            np.delete(tract_vars, rejected, axis=1))

def reshape_input(x, nb_feat):
    if isinstance(x, list):
        x = np.array(x)
    if len(x.shape) == 1:
        x = x.reshape(1, -1)
    if x.shape[1] != nb_feat:
        x = x.T
        
    return x

def save_data(values, output_file):
    
    keys = ["train_input", "output_train",
            "test_input", "test_output"]
    with h5py.File(output_file, "w") as hf:
        for key, value in zip(keys, values):
            hf.create_dataset(key, data=value)
            
def save_model(model, file):
    model.save(file)


