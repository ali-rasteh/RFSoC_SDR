from backend import *
from backend import be_np as np, be_scp as scipy
try:
    from rfsoc import RFSoC
except:
    pass
from signal_utilsrfsoc import Signal_Utils_Rfsoc
from signal_utils import Signal_Utils
from tcp_comm import Tcp_Comm_RFSoC, Tcp_Comm_LinTrack, ssh_Com_Piradio




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
            self.fs_tx=self.fs
            self.fs_rx=self.fs
            self.fs_trx=self.fs
            self.n_samples=1024
            self.nfft=self.n_samples
            self.mix_phase_off=0.0
            self.calib_params_path=os.path.join(os.getcwd(), 'calib/calib_params.npz')
            self.sig_path=os.path.join(os.getcwd(), 'sigs/txtd.npz')
            self.sig_save_path=os.path.join(os.getcwd(), 'sigs/trx.npz')
            self.channel_save_path=os.path.join(os.getcwd(), 'channels/channel.npz')
            self.figs_dir=os.path.join(os.getcwd(), 'figs/')
            self.figs_save_path=os.path.join(self.figs_dir, 'plot.pdf')
            self.sys_response_path=os.path.join(os.getcwd(), 'channels/sys_response.npz')
            self.wb_null_sc=0
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
            # self.lintrack_server_ip='10.18.242.48'
            self.lintrack_server_ip='192.168.137.100'
            self.ant_dim = 1
            self.bit_file_path=os.path.join(os.getcwd(), 'project_v1-0-58_20241001-150336.bit')       # Without DAC MTS
            # self.bit_file_path=os.path.join(os.getcwd(), 'project_v1-0-62_20241019-173825.bit')         # With DAC MTS
            self.project='sounder_if_ddr4'
            self.board='rfsoc_4x2'
            self.n_tx_ant=2
            self.n_rx_ant=2
            self.ant_dy_m = 0.020
            self.wb_bw_mode='sc'    # sc or freq
            self.wb_bw_range=[-250e6,250e6]
            self.tone_f_mode='sc'    # sc or freq
            self.sc_tone=10
            self.f_tone=10.0 * self.fs_tx / self.nfft
            self.mode='server'
            self.steer_theta_deg = 0        # Desired steering elevation in degrees
            self.n_save = 100
            self.sig_gain_db=0
            self.beamforming=False
            self.steer_phi_deg = 30        # Desired steering azimuth in degrees
            self.anim_interval=500
            self.piradio_host = '192.168.137.51'
            self.piradio_port = '22'
            self.piradio_username = 'ubuntu'
            self.piradio_password = 'temppwd'
            self.sig_modulation = '4qam'
            self.sig_mode='wideband_null'
            self.calib_iter = 100
            self.overwrite_level=True
            self.plot_level=0
            self.verbose_level=0
            self.snr_est_db=40
            self.rx_chain=[]        # filter, integrate, sync_time, sync_freq, pilot_separate, channel_est, channel_eq
            self.nf_walls = np.array([[-5,4], [-1,6]])
            self.rx_sep_dir = np.array([1,0])
            self.sig_gen_mode = 'fft'
            self.saved_sig_plot = []
            self.ant_dx_m = 0.020               # Antenna spacing in meters
            self.control_piradio=False
            self.nf_stop_thr = 0.03
            # self.rx_loc_sep = np.array([0,1])
            self.rx_loc_sep = np.array([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
            # self.ant_sep = np.array([0.5,1,2,4])
            self.ant_sep = np.array([0.5])
            self.nf_param_estimate = False
            self.use_linear_track=False


            # self.freq_hop_list = [6.0e9, 8.0e9, 10.0e9, 12.0e9]
            self.freq_hop_list = [8.75e9]
            self.tx_sig_sim = 'same'        # same or orthogonal
            self.n_rx_ch_eq=1
            self.n_frame_rd=2
            self.wb_sc_range=[-250,250]
            self.nf_npath_max = 5
            self.plt_tx_ant_id = 0
            self.plt_rx_ant_id = 0
            self.plt_frame_id = 0
            self.channel_limit = True
            self.n_rd_rep=8
            self.animate_plot_mode=['h01', 'rx_phase_diff', 'aoa_gauge']
            self.save_list = ['', '']           # signal or channel

            # self.rx_chain.append('filter')
            # self.rx_chain.append('integrate')
            self.rx_chain.append('sync_time')
            # self.rx_chain.append('sync_freq')
            # self.rx_chain.append('pilot_separate')
            # self.rx_chain.append('sys_res_deconv')
            self.rx_chain.append('channel_est')
            # self.rx_chain.append('sparse_est')
            # self.rx_chain.append('channel_eq')




        if 'h_sparse' in self.animate_plot_mode and 'sparse_est' not in self.rx_chain:
            self.rx_chain.append('sparse_est')

        system_info = platform.uname()
        if "pynq" in system_info.node.lower():
            self.mode = 'server'
            if self.overwrite_level:
                self.plot_level=4
                self.verbose_level=4
                self.nf_param_estimate=False
                self.use_linear_track=False
                self.control_piradio=False
        else:
            self.mode = 'client'
            if self.overwrite_level:
                self.plot_level=0
                self.verbose_level=1
            # if self.nf_param_estimate:
            #     self.use_linear_track=True

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

        if self.n_tx_ant==1 and self.n_rx_ant==1:
            self.ant_dim = 1
            self.beamforming = False




        self.fc = self.freq_hop_list[0]
        self.wl = constants.c / self.fc
        self.ant_dx = self.ant_dx_m/self.wl             # Antenna spacing in wavelengths (lambda)
        self.ant_dy = self.ant_dy_m/self.wl

        if self.board=='rfsoc_2x2':
            self.adc_bits = 12
            self.dac_bits = 14
        elif self.board=='rfsoc_4x2':
            self.adc_bits = 14
            self.dac_bits = 14

        if self.tx_sig_sim=='same':
            self.seed = [self.seed for i in range(self.n_tx_ant)]
        elif self.tx_sig_sim=='orthogonal':
            self.seed = [self.seed*i+i for i in range(self.n_tx_ant)]

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
                self.filter_bw_range = [self.f_tone-50e6, self.f_tone+50e6]
            elif self.sig_mode == 'tone_2':
                self.sc_range = [-1*self.sc_tone, self.sc_tone]
                self.filter_bw_range = [-1*self.f_tone-50e6, self.f_tone+50e6]
            self.null_sc_range = [0, 0]
        elif 'wideband' in self.sig_mode or self.sig_mode == 'load':
            self.f_max = max(abs(self.wb_bw_range[0]), abs(self.wb_bw_range[1]))
            self.sc_range = self.wb_sc_range
            self.filter_bw_range = [self.wb_bw_range[0]-50e6, self.wb_bw_range[1]+50e6]
            self.null_sc_range = [-1*self.wb_null_sc, self.wb_null_sc]
        else:
            raise ValueError('Unsupported signal mode: ' + self.sig_mode)
        
        if ('channel' in self.save_list):
            self.channel_limit = False
        if self.channel_limit:
            self.sc_range_ch = self.sc_range
            self.n_samples_ch = self.sc_range_ch[1] - self.sc_range_ch[0] + 1
            self.nfft_ch = self.n_samples_ch
        else:
            self.sc_range_ch = [-1*self.n_samples_trx//2, self.n_samples_trx//2-1]
            self.n_samples_ch = self.n_samples_trx
            self.nfft_ch = self.nfft_trx


        




def rfsoc_run(params):
    client_rfsoc = None
    client_lintrack = None
    client_piradio = None

    signals_inst = Signal_Utils_Rfsoc(params)
    signals_inst.print("Running the code in mode {}".format(params.mode), thr=1)
    (txtd_base, txtd) = signals_inst.gen_tx_signal()

    if params.use_linear_track:
        client_lintrack = Tcp_Comm_LinTrack(params)
        client_lintrack.init_tcp_client()
        # client_lintrack.return2home()
        # client_lintrack.go2end()

    if params.control_piradio:
        client_piradio = ssh_Com_Piradio(params)
        client_piradio.init_ssh_client()
        # client_piradio.set_frequency(verif_keyword='')

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
        params.show_saved_sigs=len(params.saved_sig_plot)>0
        if not params.show_saved_sigs:
            client_rfsoc=Tcp_Comm_RFSoC(params)
            client_rfsoc.init_tcp_client()

            if params.send_signal:
                pass
                # client_rfsoc.transmit_data()

            if params.RFFE=='sivers':
                client_rfsoc.set_frequency(params.fc)
                if params.send_signal:
                    client_rfsoc.set_mode('RXen0_TXen1')
                    client_rfsoc.set_tx_gain()
                elif params.recv_signal:
                    client_rfsoc.set_mode('RXen1_TXen0')
                    client_rfsoc.set_rx_gain()

            signals_inst.calibrate_rx_phase_offset(client_rfsoc)
            signals_inst.create_near_field_model()

            if 'channel' in params.save_list or 'signal' in params.save_list:
                signals_inst.save_signal_channel(client_rfsoc, txtd_base, save_list=params.save_list)
        
        signals_inst.animate_plot(client_rfsoc, client_lintrack, client_piradio, txtd_base, plot_mode=params.animate_plot_mode, plot_level=0)



if __name__ == '__main__':
    
    params = Params_Class()
    rfsoc_run(params)

