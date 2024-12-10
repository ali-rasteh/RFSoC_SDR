import numpy as np
import torch


# arr = np.array([[3, 7, 8],
#                 [1, 5, 2],
#                 [4, 9, 6]])

# # Sort along the first dimension (sorts each column)
# sorted_arr = np.sort(arr, axis=0)

# print(sorted_arr)




# # Example arrays
# arr1 = np.array([[3, 7, 8],
#                  [1, 5, 2],
#                  [4, 9, 6]])

# arr2 = np.array([[30, 70, 80],
#                  [10, 50, 20],
#                  [40, 90, 60]])

# # Get sorting indices based on the first array
# sorted_indices = np.argsort(arr1, axis=0)

# # Sort both arrays using the same indices
# sorted_arr1 = np.take_along_axis(arr1, sorted_indices, axis=0)
# sorted_arr2 = np.take_along_axis(arr2, sorted_indices, axis=0)

# print("Sorted arr1:")
# print(sorted_arr1)

# print("Sorted arr2:")
# print(sorted_arr2)



# print(np.dot([1+1j, 1+2j], [2+3j, 4+5j]))


# import numpy as np
# import matplotlib.pyplot as plt

# # Parameters
# Nfft = 1024
# Nshift = Nfft // 4

# n_vec = np.arange(0, Nfft)
# Non = 500
# index_zeros = np.arange(Non // 2, Nfft - Non // 2)
# index_on = np.concatenate((np.arange(0, Non // 2), np.arange(Nfft - Non // 2, Nfft)))

# # X1 and X2 are orthogonal if the discrete-time delay spread is smaller than Nshift
# # Ensure the condition L < Nshift
# # Set Nshift = Nfft / 4 so the channels of TX antennas 1 and 2 do not overlap
# # Important: Nshift = Nfft / 2 makes it impossible to distinguish the transmit antennas
# # This works if X1 has constant amplitude in FD (true for ZC sequence)

# # Generate TX signal at antenna 1
# X1 = np.exp(-1j * np.pi * n_vec**2 / Nfft)
# X1[index_zeros] = 0

# # Verify there are Nfft - Non zeros
# assert np.sum(X1 != 0) == Non, "Number of non-zero elements is incorrect"

# # Compute the IFFT for time-domain signal x1
# x1 = np.fft.ifft(X1)

# # Generate TX signal at antenna 2 by circularly shifting x1
# x2 = np.roll(x1, Nshift)

# # Plot the magnitude spectra
# plt.figure()
# plt.plot(20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(x1)))), label='Antenna 1 (x1)')
# plt.plot(20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(x2)))), '--', label='Antenna 2 (x2)')
# plt.xlabel('Frequency index')
# plt.ylabel('Magnitude (dB)')
# plt.title('Magnitude Spectrum')
# plt.legend()
# plt.grid()
# plt.show()

# # Cross correlations
# x1_dot_x1 = np.vdot(x1, x1)
# x2_dot_x2 = np.vdot(x2, x2)
# x1_dot_x2 = np.abs(np.vdot(x1, x2))

# print(f"x1*x1': {x1_dot_x1}")
# print(f"x2*x2': {x2_dot_x2}")
# print(f"|x1*x2'|: {x1_dot_x2}")



# print([1,2] + [3,4])


