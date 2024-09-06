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

        self.print("signals object initialization done", thr=1)
        

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
        n=int(np.round(self.fs_tx/self.f_max))
        t=self.t_tx[:2*n]
        sig=np.concatenate((txtd_base.real[-n:], txtd_base.real[:n]))
        self.plot_signal(x=t, sigs=sig, mode='time', scale='linear', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)

        if self.mixer_mode=='digital' and self.mix_freq!=0:
            txtd = self.freq_shift(txtd_base, shift=self.mix_freq, fs=self.fs_tx)

            # txfd = np.abs(fftshift(fft(txtd)))
            title = 'TX signal spectrum after upconversion'
            xlabel = 'Frequency (MHz)'
            ylabel = 'Magnitude (dB)'
            self.plot_signal(x=self.freq_tx, sigs=txtd, mode='fft', scale='dB20', title=title, xlabel=xlabel, ylabel=ylabel, plot_level=4)
        else:
            txtd = txtd_base.copy()
            # txfd = txfd_base.copy()

        return (txtd_base, txtd)


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
        n = 4*int(np.round(self.fs_rx/self.f_max))
        self.plot_signal(x=self.t_rx[:n], sigs=rxtd[:n], mode='time_IQ', scale='linear', title=title, xlabel=xlabel, ylabel=ylabel, legend=True, plot_level=5)


        if self.mixer_mode == 'digital' and self.mix_freq!=0:    
            rxtd_base = self.freq_shift(rxtd, shift=-1*self.mix_freq, fs=self.fs_rx)
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

