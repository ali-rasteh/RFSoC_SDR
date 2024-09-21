from backend import *
from backend import be_np as np, be_scp as scipy
from signal_utils import Signal_Utils




class Signal_Utils_Rfsoc(Signal_Utils):
    def __init__(self, params):
        super().__init__(params)

        self.f_max = params.f_max
        self.filter_signal = params.filter_signal
        self.sig_mode = params.sig_mode
        self.wb_bw = params.wb_bw
        self.f_tone = params.f_tone
        self.sig_modulation = params.sig_modulation
        self.sig_gen_mode = params.sig_gen_mode
        self.sig_path = params.sig_path
        self.mixer_mode = params.mixer_mode
        self.mix_freq = params.mix_freq
        self.filter_bw = params.filter_bw
        self.n_tx_ant = params.n_tx_ant
        self.n_rx_ant = params.n_rx_ant

        self.print("signals object initialization done", thr=1)
        

    def gen_tx_signal(self):
        txtd_base = []
        txtd = []
        for ant_id in range(self.n_tx_ant):
            if 'tone' in self.sig_mode:
                txtd_base_s = self.generate_tone(f=self.f_tone, sig_mode=self.sig_mode, gen_mode=self.sig_gen_mode)
            elif 'wideband' in self.sig_mode:
                txtd_base_s = self.generate_wideband(bw=self.wb_bw, modulation=self.sig_modulation, sig_mode=self.sig_mode, gen_mode=self.sig_gen_mode)
            elif self.sig_mode == 'load':
                txtd_base_s = np.load(self.sig_path)
            else:
                raise ValueError('Unsupported signal mode: ' + self.sig_mode)
            txtd_base_s /= np.max([np.abs(txtd_base_s.real), np.abs(txtd_base_s.imag)])
            txtd_base.append(txtd_base_s)

            title = 'TX signal spectrum in base-band for antenna {}'.format(ant_id)
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            self.plot_signal(x=self.freq_tx, sigs=txtd_base[ant_id], mode='fft', scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)
            title = 'Base-band TX signal (real) in time domain at \n the time transition for antenna {}'.format(ant_id)
            xlabel = 'Time (s)'
            ylabel = 'Magnitude'
            n=int(np.round(self.fs_tx/self.f_max))
            t=self.t_tx[:2*n]
            sig=np.concatenate((txtd_base[ant_id].real[-n:], txtd_base[ant_id].real[:n]))
            self.plot_signal(x=t, sigs=sig, mode='time', scale='linear', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)

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

        txtd_base = np.array(txtd_base)
        txtd = np.array(txtd)

        return (txtd_base, txtd)


    def animate_plot(self, client_inst, txtd_base, plot_mode='h_rxtd_rxfd', plot_level=0):
        if self.plot_level<plot_level:
            return
        plt_sig_id = 0
        tx_ant_id = 0
        rx_ant_id = 0
        
        def receive_data():
            rxtd = client_inst.receive_data(mode='once')
            rxtd = rxtd.squeeze(axis=0)
            (rxtd_base, h_est) = self.rx_operations(txtd_base, rxtd)
            rxtd_base = rxtd_base[:self.n_samples]
            rxfd_base = np.abs(fftshift(fft(rxtd_base[plt_sig_id])))
            H_est = np.abs(fftshift(fft(h_est)))
            sigs=[]
            if plot_mode=='h_H_rxfd':
                sigs.append(self.lin_to_db(np.abs(h_est) / np.max(np.abs(h_est)), mode='mag'))
                sigs.append(self.lin_to_db(H_est, mode='mag'))
                sigs.append(self.lin_to_db(rxfd_base, mode='mag'))
            elif plot_mode=='h_rxtd_rxfd':
                sigs.append(self.lin_to_db(np.abs(h_est) / np.max(np.abs(h_est)), mode='mag'))
                sigs.append(rxtd_base[plt_sig_id])
                sigs.append(self.lin_to_db(rxfd_base, mode='mag'))

            return (sigs)

        def update(frame):
            sigs = receive_data()
            line1.set_ydata(sigs[0])
            ax1.relim()
            ax1.autoscale_view()
            if plot_mode=='h_rxtd_rxfd':
                line2.set_ydata(sigs[1].real)
                line3.set_ydata(sigs[1].imag)
            elif plot_mode=='h_H_rxfd':
                line2.set_ydata(sigs[1])
            ax2.relim()
            ax2.autoscale_view()
            line4.set_ydata(sigs[2])
            ax3.relim()
            ax3.autoscale_view()

            if plot_mode=='h_H_rxfd':
                return line1, line2, line4
            elif plot_mode=='h_rxtd_rxfd':
                return line1, line2, line3, line4

        # Set up the figure and plot
        sigs = receive_data()
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
        # fig, (ax1, ax2, ax3) = plt.subplots(1, 3)

        line1, = ax1.plot(self.t, sigs[0])
        ax1.set_title("Channel response in the time domain \n between TX antenna {} and RX antenna {}".format(tx_ant_id, rx_ant_id))
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Normalized Magnitude (dB)")
        ax1.autoscale()
        # ax1.set_xlim(np.min(self.t), np.max(self.t))
        # ax1.set_ylim(np.min(sigs[0]), 1.5*np.max(sigs[0]))
        ax1.minorticks_on()
        # ax1.grid(0.2)

        if plot_mode=='h_rxtd_rxfd':
            line2, = ax2.plot(self.t, sigs[1].real, label='I')
            line3, = ax2.plot(self.t, sigs[1].imag, label='Q')
            ax2.set_title("RX signal in time domain (I and Q) for antenna {}".format(plt_sig_id))
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("Magnitude")
        elif plot_mode=='h_H_rxfd':
            line2, = ax2.plot(self.freq, sigs[1])
            ax2.set_title("Channel response in the frequency domain between TX antenna {} and RX antenna {}".format(tx_ant_id, rx_ant_id))
            ax2.set_xlabel("Frequency (MHz)")
            ax2.set_ylabel("Magnitude (dB)")
        ax2.legend()
        ax2.autoscale()
        ax2.minorticks_on()

        line4, = ax3.plot(self.freq, sigs[2])
        ax3.set_title("RX signal spectrum for antenna {}".format(plt_sig_id))
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

        h_est = self.channel_estimate(txtd_base, rxtd_base)
        # h_est = self.channel_estimate_eq(txtd_base, rxtd_base)

        for ant_id in range(self.n_rx_ant):
            # n_samples = min(len(txtd_base), len(rxtd_base))
            txfd_base = np.abs(fftshift(fft(txtd_base[ant_id,:self.n_samples])))
            rxfd_base = np.abs(fftshift(fft(rxtd_base[ant_id,:self.n_samples])))

            title = 'TX and RX signals spectrum in base-band for antenna {}'.format(ant_id)
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            scale = np.max(txfd_base)/np.max(rxfd_base)
            self.print("TX to RX spectrum scale for antenna {}: {:0.3f}".format(ant_id, scale), thr=5)
            xlim=(-2*self.f_max/1e6, 2*self.f_max/1e6)
            f1=np.abs(self.freq - xlim[0]).argmin()
            f2=np.abs(self.freq - xlim[1]).argmin()
            ylim=(np.min(rxfd_base[f1:f2]*scale), 1.1*np.max(rxfd_base[f1:f2]*scale))
            self.plot_signal(x=self.freq, sigs={"txfd_base":txfd_base, "Scaled rxfd_base":rxfd_base*scale}, scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, xlim=xlim, ylim=ylim, legend=True, plot_level=5)
            self.print("txfd_base max freq for antenna {}: {} MHz".format(ant_id, self.freq[(self.nfft>>1)+np.argmax(txfd_base[self.nfft>>1:])]), thr=5)
            self.print("rxfd_base max freq for antenna {}: {} MHz".format(ant_id, self.freq[(self.nfft>>1)+np.argmax(rxfd_base[self.nfft>>1:])]), thr=5)

        return (rxtd_base, h_est)

