#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import os as os
import numpy as np
import sys
import statistics as st
import scipy as sp
import scipy.stats as sps
from scipy.stats import kurtosis
from scipy.stats import skew

#%% Time Domian Class
class TimeDomain:
    
    # def __init__(self, data):
    #     self.data = data

    @classmethod
    def extract_features_streaming(cls, data):
        chunkified_data = data.to_numpy()
        rms = cls.get_rms(chunkified_data)
        mean = cls.get_mean(chunkified_data)
        var =  cls.get_variance(chunkified_data)
        crest = cls.get_crestfactor(chunkified_data)
        kurt = cls.get_kurtosis(chunkified_data)
        skew = cls.get_skewness(chunkified_data)
        return rms, mean, var, crest, kurt, skew
    @classmethod
    def extract_features(cls, data, window_len=20480):
        data_np = data.to_numpy()
        chunkified_data = cls.get_chunks(data_np, frame_size=window_len, frame_shift=window_len)
        rms = cls.get_rms(chunkified_data)
        mean = cls.get_mean(chunkified_data)
        var =  cls.get_variance(chunkified_data)
        crest = cls.get_crestfactor(chunkified_data)
        kurt = cls.get_kurtosis(chunkified_data)
        skew = cls.get_skewness(chunkified_data)
        return rms, mean, var, crest, kurt, skew

    @classmethod
    def get_chunks(cls, data, frame_size=100, frame_shift=50):
        # initialize the number of chunks defined.
        chunks = []
        data = cls.check1(data)
        #Check if the provided size of the input data is greater than frame_size
        if(data.shape[0]<frame_size):
            sys.exit('Oops !!! The length of input vector is smaller than the analysis window length')
        for j in range(0,len(data)-frame_size,frame_shift):
            chunks.append(data[j:j+frame_size,:])
        frames = np.array(chunks)
        return frames
    @classmethod
    def check1(cls, data):
        # Check if the provided input data is atleast an 1D array
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        if(data.ndim < 1):
            sys.exit('Oops !!! Error with the input vector')
        elif(data.ndim == 1):
            data = np.reshape(data,(data.shape[0],1))
        return data
    @classmethod
    def get_rms(cls, data):
        """
        Parameters
        ----------
            data (pandas.DataFrame): input data in the dataframe format
        Returns
        -------
            rms (numpy.ndarray): root mean squared values
        """
        if data.ndim == 3:
            rms = np.sqrt(np.mean(data**2, axis = 1))
        else:
            rms = np.sqrt(np.mean(data**2, axis = 0))
        return rms
    @classmethod
    def get_mean(cls,data):
        """
        Parameters
        ----------
            data (pandas.DataFrame): input data in the dataframe format
        Returns
        -------
            mean (numpy.ndarray): mean values
        """
        if data.ndim == 3:
            mean = np.mean(data, axis = 1)
        else:
            mean = np.mean(data, axis = 0)
        return mean
    @classmethod
    def get_variance(cls,data):
        """
        Parameters
        ----------
            data (pandas.DataFrame): input data in the dataframe format
        Returns
        -------
            v (numpy.ndarray): variance values
        """
        if data.ndim == 3:
            v = np.var(data, axis =1)
        else:
            v = np.var(data, axis =0)
        return v
        
    @classmethod  
    def get_crestfactor(cls,data):
        """
        Parameters
        ----------
            data (pandas.DataFrame): input data in the dataframe format
        Returns
        -------
            c (numpy.ndarray): crestfactor values
        """
        if data.ndim == 3:
            peaks = np.max(data, axis = 1)
            rms = cls.get_rms(data)
            c = np.divide(peaks, rms)
        else:
            peaks = np.max(data, axis = 0)
            rms = cls.get_rms(data)
            c = np.divide(peaks, rms)
        return c
    @classmethod  
    def get_kurtosis(cls,data):
        if data.ndim == 3:
            kurt = kurtosis(data, axis=1)
        else:
            kurt = kurtosis(data, axis=0)
        return kurt
        
    @classmethod   
    def get_skewness(cls,data):
        if data.ndim == 3:
            sk = skew(data, axis = 1)
        else:
            sk = skew(data, axis = 0)
        return sk
        
        
#%% Frequency Domain (stationary)
        
class FrequencyDomain:
    
    def __init__(self,data):
        self.data = data
        
    def get_cepstrumcoeffs(self,data):
        spectrum = np.fft.fft(data,axis=1)
        ceps_coeffs = np.fft.ifft(np.log(np.abs(spectrum))).real
        return ceps_coeffs

        
   
    # def get_spectralanalysis(self,data):
        
        
#%% Time - Frequency (Non Stationary )
        

class Nonstationary:
    
    
    def __init__(self,data):
        self.data = data
      
    #Emphirical Mode Decomposition
    # def get_emd(self, data):
        
    #Wavelet Packet Decomposition
    # def get_wpd(self, data):
     
        
        
        
    