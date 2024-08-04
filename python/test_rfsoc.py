from rfsoc import *
from signals import *
from numpy.fft import fft, fftshift, ifft


bit_file_path = './design_1.bit'
dac_fs = 245.76e6 * 4
adc_fs = 245.76e6 * 4
n_samples = 1024
nfft = 1024
sig_modulation = 'qam'      # qam or empty
dac_tile_id = 1
dac_block_id = 0
adc_tile_id = 2
adc_block_id = 0
mix_phase_off = 0.0
sig_path = './txtd.npy'


mix_freq = 800e6
mixer_mode = 'analog'         # analog or digital
do_mixer_settings = True
sig_mode = 'wideband'     # tone_1 or tone_2 or wideband or wideband_null or load
wb_bw = 200e6            # 16.4e6 * 2 for function generator
f_tone = 20e6
do_pll_settings = False
tx_mode = 1     # Default was 1
rx_mode = 1     # Default was 1


signals_inst = signals(seed=100, fs= dac_fs, n_samples=n_samples, nfft=nfft)

if sig_mode == 'tone_1' or sig_mode == 'tone_2':
    txtd_base = signals_inst.generate_tone(f=f_tone, sig_mode=sig_mode)
elif sig_mode == 'wideband' or sig_mode == 'wideband_null':
    txtd_base = signals_inst.generate_wideband(bw=wb_bw, modulation=sig_modulation, sig_mode=sig_mode)
elif sig_mode == 'load':
    txtd_base = np.load(sig_path)
else:
    raise ValueError('Unsupported signal mode: ' + sig_mode)
txtd_base /= np.max([np.abs(txtd_base.real), np.abs(txtd_base.imag)])


freq_tx = ((np.arange(0, nfft) / nfft) - 0.5) * dac_fs
txfd_base = np.abs(fftshift(fft(txtd_base)))
title = 'TX signal spectrum in base-band'
xlabel = 'Frequency (Hz)'
ylabel = 'Magnitude (dB)'
signals_inst.plot_signal(freq_tx, txfd_base, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel)


lmkx_freq = {'lmk_freq': 122.88, 'lmx_freq': 3932.16}
dac_adc_fs = {'dac_fs': dac_fs, 'adc_fs': adc_fs}
dac_adc_ids = {'dac_tile_id': dac_tile_id, 'dac_block_id': dac_block_id, 'adc_tile_id': adc_tile_id, 'adc_block_id': adc_block_id}
rfsoc_2x2_inst = rfsoc_2x2(lmkx_freq=lmkx_freq, dac_adc_fs=dac_adc_fs, n_samples=n_samples, dac_adc_ids=dac_adc_ids)

rfsoc_2x2_inst.load_bit_file(bit_file_path)


rfsoc_2x2_inst.allocate_inout()
rfsoc_2x2_inst.gpio_init()
rfsoc_2x2_inst.clock_init()


if mixer_mode == 'digital' and mix_freq!=0:
    txtd = signals_inst.freq_shift(txtd_base, shift=mix_freq)

    txfd = np.abs(fftshift(fft(txtd)))
    title = 'TX signal spectrum after upconversion'
    xlabel = 'Frequency (Hz)'
    ylabel = 'Magnitude (dB)'
    signals_inst.plot_signal(freq_tx, txfd, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel)

    mix_freq_dac = 0
    mix_freq_adc = 0

elif mixer_mode == 'analog':
    # do_mixer_settings = True
    mix_freq_dac = mix_freq
    mix_freq_adc = mix_freq
    txtd = txtd_base.copy()
    txfd = txfd_base.copy()
    
else:
    mix_freq_dac = 0
    mix_freq_adc = 0
    txtd = txtd_base.copy()
    txfd = txfd_base.copy()

if do_pll_settings:
    DynamicPLLConfig = (0, 122.88, 3932.16)
else:
    DynamicPLLConfig = None
rfsoc_2x2_inst.dac_init(mix_freq=mix_freq_dac, mix_phase_off=mix_phase_off, DynamicPLLConfig=DynamicPLLConfig, do_mixer_settings=do_mixer_settings)
rfsoc_2x2_inst.adc_init(mix_freq=mix_freq_adc, mix_phase_off=mix_phase_off, DynamicPLLConfig=DynamicPLLConfig, do_mixer_settings=do_mixer_settings)
rfsoc_2x2_inst.dma_init()


rfsoc_2x2_inst.send_frame(txtd, mode=tx_mode)
rfsoc_2x2_inst.recv_frame_one(mode=rx_mode)

freq_rx = ((np.arange(0, nfft) / nfft) - 0.5) * adc_fs
rxfd = np.abs(fftshift(fft(rfsoc_2x2_inst.rxtd)))
title = 'RX signal spectrum'
xlabel = 'Frequency (Hz)'
ylabel = 'Magnitude (dB)'
signals_inst.plot_signal(freq_rx, rxfd, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel)

if mixer_mode == 'digital' and mix_freq!=0:
    
    rxtd_base = signals_inst.freq_shift(rfsoc_2x2_inst.rxtd, shift=-1*mix_freq)

    rxfd_base = np.abs(fftshift(fft(rxtd_base)))
    title = 'RX signal spectrum after downconversion'
    xlabel = 'Frequency (Hz)'
    ylabel = 'Magnitude (dB)'
    signals_inst.plot_signal(freq_rx, rxfd_base, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel)

else:
    rxtd_base = rfsoc_2x2_inst.rxtd.copy()
    rxfd_base = rxfd.copy()

rxtd_base = signals_inst.filter(rxtd_base, cutoff=200e6)
rxfd_base = np.abs(fftshift(fft(rxtd_base)))
title = 'RX signal spectrum after filtering in base-band'
xlabel = 'Frequency (Hz)'
ylabel = 'Magnitude (dB)'
signals_inst.plot_signal(freq_rx, rxfd_base, scale='dB', title=title, xlabel=xlabel, ylabel=ylabel)


h_est = signals_inst.channel_estimate(txtd_base, rxtd_base)

