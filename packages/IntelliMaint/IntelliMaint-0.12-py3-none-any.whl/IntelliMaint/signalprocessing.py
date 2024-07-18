import numpy as np
from scipy.signal import hilbert, butter, lfilter
from scipy.stats import kurtosis
from scipy.fftpack import fft
import matplotlib.pyplot as plt

class SignalProcessor:
    def __init__(self, sampling_rate):
        self.sampling_rate = sampling_rate

    def ar_filter(self, signal, max_order):
        best_order = None
        max_kurtosis = -np.inf

        for order in range(1, max_order + 1):
            ar_coeffs = np.polyfit(signal[:-1], signal[1:], order)
            residual = signal[order:] - np.polyval(ar_coeffs, signal[:-order])
            k = kurtosis(residual)

            if k > max_kurtosis:
                max_kurtosis = k
                best_order = order

        ar_coeffs = np.polyfit(signal[:-best_order], signal[best_order:], best_order)
        residual = signal[best_order:] - np.polyval(ar_coeffs, signal[:-best_order])

        return residual
    
    def low_pass_filter(self, signal, cutoff_freq, order=5):
        nyquist_freq = 0.5 * self.sampling_rate
        normalized_cutoff_freq = cutoff_freq / nyquist_freq
        b, a = butter(order, normalized_cutoff_freq, btype='low', analog=False)
        filtered_signal = lfilter(b, a, signal)
        return filtered_signal

    def high_pass_filter(self, signal, cutoff_freq, order=5):
        nyquist_freq = 0.5 * self.sampling_rate
        normalized_cutoff_freq = cutoff_freq / nyquist_freq
        b, a = butter(order, normalized_cutoff_freq, btype='high', analog=False)
        filtered_signal = lfilter(b, a, signal)
        return filtered_signal

    def band_pass_filter(self, signal, low_cutoff_freq, high_cutoff_freq, order=5):
        nyquist_freq = 0.5 * self.sampling_rate
        normalized_low_cutoff_freq = low_cutoff_freq / nyquist_freq
        normalized_high_cutoff_freq = high_cutoff_freq / nyquist_freq
        b, a = butter(order, [normalized_low_cutoff_freq, normalized_high_cutoff_freq], btype='band', analog=False)
        filtered_signal = lfilter(b, a, signal)
        return filtered_signal

    def spectral_kurtosis(self, signal, window_lengths):
        num_windows = len(window_lengths)
        sk = []
        freqs = []

        for i, window_length in enumerate(window_lengths):
            window = np.hanning(window_length)
            overlap = window_length // 2

            num_segments = (len(signal) - window_length) // overlap + 1
            spec_kurtosis = np.zeros(window_length // 2 + 1)

            for j in range(num_segments):
                segment = signal[j * overlap : j * overlap + window_length]
                segment = segment * window
                spectrum = np.abs(np.fft.fft(segment))[:window_length // 2 + 1]
                spec_kurtosis += (spectrum**4) / (spectrum**2).mean()**2

            spec_kurtosis /= num_segments
            sk.append(spec_kurtosis)
            freqs.append(np.arange(window_length // 2 + 1) * self.sampling_rate / window_length)

        return sk, freqs

    def envelope_analysis(self, signal, bearing_frequencies):
        analytic_signal = hilbert(signal)
        envelope_signal = np.abs(analytic_signal)
        envelope_signal = envelope_signal - np.mean(envelope_signal)

        fft_envelope = np.abs(fft(envelope_signal)) / len(envelope_signal) * 2
        fft_envelope = fft_envelope[:len(fft_envelope)//2]

        freq_axis = np.arange(len(fft_envelope)) / len(envelope_signal) * self.sampling_rate

        plt.figure(figsize=(8, 4))
        plt.stem(freq_axis, fft_envelope, 'r', markerfmt=' ', basefmt='-b')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude')
        plt.title('Envelope Spectrum')
        plt.xlim(0, 1000)

        for fault_freq in bearing_frequencies:
            plt.axvline(x=fault_freq, color='k', linestyle='--', linewidth=1)

        plt.show()

