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

        self.adc_max_fs_mhz = 4096
        self.dac_max_fs_mhz = 6554
        self.adc_fs = 6554
        self.dac_max_fs_mhz = 6554

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

    def dac_init(self, mix_freq_mhz=500e6, mix_phase_off=0, DynamicPLLConfig=None):
        if DynamicPLLConfig is None:
            PLLConfig = (0, 122.88, 3932.16)
        else:
            PLLConfig = DynamicPLLConfig

        self.dac_tile = self.ol.usp_rf_data_converter_0.dac_tiles[self.dac_tile_id]
        # dac_tile.DynamicPLLConfig(PLLConfig[0], PLLConfig[1], PLLConfig[2])
        self.dac_block = self.dac_tile.blocks[self.dac_block_id]
        self.dac_tile.Reset()
        print("DAC init and reset done")

        self.dac_block.MixerSettings['Freq'] = mix_freq_mhz
        self.dac_block.MixerSettings['PhaseOffset'] = mix_phase_off
        # self.dac_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_IMMEDIATE
        self.dac_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_TILE
        self.dac_block.UpdateEvent(xrfdc.EVNT_SRC_TILE)
        self.dac_tile.SetupFIFO(True)

        print("DAC Mixer Settings done")

    def adc_init(self, mix_freq_mhz, mix_phase_off, DynamicPLLConfig=None):
        if DynamicPLLConfig is None:
            PLLConfig = (0, 122.88, 3932.16)
        else:
            PLLConfig = DynamicPLLConfig

        self.adc_tile = self.ol.usp_rf_data_converter_0.adc_tiles[self.adc_tile_id]
        # self.adc_tile.DynamicPLLConfig(PLLConfig[0], PLLConfig[1], PLLConfig[2])
        self.adc_block = self.adc_tile.blocks[self.adc_block_id]
        self.adc_tile.Reset()
        print("ADC init and reset done")

        self.adc_block.MixerSettings['Freq'] = mix_freq_mhz
        self.adc_block.MixerSettings['PhaseOffset'] = mix_phase_off
        # self.adc_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_IMMEDIATE
        # self.adc_block.MixerSettings['EventSource'] = xrfdc.EVNT_SRC_TILE
        self.adc_block.UpdateEvent(xrfdc.EVNT_SRC_TILE)
        self.adc_block.MixerSettings['Freq'] = mix_freq_mhz
        self.adc_tile.SetupFIFO(True)
        for toggleValue in range(0, 1):
            self.adc_tile.SetupFIFO(toggleValue)

        print("ADC Mixer Settings done")

    def dma_init(self):

        self.dma_tx = self.ol.TX_loop.axi_dma_tx.sendchannel
        print("TX DMA setup done")

        self.dma_rx = self.ol.RX_Logic.axi_dma_rx.recvchannel
        print("RX DMA setup done")

    def load_data_to_tx_buffer(self, txtd):
        self.txtd = txtd
        self.txtd *= (2 ** (self.dac_bits + 1) - 1)
        self.dac_tx_buffer[::2] = np.real(self.txtd)
        self.dac_tx_buffer[1::2] = np.imag(self.txtd)

        print("Loading txtd data to DAC TX buffer done")

    def load_data_from_rx_buffer(self):
        rx_data = np.array(self.adc_rx_buffer).astype(np.int16) / (2 ** (self.adc_bits + 1) - 1)
        n_samples = np.shape(rx_data)[0]
        self.rxtd = [0 + 1j * 0] * n_samples
        self.rxtd = rx_data[::2] + 1j * rx_data[1::2]

        print("Loading rxtd data from ADC RX buffer done")

    def send_frame(self):
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

    def recv_frame_one(self):

        self.gpio_dic['adc_enable'].write(0)
        self.gpio_dic['adc_reset'].write(0)  # Reset ON
        time.sleep(0.5)
        self.gpio_dic['adc_reset'].write(1)  # Reset OFF
        self.dma_rx.transfer(self.adc_rx_buffer)
        self.gpio_dic['adc_enable'].write(1)
        self.dma_rx.wait()
        self.load_data_from_rx_buffer()

        self.gpio_dic['adc_enable'].write(0)
        self.gpio_dic['adc_reset'].write(0)

        print("Frame received from ADC")

