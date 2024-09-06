from backend import *
from backend import be_np as np, be_scp as scipy
try:
    from rfsoc import RFSoC
except:
    pass
from signal_utilsrfsoc import Signal_Utils_Rfsoc
from tcp_comm import Tcp_Comm




class Params_Class(object):
    def __init__(self):
        # parser = argparse.ArgumentParser()
        # parser.add_argument("--bit_file_path", type=str, default="./rfsoc.bit", help="Path to the bit file")
        # parser.add_argument("--fs", type=float, default=245.76e6*4, help="sampling frequency used in signal processings")
        # parser.add_argument("--fc", type=float, default=57.51e9, help="carrier frequency")
        # parser.add_argument("--fs_tx", type=float, default=245.76e6*4, help="DAC sampling frequency")
        # parser.add_argument("--fs_rx", type=float, default=245.76e6*4, help="ADC sampling frequency")
        # parser.add_argument("--n_samples", type=int, default=1024, help="Number of samples")
        # parser.add_argument("--nfft", type=int, default=1024, help="Number of FFT points")
        # parser.add_argument("--sig_modulation", type=str, default='qam', help="Singal modulation type for sounding, qam or empty")
        # parser.add_argument("--mix_phase_off", type=float, default=0.0, help="Mixer's phase offset")
        # parser.add_argument("--sig_path", type=str, default='./txtd.npy', help="Signal path to load")
        # parser.add_argument("--wb_null_sc", type=int, default=10, help="Number of carriers to null in the wideband signal")
        # parser.add_argument("--TCP_port_Cmd", type=int, default=8080, help="Commands TCP port")
        # parser.add_argument("--TCP_port_Data", type=int, default=8081, help="Data TCP port")
        # parser.add_argument("--mix_freq", type=float, default=1000e6, help="Mixer carrier frequency")
        # parser.add_argument("--mixer_mode", type=str, default='analog', help="Mixer mode, analog or digital")
        # parser.add_argument("--do_mixer_settings", action="store_true", default=False, help="If true, performs mixer settings")
        # parser.add_argument("--sig_mode", type=str, default='wideband', help="Signal mode, tone_1 or tone_2 or wideband or wideband_null or load")
        # parser.add_argument("--sig_gen_mode", type=str, default='fft', help="signal generation mode, time, or fft or ofdm, or ZadoffChu")
        # parser.add_argument("--wb_bw", type=float, default=900e6, help="Wideband signal bandwidth")
        # parser.add_argument("--f_tone", type=float, default=20e6, help="Tone signal frequency")         # 16.4e6 * 2 for function generator
        # parser.add_argument("--do_pll_settings", action="store_true", default=False, help="If true, performs PLL settings")
        # parser.add_argument("--filter_signal", action="store_true", default=False, help="If true, performs filtering on the RX signal")
        # parser.add_argument("--filter_bw", type=float, default=900e6, help="Final filter BW on the RX signal")
        # parser.add_argument("--project", type=str, default='sounder_if_ddr4', help="Project to use, sounder_bbf_ddr4 or sounder_if_ddr4 or sounder_bbf or sounder_if")
        # parser.add_argument("--board", type=str, default='rfsoc_4x2', help="Board to use")
        # parser.add_argument("--RFFE", type=str, default='piradio', help="RF front end to use, piradio or sivers")
        # parser.add_argument("--lmk_freq_mhz", type=float, default=122.88, help="LMK frequency in MHz")
        # parser.add_argument("--lmx_freq_mhz", type=float, default=3932.16, help="LMX frequency in MHz")
        # parser.add_argument("--seed", type=int, default=100, help="Seed for random operations")
        # parser.add_argument("--run_tcp_server", action="store_true", default=False, help="If true, runs the TCP server")
        # parser.add_argument("--plot_level", type=int, default=0, help="level of plotting outputs")
        # parser.add_argument("--verbose_level", type=int, default=0, help="level of printing output")
        # parser.add_argument("--mode", type=str, default='server', help="mode of operation, server or client_tx or client_rx")
        # parser.add_argument("--server_ip", type=str, default='192.168.1.3', help="RFSoC board IP as the server")
        # parser.add_argument("--n_frame_wr", type=int, default=1, help="Number of frames to write")
        # parser.add_argument("--n_frame_rd", type=int, default=1, help="Number of frames to read")
        # parser.add_argument("--overwrite_configs", action="store_true", default=False, help="If true, overwrites configurations")
        # parser.add_argument("--send_signal", action="store_true", default=False, help="If true, sends TX signal")
        # parser.add_argument("--recv_signal", action="store_true", default=False, help="If true, receives and plots EX signal")
        # params = parser.parse_args()
        params = SimpleNamespace()
        params.overwrite_configs=True

        if params.overwrite_configs:
            self.fs=245.76e6 * 4
            self.fc = 57.51e9
            self.fs_tx=self.fs
            self.fs_rx=self.fs
            self.n_samples=1024
            self.nfft=self.n_samples
            self.sig_modulation='qam'
            self.mix_phase_off=0.0
            self.sig_path=os.path.join(os.getcwd(), 'txtd.npy')
            self.wb_null_sc=10
            self.tcp_localIP = "0.0.0.0"
            self.tcp_bufferSize=2**10
            self.TCP_port_Cmd=8080
            self.TCP_port_Data=8081
            self.lmk_freq_mhz=122.88
            self.lmx_freq_mhz=3932.16
            self.filter_bw=900e6
            self.seed=100
            self.mixer_mode='analog'
            self.RFFE='piradio'
            self.filter_signal=False

            self.mix_freq=1000e6
            self.do_mixer_settings=False
            self.do_pll_settings=False
            self.n_frame_wr=1
            self.n_frame_rd=1
            self.run_tcp_server=True
            self.send_signal=True
            self.recv_signal=True

            self.bit_file_path=os.path.join(os.getcwd(), 'project_v1-0-21_20240822-164647.bit')
            self.project='sounder_if_ddr4'
            self.board='rfsoc_4x2'
            self.mode='client_rx'
            self.sig_mode='wideband'
            self.sig_gen_mode = 'ZadoffChu'
            self.wb_bw=500e6
            self.f_tone=5.0 * self.fs_tx / self.nfft #30e6
            self.server_ip='192.168.3.1'
            self.plot_level=0
            self.verbose_level=0
            


        self.n_samples_tx = self.n_frame_wr*self.n_samples
        self.n_samples_rx = self.n_frame_rd*self.n_samples
        self.nfft_tx = self.n_frame_wr*self.nfft
        self.nfft_rx = self.n_frame_rd*self.nfft
        self.freq = ((np.arange(0, self.nfft) / self.nfft) - 0.5) * self.fs / 1e6
        self.freq_tx = ((np.arange(0, self.nfft_tx) / self.nfft_tx) - 0.5) * self.fs_tx / 1e6
        self.freq_rx = ((np.arange(0, self.nfft_rx) / self.nfft_rx) - 0.5) * self.fs_rx / 1e6
        self.beam_test = np.array([1, 5, 9, 13, 17, 21, 25, 29, 32, 35, 39, 43, 47, 51, 55, 59, 63])
        self.DynamicPLLConfig = (0, self.lmk_freq_mhz, self.lmx_freq_mhz)
        if self.mixer_mode=='digital' and self.mix_freq!=0:
            self.mix_freq_dac = 0
            self.mix_freq_adc = 0
        elif self.mixer_mode == 'analog':
            self.mix_freq_dac = self.mix_freq
            self.mix_freq_adc = self.mix_freq
        else:
            self.mix_freq_dac = 0
            self.mix_freq_adc = 0
        if self.sig_mode=='wideband' or self.sig_mode=='wideband_null':
            self.filter_bw = min(self.wb_bw + 100e6, self.fs_rx-50e6)
        else:
            self.filter_bw = min(2*np.abs(self.f_tone) + 60e6, self.fs_rx-50e6)
        if 'sounder_bbf' in self.project:
            self.do_mixer_settings=False
            self.do_pll_settings=False
        if self.board == "rfsoc_4x2":
            self.do_pll_settings=False
        
        if self.board=='rfsoc_2x2':
            self.adc_bits = 12
            self.dac_bits = 14
        elif self.board=='rfsoc_4x2':
            self.adc_bits = 14
            self.dac_bits = 14

        if 'tone' in self.sig_mode:
            self.f_max = abs(self.f_tone)
        elif 'wideband' in self.sig_mode:
            self.f_max = abs(self.wb_bw/2)
        elif self.sig_mode == 'load':
            self.f_max = abs(self.wb_bw/2)
        else:
            raise ValueError('Unsupported signal mode: ' + self.sig_mode)





def rfsoc_run(params):
    signals_inst = Signal_Utils_Rfsoc(params)
    (txtd_base, txtd) = signals_inst.gen_tx_signal()


    if params.mode=='server':
        rfsoc_inst = RFSoC(params)
        rfsoc_inst.txtd = txtd
        if params.send_signal:
            rfsoc_inst.send_frame(txtd)
        if params.recv_signal:
            rfsoc_inst.recv_frame_one(n_frame=params.n_frame_rd)
            signals_inst.rx_operations(txtd_base, rfsoc_inst.rxtd)
        if params.run_tcp_server:
            rfsoc_inst.run()


    elif params.mode=='client_tx':
        client_inst=Tcp_Comm(params)
        client_inst.init_tcp_client()
        client_inst.transmit_data()
        if params.RFFE=='sivers':
            client_inst.set_mode('RXen0_TXen1')
            client_inst.set_frequency(params.fc)
            client_inst.set_tx_gain()


    elif params.mode=='client_rx':
        client_inst=Tcp_Comm(params)
        client_inst.init_tcp_client()
        if params.RFFE=='sivers':
            client_inst.set_mode('RXen1_TXen0')
            client_inst.set_frequency(params.fc)
            client_inst.set_rx_gain()

        signals_inst.animate_plot(client_inst, txtd_base, plot_level=0)
        
        


if __name__ == '__main__':
    
    params = Params_Class()
    rfsoc_run(params)
