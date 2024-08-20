import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft, fftshift, ifft
from scipy.signal import firwin, lfilter, freqz, welch



class signals(object):
    def __init__(self, params):
        self.seed = params.seed
        self.n_samples = params.n_samples
        self.nfft = params.nfft
        self.fs = params.fs
        self.plot_level = params.plot_level
        self.verbose_level = params.verbose_level
        self.filter_signal = params.filter_signal
        self.sig_mode = params.sig_mode
        self.wb_bw = params.wb_bw
        self.f_tone = params.f_tone
        self.sig_modulation = params.sig_modulation
        self.sig_gen_mode = params.sig_gen_mode
        self.sig_path = params.sig_path
        self.wb_null_sc = params.wb_null_sc
        self.mixer_mode = params.mixer_mode
        self.mix_freq = params.mix_freq
        self.filter_bw = params.filter_bw
        self.freq = params.freq
        self.t = params.t
        self.om = params.om

        self.print("signals object initialization done", thr=1)


    def print(self, text='', thr=0):
        if self.verbose_level>=thr:
            print(text)


    def to_db(self, sig):
        return 10 * np.log10(sig)
    
    
    def generate_tone(self, f=10e6, sig_mode='tone_2', gen_mode='fft'):

        if gen_mode == 'time':
            wt = np.multiply(2 * np.pi * f, self.t)
            if sig_mode=='tone_1':
                tone_td = np.cos(wt) + 1j * np.sin(wt)
            elif sig_mode=='tone_2':
                tone_td = np.cos(wt) + 1j * np.cos(wt)
                # tone_td = np.cos(wt)

        elif gen_mode == 'fft':
            sc = int((f)*self.nfft/self.fs)
            tone_fd = np.zeros((self.nfft,), dtype='complex')
            if sig_mode=='tone_1':
                tone_fd[(self.nfft >> 1) + sc] = 1
            elif sig_mode=='tone_2':
                tone_fd[(self.nfft >> 1) + sc] = 1
                tone_fd[(self.nfft >> 1) - sc] = 1
            tone_fd = fftshift(tone_fd, axes=0)

            # Convert the waveform to time-domain
            tone_td = np.fft.ifft(tone_fd, axis=0)

        # Normalize the signal
        tone_td /= np.max([np.abs(tone_td.real), np.abs(tone_td.imag)])

        self.print("Tone generation done", thr=2)

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
            wb_fd[((self.nfft >> 1) - self.wb_null_sc):((self.nfft >> 1) + self.wb_null_sc)] = 0

        wb_fd = fftshift(wb_fd, axes=0)
        # Convert the waveform to time-domain
        wb_td = ifft(wb_fd, axis=0)
        # Normalize the signal
        wb_td /= np.max([np.abs(wb_td.real), np.abs(wb_td.imag)])

        self.print("Wide-band signal generation done", thr=2)

        return wb_td
        

    def gen_tx_signal(self):
        if self.sig_mode == 'tone_1' or self.sig_mode == 'tone_2':
            txtd_base = self.generate_tone(f=self.f_tone, sig_mode=self.sig_mode, gen_mode=self.sig_gen_mode)
        elif self.sig_mode == 'wideband' or self.sig_mode == 'wideband_null':
            txtd_base = self.generate_wideband(bw=self.wb_bw, modulation=self.sig_modulation, sig_mode=self.sig_mode)
        elif self.sig_mode == 'load':
            txtd_base = np.load(self.sig_path)
        else:
            raise ValueError('Unsupported signal mode: ' + self.sig_mode)
        txtd_base /= np.max([np.abs(txtd_base.real), np.abs(txtd_base.imag)])

        # txfd_base = np.abs(fftshift(fft(txtd_base)))
        title = 'TX signal spectrum in base-band'
        xlabel = 'Frequency (MHz)'
        ylabel = 'Magnitude (dB)'
        self.plot_signal(x=self.freq, sigs=txtd_base, mode='fft', scale='dB', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)

        if self.mixer_mode=='digital' and self.mix_freq!=0:
            txtd = self.freq_shift(txtd_base, shift=self.mix_freq)

            # txfd = np.abs(fftshift(fft(txtd)))
            title = 'TX signal spectrum after upconversion'
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            self.plot_signal(x=self.freq, sigs=txtd, mode='fft', scale='dB', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)
        else:
            txtd = txtd_base.copy()
            # txfd = txfd_base.copy()

        return (txtd_base, txtd)
    

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
        # self.print(f'Time delay between the two signals: {delay} samples', thr=3)
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
        txfd = fft(txtd)
        rxfd = fft(rxtd)
        txfd += 1e-3
        # rxfd = np.roll(rxfd, 1)

        # H_est = rxfd * np.conj(txfd) / (np.abs(txfd)**2)
        # H_est = rxfd * np.conj(txfd)
        H_est = rxfd / txfd

        h_est = ifft(H_est)
        h_est = h_est.flatten()

        t = np.arange(0, np.shape(h_est)[0])
        sig = np.abs(h_est) / np.max(np.abs(h_est))
        title = 'Channel response in the time domain'
        xlabel = 'Sample'
        ylabel = 'Normalized Magnitude'
        self.plot_signal(t, sig, scale='linear', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=3)

        return h_est


    # plot_signal(self, x, sig, mode='time_IQ', scale='linear', title='Custom Title', xlabel='Time', ylabel='Amplitude', plot_args={'color': 'red', 'linestyle': '--'}, xlim=(0, 10), ylim=(-1, 1), legend=True)
    def plot_signal(self, x, sigs, mode='time', scale='dB', plot_level=0, **kwargs):

        if self.plot_level<plot_level:
            return
        
        colors = ['blue', 'red', 'green', 'cyan', 'magenta', 'orange', 'purple']

        if isinstance(sigs, dict):
            sigs_dict = sigs
        else:
            sigs_dict = {"Signal": sigs}

        plt.figure()
        plot_args = kwargs.get('plot_args', {})

        for i, sig_name in enumerate(sigs_dict.keys()):
            if mode=='time' or mode=='time_IQ':
                sig_plot = sigs_dict[sig_name].copy()
            elif mode=='fft':
                sig_plot = np.abs(fftshift(fft(sigs_dict[sig_name])))
            elif mode=='psd':
                freq, sig_plot = welch(sigs_dict[sig_name], self.fs, nperseg=self.nfft)
                x = freq
            
            if scale=='dB':
                sig_plot = self.to_db(sig_plot)
            elif scale=='linear':
                pass

            if mode!='time_IQ':
                plt.plot(x, sig_plot, color=colors[i], label=sig_name, **plot_args)
            else:
                plt.plot(x, np.real(sig_plot), color=colors[3*i], label='I', **plot_args)
                plt.plot(x, np.imag(sig_plot), color=colors[3*i+1], label='Q', **plot_args)
                plt.plot(x, np.abs(sig_plot), color=colors[3*i+2], label='Mag', **plot_args)

        title = kwargs.get('title', 'Signal in time domain')
        xlabel = kwargs.get('xlabel', 'Sample')
        ylabel = kwargs.get('ylabel', 'Magnitude (dB)')

        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.minorticks_on()
        plt.grid()

        legend = kwargs.get('legend', False)
        if legend:
            plt.legend()

        plt.autoscale()
        if 'xlim' in kwargs:
            plt.xlim(kwargs['xlim'])
        if 'ylim' in kwargs:
            ylim=kwargs['ylim']
            if scale=='dB':
                ylim = (self.to_db(ylim[0]), self.to_db(ylim[1]))
            plt.ylim(ylim)
        plt.tight_layout()

        # plt.axvline(x=30e6, color='g', linestyle='--', linewidth=1)

        plt.show()


    def rx_operations(self, txtd_base, rxtd):
        txfd_base = np.abs(fftshift(fft(txtd_base)))

        # rxfd = np.abs(fftshift(fft(rxtd)))
        title = 'RX signal spectrum'
        xlabel = 'Frequency (MHz)'
        ylabel = 'Magnitude (dB)'
        self.plot_signal(x=self.freq, sigs=rxtd, mode='fft', scale='dB', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)

        title = 'RX signal in time domain'
        xlabel = 'Time (S)'
        ylabel = 'Magnitude'
        xlim=(0, 10/(self.filter_bw/2))
        self.plot_signal(x=self.t, sigs=rxtd, mode='time_IQ', scale='linear', title=title, xlabel=xlabel, ylabel=ylabel, legend=True, xlim=xlim, plot_level=5)


        if self.mixer_mode == 'digital' and self.mix_freq!=0:    
            rxtd_base = self.freq_shift(rxtd, shift=-1*self.mix_freq)
            title = 'RX signal spectrum after downconversion'
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            self.plot_signal(x=self.freq, sigs=rxfd_base, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)
        else:
            rxtd_base = rxtd.copy()

        if self.filter_signal:
            rxtd_base = self.filter(rxtd_base, cutoff=self.filter_bw)
            title = 'RX signal spectrum after filtering in base-band'
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            self.plot_signal(x=self.freq, sigs=rxfd_base, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)


        rxfd_base = np.abs(fftshift(fft(rxtd_base)))
        h_est = self.channel_estimate(txtd_base, rxtd_base)


        title = 'TX and RX signals spectrum in base-band'
        xlabel = 'Frequency (MHz)'
        ylabel = 'Magnitude (dB)'
        scale = np.max(txfd_base)/np.max(rxfd_base)
        self.print("TX to RX spectrum scale: {:0.3f}".format(scale), thr=5)
        xlim=(-self.filter_bw/2/1e6, self.filter_bw/2/1e6)
        f1=np.abs(self.freq - xlim[0]).argmin()
        f2=np.abs(self.freq - xlim[1]).argmin()
        ylim=(np.min(rxfd_base[f1:f2]*scale), 1.1*np.max(rxfd_base[f1:f2]*scale))
        self.plot_signal(x=self.freq, sigs={"txfd_base":txfd_base, "Scaled rxfd_base":rxfd_base*scale}, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel, xlim=xlim, ylim=ylim, legend=True, plot_level=5)
        self.print("txfd_base max freq: {} MHz".format(self.freq[(self.nfft>>1)+np.argmax(txfd_base[self.nfft>>1:])]), thr=5)
        self.print("rxfd_base max freq: {} MHz".format(self.freq[(self.nfft>>1)+np.argmax(rxfd_base[self.nfft>>1:])]), thr=5)


        # return rxfd_base
        return h_est

