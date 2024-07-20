# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 09:55:08 2020

@author: benjamin
"""

import json
import numpy as np
import numpy.matlib as npmt
from .signaltools import ( 
    ChainMatrix, 
    esprit, 
    symmetricifft,
    get_impulse_response
    )
from ._set import struct, timestruct
from tqdm import tqdm


class Waveguide:
    """ Class for analyzing and make operations on vocal tract cavities """
    #### Properties
    area_function = None # area function
    formants = None # formants
    child_wvg = None # name of the child waveguide object
    parent_wvg = None # name of the parent waveguide object
    twin_wvg = None # name of the twin waveguide object
    anabranch_wvg = None # name of the anabranch waveguide object
    child_point = None # point of connection where the child waveguide is connected
    parent_point = None # point of connection of the parent waveguide
    radiation = None # Boolean. True if the waveguide radiates (e.g. oral tract).
    transfer_function = None # transfer function of the waveguide
    impulse_response = None # impulse response of the waveguide
    transfer_function_constriction = None
    chain_matrix = None
    chain_matrix_derivative = None
    input_impedance = None
    freq = None # frequency vector of the transfer function
    actualVT = None
    velopharyngeal_port = 0
    velum_area = 0
    norder = 1

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            if key == 'area_function':
                self.area_function.parent = self  

    def computetransferfunction(self, param=None, meth='tmm', 
                                loc=-1, formants=False, verbosity=False,
                                position=0, df=50):
        """ Compute the transfer function and the impulse response of the vocal tract
        defined by area function Avt and lvt. The resonance frequencies are
        estimated via ESPRIT. They are the pole frequencies of the impulse
        response of the vocal tract. The constant values are stocked in
        param.
        The transfer function is computed using the chain paradigm by Sondhi and
        Schroeter (A hybrid time-frequency domain articulatory speech
        synthesizer, IEEE TASSP, 1987)"""

        if param is None:
            param = timestruct()
        if not hasattr(param, 'rho'):
            param.rho = 1.204/1000
        if not hasattr(param, 'c'):
            param.c = 343.4
        if not hasattr(param, 'mu'):
            param.mu = 1.9831e-5
        if not hasattr(param, 'a'):
            param.a = 130 * np.pi
        if not hasattr(param, 'b'):
            param.b = (30 * np.pi)**2
        if not hasattr(param, 'c1'):
            param.c1 = 4
        if not hasattr(param, 'wo2'):
            param.wo2 = (406 * np.pi)**2
        if not hasattr(param, 'c1n'):
            param.c1n = 72
        if not hasattr(param, 'heat_cond'):
            param.heat_cond = 0.0034
        if not hasattr(param, 'specific_heat'):
            param.specific_heat = 160
        if not hasattr(param, 'adiabatic'):
            param.adiabatic = 1.4
        if not hasattr(param, 'wallyield'):
            param.wallyield = True
        if not hasattr(param, 'loss'):
            param.loss = True

        param.freq[param.freq <= 1e-11] = 1e-11
        if df != 50:
            param.freq = np.arange(0, 5000+df, df, dtype='float') #Vector of frequencies
            param.freq = param.freq[param.freq <= 5000]
        
        freq = param.freq.reshape(-1)
        af = self.area_function.area # to make it from the lips to the glottis
        lf = self.area_function.length # to make it from the lips to the glottis
        if af is None or lf is None:
            print('Warning: the waveguide instance has no area function!')
            return None
        w = 2 * np.pi * freq # angular frequency
        lw = len(w)

        if meth.lower() == 'cmp':
            param.alp = np.sqrt(1j*w * param.c1)
            param.bet = 1j*w * param.wo2 / ((1j*w + param.a) * 1j*w + param.b) + param.alp
            param.gam = np.sqrt((param.alp + 1j*w) / (param.bet + 1j*w))
            param.sig = param.gam * (param.bet + 1j*w)

        af_size = af.shape
        if len(af_size) == 1:
            nframe = 1
            af = af.reshape(-1, 1)
            lf = lf.reshape(-1, 1)
        else:
            nframe = af_size[1]
        transFun = np.zeros((lw, nframe)) + 1j*np.zeros((lw, nframe))
        Hf_cstr = np.zeros((lw, nframe)) + 1j*np.zeros((lw, nframe))

        if isinstance(loc, int) and nframe > 1:
            loc = loc * np.ones(nframe)
        if isinstance(loc, int):
            loc = [loc]
            
        if formants:
            fmt = np.zeros((param.nform, nframe))
        Grad = param.rho * w**2 / 2. / np.pi / param.c_s    
        
        if verbosity:
            disable = False
        else:
            disable = True            
        
        for kf in tqdm(range(nframe), disable=disable,
                       position=position, desc="Transfer function", leave=True):
            if np.any(af[:, kf] <= 0):
                Hf = np.empty(len(freq))
                Hf[:] = np.nan
            else:
                Avt = af[:, kf]
                lvt = lf[:, kf]
                Jrad = 8 * param.rho * w / 3. / np.pi**(1.5) * Avt[-1]**(-0.5)
                Zrad = Grad + 1j*Jrad
    
                A, _, C, _, _ = ChainMatrix(Avt, lvt, freq, param, meth)
    
                Hf = 1 / (-C * Zrad + A)
            transFun[:, kf] = Hf
            Hf_cstr[:, kf] = Hf
    
            if loc[kf] > 0 and not np.any(af[:, kf] <= 0):
                param.lg = 0.03
                param.Ag0 = 0.4e-4
                Zg = 12 * param.mu * param.lg**3 / param.Ag0**3 + \
                0.875 * param.rho / 2 / param.Ag0**2 + \
                1j*freq * 2 * np.pi * param.rho * param.lg / param.Ag0
                k_tmp = loc[kf]
                aup = Avt[k_tmp::-1]
                adown = Avt[k_tmp+1:]
                lup = lvt[k_tmp::-1]
                ldown = lvt[k_tmp+1:]
                Aup, Bup, Cup, Dup, _ = ChainMatrix(aup, lup, freq, param, meth)
                Adown, Bdown, Cdown, Ddown, _ = ChainMatrix(adown, ldown, freq, param, meth)
                Tf_front = 1 / (Cdown * Zrad + Ddown)
                Z_front = (Adown * Zrad + Bdown) / (Cdown * Zrad + Ddown)
                Z_back = (Aup * Zg + Bup) / (Cup * Zg + Dup)
                Hf_cstr[:, kf] = Tf_front * Z_back / (Z_front + Z_back)
            
            if formants:
                if np.any(af[:, kf] <= 0):
                    fmt[:, kf] = np.zeros((fmt.shape[0], 1))
                else:
                    fmt[:, kf] = formant_from_tf(transFun[:, kf].squeeze(), 
                                             freq, 
                                             nform=param.nform)
        self.transfer_function = np.squeeze(transFun)
        self.transfer_function_constriction = np.squeeze(Hf_cstr)
        self.freq = freq
        if formants:
            self.formants = fmt
        return transFun, freq

    def computeformants(self, param=None, verbosity=False, position=0):
        """ Computes the resonance frequencies of the VT_Waveguide object.
         Use the ESPRIT method on the impulse response to estimate the poles of
         the transfer function"""

        if param is None:
            param = struct()
        if self.transfer_function is None:
            self.computetransferfunction(self, param)
        tf_size = self.transfer_function.shape
        if len(tf_size) == 1:
            nfreq = tf_size[0]
            nframe = 1
            self.transfer_function = self.transfer_function.reshape(-1, 1)
        else:
            nfreq, nframe = tf_size

        himp = get_impulse_response(self.transfer_function)
        himp -= np.mean(himp, axis=0, keepdims=True)
        df = self.freq[2] - self.freq[1]
        K = 2 * (param.nform + 2)
        fmt = np.zeros((param.nform, nframe))
        if verbosity:
            disable = False
        else:
            disable = True   
        for kf in tqdm(range(nframe), disable=disable, position=position,
                       desc="Formants", leave=True):
            if not np.any(np.isnan(self.transfer_function[:, kf])):
                try:
                    fk = esprit(himp[:, kf], df * 2 * (nfreq - 1), K)
                    if len(fk) >= param.nform:
                        fmt[:, kf] = fk[:param.nform]
                except:
                    pass
        self.formants = fmt
        return fmt

    def exportaf2json(self, fileName):
        """export the area function in a .JSON file"""
    
        af = self.area_function.area
        lf = self.area_function.length
    
        if hasattr(self, 'velopharyngeal_port'):
            vpo = self.velopharyngeal_port
        else:
            vpo = 0
        if hasattr(self, 'velum_area'):
            vArea = self.velum_area
        else:
            vArea = np.zeros_like(af)
    
        if len(af.shape) == 1:
            nFrame = 0
            nTubes = len(af)
        else:
            nTubes, nFrame = af.shape
    
        idx = fileName.find('.json')
        if idx >= 0:
            fileName = fileName[:idx]
    
        if isinstance(vpo, (float, int)) and nFrame > 0:
            vpo = vpo * np.ones(nFrame)
    
        if isinstance(vArea, (float, int)) and nFrame > 0:
            vArea = vArea * np.ones((nTubes, nFrame))
    
        if isinstance(vArea, (float, int)) and nFrame > 0:
            vArea = npmt.repmat(vArea.reshape(-1, 1), 1, nFrame)
    
        if nFrame == 0:
            fTmp = fileName + '.json'
            nFrame = 1
            vpo = [vpo]
            vArea = vArea * np.ones((nTubes, 1))
            af = af.reshape(-1, 1)
            lf = lf.reshape(-1, 1)
        for kF in range(nFrame):
            if nFrame > 1:
                fTmp = fileName + '_' + '%.5d' %(kF+1) + '.json'
            else:
                fTmp = fileName + '.json'
    
            idjson = {}
            idjson['VelumOpeningInCm'] = np.sqrt(vpo[kF]) * 1e2
            idjson['frameId'] = fTmp
            idjson['tubes'] = []
            for kT in range(nTubes):
                idjson['tubes'].append({
                    'area' : af[kT, kF] * 1e4,
                    'velumArea' : vArea[kT, kF] * 1e4,
                    'x' : lf[kT, kF] * 1e2
                })
        with open(fTmp, 'w') as f:
            json.dump(idjson, f, indent=4)
    
      
    def check_instance(self, class_type):
        """ check instance """
        return eval('isinstance(self, ' + class_type + ')')
    
def formant_from_tf(transfer_function, freq, nform=4):
    
    K = 2 * (nform + 2)
    if np.isinf(transfer_function[0]) or np.isnan(transfer_function[0]):
        transfer_function[0] = transfer_function[1]
    df = freq[2] - freq[1]
    x = symmetricifft(transfer_function)
    x = len(x) * x
    himp = x[:int(np.ceil(0.5 * len(x)))]
    himp -= np.mean(himp)
    try:
        fk = esprit(himp, df * 2 * (len(transfer_function) - 1), K)
        if len(fk) >= nform:            
            return fk[:nform]
        else:
            return np.array([np.nan]*nform)
    except:
        return np.array([np.nan]*nform)