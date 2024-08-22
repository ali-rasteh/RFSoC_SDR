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






import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft, fftshift
from scipy.signal import convolve


def config_param():
    N_blocks = 1000
    sys_param = {}

    # Signal parameters
    sys_param['N_cp'] = 32
    sys_param['N_fft'] = 128
    sys_param['M'] = 16
    n_vec = np.arange(sys_param['N_fft'])
    sys_param['x'] = np.exp(1j * np.pi * n_vec ** 2 / sys_param['N_fft'])
    # print(np.shape(sys_param['x']))
    sys_param['x_cp'] = np.concatenate((sys_param['x'][-sys_param['N_cp']:], sys_param['x']))
    # print(np.shape(sys_param['x_cp']))
    sys_param['X'] = fft(sys_param['x'])
    # print(np.shape(sys_param['X']))
    sys_param['tx_signal'] = np.tile(sys_param['x_cp'], N_blocks)
    # print(np.shape(sys_param['tx_signal']))

    return sys_param


def delay_doppler_processing(sys_param, data):
    plt.figure(1)
    plt.subplot(3, 1, 1)

    # Time synchronization
    data_sync = data[:4 * sys_param['N_fft'] - 1]
    print(np.shape(data_sync))
    rx = convolve(np.conj(sys_param['x']), data_sync, mode='full')
    print(np.shape(rx))
    plt.plot(np.abs(rx))
    index_ini = np.argmax(rx)
    print(index_ini)

    # Retrieve time-synced signal
    N_vec = (np.tile(np.arange(sys_param['N_fft']), sys_param['M']) +
             np.repeat(np.arange(sys_param['M']), sys_param['N_fft']) *
             (sys_param['N_fft'] + sys_param['N_cp']) +
             sys_param['N_cp'] + 1)
    # print(N_vec.shape)
    # print(index_ini)
    # print(np.shape(N_vec))
    # print(data[N_vec + index_ini - 3])
    # Y = data[N_vec + index_ini - 3].reshape((sys_param['N_fft'], sys_param['M']))
    Y = data[N_vec + index_ini - 3].reshape((sys_param['M'], sys_param['N_fft'])).T
    # print(np.shape(Y))
    # print(Y)

    # Equalized frequency
    # print(sys_param['X'])
    # print(fft(Y, axis=0))
    H_hat = fft(Y, axis=0) / sys_param['X'][:,None]
    # print(H_hat)
    # Averaged frequency
    H_hat_avg = np.mean(H_hat, axis=1)
    # print(H_hat_avg)

    # Equalized time
    h_hat = ifft(H_hat, axis=0)
    h_hat = h_hat[:sys_param['N_cp'], :]

    # Averaged time
    h_hat_avg = np.mean(h_hat, axis=1)

    # Plots
    plt.subplot(3, 1, 2)
    plt.plot(np.abs(h_hat_avg))

    plt.subplot(3, 1, 3)
    plt.plot(fftshift(10 * np.log10(np.abs(H_hat_avg) ** 2)))
    plt.axis([1, sys_param['N_fft'], -100, 0])

    H_dd = fft(h_hat.T, axis=0).T / np.sqrt(sys_param['N_fft'] * sys_param['M'])
    H_dd_log = 10 * np.log10(np.abs(H_dd) ** 2)
    H_dd_log[H_dd_log < -130] = -130

    plt.figure(2)
    plt.pcolor(H_dd_log)
    plt.colorbar()
    plt.show()


# Example usage
sys_param = config_param()
num_frames = 1

# Here, you would set up your SDR receiver and receive data
# For the purpose of this example, we'll assume `data` is received correctly
# data = np.random.randn(5 * sys_param['N_fft'] * sys_param['M'])
# data = sys_param['tx_signal'] + 0.1*np.random.randn(*np.shape(sys_param['tx_signal'])) + 1j*0.01*np.random.randn(*np.shape(sys_param['tx_signal']))
data = sys_param['tx_signal']

for frame in range(num_frames):
    delay_doppler_processing(sys_param, data)

# Release any resources if necessary
