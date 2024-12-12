from backend import *
from backend import be_np as np, be_scp as scipy





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

            # Constant parameters
            self.c = constants.c
            self.seed=100

            # Board and RFSoC FPGA project parameters
            self.project='sounder_if_ddr4'
            self.board='rfsoc_4x2'
            self.bit_file_path=os.path.join(os.getcwd(), 'project_v1-0-58_20241001-150336.bit')       # Without DAC MTS
            # self.bit_file_path=os.path.join(os.getcwd(), 'project_v1-0-62_20241019-173825.bit')         # With DAC MTS
            self.mode='client'
            self.run_tcp_server=True
            self.send_signal=True
            self.recv_signal=True

            # Plots and logs parameters
            self.plt_frame_id = 0
            self.overwrite_level=True
            self.plot_level=0
            self.verbose_level=0
            self.plt_tx_ant_id = 0
            self.plt_rx_ant_id = 0
            self.anim_interval=500
            self.animate_plot_mode=['h01', 'rxfd', 'IQ']

            # Mixer parameters
            self.mixer_mode='analog'
            self.mix_freq=1000e6
            self.mix_phase_off=0.0
            self.do_mixer_settings=False
            self.do_pll_settings=False
            self.lmk_freq_mhz=122.88
            self.lmx_freq_mhz=3932.16

            # RFFE and antennas parameters
            self.RFFE='piradio'
            self.ant_dim = 1
            self.n_tx_ant=2
            self.n_rx_ant=2
            self.ant_dx_m = 0.02
            self.ant_dy_m = 0.02

            # Connections parameters
            self.control_rfsoc=True
            self.control_piradio=True
            self.tcp_localIP = "0.0.0.0"
            self.tcp_bufferSize=2**10
            self.TCP_port_Cmd=8080
            self.TCP_port_Data=8081
            self.rfsoc_server_ip='192.168.3.1'
            # self.lintrack_server_ip='10.18.242.48'
            self.lintrack_server_ip='192.168.137.100'
            self.piradio_host = '192.168.137.51'
            self.piradio_ssh_port = '22'
            self.piradio_rest_port = '5111'
            self.piradio_username = 'ubuntu'
            self.piradio_password = 'temppwd'
            self.piradio_rest_protocol = 'http'
            self.host_ip = '192.168.3.100'
            self.host_username = 'wirelesslab914'
            self.host_password = ''
            self.controller_slave_ip = '192.168.1.1'
            
            # Signals information
            self.freq_hop_list = [10.0e9]
            self.fs=245.76e6 * 4
            self.fs_tx=self.fs
            self.fs_rx=self.fs
            self.fs_trx=self.fs
            self.n_samples=1024
            self.nfft=self.n_samples
            self.sig_gen_mode = 'fft'
            self.sig_mode='wideband_null'
            self.sig_modulation = '4qam'
            self.tx_sig_sim = 'same'        # same or orthogonal or shifted
            self.sig_gain_db=0
            self.n_frame_wr=1
            self.n_frame_rd=2
            self.n_rd_rep=8
            self.snr_est_db=40
            self.wb_bw_mode='sc'    # sc or freq
            self.wb_sc_range=[-250,250]
            self.wb_bw_range=[-250e6,250e6]
            self.wb_null_sc=0
            self.tone_f_mode='sc'    # sc or freq
            self.sc_tone=10
            self.f_tone=10.0 * self.fs_tx / self.nfft
            self.filter_bw_range=[-450e6,450e6]
            self.n_rx_ch_eq=1
            self.sparse_ch_samp_range=[-6,20]       # Range of samples around the strongest peak to consider for channel estimation
            self.sparse_ch_n_ignore=-1              # Number of samples to ignore around the strongest peak
            self.rx_same_delay=True            # If True, all applies the same time shift to all RX antennas
            self.rx_chain=['sync_time', 'channel_est']        # filter, integrate, sync_time, sync_time_frac, sync_freq, pilot_separate, channel_est, channel_eq
            self.channel_limit = True

            # Save parameters
            self.calib_params_dir=os.path.join(os.getcwd(), 'calib/')
            self.calib_params_path=os.path.join(os.getcwd(), 'calib/calib_params.npz')
            self.sig_dir=os.path.join(os.getcwd(), 'sigs/')
            self.sig_path=os.path.join(os.getcwd(), 'sigs/txtd.npz')
            self.sig_save_path=os.path.join(os.getcwd(), 'sigs/trx.npz')
            self.channel_dir=os.path.join(os.getcwd(), 'channels/')
            self.channel_save_path=os.path.join(os.getcwd(), 'channels/channel.npz')
            self.sys_response_path=os.path.join(os.getcwd(), 'channels/sys_response.npz')
            self.figs_dir=os.path.join(os.getcwd(), 'figs/')
            self.figs_save_path=os.path.join(self.figs_dir, 'plot.pdf')
            self.n_save = 100
            self.save_list = ['', '']           # signal or channel
            self.saved_sig_plot = []

            # Calibration parameters
            self.calib_iter = 100

            # Beamforming parameters
            self.beamforming=False
            self.steer_theta_deg = 0        # Desired steering elevation in degrees
            self.steer_phi_deg = 30        # Desired steering azimuth in degrees

            # Near field measurements parameters
            self.nf_param_estimate = False
            self.use_linear_track = False
            self.nf_walls = np.array([[-5,4], [-1,6]])
            self.nf_rx_sep_dir = np.array([1,0])
            self.nf_tx_sep_dir = np.array([1,0])
            self.nf_npath_max = [20,5]      # Dirst number is the maximum number to extract at the 1st round, 2nd number is the maximum number to extract at the 2nd round
            self.nf_stop_thr = 0.03
            # self.nf_tx_loc = None
            self.nf_tx_loc = np.array([[0.3,1.0]])
            # self.nf_tx_loc = np.array([[6,4]])
            self.nf_rx_loc_sep = np.array([0,0.2,0.4])
            self.nf_tx_ant_sep = 0.5
            self.nf_rx_ant_sep = 0.5 * np.array([1,2,4])




            # FR3 measurements parameters (overwritten)
            # self.nf_param_estimate = True
            # self.use_linear_track = True
            self.mode = 'client_master'
            self.control_rfsoc=True
            self.control_piradio=True
            self.controller_slave_ip = '10.18.134.22'
            self.ant_dx_m = 0.02               # Antenna spacing in meters
            self.n_rx_ch_eq=1
            self.wb_sc_range=[-250,250]
            self.rx_same_delay=False
            self.channel_limit = True
            self.sparse_ch_samp_range=[-5,100]
            self.sparse_ch_n_ignore=5
            self.n_rd_rep=8
            self.plt_tx_ant_id = 0
            self.plt_rx_ant_id = 0
            self.animate_plot_mode=['h01', 'rxfd']
            self.anim_interval=200
            self.save_list = ['', '']           # signal or channel
            self.n_save = 100
            self.tx_sig_sim = 'shifted'        # same or orthogonal or shifted
            self.sig_gen_mode = 'ZadoffChu'

            # self.freq_hop_list = [6.5e9]
            # self.freq_hop_list = [8.75e9]
            self.freq_hop_list = [10.0e9]
            save_name = f'{self.freq_hop_list[0]/1e9}_B_gamma_gamma_n'
            
            self.sig_save_path=os.path.join(os.getcwd(), 'sigs/' + save_name + '.npz')
            self.channel_save_path=os.path.join(os.getcwd(), 'channels/' + save_name + '.npz')


            # Chain or operations to perform (overwritten)
            self.rx_chain=[]
            # self.rx_chain.append('filter')
            # self.rx_chain.append('integrate')
            self.rx_chain.append('sync_time')
            # self.rx_chain.append('sync_time_frac')
            # self.rx_chain.append('sync_freq')
            # self.rx_chain.append('pilot_separate')
            # self.rx_chain.append('sys_res_deconv')
            self.rx_chain.append('channel_est')
            # self.rx_chain.append('sparse_est')
            # self.rx_chain.append('channel_eq')


        self.initialize()



    def initialize(self):

        if 'h_sparse' in self.animate_plot_mode and 'sparse_est' not in self.rx_chain:
            self.rx_chain.append('sparse_est')

        system_info = platform.uname()
        if "pynq" in system_info.node.lower():
            self.mode = 'server'
            if self.overwrite_level:
                self.plot_level=4
                self.verbose_level=4

            self.nf_param_estimate=False
            self.control_rfsoc=False
            self.control_piradio=False
            self.use_linear_track=False
        else:
            if self.overwrite_level:
                self.plot_level=0
                self.verbose_level=1

            if self.mode == 'client':
                pass
            elif self.mode == 'client_master':
                pass
            elif self.mode == 'client_slave':
                self.control_rfsoc=False
                self.use_linear_track=False

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
        self.wl = self.c / self.fc
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
        elif self.tx_sig_sim=='shifted':
            self.seed = [self.seed for i in range(self.n_tx_ant)]

        self.server_ip = None
        self.steer_phi_rad = np.deg2rad(self.steer_phi_deg)
        self.steer_theta_rad = np.deg2rad(self.steer_theta_deg)
        self.n_samples_tx = self.n_frame_wr*self.n_samples
        self.n_samples_rx = self.n_frame_rd*self.n_samples
        self.n_samples_trx = min(self.n_samples_tx, self.n_samples_rx)
        self.nfft_tx = self.n_frame_wr*self.nfft
        self.nfft_rx = self.n_frame_rd*self.nfft
        self.nfft_trx = min(self.nfft_tx, self.nfft_rx)
        self.freq = np.linspace(-0.5, 0.5, self.nfft, endpoint=True) * self.fs / 1e6
        self.freq_tx = np.linspace(-0.5, 0.5, self.nfft_tx, endpoint=True) * self.fs_tx / 1e6
        self.freq_rx = np.linspace(-0.5, 0.5, self.nfft_rx, endpoint=True) * self.fs_rx / 1e6
        self.freq_trx = np.linspace(-0.5, 0.5, self.nfft_trx, endpoint=True) * self.fs_trx / 1e6

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
            self.freq_ch = self.freq_trx[(self.sc_range_ch[0]+self.nfft_trx//2):(self.sc_range_ch[1]+self.nfft_trx//2+1)]
        else:
            self.sc_range_ch = [-1*self.nfft_trx//2, self.nfft_trx//2-1]
            self.n_samples_ch = self.n_samples_trx
            self.nfft_ch = self.nfft_trx
            self.freq_ch = self.freq_trx



        self.nf_n_rx_loc_sep = len(self.nf_rx_loc_sep)
        self.nf_n_ant_sep = len(self.nf_rx_ant_sep)
        self.nf_n_meas = self.nf_n_rx_loc_sep * self.nf_n_ant_sep
        p = len(self.nf_rx_sep_dir)
        # Generate the RX antenna positions
        self.nf_rx_ant_loc = np.zeros((self.n_rx_ant, self.nf_n_meas, p))
        self.nf_tx_ant_loc = np.zeros((self.n_tx_ant, self.nf_n_meas, p))
        for k in range(self.nf_n_rx_loc_sep):
            for i in range(self.nf_n_ant_sep):
                m = k*self.nf_n_ant_sep + i
                # Linear distance of the RX antennas from the origin
                t = self.nf_rx_loc_sep[k] + self.nf_rx_ant_sep[i]*np.arange(self.n_rx_ant)*self.wl
                # Position of the RX antennas
                self.nf_rx_ant_loc[:,m,:] = t[:,None]*self.nf_rx_sep_dir[None,:]

                t = self.ant_dx_m * np.arange(self.n_tx_ant)
                self.nf_tx_ant_loc[:,m,:] = self.nf_tx_loc + t[:,None]*self.nf_tx_sep_dir[None,:]


        for f in [self.calib_params_dir, self.sig_dir, self.channel_dir, self.figs_dir]:
            if not os.path.exists(f):
                os.makedirs(f)
        



    def copy(self):
        return copy.deepcopy(self)
    
