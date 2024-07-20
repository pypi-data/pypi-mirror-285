#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 16:49:54 2022

@author: benjamin
"""

import numpy as np
import scipy

def in_hull_delaunay(p, hull):
    """
    Test if points in `p` are in `hull`

    `p` should be a `NxK` coordinates of `N` points in `K` dimensions
    `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of the 
    coordinates of `M` points in `K`dimensions for which Delaunay triangulation
    will be computed
    """
    if not isinstance(hull, scipy.spatial.Delaunay):
        hull = scipy.spatial.Delaunay(hull)

    return hull.find_simplex(p)>=0

def var_range(x, axis=0):
    return np.max(x, axis=axis, keepdims=True) - np.min(x, axis=axis, keepdims=True)

def dnn_cost_function(generated, observed, relative=False):    
    if relative == True:
        return np.mean(np.abs((generated-observed)/observed))
    elif relative == False:
        return np.mean(np.abs((generated-observed)))
    elif relative == "range":
        observed_range = var_range(observed)
        return np.mean(np.abs((generated-observed)/observed_range))

def symmetricifft(x, nfft=None):
    """ returns the IFFT by symmetric inverse Fourier transform """
    if len(x.shape) == 1:
        x = x.reshape(-1,1)
    xconj = np.conj(x[-2:0:-1,:])
    xconc = np.concatenate((x, xconj), 0)
    if nfft is None:
        nfft = len(xconc)
    y = np.real(np.fft.ifft(xconc, nfft, axis=0))

    return np.squeeze(y)

def window(nwin, win_type):
    
    if win_type == 'hann':
        return scipy.signal.hann(nwin)
    elif win_type == 'hanning':
        return scipy.signal.hanning(nwin)
    elif win_type == 'hamming':
        return scipy.signal.hamming(nwin)
    else:
        raise ValueError('Wrong type of window')

def esprit(x, sr=1, K=12):
    """ estimate the frequency of the damped sinusoids that model x """
    
    z = impulse_to_poles(x, sr=sr, K=K)[0][0]
    freq = np.angle(z) / 2 / np.pi * sr
    
    return np.sort(freq[freq > 100])

def impulse_to_poles(x, sr=1, K=12):
    idx = np.argmax(x)
    x = x[idx:]
    x = x - np.mean(x)
    
    M = int(min(100, np.floor(len(x) / 2)))
    Nl = len(x) - M + 1
    Nt = int(Nl / M)
    
    R = np.zeros((M,M))
    for k in range(Nt):
        deb = int(k * M)
        fin = int(deb + 2 * M - 1)
        xtmp = x[deb:fin]
    
        H = scipy.linalg.hankel(xtmp[0:M], xtmp[M - 1:])
        R += H.dot(H.T)
        
    u, s, d = np.linalg.svd(R)
    nx, ny = u.shape
    
    Up = u[1:,:K]
    Um = u[:-1,:K]
    Phi = np.linalg.pinv(Um).dot(Up)
    return np.linalg.eig(Phi), x

def get_amplitude(x, z, sr, N):
    
    freq = np.angle(z) / 2 / np.pi * sr
    z = np.array([z[i] for i in range(len(freq)) if
                  abs(freq[i]) > 50 and abs(freq[i]) < sr/2-50])
    freq = np.angle(z) / 2 / np.pi * sr

    alp_phase = 1j * 2 * np.pi / sr
    alp = np.exp(alp_phase * (x).dot(z.reshape(1, -1)))

    E = alp[:len(x), :]
    bk, dum1, dum2, dum3 = np.linalg.lstsq(E, x.reshape(-1, 1))
    bks = np.abs([bk[i] for i in range(len(freq)) if
                  (freq[i]) > 50 and (freq[i]) < sr/2-50]).squeeze()
    freq = np.array([freq[i] for i in range(len(freq)) if
                  (freq[i]) > 50 and (freq[i]) < sr/2-50])
    idx = np.argsort(freq)
    bks = bks[idx]
    if N < len(bks):
        bks = bks[:N]
    return bks

def fill_nan(x):

    idxAll = np.arange(x.shape[0])
    idxVal = np.where(np.isfinite(x))
    try:
        f = scipy.interpolate.interp1d(idxAll[idxVal], x[idxVal], 
                                   kind='cubic', fill_value='extrapolate')
    except:
        f = scipy.interpolate.interp1d(idxAll[idxVal], x[idxVal], 
                                   kind='linear', fill_value='extrapolate')
    return np.where(np.isfinite(x), x, f(idxAll))

def fill_nan_and_zero(x):
    
    y = fill_nan(x)
    first_non_zero = np.argwhere(y>0)[0][0]
    last_non_zero = len(y) - np.argwhere(y[::-1]>0)[0][0] - 1
    y[:first_non_zero] = y[first_non_zero]
    y[last_non_zero:] = y[last_non_zero]
    
    return y

def nextpow2(x):
    return int(np.ceil(np.log2(np.abs(x))))
   
def get_impulse_response(transfer_function):
    
    tf_size = transfer_function.shape    
    if len(tf_size) == 1:
        extend = True
        transfer_function = transfer_function.reshape(-1, 1)
    elif min(tf_size) == 1: 
        extend = True
    else:
        extend = False

    Hf = transfer_function
    Hf[0, :] = Hf[1, :]
    x = symmetricifft(Hf)    
    if extend:
        x = x.reshape(-1, 1)    
    x = x.shape[0] * x
    return x[:int(np.ceil(0.5 * len(x))), :]

def ChainMatrix(af, lf, freq, param, meth='tmm',  Tf=None):
    lw = len(freq) 
    if Tf is None:
        Tf = np.tile(np.eye(2).reshape((1,2,2)),(lw, 1, 1))

    Zo = (af / (param.rho * param.c)).reshape(1, -1)

    if meth.lower() != 'cmp':
        om = param.freq * 2 * np.pi    
        S = 2 * np.sqrt(af * np.pi)        
        L = param.rho / af
        Celem = (Zo / param.c).squeeze()
        
    if meth.lower() == 'cmp':
        if param.loss:
            argh = param.sig.reshape(-1,1) @ lf.reshape(1, -1) / param.c
            gam = param.gam.reshape(-1, 1) @ np.ones((1, len(lf)))
        else:
            argh = (1j * om / param.c).reshape(-1,1) @ lf.reshape(1, -1)
            gam = 1        
        Amat = np.cosh(argh)
        Bmat = - gam * np.sinh(argh) * (np.ones((lw, 1)) @ (1 / Zo))
        Cmat = (- 1 / gam * np.sinh(argh)) * (np.ones((lw, 1)) @ Zo)
    
    for k in range(len(af)-1,-1,-1):        
        if meth.lower() == 'cmp':            
            A = Amat[:, k].squeeze()
            B = Bmat[:, k].squeeze()
            C = Cmat[:, k].squeeze()
        else:
            R = S[k]*np.sqrt(param.rho * param.mu * om) / (2 * np.sqrt(2) * af[k]**2)
            G = (param.adiabatic - 1) * S[k] / (param.rho * param.c**2) * np.sqrt(param.heat_cond * om / (2 * param.specific_heat * param.rho))
            if param.loss:
                invZw = 1 / (param.wr / S[k]**2 + 1j*om*param.wm / S[k]**2 + 1 / (1j * om * S[k]**2 / param.wc)) * param.wallyield
                gam = np.sqrt((R + 1j * om * L[k]) * (G + 1j * om * Celem[k] + invZw))
            else:
                gam = 1j * om / param.c

            A = np.cosh(gam * lf[k])
            B = -np.sinh(gam * lf[k]) / Zo.squeeze()[k]
            C = -Zo.squeeze()[k] * np.sinh(gam * lf[k]) 
        
        Tn = np.array([[A,B], [C,A]]).transpose((2,0,1))
        Tf = np.matmul( Tf, Tn )
        
    A = Tf[:, 0, 0].flatten()
    B = Tf[:, 0, 1].flatten()
    C = Tf[:, 1, 0].flatten()
    D = Tf[:, 1, 1].flatten()
    
    return A, B, C, D, Tf

def findelements(a, b):
    # find indices of elements in a that contains elements in b
    nB = len(b)
    idx = []
    
    for k in range(nB):
        bTmp = b[k]
        idxTmp = [i for i,x in enumerate(a) if x==bTmp]
        if idxTmp != []: 
            if idx == []:
                idx = idxTmp
            else:
                idx = np.concatenate((idx, idxTmp)).astype(int)
                
    return idx

def lininterp1(xi, yi, xo, axis=1):
    
    if type(xi) is list:
        f1 = scipy.interpolate.interp1d(xi, yi, 'linear', 
                                        fill_value='extrapolate')
    else:
        while axis >= len(yi.shape): 
            axis -= 1        
        f1 = scipy.interpolate.interp1d(xi, yi, 'linear',
                                        fill_value='extrapolate', axis=axis)
   
    return f1(xo)

def vtl_estimation(freq, c=343):
     
    sum_freq = 0
    for i, row in enumerate(freq.T):
        for F_ij in row:
            sum_freq += F_ij / (i + 0.5)
    return c * freq.size / (2*sum_freq)

def vtln(freq, speaker_length=None, target_length=0.16273747, c=343):    
    
    if isinstance(freq, list):
        freq = np.array(freq).reshape(1, -1)    
    if freq.shape[1] != 4 and freq.shape[0] == 4:
        freq = freq.T
    if speaker_length is None:
        speaker_length = vtl_estimation(freq)
    return (freq * speaker_length / target_length).T