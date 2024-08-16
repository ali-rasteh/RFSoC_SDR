from pynq import Overlay, allocate, interrupt, GPIO
from pynq.lib import dma
import xrfclk
import xrfdc
import numpy as np
import matplotlib.pyplot as plt
import os
import time


class rfsoc_2x2(object):
    def __init__(self, lmkx_freq=None, dac_adc_fs=None, n_samples=1024, dac_adc_ids=None):

        self.n_samples = n_samples

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

        self.txtd = None
        self.rxtd = None

        print("rfsoc_2x2 object initialization done")

    def load_bit_file(self, bit_file_path, verbose=False):

        print("Starting to load the bit-file")

        self.ol = Overlay(bit_file_path)
        if verbose:
            self.ol.ip_dict
            # ol?

        print("Bit-file loading done")

    def allocate_inout(self):

        self.dac_tx_buffer = allocate(shape=(self.n_samples * 2,), dtype=np.int16)
        self.adc_rx_buffer = allocate(shape=(self.n_samples * 2,), dtype=np.int16)

        print("Input/output buffers allocation done")

    def gpio_init(self):

        self.gpio_dic = {}

        self.gpio_dic['dac_mux_sel'] = GPIO(GPIO.get_gpio_pin(0), 'out')
        self.gpio_dic['dac_enable'] = GPIO(GPIO.get_gpio_pin(1), 'out')
        self.gpio_dic['adc_reset'] = GPIO(GPIO.get_gpio_pin(2), 'out')
        self.gpio_dic['adc_enable'] = GPIO(GPIO.get_gpio_pin(3), 'out')
        self.gpio_dic['dac_reset'] = GPIO(GPIO.get_gpio_pin(4), 'out')

        self.gpio_dic['dac_mux_sel'].write(0)
        self.gpio_dic['dac_enable'].write(0)
        self.gpio_dic['dac_reset'].write(0)
        self.gpio_dic['adc_enable'].write(0)
        self.gpio_dic['adc_reset'].write(0)

        print("PS-PL GPIOs initialization done")

    def clock_init(self):

        xrfclk.set_ref_clks(lmk_freq=self.lmkx_freq['lmk_freq'], lmx_freq=self.lmkx_freq['lmx_freq'])
        print("Xrfclk initialization done")

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

        self.dma_tx = self.ol.TX_loop.axi_dma_tx.sendchannel
        print("TX DMA setup done")

        self.dma_rx = self.ol.RX_Logic.axi_dma_rx.recvchannel
        print("RX DMA setup done")

    def load_data_to_tx_buffer(self, txtd, mode=1):
        self.txtd = txtd
        txtd_dac = self.txtd * (2 ** (self.dac_bits + 1) - 1)

        if mode==1:
            self.dac_tx_buffer[::2] = np.real(txtd_dac)
            self.dac_tx_buffer[1::2] = np.imag(txtd_dac)
        elif mode==2:
            self.dac_tx_buffer[::2] = np.imag(txtd_dac)
            self.dac_tx_buffer[1::2] = np.real(txtd_dac)
        else:
            raise ValueError('Unsupported TX mode: %d' %(mode))

        print("Loading txtd data to DAC TX buffer done")

    def load_data_from_rx_buffer(self, mode=1):
        rx_data = np.array(self.adc_rx_buffer).astype(np.int16) / (2 ** (self.adc_bits + 1) - 1)
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
        self.gpio_dic['dac_reset'].write(0)  # Reset ON
        time.sleep(0.5)
        self.gpio_dic['dac_reset'].write(1)  # Reset OFF
        self.dma_tx.transfer(self.dac_tx_buffer)
        # self.dma_tx.wait()
        self.gpio_dic['dac_mux_sel'].write(1)
        self.gpio_dic['dac_enable'].write(1)

        self.dma_tx.wait()
        print("Frame sent via DAC")

    def recv_frame_one(self, mode=1):

        self.gpio_dic['adc_enable'].write(0)
        self.gpio_dic['adc_reset'].write(0)  # Reset ON
        time.sleep(0.5)
        self.gpio_dic['adc_reset'].write(1)  # Reset OFF
        self.dma_rx.transfer(self.adc_rx_buffer)
        self.gpio_dic['adc_enable'].write(1)
        self.dma_rx.wait()
        self.load_data_from_rx_buffer(mode=mode)

        self.gpio_dic['adc_enable'].write(0)
        self.gpio_dic['adc_reset'].write(0)

        print("Frame received from ADC")

