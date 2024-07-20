#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 09:58:38 2022

@author: benjamin
"""

import json
import os
import numpy as np
from maedeep._contour import Contour
from maedeep._config import get_maedeep_model

def amo(px, py, qx, qy):
    return np.sqrt((px - qx)**2 + (py - qy)**2)
  
def check_model(model):
    
    if model is None:
        model = get_maedeep_model()
        
    if isinstance(model, str):
        if os.path.isfile(model):
            with open(model, "r") as file_id:
                return json.load(file_id)
        else:
            raise ValueError(model + " is not a valid file")
    elif isinstance(model, dict):
        return model
    else:
        raise ValueError("The model is not a valid object")
        
def contour_to_area_function(contour, c, iniva_tng, alph, beta, min_area=1e-11):
    
    low_x, low_y, up_x, up_y = contour.contours
    lip_h, lip_w = contour.lips
    ivt = [{"x": x, "y": y} for x, y in zip(low_x, low_y)]
    evt = [{"x": x, "y": y} for x, y in zip(up_x, up_y)] 

    nb_p = len(ivt)
    af = [[]]*(nb_p)

    pv, qv, rv, sv, tv = cross_distance(ivt, evt)
    for i in range(1, nb_p-1):
        p = pv[i-1]
        q = qv[i-1]
        s = sv[i-1]
        r = rv[i-1]
        t = tv[i-1]
        a1 = 0.5*(p+s+t)
        a2 = 0.5*(q+r+t)
        s1 = np.sqrt(a1*(a1-p)*(a1-s)*(a1-t))
        s2 = np.sqrt(a2*(a2-q)*(a2-r)*(a2-t))
        x1 = ivt[i-1]["x"] + evt[i-1]["x"] - ivt[i]["x"] - evt[i]["x"]
        y1 = ivt[i-1]["y"] + evt[i-1]["y"] - ivt[i]["y"] - evt[i]["y"]
        d = 0.5*np.sqrt(x1**2 + y1**2)
        w = c*(s1 + s2)/d
        j = i + iniva_tng - 3
        af[i-1] = {"x": c*d,
                   "A": 1.4*alph[j]*w**beta[j]}
        
    af[nb_p-2:] = [{"A": np.pi * lip_h * lip_w * c**2,
                    "x": 0.5*(ivt[nb_p-2]["x"] - ivt[nb_p-1]["x"])*c} for i in range(2)] 

    af = [{"A": max([min_area*1e4, x["A"]]),
           "x": max(0.01, x["x"])} for x in af]
    return {"area": [x["A"]*1e-4 for x in af], 
             "length": [x["x"]*1e-2 for x in af]}        
        
def cross_distance(ivt, evt):
    low_x, low_y, up_x, up_y = (np.array([x["x"] for x in ivt]),
                                np.array([x["y"] for x in ivt]),
                                np.array([x["x"] for x in evt]),
                                np.array([x["y"] for x in evt]))
    
    p = amo(low_x[1:], low_y[1:], low_x[:-1], low_y[:-1])
    q = amo(up_x[1:], up_y[1:], up_x[:-1], up_y[:-1])
    r = amo(low_x[:-1], low_y[:-1], up_x[:-1], up_y[:-1])
    s = amo(up_x[1:], up_y[1:], low_x[1:], low_y[1:])
    t = amo(up_x[1:], up_y[1:], low_x[:-1], low_y[:-1])
    return p, q, r, s, t

def vector_to_contours(articulatory_parameters, model, output_file=None):
    
    data = check_model(model)
        
    if isinstance(articulatory_parameters, list):
        articulatory_parameters = np.array(articulatory_parameters)
    if len(articulatory_parameters.shape) == 1:
        articulatory_parameters = articulatory_parameters.reshape(-1, 1)
    
    LIP, JAW, TNG, LRX = [int(data["semi-polar coordinates"]["number of parameters"][key])
                          for key in ["lip", "jaw", "tongue", "larynx"]]


    nvrs_lip, nvrs_tng, nvrs_lrx = [int(data[key]["parameters"]["number of variables"])
                                    for key in ["lips", "tongue", "larynx"]]

    A_lip, A_tng, A_lrx = [np.array(data[key]["statistics"]["factor"])
                           for key in ["lips", "tongue", "larynx"]]
    s_lip, s_tng, s_lrx = [(data[key]["statistics"]["standard deviation"])
                           for key in ["lips", "tongue", "larynx"]]
    u_lip, u_tng, u_lrx, u_wal = [(data[key]["statistics"]["mean"])
                           for key in ["lips", "tongue", "larynx", "wall"]]

    iniva_tng, lstva_tng = [int(data["tongue"]["parameters"][key])
                           for key in ["initial point", "last point"]]
    vtos = data["semi-polar coordinates"]["vector to semi-polar map"]
    igd, egd = [data["semi-polar coordinates"]["grids"][key] for key in ["interior", "exterior"]]
    ix0, iy0 = [data["semi-polar coordinates"]["origin"][key] for key in ["x", "y"]]
    inci_x, inci_y = [data["lips"]["statistics"]["upper lip"][key] for key in ["x", "y"]]
    inci_lip = data["semi-polar coordinates"]["incisor-lip distance"]
    vp_map = data["semi-polar coordinates"]["map coeff"]
    inci_lip_vp = inci_lip / vp_map
    DWIDTH, DHEIGHT = [data["semi-polar coordinates"]["display"][key]
                       for key in ["width", "height"]]
    TEKvt, TEKlip = [data["semi-polar coordinates"]["scale factor"][key]
                       for key in ["vocal tract", "lips"]]
    
    nb_params, nb_frame = articulatory_parameters.shape    
    contours = []
    
    for n in range(nb_frame):
        pa = articulatory_parameters[:, n].tolist()
        # pa = np.zeros(7)
        p = np.zeros(7)
        p[0] = pa[0]
        
        p[range(1, TNG+1)] = [pa[i] for i in range(1, TNG+1)]
        v_tng = np.zeros(nvrs_tng)
        v_lip = np.zeros(nvrs_lip)
        v_lrx = np.zeros(nvrs_lrx)
        for i in range(nvrs_tng):
            v = 0
            for j in range(JAW+TNG):
                v += A_tng[i, j]*p[j]
                v_tng[i] = s_tng[i]*v + u_tng[i]
                
        p[range(1, LIP+1)] = [pa[i+TNG] for i in range(1, LIP+1)]
        for i in range(nvrs_lip):
            v = 0
            for j in range(JAW+LIP):
                v += A_lip[i, j]*p[j]
                v_lip[i] = s_lip[i]*v + u_lip[i]
                if v_lip[i] < 0:
                    v_lip[i] = 0
                    
        p[range(1, LRX+1)] = [pa[i+TNG+LIP] for i in range(1, LRX+1)]
        for i in range(nvrs_lrx):
            v = 0
            for j in range(JAW+LRX):
                v += A_lrx[i, j]*p[j]
                v_lrx[i] = s_lrx[i]*v + u_lrx[i]
        
        ivt = [{"x": v_lrx[JAW] + ix0, 
                "y": v_lrx[JAW+1] + iy0}]
        evt = [{"x": v_lrx[JAW+2] + ix0, 
                "y": v_lrx[JAW+3] + iy0}]
        
        for i in range(iniva_tng, lstva_tng+1):
            j = i - iniva_tng
            v = min([v_tng[j+JAW], u_wal[j]])
            x1 = vtos[i]["x"]*v + igd[i]["x"]
            y1 = vtos[i]["y"]*v + igd[i]["y"]
            x2 = vtos[i]["x"]*u_wal[j] + igd[i]["x"]
            y2 = vtos[i]["y"]*u_wal[j] + igd[i]["y"]
            if i == iniva_tng:
                ivt.append({"x": (ivt[0]["x"]+x1)/2,
                            "y": (ivt[0]["y"]+y1)/2})
                evt.append({"x": (evt[0]["x"]+x2)/2,
                            "y": (evt[0]["y"]+y2)/2})
            ivt.append({"x": x1,
                        "y": y1})
            evt.append({"x": x2,
                        "y": y2})
        
        evt.append({"x": inci_x + ix0,
                    "y": inci_y + inci_lip_vp + iy0})
        ivt.append({"x": evt[-1]["x"],
                    "y": evt[-1]["y"] - v_lip[2]})
        
        evt.append({"x": evt[-1]["x"] - v_lip[1],
                    "y": evt[-1]["y"] })
        ivt.append({"x": evt[-1]["x"],
                    "y": ivt[-1]["y"]})
         
        P1 = np.array([[x["x"] for x in ivt],
                       [x["y"] for x in ivt],
                       [x["x"] for x in evt],
                       [x["y"] for x in evt]])
        
        lip_h = v_lip[2]/2
        lip_w = v_lip[3]/2
        
        contours.append(Contour("contours", P1, "lips", (lip_h, lip_w)))
        
    return contours