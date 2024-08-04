import numpy as np
from numpy.fft import fft, fftshift, ifft
from scipy.signal import firwin, lfilter, freqz
import matplotlib.pyplot as plt
import os
import time


class signals(object):
    def __init__(self, seed=100, fs= 245.76e6 * 4, n_samples=1024, nfft=1024):
        self.seed = seed
        self.n_samples = n_samples
        self.nfft = nfft
        self.fs = fs

        print("signals object initialization done")

        return

    def generate_tone(self, f=10e6, sig_mode='tone_2'):

        # t = np.linspace(0, self.n_samples * (1/self.fs), self.n_samples)
        t = np.arange(0, self.n_samples) / self.fs
        wt = np.multiply(2 * np.pi * f, t)

        if sig_mode=='tone_1':
            tone_td = np.cos(wt) + 1j * np.sin(wt)
        elif sig_mode=='tone_2':
            tone_td = np.cos(wt) + 1j * np.cos(wt)
            # tone_td = np.cos(wt)

        tone_td /= np.max([np.abs(tone_td.real), np.abs(tone_td.imag)])

        print("Tone generation done")

        return tone_td

    def generate_wideband(self, bw=200e6, modulation='qam', sig_mode='wideband'):

        sc_min = int(-(bw/2)*self.nfft/self.fs)
        sc_max = int((bw/2)*self.nfft/self.fs)
        np.random.seed(self.seed)
        if modulation=='qam':
            sym = (1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j)  # QAM symbols
        else:
            sym = ()
            # raise ValueError('Invalid signal modulation: ' + modulation)

        # Create the wideband sequence in frequency-domain
        wb_fd = np.zeros((self.nfft,), dtype='complex')
        if modulation == 'qam':
            wb_fd[((self.nfft >> 1) + sc_min):((self.nfft >> 1) + sc_max)] = np.random.choice(sym, len(range(sc_min, sc_max)))
        else:
            wb_fd[((self.nfft >> 1) + sc_min):((self.nfft >> 1) + sc_max)] = 1
        if sig_mode=='wideband_null':
            wb_fd[((self.nfft >> 1) - 10):((self.nfft >> 1) + 10)] = 0

        wb_fd = fftshift(wb_fd, axes=0)
        # Convert the waveform to time-domain
        wb_td = ifft(wb_fd, axis=0)
        # Normalize the signal
        wb_td /= np.max([np.abs(wb_td.real), np.abs(wb_td.imag)])

        print("Wide-band signal generation done")

        return wb_td
        

    def upsample(self, sig, up=2):

        upsampled_length = up * len(sig)
        upsampled_signal = np.zeros(upsampled_length, dtype=complex)

        # Assign the original signal values to the even indices
        upsampled_signal[::up] = sig.copy()

        return upsampled_signal


    def cross_correlation(self, sig_1, sig_2, index):
        if index >= 0:
            padded_sig_2 = np.concatenate((np.zeros(index, dtype=complex), sig_2[:len(sig_2) - index]))
        else:
            padded_sig_2 = np.concatenate((sig_2[-index:], np.zeros(-index, dtype=complex)))

        cros_corr = np.mean(sig_1 * np.conj(padded_sig_2))
        return cros_corr
    

    def extract_delay(self, sig_1, sig_2, plot_corr=False):

        cross_corr = np.correlate(sig_1, sig_2, mode='full')
        # cross_corr = np.correlate(sig_1, sig_2, mode='same')
        lags = np.arange(-len(sig_2) + 1, len(sig_1))

        if plot_corr:
            plt.figure()
            plt.plot(lags, np.abs(cross_corr), linewidth=1.0)
            plt.title('Cross-Correlation of the two signals')
            plt.xlabel('Lags')
            plt.ylabel('Correlation Coefficient')
            plt.show()

        max_idx = np.argmax(np.abs(cross_corr))
        delay = lags[max_idx]
        # print(f'Time delay between the two signals: {delay} samples')
        return delay


    def time_adjust(self, sig_1, sig_2, delay):

        n_points = np.shape(sig_1)[0]

        if delay >= 0:
            sig_1_adj = np.concatenate((sig_1[delay:], np.zeros(delay).astype(complex)))
            sig_2_adj = sig_2.copy()
        else:
            delay = abs(delay)
            sig_1_adj = sig_1.copy()
            sig_2_adj = np.concatenate((sig_2[delay:], np.zeros(delay).astype(complex)))

        mse = np.mean(np.abs(sig_1_adj[:n_points-delay] - sig_2_adj[:n_points-delay]) ** 2)
        err2sig_ratio = mse / np.mean(np.abs(sig_2) ** 2)

        return sig_1_adj, sig_2_adj, mse, err2sig_ratio


    def filter(self, sig, center_freq=0, cutoff=50e6, fil_order=1000, plot=False):

        filter_fir = firwin(fil_order, cutoff / self.fs)
        t = np.arange(0, self.n_samples) / self.fs
        om = np.linspace(-np.pi, np.pi, self.n_samples)
        t_fil = t[:len(filter_fir)]
        # filter_fir = np.exp(2 * np.pi * 1j * center_freq * t_fil) * filter_fir
        filter_fir = self.freq_shift(filter_fir, shift=center_freq)

        if plot:
            plt.figure()
            w, h = freqz(filter_fir, worN=om)
            plt.plot(w / np.pi, 20 * np.log10(np.abs(h)), linewidth=1.0)
            plt.title('Frequency response of the filter')
            plt.xlabel(r'Normalized Frequency ($\times \pi$ rad/sample)')
            plt.ylabel('Magnitude (dB)')
            plt.show()

        sig_fil = lfilter(filter_fir, 1, sig)

        return sig_fil


    def freq_shift(self, sig, shift=0):

        t = np.arange(0, len(sig)) / self.fs
        sig_shift = np.exp(2 * np.pi * 1j * shift * t) * sig

        return sig_shift


    def channel_estimate(self, txtd, rxtd):
        txfd = np.fft.fft(txtd)
        txfd += 1e-6
        rxfd = np.fft.fft(rxtd)
        H_est = rxfd * np.conj(txfd)
        H_est = H_est / (np.abs(txfd)**2)
        # H_est = rxfd / txfd
        h_est = ifft(H_est)

        t = np.arange(0, np.shape(h_est)[0])
        sig = np.abs(h_est) / np.max(np.abs(h_est))
        title = 'Channel response in the time domain'
        xlabel = 'Sample'
        ylabel = 'Normalized Magnitude'
        self.plot_signal(t, sig, scale='linear', title=title, xlabel=xlabel, ylabel=ylabel)

        return h_est


    def to_db(self, sig):
        return 10 * np.log10(sig)

    def plot_signal(self, x, sig, scale='dB', title='Signal in time domain', xlabel='Sample', ylabel='Magnitude (dB)'):

        plt.figure()
        if scale=='dB':
            sig_plot = self.to_db(sig)
        elif scale=='linear':
            sig_plot = sig
        else:
            sig_plot = sig
        plt.plot(x, sig_plot)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid()
        plt.show()