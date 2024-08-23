import numpy as np
import socket
import os




class tcp_client(object):
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


    def close(self):
        self.radio_control.close()
        self.radio_data.close()
        self.print("Client object closed", thr=1)

    def __del__(self):
        self.close()
        self.print("Client object deleted", thr=1)

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
    
