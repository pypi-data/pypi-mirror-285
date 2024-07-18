import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew
from scipy.fft import fft

def extract_features(signal, sampling_rate, bearing_info):
    # Time-domain features
    mean = np.mean(signal)
    std = np.std(signal)
    rms = np.sqrt(np.mean(signal**2))
    peak = np.max(np.abs(signal))
    skewness = skew(signal)
    kurtosis_value = kurtosis(signal)
    crest_factor = peak / rms
    shape_factor = rms / np.mean(np.abs(signal))
    impulse_factor = peak / np.mean(np.abs(signal))
    margin_factor = peak / (np.mean(np.sqrt(np.abs(signal))))**2

    # FFT features
    fft_signal = np.abs(fft(signal))
    fft_freq = np.fft.fftfreq(len(signal), 1/sampling_rate)
    fft_peaks = fft_signal[:len(signal)//2]
    fft_freqs = fft_freq[:len(signal)//2]

    # Bearing fault frequency features
    bpfo = bearing_info['bpfo']
    bpfi = bearing_info['bpfi']
    ftf = bearing_info['ftf']
    bsf = bearing_info['bsf']

    bpfo_amp = fft_signal[np.argmin(np.abs(fft_freq - bpfo))]
    bpfi_amp = fft_signal[np.argmin(np.abs(fft_freq - bpfi))]
    ftf_amp = fft_signal[np.argmin(np.abs(fft_freq - ftf))]
    bsf_amp = fft_signal[np.argmin(np.abs(fft_freq - bsf))]

    # Combine features into a dictionary
    features = {
        'mean': mean,
        'std': std,
        'rms': rms,
        'peak': peak,
        'skewness': skewness,
        'kurtosis': kurtosis_value,
        'crest_factor': crest_factor,
        'shape_factor': shape_factor,
        'impulse_factor': impulse_factor,
        'margin_factor': margin_factor,
        'fft_peaks': fft_peaks,
        'fft_freqs': fft_freqs,
        'bpfo_amp': bpfo_amp,
        'bpfi_amp': bpfi_amp,
        'ftf_amp': ftf_amp,
        'bsf_amp': bsf_amp
    }

    return features

# Example usage
bearing_info = {
    'bpfo': 3.5848,
    'bpfi': 5.4152,
    'ftf': 0.3983,
    'bsf': 4.7135
}

# Assuming you have a vibration signal and sampling rate
signal = ...  # Your vibration signal
sampling_rate = ...  # Sampling rate of the signal

features = extract_features(signal, sampling_rate, bearing_info)

# Convert features to a DataFrame
feature_df = pd.DataFrame([features])






