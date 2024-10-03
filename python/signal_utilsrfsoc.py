from backend import *
from backend import be_np as np, be_scp as scipy
from signal_utils import Signal_Utils




class Signal_Utils_Rfsoc(Signal_Utils):
    def __init__(self, params):
        super().__init__(params)

        self.f_max = params.f_max
        self.filter_signal = params.filter_signal
        self.sig_mode = params.sig_mode
        self.sig_gain_db = params.sig_gain_db
        self.wb_bw_mode = params.wb_bw_mode
        self.wb_bw = params.wb_bw
        self.wb_sc_range = params.wb_sc_range
        self.tone_f_mode = params.tone_f_mode
        self.f_tone = params.f_tone
        self.sc_tone = params.sc_tone
        self.sig_modulation = params.sig_modulation
        self.sig_gen_mode = params.sig_gen_mode
        self.sig_path = params.sig_path
        self.sig_save_path = params.sig_save_path
        self.mixer_mode = params.mixer_mode
        self.mix_freq = params.mix_freq
        self.filter_bw = params.filter_bw
        self.n_tx_ant = params.n_tx_ant
        self.n_rx_ant = params.n_rx_ant
        self.beamforming = params.beamforming
        self.ant_dx = params.ant_dx
        self.ant_dy = params.ant_dy

        self.print("signals object initialization done", thr=1)
        

    def gen_tx_signal(self):
        txtd_base = []
        txtd = []
        for ant_id in range(self.n_tx_ant):
            if 'tone' in self.sig_mode:
                if self.sig_mode=='tone_1':
                    nsc = 1
                elif self.sig_mode=='tone_2':
                    nsc = 2
                if self.tone_f_mode=='freq':
                    self.sc_tone = None
                elif self.tone_f_mode=='sc':
                    self.f_tone = None
                txtd_base_s = self.generate_tone(sc=self.sc_tone, f=self.f_tone, sig_mode=self.sig_mode, gen_mode=self.sig_gen_mode)
            elif 'wideband' in self.sig_mode:
                if self.wb_bw_mode=='freq':
                    self.wb_sc_range = None
                    nsc = int(self.wb_bw / self.fs_tx * self.nfft_tx)
                elif self.wb_bw_mode=='sc':
                    self.wb_bw = None
                    nsc = self.wb_sc_range[1] - self.wb_sc_range[0] + 1
                txtd_base_s = self.generate_wideband(sc_range=self.wb_sc_range, bw=self.wb_bw, modulation=self.sig_modulation, sig_mode=self.sig_mode, gen_mode=self.sig_gen_mode)
            elif self.sig_mode == 'load':
                txtd_base_s = np.load(self.sig_path)
            else:
                raise ValueError('Unsupported signal mode: ' + self.sig_mode)
            txtd_base_s /= np.max([np.abs(txtd_base_s.real), np.abs(txtd_base_s.imag)])
            txtd_base_s *= self.db_to_lin(self.sig_gain_db, mode='mag')
            txtd_base.append(txtd_base_s)

            self.sig_pow_dbm = self.lin_to_db(0.5 * 1000, mode='pow') + self.sig_gain_db
            bw = (nsc/self.nfft_tx) * self.fs_tx
            self.sig_psd_dbm = self.sig_pow_dbm - self.lin_to_db(bw, mode='pow')
            self.sig_psd_dbm_sc = self.sig_pow_dbm - self.lin_to_db(nsc, mode='pow')
            print('TX Signal power for antenna {}: {:0.3f} dbm'.format(ant_id, self.sig_pow_dbm))
            print('TX Signal PSD for antenna {}: {:0.3f} dBm/Hz = {:0.3f} dBm/MHz = {:0.3f} dBm/sc'.format(ant_id, self.sig_psd_dbm, self.sig_psd_dbm+self.lin_to_db(1e6, mode='pow'), self.sig_psd_dbm_sc))

            title = 'TX signal spectrum in base-band for antenna {}'.format(ant_id)
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            self.plot_signal(x=self.freq_tx, sigs=txtd_base[ant_id], mode='fft', scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)
            title = 'Base-band TX signal in time domain at \n the time transition for antenna {}'.format(ant_id)
            xlabel = 'Time (s)'
            ylabel = 'Magnitude'
            n=int(np.round(self.fs_tx/self.f_max))
            t=self.t_tx[:2*n]
            sig_real=np.concatenate((txtd_base[ant_id].real[-n:], txtd_base[ant_id].real[:n]))
            sig_imag=np.concatenate((txtd_base[ant_id].imag[-n:], txtd_base[ant_id].imag[:n]))
            self.plot_signal(x=t, sigs={'real':sig_real, 'imag':sig_imag}, mode='time', scale='linear', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4, legend=True)

        txtd_base = np.array(txtd_base)

        if self.mixer_mode=='digital' and self.mix_freq!=0:
            for ant_id in range(self.n_tx_ant):
                txtd_s = self.freq_shift(txtd_base[ant_id], shift=self.mix_freq, fs=self.fs_tx)
                txtd.append(txtd_s)
            
                # txfd = np.abs(fftshift(fft(txtd)))
                title = 'TX signal spectrum after upconversion for antenna {}'.format(ant_id)
                xlabel = 'Frequency (MHz)'
                ylabel = 'Magnitude (dB)'
                self.plot_signal(x=self.freq_tx, sigs=txtd[ant_id], mode='fft', scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)
        else:
            txtd = txtd_base.copy()
            # txfd = txfd_base.copy()

        txtd = np.array(txtd)
        
        if self.beamforming:
            txtd_base = self.beam_form(txtd_base)
            txtd = self.beam_form(txtd)

        return (txtd_base, txtd)


    def animate_plot(self, client_inst, txtd_base, plot_mode=['h', 'rxtd', 'rxfd'], save_signal=False, plot_level=0):
        if self.plot_level<plot_level:
            return
        self.anim_paused = False
        n_plots = len(plot_mode)
        tx_ant_id = 0
        rx_ant_id = 0

        if save_signal:
            # test = np.load("./mimo_1.npz")
            n_save = 1000
            txtd_save=[]
            rxtd_save=[]
            for i in range(n_save):
                time.sleep(0.01)
                print("Signal Save Iteration: ", i+1)
                rxtd = client_inst.receive_data(mode='once')
                rxtd = rxtd.squeeze(axis=0)
                rxtd_base = self.rx_operations(txtd_base, rxtd)
                rxtd_base = rxtd_base[:self.n_samples]
                txtd_save.append(txtd_base)
                rxtd_save.append(rxtd_base)
            np.savez(self.sig_save_path, txtd=np.array(txtd_save), rxtd=np.array(rxtd_save))

        
        def receive_data(txtd_base):
            rxtd = client_inst.receive_data(mode='once')
            rxtd = rxtd.squeeze(axis=0)
            rxtd_base = self.rx_operations(txtd_base, rxtd)

            h_est_full, H_est, H_est_max = self.channel_estimate(txtd_base, rxtd_base)
            # h_est_full = self.channel_estimate_eq(txtd_base, rxtd_base)
            
            tx_phase, rx_phase = self.estimate_mimo_params(H_est_max)
            # rxtd_base = self.channel_equalize(txtd_base, rxtd_base, H_est_max)
            # print("rxtd_eq: ", fft(rxtd_eq, axis=-1)[0,:2])
            
            txtd_base = txtd_base.copy()[:,:self.n_samples]
            rxtd_base = rxtd_base.copy()[:,:self.n_samples]

            h_est_full = h_est_full[tx_ant_id, rx_ant_id]
            im = np.argmax(h_est_full)
            h_est_full = np.roll(h_est_full, -im + len(h_est_full)//10)
            H_est_full = np.abs(fftshift(fft(h_est_full)))

            sigs=[]
            for item in plot_mode:
                if item=='h':
                    sigs.append(self.lin_to_db(np.abs(h_est_full) / np.max(np.abs(h_est_full)), mode='mag'))
                elif item=='H':
                    sigs.append(self.lin_to_db(H_est_full, mode='mag'))
                elif item=='rxtd':
                    sigs.append(rxtd_base[rx_ant_id])
                elif item=='rxfd':
                    sigs.append(self.lin_to_db(np.abs(fftshift(fft(rxtd_base[rx_ant_id]))), mode='mag'))
                elif item=='txtd':
                    sigs.append(txtd_base[tx_ant_id])
                elif item=='txfd':
                    sigs.append(self.lin_to_db(np.abs(fftshift(fft(txtd_base[tx_ant_id]))), mode='mag'))
                elif item=='rxtd01':
                    delay = self.extract_frac_delay(rxtd_base[0], rxtd_base[1])
                    # print("Fractional sample delay between antennas: {:0.4f}".format(delay))
                    delay = self.extract_delay(rxtd_base[0], rxtd_base[1])
                    # print("Integer sample delay between antennas: ", delay)
                    rxtd_base[0], rxtd_base[1], _, _ = self.time_adjust(rxtd_base[0], rxtd_base[1], delay)
                    phase_offset = self.calc_phase_offset(rxtd_base[0], rxtd_base[1])
                    # print("Phase offset between antennas in degrees: ", phase_offset*180/np.pi)
                    rxtd_base[0], rxtd_base[1] = self.adjust_phase(rxtd_base[0], rxtd_base[1], phase_offset)
                    sigs.append([np.abs(rxtd_base[0,:100]), np.abs(rxtd_base[1,:100])])
                elif item=='rxfd01':
                    rxfd_base_0 = self.lin_to_db(np.abs(fftshift(fft(rxtd_base[0]))), mode='mag')
                    rxfd_base_1 = self.lin_to_db(np.abs(fftshift(fft(rxtd_base[1]))), mode='mag')
                    sigs.append([rxfd_base_0, rxfd_base_1])
                elif item=='IQ':
                    sigs.append(fft(rxtd_base[rx_ant_id], axis=-1))

            return (sigs)

        def toggle_pause(event):
            if event.key == 'p':  # Press 'p' to pause/resume
                self.anim_paused = not self.anim_paused

        def update(frame):
            if self.anim_paused:
                return line
            sigs = receive_data(txtd_base)
            line_id = 0
            for i in range(n_plots):
                if plot_mode[i]=='rxtd':
                    line[line_id].set_ydata(sigs[i].real)
                    line_id+=1
                    line[line_id].set_ydata(sigs[i].imag)
                    line_id+=1
                elif plot_mode[i]=='txtd':
                    line[line_id].set_ydata(sigs[i].real)
                    line_id+=1
                    line[line_id].set_ydata(sigs[i].imag)
                    line_id+=1
                elif plot_mode[i]=='rxtd01' or plot_mode[i]=='rxfd01':
                    line[line_id].set_ydata(sigs[i][0])
                    line_id+=1
                    line[line_id].set_ydata(sigs[i][1])
                    line_id+=1
                elif plot_mode[i]=='IQ':
                    line[line_id].set_offsets(np.column_stack((sigs[i].real, sigs[i].imag)))
                    line_id+=1
                else:
                    line[line_id].set_ydata(sigs[i])
                    line_id+=1
                if plot_mode[i]!='IQ':
                    ax[i].relim()
                ax[i].autoscale_view()

            return line


        # Set up the figure and plot
        sigs = receive_data(txtd_base)
        line = [None for i in range(2*n_plots)]
        fig, ax = plt.subplots(n_plots, 1)
        if type(ax) is not np.ndarray:
            ax = [ax]
        fig.canvas.mpl_connect('key_press_event', toggle_pause)
        # fig, ax = plt.subplots(1, n_plots)

        line_id = 0
        for i in range(n_plots):
            ax[i].set_autoscale_on(True)
            if plot_mode[i]=='h':
                line[line_id], = ax[i].plot(self.t, sigs[i])
                line_id+=1
                ax[i].set_title("Channel response in the time domain between TX antenna {} and RX antenna {}".format(tx_ant_id, rx_ant_id))
                ax[i].set_xlabel("Time (s)")
                ax[i].set_ylabel("Normalized Magnitude (dB)")
                # ax[i].set_xlim(np.min(self.t), np.max(self.t))
                # ax[i].set_ylim(np.min(sigs[0]), 1.5*np.max(sigs[0]))
                # ax[i].grid(0.2)
            elif plot_mode[i]=='H':
                line[line_id], = ax[i].plot(self.freq, sigs[i])
                line_id+=1
                ax[i].set_title("Channel response in the frequency domain between TX antenna {} and RX antenna {}".format(tx_ant_id, rx_ant_id))
                ax[i].set_xlabel("Frequency (MHz)")
                ax[i].set_ylabel("Magnitude (dB)")
            elif plot_mode[i]=='rxtd':
                line[line_id], = ax[i].plot(self.t, sigs[i].real, label='I')
                line_id+=1
                line[line_id], = ax[i].plot(self.t, sigs[i].imag, label='Q')
                line_id+=1
                ax[i].set_title("RX signal in time domain (I and Q) for antenna {}".format(rx_ant_id))
                ax[i].set_xlabel("Time (s)")
                ax[i].set_ylabel("Magnitude")
            elif plot_mode[i]=='rxfd':
                line[line_id], = ax[i].plot(self.freq, sigs[i])
                line_id+=1
                ax[i].set_title("RX signal spectrum for antenna {}".format(rx_ant_id))
                ax[i].set_xlabel("Freq (MHz)")
                ax[i].set_ylabel("Magnitude (dB)")
            elif plot_mode[i]=='txtd':
                line[line_id], = ax[i].plot(self.t, sigs[i].real, label='I')
                line_id+=1
                line[line_id], = ax[i].plot(self.t, sigs[i].imag, label='Q')
                line_id+=1
                ax[i].set_title("TX signal in time domain (I and Q) for antenna {}".format(tx_ant_id))
                ax[i].set_xlabel("Time (s)")
                ax[i].set_ylabel("Magnitude")
            elif plot_mode[i]=='txfd':
                line[line_id], = ax[i].plot(self.freq, sigs[i])
                line_id+=1
                ax[i].set_title("TX signal spectrum for antenna {}".format(tx_ant_id))
                ax[i].set_xlabel("Freq (MHz)")
                ax[i].set_ylabel("Magnitude (dB)")
            elif plot_mode[i]=='rxtd01':
                line[line_id], = ax[i].plot(self.t[:100], sigs[i][0], label='Antenna 0')
                line_id+=1
                line[line_id], = ax[i].plot(self.t[:100], sigs[i][1], label='Antenna 1')
                line_id+=1
                ax[i].set_title("Aligned RX signals in time domain for antennas 0 and 1")
                ax[i].set_xlabel("Time (s)")
                ax[i].set_ylabel("Magnitude")
            elif plot_mode[i]=='rxfd01':
                line[line_id], = ax[i].plot(self.freq, sigs[i][0], label='Antenna 0')
                line_id+=1
                line[line_id], = ax[i].plot(self.freq, sigs[i][1], label='Antenna 1')
                line_id+=1
                ax[i].set_title("Aligned RX signals spectrum for antennas 0 and 1")
                ax[i].set_xlabel("Freq (MHz)")
                ax[i].set_ylabel("Magnitude (dB)")
            elif plot_mode[i]=='IQ':
                line[line_id] = ax[i].scatter(sigs[i].real, sigs[i].imag, facecolors='none', edgecolors='b', s=100)
                line_id+=1
                # ax[i].set_xlim([-3, 3])
                # ax[i].set_ylim([-3, 3])
                ax[i].set_title("RX samples in IQ plane for antenna {}".format(rx_ant_id))
                ax[i].set_xlabel("In-phase (I)")
                ax[i].set_ylabel("Quadrature (Q)")
                ax[i].axhline(0, color='black',linewidth=0.5)
                ax[i].axvline(0, color='black',linewidth=0.5)
                ax[i].set_aspect('equal')
                
            # ax[i].autoscale()
            ax[i].grid(True)
            if plot_mode[i]!='IQ':
                ax[i].relim()
            ax[i].autoscale_view()
            ax[i].minorticks_on()
            ax[i].legend()

        # Create the animation
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.4, wspace=0.4)
        anim = animation.FuncAnimation(fig, update, frames=900*2, interval=500, blit=False)
        plt.show()


    def rx_operations(self, txtd_base, rxtd):
        for ant_id in range(self.n_rx_ant):
            title = 'RX signal spectrum for antenna {}'.format(ant_id)
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            self.plot_signal(x=self.freq_rx, sigs=rxtd[ant_id], mode='fft', scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)

            title = 'RX signal in time domain (zoomed) for antenna {}'.format(ant_id)
            xlabel = 'Time (s)'
            ylabel = 'Magnitude'
            # xlim=(0, 10/(self.filter_bw/2))
            n = 4*int(np.round(self.fs_rx/self.f_max))
            self.plot_signal(x=self.t_rx[:n], sigs=rxtd[ant_id,:n], mode='time_IQ', scale='linear', title=title, xlabel=xlabel, ylabel=ylabel, legend=True, plot_level=5)

        if self.mixer_mode == 'digital' and self.mix_freq!=0:
            rxtd_base = np.zeros_like(rxtd)
            for ant_id in range(self.n_rx_ant):
                rxtd_base[ant_id,:] = self.freq_shift(rxtd[ant_id], shift=-1*self.mix_freq, fs=self.fs_rx)

                title = 'RX signal spectrum after downconversion for antenna {}'.format(ant_id)
                xlabel = 'Frequency (MHz)'
                ylabel = 'Magnitude (dB)'
                self.plot_signal(x=self.freq_rx, sigs=rxtd_base[ant_id], mode='fft', scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)
        else:
            rxtd_base = rxtd.copy()

        if self.filter_signal:
            for ant_id in range(self.n_rx_ant):
                rxtd_base[ant_id,:] = self.filter(rxtd_base[ant_id,:], cutoff=self.filter_bw)

                title = 'RX signal spectrum after filtering in base-band for antenna {}'.format(ant_id)
                xlabel = 'Frequency (MHz)'
                ylabel = 'Magnitude (dB)'
                self.plot_signal(x=self.freq_rx, sigs=rxtd_base[ant_id], mode='fft', scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=5)

        for ant_id in range(self.n_rx_ant):
            # n_samples = min(len(txtd_base), len(rxtd_base))
            txfd_base = np.abs(fftshift(fft(txtd_base[ant_id,:self.n_samples])))
            rxfd_base = np.abs(fftshift(fft(rxtd_base[ant_id,:self.n_samples])))

            title = 'TX and RX signals spectrum in base-band for antenna {}'.format(ant_id)
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            scale = np.max(txfd_base)/np.max(rxfd_base)
            self.print("TX to RX spectrum scale for antenna {}: {:0.3f}".format(ant_id, scale), thr=4)
            xlim=(-2*self.f_max/1e6, 2*self.f_max/1e6)
            f1=np.abs(self.freq - xlim[0]).argmin()
            f2=np.abs(self.freq - xlim[1]).argmin()
            ylim=(np.min(rxfd_base[f1:f2]*scale), 1.1*np.max(rxfd_base[f1:f2]*scale))
            self.plot_signal(x=self.freq, sigs={"txfd_base":txfd_base, "Scaled rxfd_base":rxfd_base*scale}, scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, xlim=xlim, ylim=ylim, legend=True, plot_level=5)
            self.print("txfd_base max freq for antenna {}: {} MHz".format(ant_id, self.freq[(self.nfft>>1)+np.argmax(txfd_base[self.nfft>>1:])]), thr=4)
            self.print("rxfd_base max freq for antenna {}: {} MHz".format(ant_id, self.freq[(self.nfft>>1)+np.argmax(rxfd_base[self.nfft>>1:])]), thr=4)

        return (rxtd_base)

