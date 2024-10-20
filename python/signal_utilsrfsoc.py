from backend import *
from backend import be_np as np, be_scp as scipy
from signal_utils import Signal_Utils




class Signal_Utils_Rfsoc(Signal_Utils):
    def __init__(self, params):
        super().__init__(params)

        self.f_max = params.f_max
        self.rx_chain = params.rx_chain
        self.sig_mode = params.sig_mode
        self.sig_gain_db = params.sig_gain_db
        self.wb_bw_mode = params.wb_bw_mode
        self.wb_bw_range = params.wb_bw_range
        self.wb_sc_range = params.wb_sc_range
        self.sc_range = params.sc_range
        self.sc_range_ch = params.sc_range_ch
        self.null_sc_range = params.null_sc_range
        self.tone_f_mode = params.tone_f_mode
        self.f_tone = params.f_tone
        self.sc_tone = params.sc_tone
        self.sig_modulation = params.sig_modulation
        self.sig_gen_mode = params.sig_gen_mode
        self.sig_path = params.sig_path
        self.sig_save_path = params.sig_save_path
        self.calib_params_path = params.calib_params_path
        self.channel_save_path = params.channel_save_path
        self.sys_response_path = params.sys_response_path
        self.deconv_sys_response = params.deconv_sys_response
        self.n_save = params.n_save
        self.mixer_mode = params.mixer_mode
        self.mix_freq = params.mix_freq
        self.filter_bw_range = params.filter_bw_range
        self.n_tx_ant = params.n_tx_ant
        self.n_rx_ant = params.n_rx_ant
        self.n_rx_ch_eq = params.n_rx_ch_eq
        self.beamforming = params.beamforming
        self.ant_dx = params.ant_dx
        self.ant_dy = params.ant_dy
        self.use_linear_track = params.use_linear_track
        self.control_piradio = params.control_piradio
        self.anim_interval = params.anim_interval
        self.freq_hop_list = params.freq_hop_list
        self.n_samples_ch = params.n_samples_ch
        self.nfft_ch = params.nfft_ch
        self.snr_est_db = params.snr_est_db
        self.calib_iter = params.calib_iter

        self.rx_phase_offset = 0

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
                txtd_base_s = self.generate_tone(freq_mode=self.tone_f_mode, sc=self.sc_tone, f=self.f_tone, sig_mode=self.sig_mode, gen_mode=self.sig_gen_mode)
            elif 'wideband' in self.sig_mode:
                nsc = self.wb_sc_range[1] - self.wb_sc_range[0] + 1
                txtd_base_s = self.generate_wideband(bw_mode=self.wb_bw_mode, sc_range=self.wb_sc_range, bw_range=self.wb_bw_range, modulation=self.sig_modulation, sig_mode=self.sig_mode, gen_mode=self.sig_gen_mode, seed=self.seed[ant_id])
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

        print("Dot product of transmitted signals: ", np.dot(txtd_base[0], txtd_base[1]))

        return (txtd_base, txtd)


    def calibrate_rx_phase_offset(self, client_rfsoc):
        '''
        This function calibrates the phase offset between the receivers ports in RFSoCs
        '''
        input_ = input("Press Y for phase offset calibration (and position the TX/RX at AoA = 0) and anything to use the saved phase offset: ")

        if input_.lower()!='y':
            self.rx_phase_offset = np.load(self.calib_params_path)['rx_phase_offset']
            self.print("Using saved phase offset between RX ports: {:0.3f} Rad".format(self.rx_phase_offset), thr=1)
            return
        else:
            phase_diff_list = []
            for i in range(self.calib_iter):
                rxtd = client_rfsoc.receive_data(mode='once')
                rxtd = rxtd.squeeze(axis=0)
                phase_diff = self.calc_phase_offset(rxtd[0,:], rxtd[1,:])
                phase_diff_list.append(phase_diff)

            self.rx_phase_offset = np.mean(phase_diff_list)
            np.savez(self.calib_params_path, rx_phase_offset=self.rx_phase_offset)
            self.print("Calibrated phase offset between RX ports: {:0.3f} Rad".format(self.rx_phase_offset), thr=1)


    def save_signal_channel(self, client_tcp, txtd_base, save_list=[]):
        deconv_sys_response_main = self.deconv_sys_response
        self.deconv_sys_response = False

        # test = np.load(self.sig_save_path)
        txtd_save=[]
        rxtd_save=[]
        h_est_full_save=[]
        H_est_save=[]
        H_est_max_save=[]
        for i in range(self.n_save):
            time.sleep(0.01)
            print("Save Iteration: ", i+1)
            rxtd = client_tcp.receive_data(mode='once')
            rxtd = rxtd.squeeze(axis=0)
            (rxtd_base, h_est_full, H_est, H_est_max) = self.rx_operations(txtd_base, rxtd)
            txtd_save.append(txtd_base)
            rxtd_save.append(rxtd_base)
            h_est_full_save.append(h_est_full)
            H_est_save.append(H_est)
            H_est_max_save.append(H_est_max)

        txtd_save = np.array(txtd_save)
        rxtd_save = np.array(rxtd_save)
        h_est_full_save = np.array(h_est_full_save)
        H_est_save = np.array(H_est_save)
        H_est_max_save = np.array(H_est_max_save)

        h_est_full_avg = np.mean(h_est_full_save, axis=0)

        if 'signal' in save_list:
            np.savez(self.sig_save_path, txtd=txtd_save, rxtd=rxtd_save)
        if 'channel' in save_list:
            np.savez(self.channel_save_path, h_est_full=h_est_full_save, h_est_full_avg=h_est_full_avg, H_est=H_est_save, H_est_max=H_est_max_save)

        self.deconv_sys_response = deconv_sys_response_main
    

    def animate_plot(self, client_rfsoc, client_lintrack, client_piradio, txtd_base, plot_mode=['h', 'rxtd', 'rxfd'], plot_level=0):
        if self.plot_level<plot_level:
            return
        self.anim_paused = False
        self.fc_id = 0
        n_plots_row = len(plot_mode)
        n_plots_col = len(self.freq_hop_list)
        tx_ant_id = 0
        rx_ant_id = 1
        # n_samples_rx = self.n_samples_rx
        n_samples_rx = self.n_samples_trx
        n_samples_trx = self.n_samples_trx
        n_samples_rx01 = 100
        n_samples_ch = self.n_samples_ch

        def receive_data(txtd_base):
            rxtd = client_rfsoc.receive_data(mode='once')
            rxtd = rxtd.squeeze(axis=0)
            (rxtd_base, h_est_full, H_est, H_est_max) = self.rx_operations(txtd_base, rxtd)
            H_est_full = fft(h_est_full, axis=-1)
            sigs=[]
            for item in plot_mode:
                if item=='h':
                    h_est_full_ = h_est_full[rx_ant_id, tx_ant_id].copy()
                    im = np.argmax(h_est_full_)
                    h_est_full_ = np.roll(h_est_full_, -im + len(h_est_full_)//10)
                    h_est_full_ = self.lin_to_db(np.abs(h_est_full_), mode='mag')
                    # h_est_full_ = self.lin_to_db(np.abs(h_est_full_) / np.max(np.abs(h_est_full_)), mode='mag')
                    p = np.percentile(h_est_full_, 25)
                    h_est_full_ = h_est_full_ - p
                    sigs.append(h_est_full_)
                elif item=='H':
                    H_est_full_ = H_est_full[rx_ant_id, tx_ant_id]
                    sigs.append(self.lin_to_db(np.abs(fftshift(H_est_full_)), mode='mag'))
                elif item=='H_phase':
                    H_est_full_ = H_est_full[rx_ant_id, tx_ant_id]
                    phi = np.angle(fftshift(H_est_full_))
                    # phi = np.unwrap(phi)
                    sigs.append(phi)
                elif item=='rxtd':
                    sigs.append(rxtd_base[rx_ant_id, :n_samples_rx])
                elif item=='rxfd':
                    sigs.append(self.lin_to_db(np.abs(fftshift(fft(rxtd_base[rx_ant_id, :n_samples_rx]))), mode='mag'))
                elif item=='txtd':
                    sigs.append(txtd_base[tx_ant_id])
                elif item=='txfd':
                    sigs.append(self.lin_to_db(np.abs(fftshift(fft(txtd_base[tx_ant_id]))), mode='mag'))
                elif item=='rxtd01':
                    # phase_offset = self.calc_phase_offset(rxtd_base[0], rxtd_base[1])
                    # rxtd_base[0], rxtd_base[1] = self.adjust_phase(rxtd_base[0], rxtd_base[1], phase_offset)
                    # sigs.append([np.abs(rxtd_base[0,:n_samples_rx01]), np.abs(rxtd_base[1,:n_samples_rx01])])
                    # sigs.append([np.angle(rxtd_base[0,:n_samples_rx01]), np.angle(rxtd_base[1,:n_samples_rx01])])
                    sigs.append([np.imag(rxtd_base[0,:n_samples_rx01]), np.imag(rxtd_base[1,:n_samples_rx01])])
                elif item=='rxfd01':
                    rxfd_base_0 = self.lin_to_db(np.abs(fftshift(fft(rxtd_base[0, :n_samples_rx]))), mode='mag')
                    rxfd_base_1 = self.lin_to_db(np.abs(fftshift(fft(rxtd_base[1, :n_samples_rx]))), mode='mag')
                    sigs.append([rxfd_base_0, rxfd_base_1])
                elif item=='IQ':
                    rxfd_base = fftshift(fft(rxtd_base[rx_ant_id], axis=-1))
                    rxfd_base = rxfd_base[self.sc_range[0]+n_samples_rx//2:self.sc_range[1]+n_samples_rx//2+1]
                    # rxfd_base = rxfd_base[np.abs(rxfd_base)>1e-1]
                    sigs.append(rxfd_base)
                elif item=='rxtd_phase':
                    phi = np.angle(rxtd_base[rx_ant_id, :n_samples_rx])
                    # phi = np.unwrap(phi)
                    sigs.append(phi)
                elif item=='rxfd_phase':
                    phi = np.angle(fftshift(fft(rxtd_base[rx_ant_id, :n_samples_rx], axis=-1)))
                    # phi = np.unwrap(phi)
                    sigs.append(phi)
                elif item=='txtd_phase':
                    phi = np.angle(txtd_base[tx_ant_id])
                    # phi = np.unwrap(phi)
                    sigs.append(phi)
                elif item=='txfd_phase':
                    phi = np.angle(fftshift(fft(txtd_base[tx_ant_id], axis=-1)))
                    # phi = np.unwrap(phi)
                    sigs.append(phi)
                elif item=='trxtd_phase_diff':
                    phi = np.angle(rxtd_base[rx_ant_id,:self.n_samples_trx] * np.conj(txtd_base[tx_ant_id,:self.n_samples_trx]))
                    # phi = np.unwrap(phi)
                    sigs.append(phi)
                elif item=='trxfd_phase_diff':
                    phi = np.angle(fftshift(fft(rxtd_base[rx_ant_id,:self.n_samples_trx], axis=-1)) * np.conj(fftshift(fft(txtd_base[tx_ant_id,:self.n_samples_trx], axis=-1))))
                    # phi = np.unwrap(phi)
                    sigs.append(phi)
                elif item=='aoa_gauge':
                    aoa = self.estimate_mimo_params(txtd_base, rxtd_base, H_est_max)
                    sigs.append(aoa)
                else:
                    raise ValueError('Unsupported plot mode: ' + item)

            return (sigs)

        def toggle_pause(event):
            if event.key == 'p':  # Press 'p' to pause/resume
                self.anim_paused = not self.anim_paused

        def update(frame):
            if self.anim_paused:
                return line
            sigs = receive_data(txtd_base)
            
            if self.use_linear_track:
                client_lintrack.move(distance=-10)
                # time.sleep(0.1)
            if self.control_piradio:
                fc = self.freq_hop_list[int(self.fc_id)]
                # client_piradio.set_frequency(fc=fc)
                self.fc_id = (self.fc_id + 1) % len(self.freq_hop_list)
                # time.sleep(0.1)
            else:
                self.fc_id = 0

            line_id = 0
            for i in range(n_plots_row):
                j = self.fc_id
                if plot_mode[i]=='rxtd':
                    line[line_id][j].set_ydata(sigs[i].real)
                    line_id+=1
                    line[line_id][j].set_ydata(sigs[i].imag)
                    line_id+=1
                elif plot_mode[i]=='txtd':
                    line[line_id][j].set_ydata(sigs[i].real)
                    line_id+=1
                    line[line_id][j].set_ydata(sigs[i].imag)
                    line_id+=1
                elif plot_mode[i]=='rxtd01' or plot_mode[i]=='rxfd01':
                    line[line_id][j].set_ydata(sigs[i][0])
                    line_id+=1
                    line[line_id][j].set_ydata(sigs[i][1])
                    line_id+=1
                elif plot_mode[i]=='IQ':
                    line[line_id][j].set_offsets(np.column_stack((sigs[i].real, sigs[i].imag)))
                    line_id+=1
                    ax[i][j].set_xlim(min(sigs[i].real) - 0, max(sigs[i].real) + 0)
                    ax[i][j].set_ylim(min(sigs[i].imag) - 0, max(sigs[i].imag) + 0)
                elif plot_mode[i]=='aoa_gauge':
                    self.gauge_update_needle(ax[i][j], np.rad2deg(sigs[i]))
                    ax[i][j].set_xlim(0, 1)
                    ax[i][j].set_ylim(0.5, 1)
                    ax[i][j].axis('off')
                else:
                    line[line_id][j].set_ydata(sigs[i])
                    line_id+=1
                if plot_mode[i]!='IQ' and plot_mode[i]!='aoa_gauge':
                    ax[i][j].relim()
                if plot_mode[i]=='h':
                    ax[i][j].set_ylim(np.min(sigs[i]), 1.1*np.max(sigs[i]))
                if plot_mode[i]!='aoa_gauge':
                    ax[i][j].autoscale_view()

            return line


        # Set up the figure and plot
        sigs = receive_data(txtd_base)
        line = [[None for j in range(n_plots_col)] for i in range(2*n_plots_row)]
        fig, ax = plt.subplots(n_plots_row, n_plots_col)
        if type(ax) is not np.ndarray:
            ax = np.array([ax])
        if len(ax.shape)<2:
            ax = ax.reshape(-1, 1)
        fig.canvas.mpl_connect('key_press_event', toggle_pause)
        # fig, ax = plt.subplots(1, n_plots)

        for j in range(n_plots_col):
            line_id = 0
            for i in range(n_plots_row):
                # ax[i].set_autoscale_on(True)
                if plot_mode[i]=='h':
                    line[line_id][j], = ax[i][j].plot(self.t_trx[:n_samples_ch], sigs[i])
                    line_id+=1
                    ax[i][j].set_title("Channel-Mag-TD, Freq {}, TX ant {}, RX ant {}".format(self.freq_hop_list[j]/1e9, tx_ant_id, rx_ant_id))
                    ax[i][j].set_xlabel("Time (s)")
                    ax[i][j].set_ylabel("Normalized Magnitude (dB)")
                    # ax[i][j].set_xlim(np.min(self.t), np.max(self.t))
                    # ax[i][j].set_ylim(np.min(sigs[0]), 1.5*np.max(sigs[0]))
                    # ax[i][j].grid(0.2)
                elif plot_mode[i]=='H':
                    line[line_id][j], = ax[i][j].plot(self.freq_trx[(self.sc_range_ch[0]+n_samples_trx//2):(self.sc_range_ch[1]+n_samples_trx//2+1)], sigs[i])
                    line_id+=1
                    ax[i][j].set_title("Channel-Mag-FD, Freq {}GHz, TX ant {}, RX ant {}".format(self.freq_hop_list[j]/1e9, tx_ant_id, rx_ant_id))
                    ax[i][j].set_xlabel("Frequency (MHz)")
                    ax[i][j].set_ylabel("Magnitude (dB)")
                elif plot_mode[i]=='H_phase':
                    line[line_id][j], = ax[i][j].plot(self.freq_trx[(self.sc_range_ch[0]+n_samples_trx//2):(self.sc_range_ch[1]+n_samples_trx//2+1)], sigs[i])
                    line_id+=1
                    ax[i][j].set_title("Channel-Phase-FD, Freq {}GHz, TX ant {}, RX ant {}".format(self.freq_hop_list[j]/1e9, tx_ant_id, rx_ant_id))
                    ax[i][j].set_xlabel("Frequency (MHz)")
                    ax[i][j].set_ylabel("Phase (radians)")
                elif plot_mode[i]=='rxtd':
                    line[line_id][j], = ax[i][j].plot(self.t_rx[:n_samples_rx], sigs[i].real, label='I')
                    line_id+=1
                    line[line_id][j], = ax[i][j].plot(self.t_rx[:n_samples_rx], sigs[i].imag, label='Q')
                    line_id+=1
                    ax[i][j].set_title("RX-TD-IQ, Freq {}GHz, RX ant {}".format(self.freq_hop_list[j]/1e9, rx_ant_id))
                    ax[i][j].set_xlabel("Time (s)")
                    ax[i][j].set_ylabel("Magnitude")
                elif plot_mode[i]=='rxfd':
                    line[line_id][j], = ax[i][j].plot(self.freq_trx, sigs[i])
                    line_id+=1
                    ax[i][j].set_title("RX-FD, Freq {}GHz, RX ant {}".format(self.freq_hop_list[j]/1e9, rx_ant_id))
                    ax[i][j].set_xlabel("Freq (MHz)")
                    ax[i][j].set_ylabel("Magnitude (dB)")
                elif plot_mode[i]=='txtd':
                    line[line_id][j], = ax[i][j].plot(self.t_tx, sigs[i].real, label='I')
                    line_id+=1
                    line[line_id][j], = ax[i][j].plot(self.t_tx, sigs[i].imag, label='Q')
                    line_id+=1
                    ax[i][j].set_title("TX-TD-IQ, Freq {}GHz, TX ant {}".format(self.freq_hop_list[j]/1e9, tx_ant_id))
                    ax[i][j].set_xlabel("Time (s)")
                    ax[i][j].set_ylabel("Magnitude")
                elif plot_mode[i]=='txfd':
                    line[line_id][j], = ax[i][j].plot(self.freq_tx, sigs[i])
                    line_id+=1
                    ax[i][j].set_title("TX-FD, Freq {}GHz, TX ant {}".format(self.freq_hop_list[j]/1e9, tx_ant_id))
                    ax[i][j].set_xlabel("Freq (MHz)")
                    ax[i][j].set_ylabel("Magnitude (dB)")
                elif plot_mode[i]=='rxtd01':
                    line[line_id][j], = ax[i][j].plot(self.t_rx[:n_samples_rx01], sigs[i][0], label='Antenna 0')
                    line_id+=1
                    line[line_id][j], = ax[i][j].plot(self.t_rx[:n_samples_rx01], sigs[i][1], label='Antenna 1')
                    line_id+=1
                    ax[i][j].set_title("Aligned RX-TD, Freq {}GHz, RX ant 0-1".format(self.freq_hop_list[j]/1e9))
                    ax[i][j].set_xlabel("Time (s)")
                    ax[i][j].set_ylabel("Magnitude")
                elif plot_mode[i]=='rxfd01':
                    line[line_id][j], = ax[i][j].plot(self.freq_trx, sigs[i][0], label='Antenna 0')
                    line_id+=1
                    line[line_id][j], = ax[i][j].plot(self.freq_trx, sigs[i][1], label='Antenna 1')
                    line_id+=1
                    ax[i][j].set_title("Aligned RX-FD, Freq {}GHz, RX ant 0-1".format(self.freq_hop_list[j]/1e9))
                    ax[i][j].set_xlabel("Freq (MHz)")
                    ax[i][j].set_ylabel("Magnitude (dB)")
                elif plot_mode[i]=='IQ':
                    line[line_id][j] = ax[i][j].scatter(sigs[i].real, sigs[i].imag, facecolors='none', edgecolors='b', s=100)
                    line_id+=1
                    # ax[i][j].set_xlim([-3, 3])
                    # ax[i][j].set_ylim([-3, 3])
                    ax[i][j].set_title("RX Constellation, Freq {}GHz, RX ant {}".format(self.freq_hop_list[j]/1e9, rx_ant_id))
                    ax[i][j].set_xlabel("In-phase (I)")
                    ax[i][j].set_ylabel("Quadrature (Q)")
                    ax[i][j].axhline(0, color='black',linewidth=0.5)
                    ax[i][j].axvline(0, color='black',linewidth=0.5)
                    ax[i][j].set_aspect('equal')
                    ax[i][j].set_xlim(min(sigs[i].real)-0, max(sigs[i].real-0))
                    ax[i][j].set_ylim(min(sigs[i].imag)-0, max(sigs[i].imag-0))
                elif plot_mode[i]=='rxtd_phase':
                    line[line_id][j], = ax[i][j].plot(self.t_rx[:n_samples_rx], sigs[i])
                    line_id+=1
                    ax[i][j].set_title("RX-Phase-TD, Freq {}GHz, RX ant {}".format(self.freq_hop_list[j]/1e9, rx_ant_id))
                    ax[i][j].set_xlabel("Time (s)")
                    ax[i][j].set_ylabel("Phase (radians)")
                elif plot_mode[i]=='rxfd_phase':
                    line[line_id][j], = ax[i][j].plot(self.freq_trx, sigs[i])
                    line_id+=1
                    ax[i][j].set_title("RX-Phase-FD, Freq {}GHz, RX ant {}".format(self.freq_hop_list[j]/1e9, rx_ant_id))
                    ax[i][j].set_xlabel("Freq (MHz)")
                    ax[i][j].set_ylabel("Phase (radians)")
                elif plot_mode[i]=='txtd_phase':
                    line[line_id][j], = ax[i][j].plot(self.t_tx, sigs[i])
                    line_id+=1
                    ax[i][j].set_title("TX-Phase-TD, Freq {}GHz, TX ant {}".format(self.freq_hop_list[j]/1e9, tx_ant_id))
                    ax[i][j].set_xlabel("Time (s)")
                    ax[i][j].set_ylabel("Phase (radians)")
                elif plot_mode[i]=='txfd_phase':
                    line[line_id][j], = ax[i][j].plot(self.freq_tx, sigs[i])
                    line_id+=1
                    ax[i][j].set_title("RX-Phase-FD, Freq {}GHz, TX ant {}".format(self.freq_hop_list[j]/1e9, tx_ant_id))
                    ax[i][j].set_xlabel("Freq (MHz)")
                    ax[i][j].set_ylabel("Phase (radians)")
                elif plot_mode[i]=='trxtd_phase_diff':
                    line[line_id][j], = ax[i][j].plot(self.t_trx, sigs[i])
                    line_id+=1
                    ax[i][j].set_title("TRX-Phase Diff-TD, Freq {}GHz, TX ant {}, RX ant {}".format(self.freq_hop_list[j]/1e9, tx_ant_id, rx_ant_id))
                    ax[i][j].set_xlabel("Time (s)")
                    ax[i][j].set_ylabel("Phase (radians)")
                elif plot_mode[i]=='trxfd_phase_diff':
                    line[line_id][j], = ax[i][j].plot(self.freq_trx, sigs[i])
                    line_id+=1
                    ax[i][j].set_title("TRX-Phase Diff-FD, Freq {}GHz, TX ant {}, RX ant {}".format(self.freq_hop_list[j]/1e9, tx_ant_id, rx_ant_id))
                    ax[i][j].set_xlabel("Freq (MHz)")
                    ax[i][j].set_ylabel("Phase (radians)")
                elif plot_mode[i]=='aoa_gauge':
                    self.draw_half_gauge(ax[i][j], min_val=-90, max_val=90)
                    self.gauge_update_needle(ax[i][j], 0, min_val=-90, max_val=90)
                    ax[i][j].set_xlim(0, 1)
                    ax[i][j].set_ylim(0.5, 1)
                    ax[i][j].axis('off')
                # ax[i].autoscale()
                ax[i][j].grid(True)
                if plot_mode[i]!='IQ':
                    ax[i][j].relim()
                ax[i][j].autoscale_view()
                ax[i][j].minorticks_on()
                ax[i][j].legend()

        # Create the animation
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.4, wspace=0.4)
        anim = animation.FuncAnimation(fig, update, frames=1000000000, interval=self.anim_interval, blit=False)
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

        if 'filter' in self.rx_chain:
            for ant_id in range(self.n_rx_ant):
                cf = (self.filter_bw_range[0]+self.filter_bw_range[1])/2
                cutoff = self.filter_bw_range[1] - self.filter_bw_range[0]
                rxtd_base[ant_id,:] = self.filter(rxtd_base[ant_id,:], center_freq=cf, cutoff=cutoff, fil_order=64, plot=False)

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


        txtd_base = txtd_base[:,:self.n_samples_trx]
        if 'integrate' in self.rx_chain:
            rxtd_base = self.integrate_signal(rxtd_base, n_samples=self.n_samples_trx)
        rxtd_base = rxtd_base[:,:self.n_samples_trx]

        if 'sync_time' in self.rx_chain:
            rxtd_base_s = self.sync_time(rxtd_base, txtd_base, sc_range=self.sc_range)
        else:
            rxtd_base_s = rxtd_base.copy()
            rxtd_base_s = np.stack((rxtd_base_s, rxtd_base_s), axis=0)
        
        if 'sync_freq' in self.rx_chain:
            cfo_coarse = self.estimate_cfo(txtd_base, rxtd_base_s, mode='coarse', sc_range=self.sc_range)
            rxtd_base_t = self.sync_frequency(rxtd_base_s, cfo_coarse, mode='time')
            cfo_fine = self.estimate_cfo(txtd_base, rxtd_base_t, mode='fine', sc_range=self.sc_range)
            cfo = cfo_coarse + cfo_fine
            rxtd_base_s = self.sync_frequency(rxtd_base_s, cfo, mode='time')

        rxtd_base = np.stack((rxtd_base_s[0,0,:self.n_samples_trx], rxtd_base_s[1,1,:self.n_samples_trx]), axis=0)

        if 'channel_est' in self.rx_chain:
            if self.deconv_sys_response:
                sys_response = np.load(self.sys_response_path)['h_est_full_avg']
            else:
                sys_response = None
            snr_est = self.db_to_lin(self.snr_est_db, mode='pow')
            h_est_full, H_est, H_est_max = self.channel_estimate(txtd_base, rxtd_base_s, sys_response=sys_response, sc_range_ch=self.sc_range_ch, snr_est=snr_est)
            self.estimate_mimo_params(txtd_base, rxtd_base, H_est_max)
        else:
            h_est_full, H_est, H_est_max = (None, None, None)

        if 'channel_eq' in self.rx_chain and 'channel_est' in self.rx_chain:
            rxtd_base = self.channel_equalize(txtd_base, rxtd_base, h_est_full, H_est, sc_range=self.sc_range, sc_range_ch=self.sc_range_ch, null_sc_range=self.null_sc_range, n_rx_ch_eq=self.n_rx_ch_eq)
        
        return (rxtd_base, h_est_full, H_est, H_est_max)
    


