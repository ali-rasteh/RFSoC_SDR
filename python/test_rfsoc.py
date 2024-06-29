from rfsoc import *
from signals import *
from numpy.fft import fft, fftshift, ifft


bit_file_path = './design_1.bit'
fs = 245.76e6 * 4
n_samples = 1024
nfft = 1024
mix_freq_mhz = 500.
mix_phase_off = 0
sig_mode = 'narrowband'     # narrowband or wideband
sig_path = './txtd.npy'     # narrowband or wideband
sc_min=-100
sc_max=100
sig_modulation = 'qam'
dac_tile_id = 1
dac_block_id = 0
adc_tile_id = 2
adc_block_id = 0


signals_inst = signals(seed=100, fs= fs, n_samples=n_samples, nfft=nfft)

if sig_mode == 'narrowband':
    txtd = signals_inst.generate_tone(f=10e6)
elif sig_mode == 'wideband':
    txtd = signals_inst.generate_wideband(sc_min=sc_min, sc_max=sc_max, mode=sig_modulation)
elif sig_mode == 'load':
    txtd = np.load(sig_path)
else:
    raise ValueError('Unsupported signal mode: ' + sig_mode)
txtd /= np.max([np.abs(txtd.real), np.abs(txtd.imag)])


freq = ((np.arange(1, nfft + 1) / nfft) - 0.5) * fs
txfd = np.abs(fftshift(fft(txtd)))
title = 'TX signal spectrum'
xlabel = 'Frequency (Hz)'
ylabel = 'Magnitude (dB)'
signals_inst.plot_signal(freq, txfd, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel)


lmkx_freq = {'lmk_freq': 122.88, 'lmx_freq': 3932.16}
dac_adc_ids = {'dac_tile_id': dac_tile_id, 'dac_block_id': dac_block_id, 'adc_tile_id': adc_tile_id, 'adc_block_id': adc_block_id}
rfsoc_2x2_inst = rfsoc_2x2(lmkx_freq=lmkx_freq, n_samples=n_samples, dac_ads_ids=dac_adc_ids)


rfsoc_2x2_inst.load_bit_file(bit_file_path)
rfsoc_2x2_inst.allocate_inout()
rfsoc_2x2_inst.gpio_init()
rfsoc_2x2_inst.clock_init()
rfsoc_2x2_inst.dac_init(mix_freq_mhz=mix_freq_mhz, mix_phase_off=mix_phase_off, DynamicPLLConfig=None)
rfsoc_2x2_inst.adc_init(mix_freq_mhz=mix_freq_mhz, mix_phase_off=mix_phase_off, DynamicPLLConfig=None)
rfsoc_2x2_inst.dma_init()
rfsoc_2x2_inst.send_frame()
rfsoc_2x2_inst.load_data_to_tx_buffer(txtd)
rfsoc_2x2_inst.recv_frame_one()
h_est = signals_inst.channel_estimate(rfsoc_2x2_inst.txtd, rfsoc_2x2_inst.rxtd)

rxfd = np.abs(fftshift(fft(rfsoc_2x2_inst.rxtd)))
title = 'RX signal spectrum'
xlabel = 'Frequency (Hz)'
ylabel = 'Magnitude (dB)'
signals_inst.plot_signal(freq, rxfd, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel)
