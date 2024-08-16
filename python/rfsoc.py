from pynq import Overlay, allocate, MMIO, Clocks, interrupt, GPIO
from pynq.lib import dma
import xrfclk
import xrfdc
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import socket
from siversController import *
from pyftdi.ftdi import Ftdi


class rfsoc(object):
    def __init__(self, lmkx_freq=None, dac_adc_fs=None, n_samples=1024, dac_adc_ids=None,
                 project='ddr4', board='rfsoc_2x2', RFFE='piradio', TCPPortCmd=8080,
                 TCPPortData=8081):

        self.n_samples = n_samples
        self.beam_test = np.array([1, 5, 9, 13, 17, 21, 25, 29, 32, 35, 39, 43, 47, 51, 55, 59, 63])
        self.project = project
        self.board = board
        self.RFFE = RFFE
        self.TCPPortCmd = TCPPortCmd
        self.TCPPortData = TCPPortData

        if lmkx_freq is None:
            self.lmkx_freq = {}
            self.lmkx_freq['lmk_freq'] = 122.88
            self.lmkx_freq['lmx_freq'] = 3932.16
        else:
            self.lmkx_freq = lmkx_freq

        if dac_adc_fs is None:
            self.dac_adc_fs = {}
            self.dac_adc_fs['dac_fs'] = 245.76e6 * 4
            self.dac_adc_fs['adc_fs'] = 245.76e6 * 4
        else:
            self.dac_adc_fs = dac_adc_fs

        if dac_adc_ids is None:
            self.dac_adc_ids = {'dac_tile_id': 1, 'dac_block_id': 0, 'adc_tile_id': 2, 'adc_block_id': 0}
        else:
            self.dac_adc_ids = dac_adc_ids

        self.dac_tile_id = self.dac_adc_ids['dac_tile_id']
        self.dac_block_id = self.dac_adc_ids['dac_block_id']
        self.adc_tile_id = self.dac_adc_ids['adc_tile_id']
        self.adc_block_id = self.dac_adc_ids['adc_block_id']

        self.adc_bits = 12
        self.dac_bits = 14

        self.adc_max_fs = 4096e6
        self.dac_max_fs = 6554e6

        self.n_par_strms_tx = 4
        self.n_par_strms_rx = 4
        self.n_skip = 0

        self.CLOCKWIZARD_LOCK_ADDRESS = 0x0004
        self.CLOCKWIZARD_RESET_ADDRESS = 0x0000
        self.CLOCKWIZARD_RESET_TOKEN = 0x000A

        self.txtd = None
        self.rxtd = None

        if self.RFFE=='sivers':
            self.init_sivers()

        print("rfsoc initialization done")


    def load_bit_file(self, bit_file_path, verbose=False):
        print("Starting to load the bit-file")

        self.ol = Overlay(bit_file_path)
        if verbose:
            self.ol.ip_dict
            # ol?

        print("Bit-file loading done")


    def init_sivers(self):
        print("Starting Sivers EVK controller")
        allDevices=Ftdi.list_devices()
        Ftdi.show_devices()
        strFTDIdesc = str(allDevices[0][0])
        snStr = strFTDIdesc[strFTDIdesc.find('sn=')+4:strFTDIdesc.find('sn=')+14]
        siverEVKAddr = 'ftdi://ftdi:4232:'+ snStr
        print('siverEVKAddr: {}'.format(siverEVKAddr))            
        self.siversControllerObj = siversController(siverEVKAddr)
        self.siversControllerObj.init()
        print("Sivers EVK controller is loaded")


    def init_tcp_server(self):
        ## TCP Server
        print("Starting TCP server")
        self.localIP = "0.0.0.0"
        self.bufferSize = 2**10
        
        ## Command 
        self.TCPServerSocketCmd = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)# Create a datagram socket
        self.TCPServerSocketCmd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.TCPServerSocketCmd.bind((self.localIP, self.TCPPortCmd)) # Bind to address and ip
        
        ## Data
        self.TCPServerSocketData = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)         # Create a datagram socket
        self.TCPServerSocketData.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.TCPServerSocketData.bind((self.localIP, self.TCPPortData))                # Bind to address and ip

        bufsize = self.TCPServerSocketData.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) 
        # print ("Buffer size [Before]:%d" %bufsize)
        print("TCP server is up")


    def allocate_input(self, n_frame=1):
        self.adc_rx_buffer = allocate(shape=(n_frame * self.n_samples * 2,), dtype=np.int16)
        print("Input buffers allocation done")


    def allocate_output(self, n_frame=1):
        self.dac_tx_buffer = allocate(shape=(n_frame * self.n_samples * 2,), dtype=np.int16)
        print("Output buffers allocation done")


    def gpio_init(self):
        self.gpio_dic = {}

        if 'ddr4' in self.project:
            if self.board=='rfsoc_2x2':
                self.gpio_dic['lmk_reset'] = GPIO(GPIO.get_gpio_pin(84), 'out')
            elif self.board=='rfsoc_4x2':
                self.gpio_dic['lmk_reset'] = GPIO(GPIO.get_gpio_pin(-78+7), 'out')
            self.gpio_dic['dac_mux_sel'] = GPIO(GPIO.get_gpio_pin(3), 'out')
            self.gpio_dic['adc_enable'] = GPIO(GPIO.get_gpio_pin(34), 'out')
            self.gpio_dic['dac_enable'] = GPIO(GPIO.get_gpio_pin(2), 'out')
            self.gpio_dic['adc_reset'] = GPIO(GPIO.get_gpio_pin(32), 'out')
            self.gpio_dic['dac_reset'] = GPIO(GPIO.get_gpio_pin(0), 'out')
            self.gpio_dic['led'] = GPIO(GPIO.get_gpio_pin(80), 'out')
        else:
            self.gpio_dic['dac_mux_sel'] = GPIO(GPIO.get_gpio_pin(0), 'out')
            self.gpio_dic['adc_enable'] = GPIO(GPIO.get_gpio_pin(3), 'out')
            self.gpio_dic['dac_enable'] = GPIO(GPIO.get_gpio_pin(1), 'out')
            self.gpio_dic['adc_reset'] = GPIO(GPIO.get_gpio_pin(2), 'out')
            self.gpio_dic['dac_reset'] = GPIO(GPIO.get_gpio_pin(4), 'out')

        if 'ddr4' in self.project:
            self.gpio_dic['led'].write(0)
            self.gpio_dic['dac_mux_sel'].write(0)
            self.gpio_dic['adc_enable'].write(0)
            self.gpio_dic['dac_enable'].write(0)
            self.gpio_dic['adc_reset'].write(1)
            self.gpio_dic['dac_reset'].write(1)
        else:
            self.gpio_dic['dac_mux_sel'].write(0)
            self.gpio_dic['adc_enable'].write(0)
            self.gpio_dic['dac_enable'].write(0)
            self.gpio_dic['adc_reset'].write(0)
            self.gpio_dic['dac_reset'].write(0)

        print("PS-PL GPIOs initialization done")


    def clock_init(self):
        if 'ddr4' in self.project:
            self.gpio_dic['lmk_reset'].write(1)
            self.gpio_dic['lmk_reset'].write(0)

        xrfclk.set_ref_clks(lmk_freq=self.lmkx_freq['lmk_freq'], lmx_freq=self.lmkx_freq['lmx_freq'])
        print("Xrfclk initialization done")


    def verify_clock_tree(self):
        if 'ddr4' in self.project:
            status = self.ol.clocktreeMTS.clk_wiz_0.read(self.CLOCKWIZARD_LOCK_ADDRESS)
            if (status != 1):
                raise Exception("The MTS ClockTree has failed to LOCK. Please verify board clocking configuration")


    def init_rfdc(self):
        self.rfdc = self.ol.usp_rf_data_converter_0


    def init_tile_sync(self):
        self.sync_tiles(0x1, 0x1)
        self.ol.clocktreeMTS.clk_wiz_0.mmio.write_reg(self.CLOCKWIZARD_RESET_ADDRESS, self.CLOCKWIZARD_RESET_TOKEN)
        time.sleep(0.1)

        self.rfdc.dac_tiles[0].Reset()
        self.rfdc.dac_tiles[2].Reset()

        for toggleValue in range(0,1):
            self.rfdc.adc_tiles[0].SetupFIFO(toggleValue)
            self.rfdc.adc_tiles[2].SetupFIFO(toggleValue)
    

    def sync_tiles(self, dacTiles = 0, adcTiles = 0):
        self.rfdc.mts_dac_config.RefTile = 0  # MTS starts at DAC Tile 228
        self.rfdc.mts_adc_config.RefTile = 0  # MTS starts at ADC Tile 224
        self.rfdc.mts_dac_config.Target_Latency = -1
        self.rfdc.mts_adc_config.Target_Latency = -1
        if dacTiles > 0:
            self.rfdc.mts_dac_config.Tiles = dacTiles # group defined in binary 0b1111
            self.rfdc.mts_dac_config.SysRef_Enable = 1
            self.rfdc.mts_dac()
        else:
            self.rfdc.mts_dac_config.Tiles = 0x0
            self.rfdc.mts_dac_config.SysRef_Enable = 0

        if adcTiles > 0:
            self.rfdc.mts_adc_config.Tiles = adcTiles
            self.rfdc.mts_adc_config.SysRef_Enable = 1
            self.rfdc.mts_adc()
        else:
            self.rfdc.mts_adc_config.Tiles = 0x0
            self.rfdc.mts_adc_config.SysRef_Enable = 0
    

    def dac_init(self, mix_freq=500e6, mix_phase_off=0, DynamicPLLConfig=None, do_mixer_settings=True):
        cofig_str = 'DAC configs: mix_freq: {:.2e}, mix_phase_off: {:.2f}'.format(mix_freq, mix_phase_off)
        cofig_str += ', DynamicPLLConfig: ' + str(DynamicPLLConfig)
        cofig_str += ', do_mixer_settings: ' + str(do_mixer_settings)
        print(cofig_str)
        
        if DynamicPLLConfig is None:
            PLLConfig = (0, 122.88, 3932.16)
        else:
            PLLConfig = DynamicPLLConfig

        self.dac_tile = self.ol.usp_rf_data_converter_0.dac_tiles[self.dac_tile_id]
        if DynamicPLLConfig is not None:
            self.dac_tile.DynamicPLLConfig(PLLConfig[0], PLLConfig[1], PLLConfig[2])
        self.dac_block = self.dac_tile.blocks[self.dac_block_id]
        self.dac_tile.Reset()
        print("DAC init and reset done")
        # print(self.ol.usp_rf_data_converter_0.dac_tiles[self.dac_tile_id].blocks[self.dac_block_id].MixerSettings)

        if do_mixer_settings:
            self.dac_block.MixerSettings['Freq'] = mix_freq/1e6
            self.dac_block.MixerSettings['PhaseOffset'] = mix_phase_off
            # self.dac_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_IMMEDIATE
            self.dac_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_TILE
            self.dac_block.UpdateEvent(xrfdc.EVNT_SRC_TILE)

        self.dac_tile.SetupFIFO(True)

        print("DAC Mixer Settings done")


    def adc_init(self, mix_freq=500e6, mix_phase_off=0, DynamicPLLConfig=None, do_mixer_settings=True):
        cofig_str = 'ADC configs: mix_freq: {:.2e}, mix_phase_off: {:.2f}'.format(mix_freq, mix_phase_off)
        cofig_str += ', DynamicPLLConfig: ' + str(DynamicPLLConfig)
        cofig_str += ', do_mixer_settings: ' + str(do_mixer_settings)
        print(cofig_str)

        if DynamicPLLConfig is None:
            PLLConfig = (0, 122.88, 3932.16)
        else:
            PLLConfig = DynamicPLLConfig

        self.adc_tile = self.ol.usp_rf_data_converter_0.adc_tiles[self.adc_tile_id]
        if DynamicPLLConfig is not None:
            self.adc_tile.DynamicPLLConfig(PLLConfig[0], PLLConfig[1], PLLConfig[2])
        self.adc_block = self.adc_tile.blocks[self.adc_block_id]
        self.adc_tile.Reset()
        print("ADC init and reset done")
        # print(self.ol.usp_rf_data_converter_0.adc_tiles[self.adc_tile_id].blocks[self.adc_block_id].MixerSettings)
        # attributes = dir(self.ol.usp_rf_data_converter_0.adc_tiles[self.adc_tile_id].blocks[self.adc_block_id].MixerSettings)
        # for name in attributes:
        #     print(name)

        if do_mixer_settings:
            # self.adc_block.NyquistZone = 1
            # self.adc_block.MixerSettings = {
            #     'CoarseMixFreq'  : xrfdc.COARSE_MIX_BYPASS,
            #     'EventSource'    : xrfdc.EVNT_SRC_TILE,
            #     'FineMixerScale' : xrfdc.MIXER_SCALE_1P0,
            #     'Freq'           : -1*mix_freq/1e6,
            #     'MixerMode'      : xrfdc.MIXER_MODE_R2C,
            #     'MixerType'      : xrfdc.MIXER_TYPE_FINE,
            #     'PhaseOffset'    : 0.0
            # }

            self.adc_block.MixerSettings['Freq'] = -1*mix_freq/1e6
            self.adc_block.MixerSettings['PhaseOffset'] = mix_phase_off
            # self.adc_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_IMMEDIATE
            # self.adc_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_TILE
            # self.adc_block.UpdateEvent(xrfdc.EVENT_MIXER)
            self.adc_block.UpdateEvent(xrfdc.EVNT_SRC_TILE)
            self.adc_block.MixerSettings['Freq'] = -1*mix_freq/1e6
        
        self.adc_tile.SetupFIFO(True)
        for toggleValue in range(0, 1):
            self.adc_tile.SetupFIFO(toggleValue)

        print("ADC Mixer Settings done")


    def dma_init(self):
        if 'ddr4' in self.project:
            self.ol.dac_path.axi_dma_0.set_up_tx_channel()
            self.dma_tx = self.ol.dac_path.axi_dma_0.sendchannel
        else:
            self.dma_tx = self.ol.TX_loop.axi_dma_tx.sendchannel
        print("TX DMA setup done")

        if 'ddr4' in self.project:
            self.ol.adc_path.axi_dma_0.set_up_rx_channel()
            self.dma_rx = self.ol.adc_path.axi_dma_0.recvchannel
            self.rx_reg = self.ol.adc_path.axis_flow_ctrl_0
        else:
            self.dma_rx = self.ol.RX_Logic.axi_dma_rx.recvchannel
        print("RX DMA setup done")


    def load_data_to_tx_buffer(self, txtd, mode=1):
        self.txtd = txtd
        txtd_dac = self.txtd * (2 ** (self.dac_bits + 1) - 1)
        txtd_dac_real = np.int16(txtd_dac.real).reshape(-1, self.n_par_strms_tx)
        txtd_dac_imag = np.int16(txtd_dac.imag).reshape(-1, self.n_par_strms_tx)

        data = np.zeros((txtd_dac_real.shape[0] * 2, txtd_dac_real.shape[1]), dtype='int16')

        if mode==1:
            data[::2] = np.int16(txtd_dac_real)
            data[1::2] = np.int16(txtd_dac_imag)
        elif mode==2:
            data[::2] = np.int16(txtd_dac_imag)
            data[1::2] = np.int16(txtd_dac_real)
        else:
            raise ValueError('Unsupported TX mode: %d' %(mode))
        
        data = data.flatten()
        self.dac_tx_buffer[:] = data[:]

        print("Loading txtd data to DAC TX buffer done")


    def load_data_from_rx_buffer(self, mode=1):
        rx_data = np.array(self.adc_rx_buffer).astype('int16') / (2 ** (self.adc_bits + 1) - 1)
        n_samples = np.shape(rx_data)[0]
        self.rxtd = [0 + 1j * 0] * n_samples
        
        if mode==1:
            self.rxtd = rx_data[::2] + 1j * rx_data[1::2]
        elif mode==2:
            self.rxtd = rx_data[1::2] + 1j * rx_data[::2]
        else:
            raise ValueError('Unsupported RX mode: %d' %(mode))
        
        print("Loading rxtd data from ADC RX buffer done")


    def send_frame(self, txtd, mode=1):
        self.load_data_to_tx_buffer(txtd, mode=mode)

        self.gpio_dic['dac_mux_sel'].write(0)
        self.gpio_dic['dac_enable'].write(0)
        if 'ddr4' in self.project:
            self.gpio_dic['dac_reset'].write(1)  # Reset ON
        else:
            self.gpio_dic['dac_reset'].write(0)
        time.sleep(0.5)
        if 'ddr4' in self.project:
            self.gpio_dic['dac_reset'].write(0)  # Reset OFF
        else:
            self.gpio_dic['dac_reset'].write(1)
        self.dma_tx.transfer(self.dac_tx_buffer)
        self.dma_tx.wait()
        self.gpio_dic['dac_mux_sel'].write(1)
        self.gpio_dic['dac_enable'].write(1)

        # self.dma_tx.wait()
        print("Frame sent via DAC")


    def recv_frame_one(self, mode=1, nframe=1):

        if 'ddr4' in self.project:
            self.rx_reg.write(0, self.n_samples // self.n_par_strms_rx)
            self.rx_reg.write(4, self.n_skip // self.n_par_strms_rx)
            self.rx_reg.write(8, nframe * self.n_samples * 4)

            self.gpio_dic['adc_reset'].write(0)
        else:
            self.gpio_dic['adc_enable'].write(0)
            self.gpio_dic['adc_reset'].write(0)  # Reset ON
            time.sleep(0.01)
            self.gpio_dic['adc_reset'].write(1)  # Reset OFF

        self.dma_rx.transfer(self.adc_rx_buffer)
        self.gpio_dic['adc_enable'].write(1)
        self.dma_rx.wait()
        self.load_data_from_rx_buffer(mode=mode)

        self.gpio_dic['adc_enable'].write(0)

        if 'ddr4' in self.project:
            self.gpio_dic['adc_reset'].write(1)
        else:
            self.gpio_dic['adc_reset'].write(0)

        print("Frames received from ADC")

