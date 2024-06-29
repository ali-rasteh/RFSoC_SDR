import numpy as np
from numpy.fft import fft, fftshift, ifft
import matplotlib.pyplot as plt
import os
import time


class signals(object):
    def __init__(self, seed=100, fs= 245.76e6 * 4, n_samples=1024, nfft=1024):
        self.seed = seed
        self.n_samples = n_samples
        self.nfft = nfft
        self.fs = fs

        return

    def generate_tone(self, f=10e6):

        t = np.linspace(0, self.n_samples * self.fs, self.n_samples)
        wt = np.multiply(2 * np.pi * f, t)
        tone_td = np.cos(wt) + 1j * np.sin(wt + np.pi / 2)

        return tone_td

    def generate_wideband(self, sc_min=-100, sc_max=100, mode='qam'):
        np.random.seed(self.seed)
        if mode=='qam':
            sym = (1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j)  # QAM symbols
        else:
            sym = ()
            # raise ValueError('Invalid signal mode: ' + mode)

        # Create the wideband sequence in frequency-domain
        wb_fd = np.zeros((self.nfft,), dtype='complex')
        if mode == 'qam':
            wb_fd[((self.nfft >> 1) + sc_min):((self.nfft >> 1) + sc_max)] = np.random.choice(sym, len(range(sc_min, sc_max)))
        else:
            wb_fd[((self.nfft >> 1) + sc_min):((self.nfft >> 1) + sc_max)] = 1
        wb_fd[((self.nfft >> 1) - 10):((self.nfft >> 1) + 10)] = 0

        wb_fd = fftshift(wb_fd, axes=0)
        # Convert the waveform to time-domain
        wb_td = ifft(wb_fd, axis=0)
        # Normalize the signal
        wb_td /= np.max([np.abs(wb_td.real), np.abs(wb_td.imag)])

        return wb_td


    def channel_estimate(self, txtd, rxtd):
        txfd = np.fft.fft(txtd)
        rxfd = np.fft.fft(rxtd)
        H_est = rxfd * np.conj(txfd)
        h_est = ifft(H_est)

        t = np.arange(0, np.shape(h_est)[0])
        sig = np.abs(h_est) / np.max(np.abs(h_est))
        title = 'Channel response in the time domain'
        xlabel = 'Sample'
        ylabel = 'Normalized Magnitude (dB)'
        self.plot_signal(t, sig, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel)

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
        plt.show()