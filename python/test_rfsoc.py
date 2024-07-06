from rfsoc import *
from signals import *
from numpy.fft import fft, fftshift, ifft


bit_file_path = './design_1.bit'
dac_fs = 245.76e6 * 4
adc_fs = 245.76e6 * 4
n_samples = 1024
nfft = 1024
mix_freq_mhz = 800.
mix_phase_off = 0
sig_mode = 'wideband'     # tone or wideband or load
sig_path = './txtd.npy'
wb_sc_min = -200
wb_sc_max = 200
f_tone = 20e6
sig_modulation = 'qam'      # qam or empty
dac_tile_id = 1
dac_block_id = 0
adc_tile_id = 2
adc_block_id = 0


signals_inst = signals(seed=100, fs= dac_fs, n_samples=n_samples, nfft=nfft)

if sig_mode == 'tone':
    txtd = signals_inst.generate_tone(f=f_tone)
elif sig_mode == 'wideband':
    txtd = signals_inst.generate_wideband(sc_min=wb_sc_min, sc_max=wb_sc_max, mode=sig_modulation)
elif sig_mode == 'load':
    txtd = np.load(sig_path)
else:
    raise ValueError('Unsupported signal mode: ' + sig_mode)
txtd /= np.max([np.abs(txtd.real), np.abs(txtd.imag)])


freq_tx = ((np.arange(1, nfft + 1) / nfft) - 0.5) * dac_fs
txfd = np.abs(fftshift(fft(txtd)))
title = 'TX signal spectrum'
xlabel = 'Frequency (Hz)'
ylabel = 'Magnitude (dB)'
signals_inst.plot_signal(freq_tx, txfd, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel)


lmkx_freq = {'lmk_freq': 122.88, 'lmx_freq': 3932.16}
dac_adc_fs = {'dac_fs': dac_fs, 'adc_fs': adc_fs}
dac_adc_ids = {'dac_tile_id': dac_tile_id, 'dac_block_id': dac_block_id, 'adc_tile_id': adc_tile_id, 'adc_block_id': adc_block_id}
rfsoc_2x2_inst = rfsoc_2x2(lmkx_freq=lmkx_freq, dac_adc_fs=dac_adc_fs, n_samples=n_samples, dac_adc_ids=dac_adc_ids)

rfsoc_2x2_inst.load_bit_file(bit_file_path)


rfsoc_2x2_inst.allocate_inout()
rfsoc_2x2_inst.gpio_init()
rfsoc_2x2_inst.clock_init()


rfsoc_2x2_inst.dac_init(mix_freq_mhz=mix_freq_mhz, mix_phase_off=mix_phase_off, DynamicPLLConfig=None)
rfsoc_2x2_inst.adc_init(mix_freq_mhz=mix_freq_mhz, mix_phase_off=mix_phase_off, DynamicPLLConfig=None)
rfsoc_2x2_inst.dma_init()


rfsoc_2x2_inst.load_data_to_tx_buffer(txtd)
rfsoc_2x2_inst.send_frame()

rfsoc_2x2_inst.recv_frame_one()

freq_rx = ((np.arange(1, nfft + 1) / nfft) - 0.5) * adc_fs
rxfd = np.abs(fftshift(fft(rfsoc_2x2_inst.rxtd)))
title = 'RX signal spectrum'
xlabel = 'Frequency (Hz)'
ylabel = 'Magnitude (dB)'
signals_inst.plot_signal(freq_rx, rxfd, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel)

h_est = signals_inst.channel_estimate(rfsoc_2x2_inst.txtd, rfsoc_2x2_inst.rxtd)