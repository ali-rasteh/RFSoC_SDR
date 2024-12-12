"""
This module conditionally imports various libraries and modules based on the specified flags.
It also sets up some common functions and constants for numerical and scientific computing.

Flags:
    import_general (bool): If True, imports general-purpose libraries.
    import_networking (bool): If True, imports networking libraries.
    import_matplotlib (bool): If True, imports matplotlib for plotting.
    import_numpy (bool): If True, imports numpy for numerical computations.
    import_scipy (bool): If True, imports scipy for scientific computations.
    import_cupy (bool): If True, attempts to import cupy for GPU-accelerated numerical computations.
    import_cupyx (bool): If True, attempts to import cupyx for GPU-accelerated scientific computations.
    import_sklearn (bool): If True, imports scikit-learn for machine learning.
    import_cv2 (bool): If True, imports OpenCV for computer vision.
    import_torch (bool): If True, imports PyTorch for deep learning.
    import_pynq (bool): If True, imports PYNQ libraries for FPGA development.
    import_sivers (bool): If True, imports pyftdi for FTDI communication.
    import_adafruit (bool): If True, imports Adafruit libraries for hardware control.

Attributes:
    be_np (module): Backend module for numerical computations (numpy or cupy).
    be_scp (module): Backend module for scientific computations (scipy or cupyx.scipy).
    be_scp_sig (module): Backend module for signal processing (scipy.signal or cupyx.scipy.signal).
"""

import_general=True
import_networking=True
import_matplotlib=True
import_numpy=True
import_scipy=True
import_cupy=False
import_cupyx=False
import_sklearn=False
import_cv2=False
import_torch=True
import_pynq=False
import_sivers=False
import_adafruit=False

be_np = None
be_scp = None


if import_general:
    import importlib
    import os
    import shutil
    import nbformat
    import copy
    import platform
    import argparse
    import time
    import datetime
    import subprocess
    import random
    import string
    import paramiko
    from types import SimpleNamespace
    import itertools
    import heapq
    import atexit

if import_networking:
    from scp import SCPClient
    import requests
    import socket

if import_matplotlib:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.colors import LogNorm
    from matplotlib.patches import Wedge, Circle, FancyArrow
    # matplotlib.use('TkAgg')
    # matplotlib.use('WebAgg')
    # matplotlib.use('Agg')

if import_numpy:
    import numpy
    be_np = importlib.import_module('numpy')

if import_scipy:
    be_scp = importlib.import_module('scipy')
    be_scp_sig = importlib.import_module('scipy.signal')

if import_cupy:
    try:
        be_np = importlib.import_module('cupy')
    except ImportError:
        be_np = importlib.import_module('numpy')

if import_cupyx:
    try:
        be_scp = importlib.import_module('cupyx.scipy')
        be_scp_sig = importlib.import_module('cupyx.scipy.signal')
    except ImportError:
        be_scp = importlib.import_module('scipy')
        be_scp_sig = importlib.import_module('scipy.signal')

if import_numpy or import_cupy:
    fft = be_np.fft.fft
    ifft = be_np.fft.ifft
    fftshift = be_np.fft.fftshift
    ifftshift = be_np.fft.ifftshift

    randn = be_np.random.randn
    rand = be_np.random.rand
    randint = be_np.random.randint
    uniform = be_np.random.uniform
    normal = be_np.random.normal
    choice = be_np.random.choice
    exponential = be_np.random.exponential

if import_scipy or import_cupyx:
    constants = be_scp.constants
    chi2 = be_scp.stats.chi2

    firwin = be_scp_sig.firwin
    lfilter = be_scp_sig.lfilter
    filtfilt = be_scp_sig.filtfilt
    freqz = be_scp_sig.freqz
    welch = be_scp_sig.welch
    upfirdn = be_scp_sig.upfirdn
    convolve = be_scp_sig.convolve
    resample = be_scp_sig.resample

if import_sklearn:
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

if import_cv2:
    try:
        import cv2
    except ImportError:
        pass

if import_torch:
    try:
        import torch
        from torch import nn, optim
        import torch.nn.functional as F
        from torch.utils.data import Dataset, DataLoader, random_split
        import torchvision.transforms as transforms
    except ImportError:
        pass


if import_pynq:
    from pynq import Overlay, allocate, MMIO, Clocks, interrupt, GPIO
    from pynq.lib import dma
    import xrfclk
    import xrfdc

if import_sivers:
    from pyftdi.ftdi import Ftdi

if import_adafruit:
    import board
    from adafruit_motorkit import MotorKit
    from adafruit_motor import stepper