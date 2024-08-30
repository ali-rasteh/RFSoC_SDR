import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from numpy.fft import fft, fftshift, ifft
from scipy.signal import firwin, lfilter, freqz, welch, convolve



class Signals(object):
    def __init__(self, params):
        self.seed = params.seed
        self.n_samples = params.n_samples
        self.n_samples_tx = params.n_samples_tx
        self.n_samples_rx = params.n_samples_rx
        self.nfft = params.nfft
        self.nfft_tx = params.nfft_tx
        self.nfft_rx= params.nfft_rx
        self.fs = params.fs
        self.dac_fs = params.dac_fs
        self.adc_fs = params.adc_fs
        self.f_max = params.f_max
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
        self.freq_tx = params.freq_tx
        self.freq_rx = params.freq_rx
        self.t = params.t
        self.t_tx = params.t_tx
        self.t_rx = params.t_rx
        self.om = params.om
        self.om_tx = params.om_tx
        self.om_rx = params.om_rx

        self.print("signals object initialization done", thr=1)


    def print(self, text='', thr=0):
        if self.verbose_level>=thr:
            print(text)


    def lin_to_db(self, x, mode='pow'):
        if mode=='pow':
            return 10*np.log10(x)
        elif mode=='mag':
            return 20*np.log10(x)
    

    def generate_tone(self, f=10e6, sig_mode='tone_2', gen_mode='fft'):

        if gen_mode == 'time':
            wt = np.multiply(2 * np.pi * f, self.t_tx)
            if sig_mode=='tone_1':
                tone_td = np.cos(wt) + 1j * np.sin(wt)
            elif sig_mode=='tone_2':
                tone_td = np.cos(wt) + 1j * np.cos(wt)
                # tone_td = np.cos(wt)

        elif gen_mode == 'fft':
            sc = int(np.round((f)*self.nfft_tx/self.dac_fs))
            tone_fd = np.zeros((self.nfft_tx,), dtype='complex')
            if sig_mode=='tone_1':
                tone_fd[(self.nfft_tx >> 1) + sc] = 1
            elif sig_mode=='tone_2':
                tone_fd[(self.nfft_tx >> 1) + sc] = 1
                tone_fd[(self.nfft_tx >> 1) - sc] = 1
            tone_fd = fftshift(tone_fd, axes=0)

            # Convert the waveform to time-domain
            tone_td = np.fft.ifft(tone_fd, axis=0)

        # Normalize the signal
        tone_td /= np.max([np.abs(tone_td.real), np.abs(tone_td.imag)])

        self.print("Tone generation done", thr=2)

        return tone_td

    def generate_wideband(self, bw=200e6, modulation='qam', sig_mode='wideband', gen_mode='fft'):

        if gen_mode == 'fft':
            sc_min = int(np.round(-(bw/2)*self.nfft_tx/self.dac_fs))
            sc_max = int(np.round((bw/2)*self.nfft_tx/self.dac_fs))
            np.random.seed(self.seed)
            if modulation=='qam':
                sym = (1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j)  # QAM symbols
            else:
                sym = ()
                # raise ValueError('Invalid signal modulation: ' + modulation)

            # Create the wideband sequence in frequency-domain
            wb_fd = np.zeros((self.nfft_tx,), dtype='complex')
            if modulation == 'qam':
                wb_fd[((self.nfft_tx >> 1) + sc_min):((self.nfft_tx >> 1) + sc_max)] = np.random.choice(sym, len(range(sc_min, sc_max)))
            else:
                wb_fd[((self.nfft_tx >> 1) + sc_min):((self.nfft_tx >> 1) + sc_max)] = 1
            if sig_mode=='wideband_null':
                wb_fd[((self.nfft_tx >> 1) - self.wb_null_sc):((self.nfft_tx >> 1) + self.wb_null_sc)] = 0

            wb_fd = fftshift(wb_fd, axes=0)
            # Convert the waveform to time-domain
            wb_td = ifft(wb_fd, axis=0)

        elif gen_mode == 'ZadoffChu':
            cf = self.nfft_tx % 2
            q = 0.5
            u = 3
            wb_fd = np.exp(-1j * np.pi * u * np.arange(self.nfft_tx) * (np.arange(self.nfft_tx) + cf + 2*q) / self.nfft_tx)
            # cf = 0
            # q = 0
            # u = 3
            # wb_fd = np.exp(2j * np.pi * u * np.arange(self.nfft_tx) * (np.arange(self.nfft_tx) + cf + 2*q) / self.nfft_tx)
            wb_td = ifft(wb_fd, axis=0)

        elif gen_mode == 'ofdm':
            # N_blocks = 1000
            N_cp = 256
            N_fft = 768
            M = 16
            n_vec = np.arange(N_fft)
            x = np.exp(1j * np.pi * n_vec ** 2 / N_fft)
            x_cp = np.concatenate((x[-N_cp:], x))
            wb_td = x_cp
            # wb_td = np.tile(x_cp, N_blocks)

        # Normalize the signal
        wb_td /= np.max([np.abs(wb_td.real), np.abs(wb_td.imag)])

        self.print("Wide-band signal generation done", thr=2)

        return wb_td
        

    def gen_tx_signal(self):
        if 'tone' in self.sig_mode:
            txtd_base = self.generate_tone(f=self.f_tone, sig_mode=self.sig_mode, gen_mode=self.sig_gen_mode)
        elif 'wideband' in self.sig_mode:
            txtd_base = self.generate_wideband(bw=self.wb_bw, modulation=self.sig_modulation, sig_mode=self.sig_mode, gen_mode=self.sig_gen_mode)
        elif self.sig_mode == 'load':
            txtd_base = np.load(self.sig_path)
        else:
            raise ValueError('Unsupported signal mode: ' + self.sig_mode)
        txtd_base /= np.max([np.abs(txtd_base.real), np.abs(txtd_base.imag)])

        title = 'TX signal spectrum in base-band'
        xlabel = 'Frequency (MHz)'
        ylabel = 'Magnitude (dB)'
        self.plot_signal(x=self.freq_tx, sigs=txtd_base, mode='fft', scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)
        title = 'Base-band TX signal in time domain at the time transition'
        xlabel = 'Time (s)'
        ylabel = 'Magnitude'
        n=int(np.round(self.dac_fs/self.f_max))
        t=self.t_tx[:2*n]
        sig=np.concatenate((txtd_base.real[-n:], txtd_base.real[:n]))
        self.plot_signal(x=t, sigs=sig, mode='time', scale='linear', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)

        if self.mixer_mode=='digital' and self.mix_freq!=0:
            txtd = self.freq_shift(txtd_base, shift=self.mix_freq, fs=self.dac_fs)

            # txfd = np.abs(fftshift(fft(txtd)))
            title = 'TX signal spectrum after upconversion'
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            self.plot_signal(x=self.freq_tx, sigs=txtd, mode='fft', scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)
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
        """
        Calculate the delay of signal 1 with respect to signal 2 (signal 1 is ahead of signal 2)

        Args:
            sig_1 (np.array): First signal.
            sig_2 (np.array): Second signal.
            plot_corr (bool): Whether to plot the cross-correlation or not.

        Returns:
            delay (int): The delay of signal 1 with respect to signal 2 in samples.
        """
        cross_corr = np.correlate(sig_1, sig_2, mode='full')
        # cross_corr = np.correlate(sig_1, sig_2, mode='same')
        lags = np.arange(-len(sig_2) + 1, len(sig_1))

        if plot_corr:
            plt.figure()
            plt.plot(lags, np.abs(cross_corr), linewidth=1.0)
            plt.title('Cross-Correlation of the two signals')
            plt.xlabel('Lags')
            plt.ylabel('Correlation Coefficient')
            # plt.show()

        max_idx = np.argmax(np.abs(cross_corr))
        delay = int(lags[max_idx])
        # self.print(f'Time delay between the two signals: {delay} samples',4)
        return delay


    def time_adjust(self, sig_1, sig_2, delay):
        """
        Adjust the time of sig_1 with respect to sig_2 based on the given delay.

        Args:
            sig_1 (np.array): First signal.
            sig_2 (np.array): Second signal.
            delay (int): The delay of sig_1 with respect to sig_2 in samples.

        Returns:
            sig_1_adj (np.array): Adjusted sig_1.
            sig_2_adj (np.array): Adjusted sig_2.
            mse (float): Mean squared error between adjusted signals.
            err2sig_ratio (float): Ratio of MSE to mean squared value of sig_2.
        """
        n_points = np.shape(sig_1)[0]

        if delay >= 0:
            sig_1_adj = np.concatenate((sig_1[delay:], np.zeros(delay).astype(complex)))
            sig_2_adj = sig_2.copy()
        else:
            delay = abs(delay)
            sig_1_adj = sig_1.copy()
            sig_2_adj = np.concatenate((sig_2[delay:], np.zeros(delay).astype(complex)))

        mse = float(np.mean(np.abs(sig_1_adj[:n_points-delay] - sig_2_adj[:n_points-delay]) ** 2))
        err2sig_ratio = float(mse / np.mean(np.abs(sig_2) ** 2))

        return sig_1_adj, sig_2_adj, mse, err2sig_ratio


    def filter(self, sig, center_freq=0, cutoff=50e6, fil_order=1000, plot=False):

        filter_fir = firwin(fil_order, cutoff / self.adc_fs)
        filter_fir = self.freq_shift(filter_fir, shift=center_freq)

        if plot:
            plt.figure()
            w, h = freqz(filter_fir, worN=self.om_rx)
            plt.plot(w / np.pi, 20 * np.log10(np.abs(h)), linewidth=1.0)
            plt.title('Frequency response of the filter')
            plt.xlabel(r'Normalized Frequency ($\times \pi$ rad/sample)')
            plt.ylabel('Magnitude (dB)')
            plt.show()

        sig_fil = lfilter(filter_fir, 1, sig)

        return sig_fil


    def freq_shift(self, sig, shift=0, fs=200e6):

        t = np.arange(0, len(sig)) / fs
        sig_shift = np.exp(2 * np.pi * 1j * shift * t) * sig

        return sig_shift


    def channel_estimate(self, txtd, rxtd):
        n_samples = min(len(txtd), len(rxtd))
        t = self.t_rx if self.n_samples_rx<self.n_samples_tx else self.t_tx
        freq = self.freq_rx if self.nfft_rx<self.nfft_tx else self.freq_tx
        txtd=txtd[:n_samples]
        rxtd=rxtd[:n_samples]
        
        txfd = fft(txtd)
        rxfd = fft(rxtd)
        # rxfd = np.roll(rxfd, 1)
        # txfd = np.roll(txfd, 1)

        tol = 1e-8
        txmean = np.mean(np.abs(txfd)**2)
        H_est = rxfd * np.conj(txfd) / ((np.abs(txfd)**2) + tol*txmean)
        # H_est = rxfd * np.conj(txfd)
        # H_est = rxfd / txfd

        h_est = ifft(H_est)
        im = np.argmax(h_est)
        h_est = np.roll(h_est, -im + len(h_est)//50)
        h_est = h_est.flatten()

        sig = np.abs(h_est) / np.max(np.abs(h_est))
        title = 'Channel response in the time domain'
        xlabel = 'Time (s)'
        ylabel = 'Normalized Magnitude (dB)'
        self.plot_signal(t, sig, scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=3)

        sig = np.abs(fftshift(H_est))
        title = 'Channel response in the frequency domain'
        xlabel = 'Frequency (MHz)'
        ylabel = 'Magnitude (dB)'
        self.plot_signal(freq, sig, scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=3)

        return h_est


    def channel_estimate_eq(self, txtd, rxtd):
        txfd = fft(txtd)
        rxfd = fft(rxtd)

        # Signal parameters
        N_cp = 256
        N_fft = 768
        M = 16
        x = txtd[N_cp:]
        X = fft(x)

        plt.figure(1)
        plt.subplot(3, 1, 1)

        # Time synchronization
        data_sync = rxtd[:4 * N_fft - 1]
        rx = convolve(np.conj(x), data_sync, mode='full')
        plt.plot(np.abs(rx))
        index_ini = np.argmax(rx)

        # Retrieve time-synced signal
        N_vec = (np.tile(np.arange(N_fft), M) + np.repeat(np.arange(M), N_fft) * (N_fft + N_cp) + N_cp + 1)
        Y = rxtd[N_vec + index_ini - 3].reshape((M, N_fft)).T

        # Equalized frequency
        H_hat = fft(Y, axis=0) / X[:,None]
        # Averaged frequency
        H_hat_avg = np.mean(H_hat, axis=1)

        # Equalized time
        h_hat = ifft(H_hat, axis=0)
        h_hat = h_hat[:N_cp, :]

        # Averaged time
        h_hat_avg = np.mean(h_hat, axis=1)

        # Plots
        plt.subplot(3, 1, 2)
        plt.plot(np.abs(h_hat_avg))

        plt.subplot(3, 1, 3)
        plt.plot(fftshift(10 * np.log10(np.abs(H_hat_avg) ** 2)))
        plt.axis([1, N_fft, -100, 0])

        H_dd = fft(h_hat.T, axis=0).T / np.sqrt(N_fft * M)
        H_dd_log = 10 * np.log10(np.abs(H_dd) ** 2)
        H_dd_log[H_dd_log < -130] = -130

        plt.figure(2)
        plt.pcolor(H_dd_log)
        plt.colorbar()
        plt.show()


    # plot_signal(self, x, sig, mode='time_IQ', scale='linear', title='Custom Title', xlabel='Time', ylabel='Amplitude', plot_args={'color': 'red', 'linestyle': '--'}, xlim=(0, 10), ylim=(-1, 1), legend=True)
    def plot_signal(self, x, sigs, mode='time', scale='dB10', plot_level=0, **kwargs):

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
            
            if scale=='dB10':
                sig_plot = self.lin_to_db(sig_plot, mode='pow')
            if scale=='dB20':
                sig_plot = self.lin_to_db(sig_plot, mode='mag')
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
        plt.grid(0.2)

        legend = kwargs.get('legend', False)
        if legend:
            plt.legend()

        plt.autoscale()
        if 'xlim' in kwargs:
            plt.xlim(kwargs['xlim'])
        if 'ylim' in kwargs:
            ylim=kwargs['ylim']
            if scale=='dB10':
                ylim = (self.lin_to_db(ylim[0], mode='pow'), self.lin_to_db(ylim[1], mode='pow'))
            if scale=='dB20':
                ylim = (self.lin_to_db(ylim[0], mode='mag'), self.lin_to_db(ylim[1], mode='mag'))
            plt.ylim(ylim)
        plt.tight_layout()

        # plt.axvline(x=30e6, color='g', linestyle='--', linewidth=1)

        plt.show()


    def animate_plot(self, client_inst, txtd_base, plot_level=0):
        if self.plot_level<plot_level:
            return
        
        def receive_data():
            rxtd = client_inst.receive_data(mode='once').flatten()
            (rxtd_base, h_est) = self.rx_operations(txtd_base, rxtd)
            rxtd_base = rxtd_base[:self.n_samples]
            rxfd_base = np.abs(fftshift(fft(rxtd_base)))
            H_est = np.abs(fftshift(fft(h_est)))
            sigs=[]
            sigs.append(self.lin_to_db(np.abs(h_est) / np.max(np.abs(h_est)), mode='mag'))
            sigs.append(self.lin_to_db(H_est, mode='mag'))
            # sigs.append(rxtd_base)
            sigs.append(self.lin_to_db(rxfd_base, mode='mag'))

            return (sigs)

        def update(frame):
            sigs = receive_data()
            line1.set_ydata(sigs[0])
            ax1.relim()
            ax1.autoscale_view()
            line2.set_ydata(sigs[1])
            # line3.set_ydata(sigs[1].imag)
            # line2.set_ydata(sigs[1].imag)
            ax2.relim()
            ax2.autoscale_view()
            line4.set_ydata(sigs[2])
            ax3.relim()
            ax3.autoscale_view()

            return line1, line2, line4
            # return line1, line2, line3, line4

        # Set up the figure and plot
        sigs = receive_data()
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
        # fig, (ax1, ax2, ax3) = plt.subplots(1, 3)

        line1, = ax1.plot(self.t, sigs[0])
        ax1.set_title("Channel response in the time domain")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Normalized Magnitude (dB)")
        ax1.autoscale()
        # ax1.set_xlim(np.min(self.t), np.max(self.t))
        # ax1.set_ylim(np.min(sigs[0]), 1.5*np.max(sigs[0]))
        ax1.minorticks_on()
        # ax1.grid(0.2)

        line2, = ax2.plot(self.freq, sigs[1])
        ax2.set_title("Channel response in the frequency domain")
        ax2.set_xlabel("Frequency (MHz)")
        ax2.set_ylabel("Magnitude (dB)")
        # line2, = ax2.plot(self.t, sigs[1].real, label='I')
        # line3, = ax2.plot(self.t, sigs[1].imag, label='Q')
        # ax2.set_title("RX signal in time domain (I and Q)")
        # ax2.set_xlabel("Time (s)")
        # ax2.set_ylabel("Magnitude")
        ax2.legend()
        ax2.autoscale()
        ax2.minorticks_on()

        line4, = ax3.plot(self.freq, sigs[2])
        ax3.set_title("RX signal spectrum")
        ax3.set_xlabel("Freq (MHz)")
        ax3.set_ylabel("Magnitude (dB)")
        ax3.autoscale()
        ax3.minorticks_on()

        # Create the animation
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.4, wspace=0.4)
        anim = animation.FuncAnimation(fig, update, frames=900*2, interval=500, blit=True)
        plt.show()


    def rx_operations(self, txtd_base, rxtd):
        title = 'RX signal spectrum'
        xlabel = 'Frequency (MHz)'
        ylabel = 'Magnitude (dB)'
        self.plot_signal(x=self.freq_rx, sigs=rxtd, mode='fft', scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)

        title = 'RX signal in time domain (zoomed)'
        xlabel = 'Time (s)'
        ylabel = 'Magnitude'
        # xlim=(0, 10/(self.filter_bw/2))
        n = 4*int(np.round(self.adc_fs/self.f_max))
        self.plot_signal(x=self.t_rx[:n], sigs=rxtd[:n], mode='time_IQ', scale='linear', title=title, xlabel=xlabel, ylabel=ylabel, legend=True, plot_level=5)


        if self.mixer_mode == 'digital' and self.mix_freq!=0:    
            rxtd_base = self.freq_shift(rxtd, shift=-1*self.mix_freq, fs=self.adc_fs)
            title = 'RX signal spectrum after downconversion'
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            self.plot_signal(x=self.freq_rx, sigs=rxfd_base, scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)
        else:
            rxtd_base = rxtd.copy()

        if self.filter_signal:
            rxtd_base = self.filter(rxtd_base, cutoff=self.filter_bw)
            title = 'RX signal spectrum after filtering in base-band'
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            self.plot_signal(x=self.freq_rx, sigs=rxfd_base, scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)

        h_est = self.channel_estimate(txtd_base, rxtd_base)
        # h_est = self.channel_estimate_eq(txtd_base, rxtd_base)

        # n_samples = min(len(txtd_base), len(rxtd_base))
        txfd_base = np.abs(fftshift(fft(txtd_base[:self.n_samples])))
        rxfd_base = np.abs(fftshift(fft(rxtd_base[:self.n_samples])))

        title = 'TX and RX signals spectrum in base-band'
        xlabel = 'Frequency (MHz)'
        ylabel = 'Magnitude (dB)'
        scale = np.max(txfd_base)/np.max(rxfd_base)
        self.print("TX to RX spectrum scale: {:0.3f}".format(scale), thr=5)
        xlim=(-2*self.f_max/1e6, 2*self.f_max/1e6)
        f1=np.abs(self.freq - xlim[0]).argmin()
        f2=np.abs(self.freq - xlim[1]).argmin()
        ylim=(np.min(rxfd_base[f1:f2]*scale), 1.1*np.max(rxfd_base[f1:f2]*scale))
        self.plot_signal(x=self.freq, sigs={"txfd_base":txfd_base, "Scaled rxfd_base":rxfd_base*scale}, scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, xlim=xlim, ylim=ylim, legend=True, plot_level=5)
        self.print("txfd_base max freq: {} MHz".format(self.freq[(self.nfft>>1)+np.argmax(txfd_base[self.nfft>>1:])]), thr=5)
        self.print("rxfd_base max freq: {} MHz".format(self.freq[(self.nfft>>1)+np.argmax(rxfd_base[self.nfft>>1:])]), thr=5)

        return (rxtd_base, h_est)

