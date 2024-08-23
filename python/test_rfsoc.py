try:
    from rfsoc import rfsoc
except:
    pass
from signals import signals
import numpy as np
import os
import time
import socket
import argparse
from types import SimpleNamespace




class client(object):
    def __init__(self, params):
        self.mode = params.mode
        self.verbose_level = params.verbose_level
        self.fc = params.fc
        self.beam_test = params.beam_test
        self.server_ip = params.server_ip
        self.TCP_port_Cmd = params.TCP_port_Cmd
        self.TCP_port_Data = params.TCP_port_Data
        self.adc_bits = params.adc_bits
        self.dac_bits = params.dac_bits

        if params.RFFE=='sivers':
            self.tx_bb_gain = 0x3
            self.tx_bb_phase = 0x0
            self.tx_bb_iq_gain = 0x77
            self.tx_bfrf_gain = 0x7F
            self.rx_gain_ctrl_bb1 = 0x33
            self.rx_gain_ctrl_bb2 = 0x00
            self.rx_gain_ctrl_bb3 = 0x33
            self.rx_gain_ctrl_bfrf = 0x7F

        self.nbytes = 2
        self.nread = params.n_frame_rd * params.n_samples

        self.radio_control = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.radio_control.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.radio_control.connect((self.server_ip, self.TCP_port_Cmd))

        self.radio_data = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.radio_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.radio_data.connect((self.server_ip, self.TCP_port_Data))

        self.print("Client object init done, Succesfully connected to the server", thr=1)


    def print(self, text='', thr=0):
        if self.verbose_level>=thr:
            print(text)

    def set_mode(self, mode):
        if mode == 'RXen0_TXen1' or mode == 'RXen1_TXen0' or mode == 'RXen0_TXen0':
            self.radio_control.sendall(b"setModeSiver "+str.encode(str(mode)))
            data = self.radio_control.recv(1024)
            self.print("Result of set_mode: {}".format(data),thr=1)
            return data
        
    def set_frequency(self, fc):
        self.radio_control.sendall(b"setCarrierFrequency "+str.encode(str(fc)))
        data = self.radio_control.recv(1024)
        self.print("Result of set_frequency: {}".format(data),thr=1)
        return data

    def set_tx_gain(self):
        self.radio_control.sendall(b"setGainTX " + str.encode(str(int(self.tx_bb_gain)) + " ") \
                                                    + str.encode(str(int(self.tx_bb_phase)) + " ") \
                                                    + str.encode(str(int(self.tx_bb_iq_gain)) + " ") \
                                                    + str.encode(str(int(self.tx_bfrf_gain))))
        data = self.radio_control.recv(1024)
        self.print("Result of set_tx_gain: {}".format(data),thr=1)
        return data

    def set_rx_gain(self):
        self.radio_control.sendall(b"setGainRX " + str.encode(str(int(self.rx_gain_ctrl_bb1)) + " ") \
                                                    + str.encode(str(int(self.rx_gain_ctrl_bb2)) + " ") \
                                                    + str.encode(str(int(self.rx_gain_ctrl_bb3)) + " ") \
                                                    + str.encode(str(int(self.rx_gain_ctrl_bfrf))))
        data = self.radio_control.recv(1024)
        self.print("Result of set_rx_gain: {}".format(data),thr=1)
        return data

    def transmit_data(self):
        self.radio_control.sendall(b"transmitSamples")
        data = self.radio_control.recv(1024)
        self.print("Result of transmit_data: {}".format(data),thr=1)
        return data

    def receive_data(self, mode='once'):
        if mode=='once':
            nbeams = 1
            self.radio_control.sendall(b"receiveSamplesOnce")
        elif mode=='beams':
            nbeams = len(self.beam_test)
            self.radio_control.sendall(b"receiveSamples")
        nbytes = nbeams * self.nbytes * self.nread * 2
        buf = bytearray()

        while len(buf) < nbytes:
            data = self.radio_data.recv(nbytes)
            buf.extend(data)
        data = np.frombuffer(buf, dtype=np.int16)
        data = data/(2 ** (self.adc_bits + 1) - 1)
        rxtd = data[:self.nread*nbeams] + 1j*data[self.nread*nbeams:]
        rxtd = rxtd.reshape(nbeams, self.nread)
        return rxtd




def rfsoc_run(params):
    signals_inst = signals(params)
    (txtd_base, txtd) = signals_inst.gen_tx_signal()


    if params.mode=='server':
        rfsoc_inst = rfsoc(params)
        rfsoc_inst.txtd = txtd
        if params.send_signal:
            rfsoc_inst.send_frame(txtd)
        if params.recv_signal:
            rfsoc_inst.recv_frame_one(n_frame=params.n_frame_rd)
            signals_inst.rx_operations(txtd_base, rfsoc_inst.rxtd)
        if params.run_tcp_server:
            rfsoc_inst.run()


    elif params.mode=='client_tx':
        client_inst=client(params)
        client_inst.transmit_data()
        if params.RFFE=='sivers':
            client_inst.set_mode('RXen0_TXen1')
            client_inst.set_frequency(params.fc)
            client_inst.set_tx_gain()


    elif params.mode=='client_rx':
        client_inst=client(params)
        if params.RFFE=='sivers':
            client_inst.set_mode('RXen1_TXen0')
            client_inst.set_frequency(params.fc)
            client_inst.set_rx_gain()

        signals_inst.animate_plot(client_inst, txtd_base, plot_level=0)
        
        





if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--bit_file_path", type=str, default="./rfsoc.bit", help="Path to the bit file")
    # parser.add_argument("--fs", type=float, default=245.76e6*4, help="sampling frequency used in signal processings")
    # parser.add_argument("--fc", type=float, default=57.51e9, help="carrier frequency")
    # parser.add_argument("--dac_fs", type=float, default=245.76e6*4, help="DAC sampling frequency")
    # parser.add_argument("--adc_fs", type=float, default=245.76e6*4, help="ADC sampling frequency")
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
        params.fs=245.76e6 * 4
        params.fc = 57.51e9
        params.dac_fs=params.fs
        params.adc_fs=params.fs
        params.n_samples=1024
        params.nfft=params.n_samples
        params.sig_modulation='qam'
        params.mix_phase_off=0.0
        params.sig_path=os.path.join(os.getcwd(), 'txtd.npy')
        params.wb_null_sc=10
        params.TCP_port_Cmd=8080
        params.TCP_port_Data=8081
        params.lmk_freq_mhz=122.88
        params.lmx_freq_mhz=3932.16
        params.filter_bw=900e6
        params.seed=100
        params.mixer_mode='analog'
        params.RFFE='piradio'
        params.filter_signal=False

        params.mix_freq=1000e6
        params.do_mixer_settings=False
        params.do_pll_settings=False
        params.n_frame_wr=1
        params.n_frame_rd=1
        params.run_tcp_server=True
        params.send_signal=True
        params.recv_signal=True

        params.bit_file_path=os.path.join(os.getcwd(), 'project_v1-0-21_20240822-164647.bit')
        params.project='sounder_if_ddr4'
        params.board='rfsoc_4x2'
        params.mode='client_rx'
        params.sig_mode='wideband'
        params.sig_gen_mode = 'ZadoffChu'
        params.wb_bw=500e6
        params.f_tone=5.0 * params.dac_fs / params.nfft #30e6
        params.server_ip='192.168.3.1'
        params.plot_level=0
        params.verbose_level=0
        





    params.n_samples_tx = params.n_frame_wr*params.n_samples
    params.n_samples_rx = params.n_frame_rd*params.n_samples
    params.nfft_tx = params.n_frame_wr*params.nfft
    params.nfft_rx = params.n_frame_rd*params.nfft
    params.beam_test = np.array([1, 5, 9, 13, 17, 21, 25, 29, 32, 35, 39, 43, 47, 51, 55, 59, 63])
    params.DynamicPLLConfig = (0, params.lmk_freq_mhz, params.lmx_freq_mhz)
    params.t = np.arange(0, params.n_samples) / params.fs
    params.t_tx = np.arange(0, params.n_samples_tx) / params.dac_fs
    params.t_rx = np.arange(0, params.n_samples_rx) / params.adc_fs
    params.freq = ((np.arange(0, params.nfft) / params.nfft) - 0.5) * params.fs / 1e6
    params.freq_tx = ((np.arange(0, params.nfft_tx) / params.nfft_tx) - 0.5) * params.dac_fs / 1e6
    params.freq_rx = ((np.arange(0, params.nfft_rx) / params.nfft_rx) - 0.5) * params.adc_fs / 1e6
    params.om = np.linspace(-np.pi, np.pi, params.nfft)
    params.om_tx = np.linspace(-np.pi, np.pi, params.nfft_tx)
    params.om_rx = np.linspace(-np.pi, np.pi, params.nfft_rx)
    if params.mixer_mode=='digital' and params.mix_freq!=0:
        params.mix_freq_dac = 0
        params.mix_freq_adc = 0
    elif params.mixer_mode == 'analog':
        params.mix_freq_dac = params.mix_freq
        params.mix_freq_adc = params.mix_freq
    else:
        params.mix_freq_dac = 0
        params.mix_freq_adc = 0
    if params.sig_mode=='wideband' or params.sig_mode=='wideband_null':
        params.filter_bw = min(params.wb_bw + 100e6, params.adc_fs-50e6)
    else:
        params.filter_bw = min(2*np.abs(params.f_tone) + 60e6, params.adc_fs-50e6)
    if 'sounder_bbf' in params.project:
        params.do_mixer_settings=False
        params.do_pll_settings=False
    if params.board == "rfsoc_4x2":
        params.do_pll_settings=False
    
    if params.board=='rfsoc_2x2':
        params.adc_bits = 12
        params.dac_bits = 14
    elif params.board=='rfsoc_4x2':
        params.adc_bits = 14
        params.dac_bits = 14

    if 'tone' in params.sig_mode:
        params.f_max = abs(params.f_tone)
    elif 'wideband' in params.sig_mode:
        params.f_max = abs(params.wb_bw/2)
    elif params.sig_mode == 'load':
        params.f_max = abs(params.wb_bw/2)
    else:
        raise ValueError('Unsupported signal mode: ' + params.sig_mode)


    rfsoc_run(params)

