from backend import *
from backend import be_np as np, be_scp as scipy
from general import General





class Signal_Utils(General):
    def __init__(self, params):
        super().__init__(params)
        
        self.fc=getattr(params, 'fc', None)
        self.fs=getattr(params, 'fs', None)
        self.fs_tx=getattr(params, 'fs_tx', self.fs)
        self.fs_rx=getattr(params, 'fs_rx', self.fs)
        self.fs_trx=getattr(params, 'fs_trx', min(self.fs_tx, self.fs_rx))
        self.n_samples=getattr(params, 'n_samples', None)
        self.n_samples_tx=getattr(params, 'n_samples_tx', self.n_samples)
        self.n_samples_rx=getattr(params, 'n_samples_rx', self.n_samples)
        self.n_samples_trx=getattr(params, 'n_samples_trx', min(self.n_samples_tx, self.n_samples_rx))
        self.sc_range_ch = getattr(params, 'sc_range_ch', [-1*self.n_samples_trx//2, self.n_samples_trx//2-1])
        self.n_samples_ch=getattr(params, 'n_samples_ch', self.sc_range_ch[1] - self.sc_range_ch[0] + 1)
        self.nfft = getattr(params, 'nfft', 2 ** np.ceil(np.log2(self.n_samples)).astype(int))
        self.nfft_tx = getattr(params, 'nfft_tx', self.nfft)
        self.nfft_rx = getattr(params, 'nfft_rx', self.nfft)
        self.nfft_trx = getattr(params, 'nfft_trx', min(self.nfft_tx, self.nfft_rx))
        self.nfft_ch = getattr(params, 'nfft_ch', self.n_samples_ch)
        self.snr=getattr(params, 'snr', None)
        self.sig_noise=getattr(params, 'sig_noise', None)
        self.sig_sel_id=getattr(params, 'sig_sel_id', None)
        self.rx_sel_id=getattr(params, 'rx_sel_id', None)
        self.N_r=getattr(params, 'N_r', None)
        self.N_sig=getattr(params, 'N_sig', None)
        self.rand_params=getattr(params, 'rand_params', None)
        self.cf_range=getattr(params, 'cf_range', None)
        self.psd_range=getattr(params, 'psd_range', None)
        self.bw_range=getattr(params, 'bw_range', None)
        self.spat_sig_range=getattr(params, 'spat_sig_range', None)
        self.az_range=getattr(params, 'az_range', None)
        self.el_range=getattr(params, 'el_range', None)
        self.aoa_mode=getattr(params, 'aoa_mode', None)
        self.ant_dim=getattr(params, 'ant_dim', None)
        self.ant_dy=getattr(params, 'ant_dy', None)
        self.ant_dx=getattr(params, 'ant_dx', None)
        self.wl=getattr(params, 'wl', None)
        self.steer_phi_rad=getattr(params, 'steer_phi_rad', None)
        self.steer_theta_rad=getattr(params, 'steer_theta_rad', None)

        self.n_sigs_max = getattr(params, 'n_sigs_max', None)
        self.size_sam_mode = getattr(params, 'size_sam_mode', None)
        self.snr_sam_mode = getattr(params, 'snr_sam_mode', None)
        self.noise_power = getattr(params, 'noise_power', None)
        self.mask_mode = getattr(params, 'mask_mode', None)
        self.eval_smooth = getattr(params, 'eval_smooth', None)
        self.seed = getattr(params, 'seed', None)

        self.t = getattr(params, 't', np.arange(0, self.n_samples) / self.fs)
        self.t_tx = getattr(params, 't_tx', np.arange(0, self.n_samples_tx) / self.fs_tx)
        self.t_rx = getattr(params, 't_rx', np.arange(0, self.n_samples_rx) / self.fs_rx)
        self.t_trx = getattr(params, 't_trx', np.arange(0, self.n_samples_trx) / self.fs_trx)
        self.t_ch = getattr(params, 't_ch', np.arange(0, self.n_samples_ch) / self.fs_trx)
        self.freq = getattr(params, 'freq', np.linspace(-0.5, 0.5, self.nfft, endpoint=True) * self.fs)
        self.freq_tx = getattr(params, 'freq_tx', np.linspace(-0.5, 0.5, self.nfft_tx, endpoint=True) * self.fs_tx)
        self.freq_rx = getattr(params, 'freq_rx', np.linspace(-0.5, 0.5, self.nfft_rx, endpoint=True) * self.fs_rx)
        self.freq_trx = getattr(params, 'freq_trx', np.linspace(-0.5, 0.5, self.nfft_trx, endpoint=True) * self.fs_trx)
        self.freq_ch = getattr(params, 'freq_ch', self.freq_trx[(self.sc_range_ch[0]+self.nfft_trx//2):(self.sc_range_ch[1]+self.nfft_trx//2+1)])
        self.om = getattr(params, 'om', np.linspace(-np.pi, np.pi, self.nfft, endpoint=True))
        self.om_tx = getattr(params, 'om_tx', np.linspace(-np.pi, np.pi, self.nfft_tx, endpoint=True))
        self.om_rx = getattr(params, 'om_rx', np.linspace(-np.pi, np.pi, self.nfft_rx, endpoint=True))
        self.om_trx = getattr(params, 'om_trx', np.linspace(-np.pi, np.pi, self.nfft_trx, endpoint=True))
        self.om_ch = getattr(params, 'om_ch', self.om_trx[(self.sc_range_ch[0]+self.nfft_trx//2):(self.sc_range_ch[1]+self.nfft_trx//2+1)])


    def lin_to_db(self, x, mode='pow'):
        if mode=='pow':
            return 10*np.log10(x)
        elif mode=='mag':
            return 20*np.log10(x)

    def db_to_lin(self, x, mode='pow'):
        if mode == 'pow':
            return 10**(x/10)
        elif mode == 'mag':
            return 10**(x/20)
        

    def aoa_to_phase(self, aoa, wl=0.01, ant_dim=1, ant_dx_m=0, ant_dy_m=0):
        if ant_dim == 1:
            phase = 2 * np.pi * ant_dx_m / wl * np.sin(aoa)
        elif ant_dim == 2:
            phase = 2 * np.pi * ant_dx_m / wl * np.sin(aoa[0]) + 2 * np.pi * ant_dy_m / wl * np.sin(aoa[1])
        return phase
    

    def phase_to_aoa(self, phase, wl=0.01, ant_dim=1, ant_dx_m=0, ant_dy_m=0):
        if ant_dim == 1:
            aoa = np.arcsin(phase * wl / (2 * np.pi * ant_dx_m))
        elif ant_dim == 2:
            aoa = np.array([np.arcsin(phase * wl / (2 * np.pi * ant_dx_m)), np.arcsin(phase * wl / (2 * np.pi * ant_dy_m))])
        return aoa
        

    def upsample(self, signal, up=2):
        """
        Upsample a signal by a factor of 2 by inserting zeros between the original samples.

        Args:
            signal (np.array): Input signal to be upsampled.

        Returns:
            np.array: Upsampled signal with zeros inserted.
        """
        upsampled_len = up * len(signal)
        upsampled_sig = np.zeros(upsampled_len, dtype=complex)

        # Assign the original signal values to the even indices
        upsampled_sig[::up] = signal.copy()

        return upsampled_sig


    def cross_correlation(self, sig_1, sig_2, index):
        if index >= 0:
            padded_sig_2 = np.concatenate((np.zeros(index, dtype=complex), sig_2[:len(sig_2) - index]))
        else:
            padded_sig_2 = np.concatenate((sig_2[-index:], np.zeros(-index, dtype=complex)))

        cros_corr = np.mean(sig_1 * np.conj(padded_sig_2))
        return cros_corr
    

    def integrate_signal(self, signal, n_samples=1024):
        n_ant = signal.shape[0]
        signal = signal.reshape(n_ant, -1, n_samples)
        signal = np.mean(signal, axis=1)

        return signal


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
    

    def extract_frac_delay(self, sig_1, sig_2, sc_range=[0, 0]):
    
        # corr = np.correlate(sig_1, sig_2, mode='full')
        # max_corr_index = np.argmax(np.abs(corr))
        # # delay_samples = max_corr_index - len(sig_2) + 1
        
        # y0 = np.abs(corr[max_corr_index - 1])
        # y1 = np.abs(corr[max_corr_index])
        # y2 = np.abs(corr[max_corr_index + 1])
        
        # frac_delay = 0.5 * (y0 - y2) / (y0 - 2*y1 + y2)



        # # Upsample the transmitted and compensated signals to estimate fractional delay
        # us_rate = 100
        # sig_1_us = resample(sig_1, len(sig_1) * us_rate)
        # sig_2_us = resample(sig_2, len(sig_2) * us_rate)

        # # Perform cross-correlation again on the upsampled signals
        # frac_delay_us = self.extract_delay(sig_1_us, sig_2_us)

        # # Convert the upsampled delay to a fractional delay
        # frac_delay = frac_delay_us / us_rate


        sig_1_f = fftshift(fft(sig_1, axis=-1))
        sig_2_f = fftshift(fft(sig_2, axis=-1))
        nfft = len(sig_1_f)

        phi = np.angle(sig_1_f * np.conj(sig_2_f))
        phi = phi[(sc_range[0]+nfft//2):(sc_range[1]+nfft//2+1)]

        # Unwrap the phase to prevent discontinuities
        phi = np.unwrap(phi)

        # Perform linear regression to find the slope of the phase difference
        p = np.polyfit(np.arange(len(phi)), phi, deg=1)
        slope = p[0]             # Slope of the fitted line
        # Estimate the fractional delay using the slope
        frac_delay = -1 * (slope / (2 * np.pi))*nfft

        return frac_delay
    

    def calc_phase_offset(self, sig_1, sig_2, sc_range=[0, 0]):
        # Return the phase offset between two signals in radians
        corr = np.correlate(sig_1, sig_2)
        max_idx = np.argmax(corr)
        phase_offest = np.angle(corr[max_idx])

        return phase_offest
    

    def adjust_phase(self, sig_1, sig_2, phase_offset):
        # Adjust the phase of sig_1 with respect to sig_2 based on the given phase offset
        sig_1_adj = sig_1 * np.exp(-1j * phase_offset)
        sig_2_adj = sig_2.copy()

        return sig_1_adj, sig_2_adj
    

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
        n_points = min(sig_1.shape[0], sig_2.shape[0])
        delay = int(delay)

        # if delay >= 0:
        #     sig_1_adj = np.concatenate((sig_1[delay:], np.zeros(delay).astype(complex)))
        #     sig_2_adj = sig_2.copy()
        # else:
        #     delay = abs(delay)
        #     sig_1_adj = sig_1.copy()
        #     sig_2_adj = np.concatenate((sig_2[delay:], np.zeros(delay).astype(complex)))
        sig_1_adj = np.roll(sig_1, -1*delay)
        sig_2_adj = sig_2.copy()

        # mse = float(np.mean(np.abs(sig_1_adj[max(-1*delay,0):n_points+min(-1*delay,0)] - sig_2_adj[max(-1*delay,0):n_points+min(-1*delay,0)]) ** 2))
        mse = float(np.mean(np.abs(sig_1_adj[:n_points] - sig_2_adj[:n_points]) ** 2))
        err2sig_ratio = float(mse / np.mean(np.abs(sig_2) ** 2))

        return sig_1_adj, sig_2_adj, mse, err2sig_ratio


    def adjust_frac_delay(self, sig_1, sig_2, frac_delay):
        sig_1 = sig_1.copy()
        sig_2 = sig_2.copy()
        n_samples = sig_1.shape[0]

        sig_1_f = fftshift(fft(sig_1, axis=-1))
        sig_2_f = fftshift(fft(sig_2, axis=-1))
        omega = np.linspace(-np.pi, np.pi, n_samples)
        sig_1_f = np.exp(1j * omega * frac_delay) * sig_1_f
        sig_1_adj = ifft(ifftshift(sig_1_f), axis=-1)


        # sig_1 = np.roll(sig_1, 1)
        # frac_delay = 1-frac_delay

        # sig_1_adj = resample(sig_1, int(n_samples * (1 + abs(frac_delay))))
        # sig_1_adj =  sig_1_adj[:n_samples]  # Return signal with original length

        # # Design FIR filter for fractional delay
        # num_taps = 64
        # h = firwin(num_taps, 0.5, window="hamming", scale=False)
        # h = np.sinc(np.arange(-num_taps // 2, num_taps // 2) - frac_delay)
        # h *= np.hamming(num_taps)  # Apply a window to the filter coefficients
        # # Apply the filter to the signal
        # sig_1_adj = lfilter(h, 1.0, sig_1)


        # sig_1_adj = sig_1.copy()
        sig_2_adj = sig_2.copy()

        return sig_1_adj, sig_2_adj
    

    def gen_spatial_sig(self, ant_dim=1, N_sig=1, N_r=1, az_range=[-np.pi, np.pi], el_range=[-np.pi/2, np.pi/2], mode='uniform'):
        if ant_dim == 1:
            if mode=='uniform':
                az = uniform(az_range[0], az_range[1], N_sig)
            elif mode=='sweep':
                az_range_t = az_range[1]-az_range[0]
                az = np.linspace(az_range[0], az_range[1]-az_range_t/N_sig, N_sig)
            spatial_sig = np.exp(
                2 * np.pi * 1j * self.ant_dx / self.wl * np.arange(N_r).reshape((N_r, 1)) * np.sin(az.reshape((1, N_sig))))
            return spatial_sig, [az]
        elif ant_dim == 2:
            spatial_sig = np.zeros((N_r, N_sig)).astype(complex)
            if mode == 'uniform':
                az = uniform(az_range[0], az_range[1], N_sig)
                el = uniform(el_range[0], el_range[1], N_sig)
            elif mode == 'sweep':
                az_range_t = az_range[1] - az_range[0]
                el_range_t = el_range[1] - el_range[0]
                az = np.linspace(az_range[0], az_range[1]-az_range_t/N_sig, N_sig)
                el = np.linspace(el_range[0], el_range[1]-el_range_t/N_sig, N_sig)
            k = 2 * np.pi / self.wl
            M = np.sqrt(N_r)
            N = np.sqrt(N_r)
            for i in range(N_sig):
                ax = np.exp(1j * k * self.ant_dx * np.arange(M) * np.sin(el[i]) * np.cos(az[i]))
                ay = np.exp(1j * k * self.ant_dy * np.arange(N) * np.sin(el[i]) * np.sin(az[i]))
                spatial_sig[:, i] = np.kron(ax, ay)
            return spatial_sig, [az,el]


    def gen_rand_params(self):
        self.print('Generating a set of random parameters.', 2)

        if self.rand_params:
            sig_bw = uniform(self.bw_range[0], self.bw_range[1], self.N_sig)
            psd_range = self.psd_range/1e3/1e6
            sig_psd = uniform(psd_range[0], psd_range[1], self.N_sig)
            sig_cf = uniform(self.cf_range[0], self.cf_range[1], self.N_sig)

            # spatial_sig = uniform(self.spat_sig_range[0], self.spat_sig_range[1], (self.N_r, self.N_sig))
            # spat_sig_mag = uniform(self.spat_sig_range[0], self.spat_sig_range[1], (self.N_r, self.N_sig))
            # spat_sig_ang = uniform(0, 2 * np.pi, (self.N_r, self.N_sig))
            # spatial_sig = spat_sig_mag * np.cos(spat_sig_ang) + 1j * spat_sig_mag * np.sin(spat_sig_ang)

            spat_sig_mag = uniform(self.spat_sig_range[0], self.spat_sig_range[1], (1, self.N_sig))
            spat_sig_mag = np.tile(spat_sig_mag, (self.N_r, 1))
            spatial_sig, aoa = self.gen_spatial_sig(ant_dim=self.ant_dim, N_sig=self.N_sig, N_r=self.N_r, az_range=self.az_range, el_range=self.el_range, mode=self.aoa_mode)
            spatial_sig = spat_sig_mag * spatial_sig

        else:
            self.N_sig = 8
            self.N_r = 4
            sig_bw = np.array([23412323.42206957, 29720830.74807138, 28854411.42943605,
                               13436699.17479161, 32625455.26622169, 32053137.51678639,
                               35113044.93237082, 21712944.94126201])
            sig_psd = np.array([1.82152663e-10+0.j, 2.18261433e-10+0.j, 2.10519428e-10+0.j,
                               1.72903294e-10+0.j, 2.25096120e-10+0.j, 1.42163622e-10+0.j,
                               1.16246992e-10+0.j, 1.26733169e-10+0.j])
            sig_cf = np.array([ 76368431.6004079 ,  10009408.65004128, -17835240.41355851,
                               -17457600.99681053, -11925292.61281498,  36570531.45445453,
                                28089213.97482219,  36680162.41373056])
            spatial_sig = np.array([[ 0.28560148+0.j        ,  0.49996994+0.j        ,
                                     0.65436809+0.j        ,  0.77916855+0.j        ,
                                     0.77740179+0.j        ,  0.72816271+0.j        ,
                                     0.70354769+0.j        ,  0.79870358+0.j        ],
                                   [ 0.28247656-0.04213306j,  0.23454661-0.44154029j,
                                     0.38195112-0.5313294j ,  0.53913962+0.56252299j,
                                     0.72772125+0.27345077j, -0.08719831-0.72292281j,
                                     0.30553255-0.63374223j,  0.73871532+0.30368912j],
                                   [ 0.21580258+0.18707605j,  0.3849812 +0.31899753j,
                                     0.65124563-0.06384924j, -0.75863413-0.17770168j,
                                     0.57519734-0.52297377j, -0.44911618-0.5731628j ,
                                     0.3280136 -0.62240375j,  0.33967472+0.72287516j],
                                   [ 0.24103957+0.1531931j ,  0.46232038-0.19034129j,
                                     0.32828468-0.56606251j, -0.39663875-0.6706574j ,
                                     0.72239466-0.28722724j, -0.51525611+0.51452121j,
                                    -0.41820151-0.56576218j,  0.0393057 +0.79773584j]])
            aoa = None

        sig_psd = sig_psd.astype(complex)
        spatial_sig = spatial_sig.astype(complex)

        self.sig_bw = sig_bw
        self.sig_psd = sig_psd
        self.sig_cf = sig_cf
        self.spatial_sig = spatial_sig
        self.aoa = aoa

        return (sig_bw, sig_psd, sig_cf, spatial_sig, aoa)


    def gen_noise(self, mode='complex'):
        if mode=='real':
            noise = randn(self.n_samples).astype(complex)           # Generate noise with PSD=1/fs W/Hz
            # noise = normal(loc=0, scale=1, size=self.n_samples).astype(complex)
        elif mode=='complex':
            noise = (randn(self.n_samples) + 1j*randn(self.n_samples)).astype(complex)           # Generate noise with PSD=2/fs W/Hz

        return noise


    def generate_signals(self, sig_bw, sig_psd, sig_cf, spatial_sig):
        self.print('Generating a set of signals and a rx signal.',2)

        rx = np.zeros((self.N_r, self.n_samples), dtype=complex)
        sigs = np.zeros((self.N_sig, self.n_samples), dtype=complex)

        for i in range(self.N_sig):
            fil_sig = firwin(1001, sig_bw[i] / self.fs)
            # sigs[i, :] = np.exp(2 * np.pi * 1j * sig_cf[i] * t) * sig_psd[i] * np.convolve(noise, fil_sig, mode='same')
            sigs[i, :] = np.exp(2 * np.pi * 1j * sig_cf[i] * self.t) * np.sqrt(
                sig_psd[i]*(self.fs/2)) * lfilter(fil_sig, np.array([1]), self.gen_noise(mode='complex'))
            rx += np.outer(spatial_sig[:, i], sigs[i, :])

            if self.sig_noise:
                yvar = np.mean(np.abs(sigs[i, :]) ** 2)
                wvar = yvar / self.snr
                sigs[i, :] += np.sqrt(wvar / 2) * self.gen_noise(mode='complex')

        yvar = np.mean(np.abs(rx) ** 2, axis=1)
        wvar = yvar / self.snr
        noise_rx = np.array([self.gen_noise(mode='complex') for _ in range(self.N_r)])
        # rx += np.sqrt(wvar[:, None] / 2) * noise
        # rx += np.outer(np.sqrt(wvar / 2), self.gen_noise(mode='complex'))
        rx += np.sqrt(wvar[:, None] / 2) * noise_rx

        if self.plot_level >= 2:
            plt.figure()
            # plt.figure(figsize=(10,6))
            # plt.tight_layout()
            plt.subplots_adjust(wspace=0.5, hspace=1.0)
            plt.subplot(3, 1, 1)
            for i in range(self.N_sig):
                spectrum = fftshift(fft(sigs[i, :]))
                spectrum = self.lin_to_db(np.abs(spectrum), mode='mag')
                plt.plot(self.freq, spectrum, color=rand(3), linewidth=0.5)
            plt.title('Frequency spectrum of initial wideband signals')
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Magnitude (dB)')

            plt.subplot(3, 1, 2)
            spectrum = fftshift(fft(rx[self.rx_sel_id, :]))
            spectrum = self.lin_to_db(np.abs(spectrum), mode='mag')
            plt.plot(self.freq, spectrum, 'b-', linewidth=0.5)
            plt.title('Frequency spectrum of RX signal in a selected antenna')
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Magnitude (dB)')

            plt.subplot(3, 1, 3)
            spectrum = fftshift(fft(sigs[self.sig_sel_id, :]))
            spectrum = self.lin_to_db(np.abs(spectrum), mode='mag')
            plt.plot(self.freq, spectrum, 'r-', linewidth=0.5)
            plt.title('Frequency spectrum of the desired wideband signal')
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Magnitude (dB)')

            plt.savefig(os.path.join(self.figs_dir, 'tx_rx_sigs.pdf'), format='pdf')
            # plt.show(block=False)

            # frequencies, psd = welch(rx[0,:], self.fs, nperseg=1024)
            # plt.figure(figsize=(10, 6))
            # plt.semilogy(frequencies, psd)
            # plt.title('Power Spectral Density (PSD) of Signal')
            # plt.xlabel('Frequency (Hz)')
            # plt.ylabel(r'PSD ($V^2$/Hz)')
            # plt.grid(True)
            # plt.show()
            # raise InterruptedError("Plot interrupt")

        return (rx, sigs)


    def generate_random_regions(self, shape=(1000,), n_regions=1, min_size=None, max_size=None, size_sam_mode='log'):
        regions = []
        ndims = len(shape)
        for _ in range(n_regions):
            region_slices = []
            for d, dim in enumerate(shape):
                if min_size is not None and max_size is not None:
                    s1 = min_size[d]
                    s2 = max_size[d] + 1
                else:
                    s1 = 1
                    s2 = min(101, (dim+1)//2+1)
                if size_sam_mode=='lin':
                    size = randint(s1, s2)
                elif size_sam_mode=='log':
                    margin=1e-9
                    size = uniform(np.log10(s1), np.log10(s2-margin))
                    size = int(10 ** size)
                start = randint(0, dim-size+1)
                size = min(size, dim-start)
                region_slices.append(slice(start, start + size))
            regions.append(tuple(region_slices))

        return regions


    def generate_random_PSD(self, shape=(1000,), sig_regions=None, n_sigs=1, n_sigs_max=1, sig_size_min=None, sig_size_max=None, noise_power=1, snr_range=np.array([10,10]), size_sam_mode='log', snr_sam_mode='log', mask_mode='binary'):

        sig_power_range = noise_power * snr_range.astype(float)
        psd = exponential(noise_power, shape)
        if mask_mode=='binary' or mask_mode=='snr':
            mask = np.zeros(shape, dtype=float)
        elif mask_mode=='channels':
            mask = np.zeros((n_sigs_max,)+shape, dtype=float)

        if sig_regions is None:
            regions = self.generate_random_regions(shape=shape, n_regions=n_sigs, min_size=sig_size_min, max_size=sig_size_max, size_sam_mode=size_sam_mode)
        else:
            regions = sig_regions

        for sig_id, region in enumerate(regions):
            if snr_sam_mode=='lin':
                # sig_power = choice(sig_powers)
                sig_power = uniform(sig_power_range[0], sig_power_range[1])
            elif snr_sam_mode=='log':
                sig_power = uniform(np.log10(sig_power_range[0]), np.log10(sig_power_range[1]))
                sig_power = 10**sig_power
            region_shape = tuple(slice_.stop - slice_.start for slice_ in region)
            region_power = exponential(sig_power, region_shape)
            psd[region] += region_power
            if mask_mode=='binary':
                mask[region] = 1.0
            elif mask_mode=='snr':
                mask[region] += sig_power/noise_power
            elif mask_mode=='channels':
                region_m=(slice(sig_id, sig_id+1),)+region
                mask[region_m] = 1.0
    
        return (psd, mask)
    

    def slice_size(self, slice=None):
        if slice is None:
            size = 0
        else:
            size = 1
            for s in slice:
                size *= (s.stop - s.start)
        return size


    def slice_intersection(self, slice_1, slice_2):
        intersect = []
        if slice_1 is None or slice_2 is None:
            return None
        for s1, s2 in zip(slice_1, slice_2):
            start = max(s1.start, s2.start)
            stop = min(s1.stop, s2.stop)
            if start < stop:
                intersect.append(slice(start, stop))
            else:
                # If the slices do not intersect
                return None
        return tuple(intersect)
    

    def slice_union(self, slice_1, slice_2):
        union = []
        if slice_1 is None:
            return slice_2
        elif slice_2 is None:
            return slice_1
        for s1, s2 in zip(slice_1, slice_2):
            start = min(s1.start, s2.start)
            stop = max(s1.stop, s2.stop)
            if start < stop:
                union.append(slice(start, stop))
            else:
                # If the slices do not intersect
                return None
        return tuple(union)


    def compute_slices_similarity(self, slice_1, slice_2):
        if slice_1 is None and slice_2 is not None:
            ratio = 0.0
        if slice_2 is None and slice_1 is not None:
            ratio = 0.0
        if slice_1 is None and slice_2 is None:
            ratio = 1.0
        else:
            intersection = self.slice_intersection(slice_1, slice_2)
            union = self.slice_union(slice_1, slice_2)
            intersection_size = self.slice_size(intersection)
            union_size = self.slice_size(union)

            # max_size = max(self.slice_size(slice_1), self.slice_size(slice_2))
            # ratio = intersection_size / max_size
            ratio = intersection_size / union_size

        return ratio
    

    def generate_psd_dataset(self, dataset_path='./data/psd_dataset.npz', n_dataset=1000, shape=(1000,), n_sigs_min=1, n_sigs_max=1, n_sigs_p_dist=None, sig_size_min=None, sig_size_max=None, snr_range=np.array([10,10]), mask_mode='binary'): 
        print("Starting to generate PSD dataset with n_dataset={}, shape={}, n_sigs={}-{}, n_sigs_p_dist:{}, sig_size={}-{}, snrs={:0.3f}-{:0.3f}...".format(n_dataset, shape, n_sigs_min, n_sigs_max, n_sigs_p_dist, sig_size_min, sig_size_max, snr_range[0], snr_range[1]))
        
        n_sigs_list = np.arange(n_sigs_min, n_sigs_max+1)
        data = []
        masks = []
        bboxes = []
        objectnesses = []
        classes = []
        for _ in range(n_dataset):
            n_sigs = np.random.choice(n_sigs_list, p=n_sigs_p_dist)
            # n_sigs = randint(n_sigs_min, n_sigs_max+1)
            regions = self.generate_random_regions(shape=shape, n_regions=n_sigs, min_size=sig_size_min, max_size=sig_size_max, size_sam_mode=self.size_sam_mode)
            (psd, mask) = self.generate_random_PSD(shape=shape, sig_regions=regions, n_sigs=n_sigs, n_sigs_max=n_sigs_max, sig_size_min=sig_size_min, sig_size_max=sig_size_max, noise_power=self.noise_power, snr_range=snr_range, size_sam_mode=self.size_sam_mode, snr_sam_mode=self.snr_sam_mode, mask_mode=mask_mode)
            data.append(psd)
            masks.append(mask)
            bbox = np.zeros((n_sigs_max, 2*len(shape)), dtype=float)
            for i, region in enumerate(regions):
                bbox[i] = np.array([slice_.start for slice_ in region] + [slice_.stop-slice_.start for slice_ in region])
            bbox = bbox.flatten()
            bboxes.append(bbox)
            objectness = np.array([1.0]*n_sigs + [0.0]*(n_sigs_max-n_sigs), dtype=float)
            objectnesses.append(objectness)
            class_ = np.array([0.0]*n_sigs_max, dtype=float)
            classes.append(class_)
        data = np.array(data)
        masks = np.array(masks)
        bboxes = np.array(bboxes)
        objectnesses = np.array(objectnesses)
        classes = np.array(classes)
        np.savez(dataset_path, data=data, masks=masks, bboxes=bboxes, objectnesses=objectnesses, classes=classes)
        
        print(f"Dataset of data shape {data.shape} and mask shape {masks.shape} saved to {dataset_path}")


    def generate_tone(self, freq_mode='sc', sc=None, f=None, sig_mode='tone_2', gen_mode='fft'):
        if freq_mode=='sc':
            f = sc*self.fs_tx/self.nfft_tx
        elif freq_mode=='freq':
            sc = int(np.round((f)*self.nfft_tx/self.fs_tx))
        else:
            raise ValueError('Invalid frequency mode: ' + freq_mode)

        if gen_mode == 'time':
            wt = np.multiply(2 * np.pi * f, self.t_tx)
            if sig_mode=='tone_1':
                tone_td = np.cos(wt) + 1j * np.sin(wt)
            elif sig_mode=='tone_2':
                # tone_td = np.cos(wt) + 1j * np.cos(wt)
                tone_td = np.cos(wt)

        elif gen_mode == 'fft':
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


    def generate_wideband(self, bw_mode='sc', sc_range=None, bw_range=None, wb_null_sc=0, modulation='4qam', sig_mode='wideband', gen_mode='fft', seed=100):
        if bw_mode=='sc':
            bw_range = [sc_range[0]*self.fs_tx/self.nfft_tx, sc_range[1]*self.fs_tx/self.nfft_tx]
        elif bw_mode=='freq':
            sc_range = [int(np.round(bw_range[0]*self.nfft_tx/self.fs_tx)), int(np.round(bw_range[1]*self.nfft_tx/self.fs_tx))]

        np.random.seed(seed)
        if gen_mode == 'fft':
            if modulation=='psk':
                sym = [1, -1]
            elif modulation=='4qam':
                sym = [I + 1j*Q for I in [-1, 1] for Q in [-1, 1]]
            elif modulation=='16qam':
                sym = [I + 1j*Q for I in [-3, -1, 1, 3] for Q in [-3, -1, 1, 3]]
            elif modulation=='64qam':
                sym = [I + 1j*Q for I in [-7, -5, -3, -1, 1, 3, 5, 7] for Q in [-7, -5, -3, -1, 1, 3, 5, 7]]
            else:
                sym = []
                # raise ValueError('Invalid signal modulation: ' + modulation)

            # Create the wideband sequence in frequency-domain
            wb_fd = np.zeros((self.nfft_tx,), dtype='complex')
            if len(sym)>0:
                wb_fd[((self.nfft_tx >> 1) + sc_range[0]):((self.nfft_tx >> 1) + sc_range[1] + 1)] = np.random.choice(sym, len(range(sc_range[0], sc_range[1]+1)))
            else:
                wb_fd[((self.nfft_tx >> 1) + sc_range[0]):((self.nfft_tx >> 1) + sc_range[1] + 1)] = 1
            if sig_mode=='wideband_null':
                wb_fd[((self.nfft_tx >> 1) - wb_null_sc):((self.nfft_tx >> 1) + wb_null_sc + 1)] = 0

            wb_fd = fftshift(wb_fd, axes=0)
            # Convert the waveform to time-domain
            wb_td = ifft(wb_fd, axis=0)

        elif gen_mode == 'ZadoffChu':
            prime_nums = [3, 5, 7, 11, 13, 17]
            cf = self.nfft_tx % 2
            q = 0.5
            # u = 3
            u = np.random.choice(prime_nums)
            print(f"u={u}")
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
    

    def create_mesh_grid(self, npoints = 1000, xlim = [1,1]):
        # Create a set of points x uniformly distributed in the area using meshgrid
        x1 = np.linspace(0, xlim[0], npoints)
        x2 = np.linspace(0, xlim[1], npoints)
        X1, X2 = np.meshgrid(x1, x2)
        X = np.zeros((npoints**2,2))
        X[:,0] = X1.flatten()
        X[:,1] = X2.flatten()


    def multi_arr_corr(x, arr, r, lam):
        """
        Computes the correlation between the received signal and the expected signal
        for a batch of candidate target locations at a set of arrays

        Parameters
        ----------
        x : np.array of shape (npoints,p)
            Location of the candidate targets 
            where nx is the number of candidate targets and p is the 
            dimension of the space
        arr : np.array  of shape (m,nrx,p)
            Array locations where arr[i,j,:] is the location
            of element j in the measurement i where m is the number of 
            measurements
        r : complex np.array of size (m, nrx)
            measured values where r[i,j] is the complex measured 
            value in measurement i on element j
        lam : float
            Wavelength of the signal
            
        Returns
        -------
        rho : np.array of shape (m)
            The real values of the summed correlation at each of the measurements
        """
        
        # Compute the distances from the arrays to the target
        # (:,m,nrx,p) * (npoints,:,:,p)
        d = np.sqrt(np.sum((arr[None,:,:,:] - x[:,None,None,:])**2, axis=3))

        # Compute the phase difference
        dexp = np.exp(-2*np.pi*1j/lam*d)

        #(npoints, m, nrx)
        # Compute the correlation
        # (npoints, m)
        # (npoints)
        rho = np.sum( np.abs(np.sum(r[None,:,:]*dexp, axis=2))**2, axis=1 )

        return rho


    def feval_torch(x, arr, r, lam):
        """
        Torch version of the above function.
        Computes the correlation between the received signal and the expected signal
        for a batch of candidate target locations

        Parameters
        ----------
        x : torch.Tensor of shape (p)
            Location of the candidate targets 
            where nx is the number of candidate targets and p is the 
            dimension of the space
        arr : torch.Tensor of shape (m, nrx, p)
            Array locations where arr[i, j, :] is the location
            of element j in the measurement i where m is the number of 
            measurements
        r : torch.Tensor of size (m, nrx)
            measured values where r[i, j] is the complex measured 
            value in measurement i on element j
        lam : float
            Wavelength of the signal
            
        Returns
        -------
        rho : scalar
            The real values of the summed correlation at each of the measurements
        """

        # Compute the distances from the arrays to the target
        d = torch.sqrt(torch.sum((arr[:, :, :] - x[None, None, :]) ** 2, dim=2))

        # Compute the phase difference
        dexp = torch.exp(-2 * np.pi * 1j / lam * d)

        # Compute the correlation
        rho = torch.sum(torch.abs(torch.sum(r * dexp, dim=1)) ** 2, dim=0)

        return rho


    def beam_form(self, sigs):
        sigs_bf = sigs.copy()
        n_sigs = sigs.shape[0]
        if self.ant_dim == 1:
            n_ant = n_sigs
        elif self.ant_dim == 2:
            n_ant_x = int(np.sqrt(n_sigs))
            n_ant_y = int(np.sqrt(n_sigs))
        for i in range(n_sigs):
            if self.ant_dim == 1:
                theta = -2 * np.pi * self.ant_dx * np.sin(self.steer_phi_rad) * i
            elif self.ant_dim == 2:
                m = i // n_ant_y
                n = i % n_ant_y
                theta = -2 * np.pi * (m*self.ant_dx*np.sin(self.steer_theta_rad)*np.cos(self.steer_phi_rad) +\
                                      n*self.ant_dy*np.sin(self.steer_theta_rad)*np.sin(self.steer_phi_rad))
            print('Theta: ', theta)
            sigs_bf[i, :] = np.exp(1j * theta) * sigs[i, :]

        return sigs_bf

    
    def filter_noise_symbols(self, sig, mag_thr=1e-2):
        sig_fil = sig.copy()
        sig_fil = sig_fil[np.abs(sig_fil) > mag_thr]
        # sig_fil[np.abs(sig_fil) < mag_thr] = 0

        return sig_fil


    def filter(self, sig, center_freq=0, cutoff=50e6, fil_order=1000, plot=False):
        filter_fir = firwin(fil_order, cutoff / self.fs_rx)
        filter_fir = self.freq_shift(filter_fir, shift=center_freq, fs=self.fs_rx)

        if plot:
            plt.figure()
            w, h = freqz(filter_fir, worN=self.om_rx)
            plt.plot(w / np.pi, 20 * np.log10(np.abs(h)), linewidth=1.0)
            plt.title('Frequency response of the filter')
            plt.xlabel(r'Normalized Frequency ($\times \pi$ rad/sample)')
            plt.ylabel('Magnitude (dB)')
            plt.show()

        sig_fil = lfilter(filter_fir, 1, sig)
        # sig_fil = filtfilt(filter_fir, 1, sig)

        return sig_fil


    def freq_shift(self, sig, shift=0, fs=200e6):
        t = np.arange(0, len(sig)) / fs
        sig_shift = np.exp(2 * np.pi * 1j * shift * t) * sig

        return sig_shift

    
    def estimate_cfo(self, txtd, rxtd, mode='fine', sc_range=[0,0]):
        n_samples = min(txtd.shape[1], rxtd.shape[1])
        txtd = txtd.copy()[:,:n_samples]
        rxtd = rxtd.copy()[:,:n_samples]

        # h_est_full = h_est_full.copy()
        txfd = fft(txtd, axis=-1)
        rxfd = fft(rxtd, axis=-1)

        n_rx_ant = rxtd.shape[0]
        n_tx_ant = txtd.shape[0]

        cfo_est = np.zeros((n_rx_ant))

        for tx_ant_id in range(1):
            for rx_ant_id in range(n_rx_ant):

                if mode == 'coarse':
                    N = len(txtd[tx_ant_id])
                    # Compute the correlation between the two halves
                    Corr = np.sum(rxtd[rx_ant_id, :N//2] * np.conj(rxtd[rx_ant_id, N//2:N]))
                    # Estimate the frequency offset
                    coarse_cfo = -1 * np.angle(Corr) / (2 * np.pi * (N//2)) * (self.fs_rx)
                    cfo_est[rx_ant_id] = coarse_cfo

                elif mode == 'fine':
                    # h_est_full_ = h_est_full[rx_ant_id, tx_ant_id]
                    # H_est_full_ = fft(h_est_full_)
                    # phi = np.angle(fftshift(H_est_full_))

                    # phi = np.angle(rxtd[rx_ant_id] * np.conj(txtd[tx_ant_id]))
                    phi = np.angle(rxfd[rx_ant_id] * np.conj(txfd[tx_ant_id]))
                    phi = phi[(sc_range[0]+n_samples//2):(sc_range[1]+n_samples//2+1)]

                    # Unwrap the phase to prevent discontinuities
                    phi = np.unwrap(phi)

                    # Perform linear regression to find the slope of the phase difference
                    N = np.arange(len(phi))
                    p = np.polyfit(N, phi, deg=1)
                    slope = p[0]             # Slope of the fitted line
                    # Estimate the frequency offset using the slope
                    fine_cfo = (slope / (2 * np.pi))*(self.fs_rx)
                    cfo_est[rx_ant_id] = fine_cfo

                else:
                    raise ValueError('Invalid CFO estimation mode: ' + mode)

            # self.print(f"Estimated frequency offset: {} Hz".firmat(cfo_est), 0)

        return cfo_est

    
    def sync_frequency(self, rxtd, cfo, mode='time'):
        rxtd = rxtd.copy()
        n_rx_ant = rxtd.shape[0]
        rxfd = fft(rxtd, axis=-1)
        if mode == 'time':
            for i in range(n_rx_ant):
                rxtd[i, :] = self.freq_shift(rxtd[i, :], shift=-1*cfo[i], fs=self.fs_rx)
        elif mode == 'freq':
            for i in range(n_rx_ant):
                rxfd[i, :] = self.freq_shift(rxfd[i, :], shift=-1*cfo[i], fs=self.fs_rx)
            rxtd = ifft(rxfd, axis=-1)
        return rxtd
    

    def sync_time(self, rxtd, txtd, sc_range=[0,0]):
        n_samples_rx = rxtd.shape[-1]
        n_samples = min(txtd.shape[-1], rxtd.shape[-1])
        txtd_ = txtd.copy()[:,:n_samples]
        rxtd_ = rxtd.copy()[:,:n_samples]
        n_rx_ant = rxtd.shape[0]
        n_tx_ant = txtd.shape[0]
        rxtd_sync = np.zeros((n_rx_ant, n_tx_ant, n_samples_rx), dtype='complex')

        for tx_ant_id in range(n_tx_ant):
            for rx_ant_id in range(n_rx_ant):
                delay = self.extract_delay(rxtd_[rx_ant_id], txtd_[tx_ant_id])
                rxtd_sync[rx_ant_id,tx_ant_id], _, _, _ = self.time_adjust(rxtd[rx_ant_id], txtd_[tx_ant_id], delay)

                frac_delay = self.extract_frac_delay(rxtd_sync[rx_ant_id,tx_ant_id,:n_samples], txtd_[tx_ant_id], sc_range=sc_range)
                # print(f"Fractional delay: {frac_delay}")
                rxtd_sync[rx_ant_id,tx_ant_id], _ = self.adjust_frac_delay(rxtd_sync[rx_ant_id,tx_ant_id], txtd_[tx_ant_id], frac_delay)

        return rxtd_sync


    def sparse_est(self, h, g=None, sc_range_ch=[0,0], npaths=1, nframe_avg=1, ndly=10000, drange=[-6,20], cv=False):
        """
        Estimates the sparse channel using Orthogonal Matching Pursuit (OMP).
        Parameters:
        -----------
        h : np.array of shape (nfft, nrx, ntx, nframe)
            The time-domain channel estimate.
        g : np.array of shape (nfft, nrx, ntx)
            The system response in the time-domain.
        npaths : int, optional
            Maximum number of paths to estimate. Default is 1.
        nframe_avg : int, optional
            Number of frames to average for channel estimation. Default is 1.
        ndly : int, optional
            Number of delay points to test around the peak. Default is 10000.
        drange : list, optional
            Range of delays to test around the peak. Default is [-6, 20].
        cv : bool, optional
            Whether to use cross-validation to stop the path estimation. Default is True.
        Raises:
        -------
        ValueError
            If there are not enough frames for cross-validation or averaging.
        Notes:
        ------
        - The method uses cross-validation to stop the path estimation when the test error exceeds the training error by a certain tolerance.
        - The delays are set to test around the peak of the time-domain channel estimate.
        - The method uses Orthogonal Matching Pursuit (OMP) to find the sparse solution.        
        """

        # Number of paths stops when test error exceeds training error
        # by 1+cv_tol
        cv_tol = 0.1

        # Compute the channel estimates for training and test
        # by averaging over the different frames

        H = fft(h, axis=0)
        nframe = H.shape[3]
        nfft = H.shape[0]
        n_rx_ant = H.shape[1]
        n_tx_ant = H.shape[2]
        if g is None:
            G = np.ones((H.shape[0], H.shape[1], H.shape[2]), dtype='complex')
            g = ifft(G, axis=0)
            nff_g = nfft
        else:
            G = fft(g, axis=0)
            nff_g = G.shape[0]
        G = ifftshift(fftshift(G, axes=0)[(sc_range_ch[0]+nff_g//2):(sc_range_ch[1]+nff_g//2+1)], axes=0)

        h_tr_mat = [[None for i in range(n_tx_ant)] for j in range(n_rx_ant)]
        dly_est_mat = [[None for i in range(n_tx_ant)] for j in range(n_rx_ant)]
        peaks_mat = [[None for i in range(n_tx_ant)] for j in range(n_rx_ant)]
        npaths_est_mat = [[None for i in range(n_tx_ant)] for j in range(n_rx_ant)]

        for irx in range(n_rx_ant):
            for itx in range(n_tx_ant):
                if cv:
                    if (nframe < 2*nframe_avg):
                        raise ValueError('Not enough frames for cross-validation')
                    Itr = np.arange(0,nframe_avg)*2
                    Its = Itr + 1
                    H_tr = np.mean(H[:,irx,itx,Itr], axis=1)
                    H_ts = np.mean(H[:,irx,itx,Its], axis=1)

                    # For the FA probability, we set the threhold to the energy
                    # of the max on nfft random basis functions.  The energy
                    # on each basis function is exponential with mean 1/nfft.
                    # So, the maximum energy is exponential with mean 1/nfft* (\sum_k 1/k)
                    t = np.arange(1, nfft)
                    cv_dec = (1 - 2*np.sum(1/t)/nfft)
                else:
                    if (nframe < nframe_avg):
                        raise ValueError('Not enough frames for averaging')
                    H_tr = H[:,irx,itx,:nframe_avg]
                h_tr = np.fft.ifft(H_tr, axis=0)

                # Set the delays to test around the peak
                idx = np.argmax(np.abs(h_tr))

                dly_test = (idx + np.linspace(drange[0], drange[1],ndly))/self.fs_trx
                # Create the basis vectors
                freq = (np.arange(nfft)/nfft)*self.fs_trx + self.fc - self.fs_trx/2
                B = G[:,irx,itx,None]*np.exp(-2*np.pi*1j*freq[:,None] * dly_test[None,:])

                # Use OMP to find the sparse solution
                coeff_est = np.zeros(npaths)
                
                resid = H_tr
                indices = []
                indices1 = []
                mse_tr = np.zeros(npaths)
                mse_ts = np.zeros(npaths)

                npaths_est = 0
                for i in range(npaths):
                    
                    # Compute the correlation
                    cor = np.abs(B.conj().T.dot(resid))

                    # Add the highest correlation to the list
                    idx = np.argmax(cor)
                    indices1.append(idx)

                    # Use least squares to estimate the coefficients
                    coeffs_est = np.linalg.lstsq(B[:,indices1], H_tr, rcond=None)[0]

                    # Compute the resulting sparse channel
                    H_sparse = B[:,indices1].dot(coeffs_est)

                    # Compute the current residual 
                    resid = H_tr - H_sparse
                    
                    # Compute the MSE on the training data
                    mse_tr[i] = np.mean(np.abs(resid)**2)/np.mean(np.abs(H_tr)**2)

                    # Compute the MSE on the test data if CV is used
                    if cv:
                        resid_ts = H_ts - H_sparse
                        mse_ts[i] = np.mean(np.abs(resid_ts)**2)/np.mean(np.abs(H_ts)**2)

                        # Check if path is valid
                        if (i > 0):
                            if (mse_ts[i] > cv_dec*mse_ts[i-1]):
                                break
                        if (mse_ts[i] > (1+cv_tol)*mse_tr[i]):
                            break

                    # Updated the number of paths
                    npaths_est = i+1
                    indices.append(idx)

                # dly_est = dly_test[indices]
                # dly_est = np.array(list(dly_test[indices]) + [0]*(npaths-npaths_est))
                dly_est = np.pad(dly_test[indices], (0, npaths - npaths_est), constant_values=0)

                # Use least squares to estimate the coefficients
                coeffs_est = np.linalg.lstsq(B[:,indices], H_tr, rcond=None)[0]

                # Compute the resulting sparse channel
                H_sparse = B[:,indices].dot(coeffs_est)
                h_sparse = np.fft.ifft(H_sparse, axis=0)

                scale = np.mean(np.abs(G))**2
                # peaks  = np.abs(coeffs_est)**2 * scale
                peaks  = coeffs_est.copy() * np.sqrt(scale)
                # peaks = np.array(list(peaks) + [0]*(npaths-npaths_est))
                peaks = np.pad(peaks, (0, npaths - npaths_est), constant_values=0)

                h_tr_mat[irx][itx] = h_tr.copy()
                if len(dly_est) == npaths:
                    dly_est_mat[irx][itx] = dly_est.copy()
                else:
                    # dly_est_mat[irx][itx] = dly_est.copy().extend([0]*(npaths-npaths_est))
                    dly_est_mat[irx][itx] = np.array([0] * npaths)
                if len(peaks) == npaths:
                    peaks_mat[irx][itx] = peaks.copy()
                else:
                    # peaks_mat[irx][itx] = peaks.copy() + [0]*(npaths-npaths_est)
                    peaks_mat[irx][itx] = np.array([0] * npaths)

                npaths_est_mat[irx][itx] = npaths_est
        
        h_tr_mat = np.array(h_tr_mat)
        dly_est_mat = np.array(dly_est_mat)
        peaks_mat = np.array(peaks_mat)
        npaths_est_mat = np.array(npaths_est_mat)

        return (h_tr_mat, dly_est_mat, peaks_mat, npaths_est_mat)


    def channel_estimate(self, txtd, rxtd_s, sys_response=None, sc_range_ch=[0,0], snr_est=100):
        if len(rxtd_s.shape) == 4:
            rxtd_s = np.mean(rxtd_s.copy(), axis=0)
        deconv_sys_response = (sys_response is not None)

        n_samples = min(txtd.shape[-1], rxtd_s.shape[-1])
        n_samples_ch = sc_range_ch[1] - sc_range_ch[0] + 1
        # n_samples_ch = n_samples

        txtd=txtd.copy()[:,:n_samples]
        rxtd_s=rxtd_s.copy()[:,:,:n_samples]
        n_rx_ant = rxtd_s.shape[0]
        n_tx_ant = txtd.shape[0]

        t_ch = self.t_trx[:n_samples_ch]
        freq_ch = self.freq_trx[(sc_range_ch[0]+n_samples//2):(sc_range_ch[1]+n_samples//2+1)]

        H_est_full = np.zeros((n_rx_ant, n_tx_ant, n_samples_ch), dtype='complex')
        h_est_full = np.zeros((n_rx_ant, n_tx_ant, n_samples_ch), dtype='complex')
        
        txfd = fft(txtd, axis=-1)
        rxfd_s = fft(rxtd_s, axis=-1)
        # rxfd_s = np.roll(rxfd_s, 1, axis=1)
        # txfd = np.roll(txfd, 1, axis=1)

        if deconv_sys_response:
            g = sys_response.copy()[:,:n_samples]
            G = fft(g, axis=-1)

        for tx_ant_id in range(n_tx_ant):
            for rx_ant_id in range(n_rx_ant):
                if deconv_sys_response:
                    txfd_ = txfd[tx_ant_id] * G[rx_ant_id, tx_ant_id]
                else:
                    txfd_ = txfd[tx_ant_id]
                rxfd_ = rxfd_s[rx_ant_id, tx_ant_id]
                rx_pow = np.mean(np.abs(rxfd_)**2)
                noise_pow = rx_pow / snr_est
                H_est_full_ = rxfd_s[rx_ant_id, tx_ant_id] * np.conj(txfd_) / ((np.abs(txfd_)**2) + noise_pow)
                # H_est_full_ = rxfd[rx_ant_id] * np.conj(txfd_)
                # H_est_full_ = rxfd[rx_ant_id] / txfd_

                H_est_full_ = ifftshift(fftshift(H_est_full_)[(sc_range_ch[0]+n_samples//2):(sc_range_ch[1]+n_samples//2+1)])

                h_est_full_ = ifft(H_est_full_)
                H_est_full[rx_ant_id, tx_ant_id, :] = H_est_full_.copy()
                h_est_full[rx_ant_id, tx_ant_id, :] = h_est_full_.copy()

                im = np.argmax(np.abs(h_est_full_))
                h_est_full_ = np.roll(h_est_full_, -im + len(h_est_full_)//10)
                h_est_full_ = h_est_full_.flatten()

                sig = np.abs(h_est_full_) / np.max(np.abs(h_est_full_))
                title = 'Channel response in the time domain \n between TX antenna {} and RX antenna {}'.format(tx_ant_id, rx_ant_id)
                xlabel = 'Time (s)'
                ylabel = 'Normalized Magnitude (dB)'
                self.plot_signal(t_ch, sig, scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)

                sig = np.abs(fftshift(H_est_full_))
                title = 'Channel response in the frequency domain \n between TX antenna {} and RX antenna {}'.format(tx_ant_id, rx_ant_id)
                xlabel = 'Frequency (MHz)'
                ylabel = 'Magnitude (dB)'
                self.plot_signal(freq_ch, sig, scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)

        # H_est = np.linalg.pinv(txfd.T) @ rxfd.T
        # H_est = H_est.T
        # H_est = rxfd @ np.linalg.pinv(txfd)
        H_est = np.mean(H_est_full, axis=-1)

        time_pow = np.sum(np.abs(H_est_full)**2, axis=(0,1))
        idx_max  = np.argmax(time_pow)
        H_est_max = H_est_full[:,:,idx_max]

        return h_est_full, H_est, H_est_max


    # def channel_estimate_eq(self, txtd, rxtd):
    #     txfd = fft(txtd)
    #     rxfd = fft(rxtd)

    #     # Signal parameters
    #     N_cp = 256
    #     N_fft = 768
    #     M = 16
    #     x = txtd[N_cp:]
    #     X = fft(x)

    #     plt.figure(1)
    #     plt.subplot(3, 1, 1)

    #     # Time synchronization
    #     data_sync = rxtd[:4 * N_fft - 1]
    #     rx = convolve(np.conj(x), data_sync, mode='full')
    #     plt.plot(np.abs(rx))
    #     index_ini = np.argmax(rx)

    #     # Retrieve time-synced signal
    #     N_vec = (np.tile(np.arange(N_fft), M) + np.repeat(np.arange(M), N_fft) * (N_fft + N_cp) + N_cp + 1)
    #     Y = rxtd[N_vec + index_ini - 3].reshape((M, N_fft)).T

    #     # Equalized frequency
    #     H_hat = fft(Y, axis=0) / X[:,None]
    #     # Averaged frequency
    #     H_hat_avg = np.mean(H_hat, axis=1)

    #     # Equalized time
    #     h_hat = ifft(H_hat, axis=0)
    #     h_hat = h_hat[:N_cp, :]

    #     # Averaged time
    #     h_hat_avg = np.mean(h_hat, axis=1)

    #     # Plots
    #     plt.subplot(3, 1, 2)
    #     plt.plot(np.abs(h_hat_avg))

    #     plt.subplot(3, 1, 3)
    #     plt.plot(fftshift(10 * np.log10(np.abs(H_hat_avg) ** 2)))
    #     plt.axis([1, N_fft, -100, 0])

    #     H_dd = fft(h_hat.T, axis=0).T / np.sqrt(N_fft * M)
    #     H_dd_log = 10 * np.log10(np.abs(H_dd) ** 2)
    #     H_dd_log[H_dd_log < -130] = -130

    #     plt.figure(2)
    #     plt.pcolor(H_dd_log)
    #     plt.colorbar()
    #     plt.show()


    def channel_equalize(self, txtd, rxtd, h_full, H, sc_range=[0,0], sc_range_ch=[0,0], null_sc_range=[0,0], n_rx_ch_eq=1):
        n_samples = min(txtd.shape[-1], rxtd.shape[-1])
        n_samples_ch = sc_range_ch[1] - sc_range_ch[0] + 1
        txtd=txtd.copy()[:,:n_samples]
        rxtd=rxtd.copy()[:,:n_samples]

        txfd = fft(txtd, axis=-1)
        rxfd = fft(rxtd, axis=-1)
        H_full = fft(h_full, axis=-1)

        rxtd_eq = rxtd.copy()
        rxfd_eq = rxfd.copy()

        # print('H_det: {}'.format(np.abs(np.linalg.det(H))))
        
        # if np.linalg.matrix_rank(H) == min(H.shape) and np.abs(np.linalg.det(H)) > 1e-3:
        #     H_inv = np.linalg.pinv(H)
        # else:
        #     epsilon = 1e-6
        #     H = H + epsilon * np.eye(H.shape[0])
        #     H_inv = np.linalg.pinv(H)

        # if np.abs(np.linalg.det(H)) > 1e-3:
        #     rxfd_eq = H_inv @ rxfd
        # else:
        #     for rx_ant_id in range(rxtd_eq.shape[0]):
        #         phase_offset = self.calc_phase_offset(rxfd[rx_ant_id], txfd[0])
        #         rxfd_eq[rx_ant_id], _ = self.adjust_phase(rxfd[rx_ant_id], txfd[0], phase_offset)


        rxfd_ = fftshift(rxfd, axes=-1)
        rxfd_eq_ = fftshift(rxfd_eq, axes=-1)
        H_full_ = fftshift(H_full, axes=-1)
        if n_rx_ch_eq == 1:
            for rx_ant_id in range(rxtd_eq.shape[0]):
                # rxfd_eq[rx_ant_id] = rxfd[rx_ant_id] / H[rx_ant_id, rx_ant_id]

                for i, sc in enumerate(range(sc_range[0], sc_range[1]+1)):
                    if not sc in range(null_sc_range[0], null_sc_range[1]+1):
                        rxfd_eq_[rx_ant_id, sc+n_samples//2] = rxfd_[rx_ant_id, sc+n_samples//2] / H_full_[rx_ant_id, rx_ant_id, i]
                rxfd_eq[rx_ant_id] = ifftshift(rxfd_eq_[rx_ant_id])
        else:
            tol = 1e-6
            for i, sc in enumerate(range(sc_range[0], sc_range[1]+1)):
                if not sc in range(null_sc_range[0], null_sc_range[1]+1):
                    H_sc = H_full_[:,:,i]
                    # H_sc += tol*np.eye(H_sc.shape[0])
                    # H_sc_inv = np.linalg.pinv(H_sc)
                    H_sc_inv = (np.conj(H_sc.T) * H_sc + tol*np.eye(H_sc.shape[0])) * np.conj(H_sc.T)
                    rxfd_eq_[:,sc+n_samples//2] = H_sc_inv @ rxfd_[:,sc+n_samples//2]

            rxfd_eq = ifftshift(rxfd_eq_, axes=-1)

        rxtd_eq = ifft(rxfd_eq, axis=-1)

        return rxtd_eq


    def filter_aoa(self, rx_phase_list, rx_phase, aoa_list, aoa):
        alpha_phase = 0.5
        alpha_aoa = 0.5

        if len(aoa_list) > 0:
            aoa_last = aoa_list[-1]
        else:
            if aoa is None:
                aoa_last = 0
            else:
                aoa_last = aoa
        if aoa is None:
            aoa = aoa_last
        else:
            aoa = alpha_aoa * aoa + (1 - alpha_aoa) * aoa_last


        if len(rx_phase_list) > 0:
            rx_phase_last = rx_phase_list[-1]
        else:
            if rx_phase is None:
                rx_phase_last = 0
            else:
                rx_phase_last = rx_phase
        if rx_phase is None:
            rx_phase = rx_phase_last
        else:
            rx_phase = alpha_phase * rx_phase + (1 - alpha_phase) * rx_phase_last

        rx_phase_list.append(rx_phase)
        aoa_list.append(aoa)

        return rx_phase_list, aoa_list


    def angle_of_arrival(self, txtd, rxtd, h_full, rx_phase_list, aoa_list, rx_phase_offset=0):
        if len(rxtd.shape) == 3:
            rxtd = np.mean(rxtd.copy(), axis=0)
        rx_phase = self.calc_phase_offset(rxtd[0,:], rxtd[1,:])

        # h_full_ = h_full.copy()[:,0,:]
        # h_full_ = np.sum(np.abs(h_full_)**2, axis=0)
        # im = np.argmax(h_full_)
        # # i0 = np.maximum(0, im-10)
        # # i1 = np.minimum(self.nfft_ch, im+10)
        # # z = np.mean(rxtd[0, i0:i1] * np.conj(rxtd[1, i0:i1]))
        # # rx_phase = np.angle(z)
        # rx_phase = np.angle(rxtd[0,im] * np.conj(rxtd[1,im]))

        rx_phase -= rx_phase_offset
        # print("rx_phase: ", rx_phase)

        angle_sin = rx_phase/(2*np.pi*self.ant_dx)
        if angle_sin > 1 or angle_sin < -1:
            # angle = np.nan
            aoa = None
            rx_phase = None
            self.print("AoA sin is out of range: {}".format(angle_sin), 1)
        else:
            aoa = np.arcsin(angle_sin)

        rx_phase_list, aoa_list = self.filter_aoa(rx_phase_list, rx_phase, aoa_list, aoa)

        return rx_phase_list, aoa_list
    

    def estimate_mimo_params(self, txtd, rxtd, h_full, H, rx_phase_list, aoa_list):
        # U, S, Vh = np.linalg.svd(H)
        # W_tx = Vh.conj().T
        # W_rx = U
        # rx_phase = np.mean(np.angle(U[0,:]*np.conj(U[1,:])))
        # tx_phase = np.mean(np.angle(Vh[:,0]*np.conj(Vh[:,1])))

        rx_phase_list, aoa_list = self.angle_of_arrival(txtd=txtd, rxtd=rxtd, h_full=h_full, rx_phase_list=rx_phase_list, aoa_list=aoa_list, rx_phase_offset=self.rx_phase_offset)
        # print("AoA: {} deg".format(np.rad2deg(aoa)))

        return rx_phase_list, aoa_list


    # plot_signal(self, x, sig, mode='time_IQ', scale='linear', title='Custom Title', xlabel='Time', ylabel='Amplitude', plot_args={'color': 'red', 'linestyle': '--'}, xlim=(0, 10), ylim=(-1, 1), legend=True)
    def plot_signal(self, x, sigs, mode='time', scale='linear', plot_level=0, **kwargs):
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


    def draw_half_gauge(self, ax, min_val=-90, max_val=90):
        ax.add_patch(Wedge((0.5, 0.5), 0.4, 90, -90, color='#f0f0f0', zorder=1))
        ax.add_patch(Wedge((0.5, 0.5), 0.35, 90, -90, color='#e0e0e0', zorder=2))

        num_ticks = 18
        for i in range(num_ticks + 1):
            angle = i * (180 / num_ticks)
            tick_length = 0.05 if i % 2 == 0 else 0.03
            ax.plot([0.5 + 0.35 * np.cos(np.radians(angle)), 0.5 + (0.35 - tick_length) * np.cos(np.radians(angle))],
                    [0.5 + 0.35 * np.sin(np.radians(angle)), 0.5 + (0.35 - tick_length) * np.sin(np.radians(angle))],
                    color='black', lw=1, zorder=3)

        for i in range(num_ticks + 1):
            angle = i * (180 / num_ticks)
            value = -1 * (min_val + (max_val - min_val) * (i / num_ticks))
            x = 0.5 + 0.28 * np.cos(np.radians(angle))
            y = 0.5 + 0.28 * np.sin(np.radians(angle))
            ax.text(x, y, f'{int(value)}', fontsize=10, ha='center', va='center')

        ax.add_patch(Circle((0.5, 0.5), 0.05, color='black', zorder=5))
        ax.text(0.5, 0.95, "Angle of Arrival", fontsize=30, fontweight='bold', horizontalalignment='center')
        ax.set_aspect('equal')


    def gauge_update_needle(self, ax, value, min_val=90, max_val=-90):
        if value != np.nan and value != None:
            angle = (value - min_val) * 180 / (max_val - min_val)
        else:
            return
        x = 0.5 + 0.35 * np.cos(np.radians(angle))
        y = 0.5 + 0.35 * np.sin(np.radians(angle))

        arrow = FancyArrow(0.5, 0.5, x-0.5, y-0.5, width=0.02, head_width=0.05, head_length=0.08, color='darkblue', zorder=6)

        old_arrows = [p for p in ax.patches if isinstance(p, FancyArrow)]
        for old_arrow in old_arrows:
            old_arrow.remove()

        ax.add_patch(arrow)

