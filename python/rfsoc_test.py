from backend import *
from backend import be_np as np, be_scp as scipy
try:
    from rfsoc import RFSoC
except:
    pass
from signal_utilsrfsoc import Signal_Utils_Rfsoc
from signal_utils import Signal_Utils
from tcp_comm import Tcp_Comm_RFSoC, Tcp_Comm_LinTrack




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
        # parser.add_argument("--wb_bw_range", type=float, default=[-450e6,450e6], help="Wideband signal bandwidth range")
        # parser.add_argument("--f_tone", type=float, default=20e6, help="Tone signal frequency")         # 16.4e6 * 2 for function generator
        # parser.add_argument("--do_pll_settings", action="store_true", default=False, help="If true, performs PLL settings")
        # parser.add_argument("--filter_signal", action="store_true", default=False, help="If true, performs filtering on the RX signal")
        # parser.add_argument("--filter_bw_range", type=float, default=[-450e6, 450e6], help="Final filter BW range on the RX signal")
        # parser.add_argument("--project", type=str, default='sounder_if_ddr4', help="Project to use, sounder_bbf_ddr4 or sounder_if_ddr4 or sounder_bbf or sounder_if")
        # parser.add_argument("--board", type=str, default='rfsoc_4x2', help="Board to use")
        # parser.add_argument("--RFFE", type=str, default='piradio', help="RF front end to use, piradio or sivers")
        # parser.add_argument("--lmk_freq_mhz", type=float, default=122.88, help="LMK frequency in MHz")
        # parser.add_argument("--lmx_freq_mhz", type=float, default=3932.16, help="LMX frequency in MHz")
        # parser.add_argument("--seed", type=int, default=100, help="Seed for random operations")
        # parser.add_argument("--run_tcp_server", action="store_true", default=False, help="If true, runs the TCP server")
        # parser.add_argument("--plot_level", type=int, default=0, help="level of plotting outputs")
        # parser.add_argument("--verbose_level", type=int, default=0, help="level of printing output")
        # parser.add_argument("--mode", type=str, default='server', help="mode of operation, server or client")
        # parser.add_argument("--rfsoc_server_ip", type=str, default='192.168.1.3', help="RFSoC board IP as the server")
        # parser.add_argument("--lintrack_server_ip", type=str, default='0.0.0.0', help="Linear track controller board IP as the server")
        # parser.add_argument("--n_frame_wr", type=int, default=1, help="Number of frames to write")
        # parser.add_argument("--n_frame_rd", type=int, default=1, help="Number of frames to read")
        # parser.add_argument("--n_tx_ant", type=int, default=1, help="Number transmitter antennas")
        # parser.add_argument("--n_rx_ant", type=int, default=1, help="Number of receiver antennas")
        # parser.add_argument("--overwrite_configs", action="store_true", default=False, help="If true, overwrites configurations")
        # parser.add_argument("--send_signal", action="store_true", default=False, help="If true, sends TX signal")
        # parser.add_argument("--recv_signal", action="store_true", default=False, help="If true, receives and plots EX signal")
        # params = parser.parse_args()
        params = SimpleNamespace()
        params.overwrite_configs=True

        if params.overwrite_configs:
            self.fs=245.76e6 * 4
            self.fc = 57.51e9
            self.wl = constants.c / self.fc
            self.fs_tx=self.fs
            self.fs_rx=self.fs
            self.fs_trx=self.fs
            self.n_samples=1024
            self.nfft=self.n_samples
            self.mix_phase_off=0.0
            self.sig_path=os.path.join(os.getcwd(), 'sigs/txtd.npy')
            self.sig_save_path=os.path.join(os.getcwd(), 'sigs/mimo_trx.npz')
            self.channel_save_path=os.path.join(os.getcwd(), 'channels/channel_response.npz')
            self.sys_response_path=self.channel_save_path
            self.wb_null_sc=10
            self.tcp_localIP = "0.0.0.0"
            self.tcp_bufferSize=2**10
            self.TCP_port_Cmd=8080
            self.TCP_port_Data=8081
            self.lmk_freq_mhz=122.88
            self.lmx_freq_mhz=3932.16
            self.filter_bw_range=[-450e6,450e6]
            self.seed=100
            self.mixer_mode='analog'
            self.RFFE='piradio'

            self.mix_freq=1000e6
            self.do_mixer_settings=False
            self.do_pll_settings=False
            self.n_frame_wr=1
            self.run_tcp_server=True
            self.send_signal=True
            self.recv_signal=True
            self.rfsoc_server_ip='192.168.3.1'
            self.lintrack_server_ip='10.18.239.141'
            self.ant_dim = 1
            self.ant_dx = 0.5             # Antenna spacing in wavelengths (lambda)
            self.ant_dy = 0.5
            self.sig_modulation = '4qam'
            self.bit_file_path=os.path.join(os.getcwd(), 'project_v1-0-58_20241001-150336.bit')
            self.project='sounder_if_ddr4'
            self.board='rfsoc_4x2'
            self.n_tx_ant=2
            self.n_rx_ant=2
            self.sig_gen_mode = 'fft'
            self.wb_bw_mode='sc'    # sc or freq
            self.wb_bw_range=[-250e6,250e6]
            self.tone_f_mode='sc'    # sc or freq
            self.sc_tone=10
            self.f_tone=10.0 * self.fs_tx / self.nfft
            self.mode='server'
            self.overwrite_level=True
            self.plot_level=0
            self.verbose_level=0
            self.sig_mode='wideband'
            self.steer_theta_deg = 0        # Desired steering elevation in degrees
            self.n_save = 100
            self.sig_gain_db=0
            self.filter_signal=False

            self.n_frame_rd=1
            self.use_linear_track=False
            self.animate_plot_mode=['rxfd', 'h', "H"]
            self.wb_sc_range=[-250,250]
            self.beamforming=False
            self.steer_phi_deg = 30        # Desired steering azimuth in degrees
            self.save_list = []           # signal or channel
            self.deconv_sys_response = True
            


        system_info = platform.uname()
        if "pynq" in system_info.node.lower():
            self.mode = 'server'
            if self.overwrite_level:
                self.plot_level=5
                self.verbose_level=4
                self.use_linear_track=False
        else:
            self.mode = 'client'
            if self.overwrite_level:
                self.plot_level=0
                self.verbose_level=1
        self.server_ip = None
        self.steer_phi_rad = np.deg2rad(self.steer_phi_deg)
        self.steer_theta_rad = np.deg2rad(self.steer_theta_deg)
        self.n_samples_tx = self.n_frame_wr*self.n_samples
        self.n_samples_rx = self.n_frame_rd*self.n_samples
        self.n_samples_trx = min(self.n_samples_tx, self.n_samples_rx)
        self.nfft_tx = self.n_frame_wr*self.nfft
        self.nfft_rx = self.n_frame_rd*self.nfft
        self.nfft_trx = min(self.nfft_tx, self.nfft_rx)
        self.freq = ((np.arange(0, self.nfft) / self.nfft) - 0.5) * self.fs / 1e6
        self.freq_tx = ((np.arange(0, self.nfft_tx) / self.nfft_tx) - 0.5) * self.fs_tx / 1e6
        self.freq_rx = ((np.arange(0, self.nfft_rx) / self.nfft_rx) - 0.5) * self.fs_rx / 1e6
        self.freq_trx = ((np.arange(0, self.nfft_trx) / self.nfft_trx) - 0.5) * self.fs_trx / 1e6
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
            
        if 'sounder_bbf' in self.project:
            self.do_mixer_settings=False
            self.do_pll_settings=False
            self.n_tx_ant=1
            self.n_rx_ant=1
        if self.board == "rfsoc_4x2":
            self.do_pll_settings=False
        
        if self.board=='rfsoc_2x2':
            self.adc_bits = 12
            self.dac_bits = 14
        elif self.board=='rfsoc_4x2':
            self.adc_bits = 14
            self.dac_bits = 14

        if self.tone_f_mode=='sc':
            self.f_tone = self.sc_tone * self.fs_tx/self.nfft_tx
        elif self.tone_f_mode=='freq':
            self.sc_tone = int(np.round((self.f_tone)*self.nfft_tx/self.fs_tx))
        else:
            raise ValueError('Invalid tone_f_mode mode: ' + self.tone_f_mode)
        
        if self.wb_bw_mode=='sc':
            self.wb_bw_range = [self.wb_sc_range[0]*self.fs_tx/self.nfft_tx, self.wb_sc_range[1]*self.fs_tx/self.nfft_tx]
        elif self.wb_bw_mode=='freq':
            self.wb_sc_range = [int(np.round(self.wb_bw_range[0]*self.nfft_tx/self.fs_tx)), int(np.round(self.wb_bw_range[1]*self.nfft_tx/self.fs_tx))]
        else:
            raise ValueError('Invalid wb_bw_mode mode: ' + self.tone_f_mode)

        if 'tone' in self.sig_mode:
            self.f_max = abs(self.f_tone)
            if self.sig_mode == 'tone_1':
                self.sc_range = [self.sc_tone, self.sc_tone]
                # self.filter_bw_range = min(2*np.abs(self.f_tone) + 60e6, self.fs_rx-50e6)
                self.filter_bw_range = [self.f_tone-50e6, self.f_tone+50e6]
            elif self.sig_mode == 'tone_2':
                self.sc_range = [-1*self.sc_tone, self.sc_tone]
                self.filter_bw_range = [-1*self.f_tone-50e6, self.f_tone+50e6]
        elif 'wideband' in self.sig_mode:
            self.f_max = max(abs(self.wb_bw_range[0]), abs(self.wb_bw_range[1]))
            self.sc_range = self.wb_sc_range
            self.filter_bw_range = [self.wb_bw_range[0]-50e6, self.wb_bw_range[1]+50e6]
        elif self.sig_mode == 'load':
            self.f_max = max(abs(self.wb_bw_range[0]), abs(self.wb_bw_range[1]))
            self.sc_range = self.wb_sc_range
            self.filter_bw_range = [self.wb_bw_range[0]-50e6, self.wb_bw_range[1]+50e6]
        else:
            raise ValueError('Unsupported signal mode: ' + self.sig_mode)


        self.sc_range_ch = self.sc_range
        # self.sc_range_ch = [-1*self.n_samples_trx//2, self.n_samples_trx//2-1]
        self.n_samples_ch = self.sc_range_ch[1] - self.sc_range_ch[0] + 1
        # self.n_samples_ch = self.n_samples_trx
        self.nfft_ch = self.n_samples_ch
        # self.nfft_ch = self.nfft_trx

        if self.n_tx_ant==1 and self.n_rx_ant==1:
            self.ant_dim = 1
            self.beamforming = False






def rfsoc_run(params):
    signals_inst = Signal_Utils_Rfsoc(params)
    signals_inst.print("Running the code in mode {}".format(params.mode), thr=1)
    (txtd_base, txtd) = signals_inst.gen_tx_signal()

    if params.use_linear_track:
        client_lintrack_inst = Tcp_Comm_LinTrack(params)
        client_lintrack_inst.init_tcp_client()
        # client_lintrack_inst.return2home()
        # client_lintrack_inst.go2end()
    else:
        client_lintrack_inst = None

    if params.mode=='server':
        rfsoc_inst = RFSoC(params)
        rfsoc_inst.txtd = txtd
        if params.send_signal:
            rfsoc_inst.send_frame(txtd)
        if params.recv_signal:
            rfsoc_inst.recv_frame_one(n_frame=params.n_frame_rd)
            signals_inst.rx_operations(txtd_base, rfsoc_inst.rxtd)
        if params.run_tcp_server:
            rfsoc_inst.run_tcp()


    elif params.mode=='client':
        client_inst=Tcp_Comm_RFSoC(params)
        client_inst.init_tcp_client()

        if params.send_signal:
            client_inst.transmit_data()

        if params.RFFE=='sivers':
            client_inst.set_frequency(params.fc)
            if params.send_signal:
                client_inst.set_mode('RXen0_TXen1')
                client_inst.set_tx_gain()
            elif params.recv_signal:
                client_inst.set_mode('RXen1_TXen0')
                client_inst.set_rx_gain()


        if len(params.save_list)>0:
            signals_inst.save_signal_channel(client_inst, txtd_base, save_list=params.save_list)
        signals_inst.animate_plot(client_inst, client_lintrack_inst, txtd_base, plot_mode=params.animate_plot_mode, plot_level=0)
        
        


if __name__ == '__main__':
    
    params = Params_Class()
    rfsoc_run(params)

