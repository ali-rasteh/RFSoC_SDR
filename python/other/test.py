import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft, fftshift, ifft
from scipy.signal import firwin, lfilter, freqz, welch
import os
import time



plt.figure()
txtd_base_up = signals_inst.upsample(txtd_base, up=2)
txfd_base_up = np.abs(fftshift(fft(txtd_base_up)))
freq_tx_up = ((np.arange(0, 2*nfft) / nfft) - 1.0) * 0.5 * adc_fs
plt.plot(freq_tx_up,txfd_base_up,'g-')
plt.xlim(-100e6, 100e6)
plt.show()