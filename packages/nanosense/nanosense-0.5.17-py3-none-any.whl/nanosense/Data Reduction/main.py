from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDialog,
                             QTabWidget, QPushButton, QLabel, QLineEdit, QCheckBox, QComboBox,
                             QProgressBar, QFileDialog, QListWidget, QGroupBox, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QScrollArea, QSplitter, QTableWidget, 
                             QTextEdit, QTableWidgetItem, QToolBar,QListWidgetItem, QSizePolicy,QMessageBox, QInputDialog, QStyleFactory, QDialogButtonBox)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QValidator, QTextCursor,QPalette, QColor
from PySide6.QtGui import QIcon, QValidator, QTextCursor,QPalette, QColor
import sys, os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import neo
from neo.rawio.axonrawio import AxonRawIO
from neo.rawio import AxonRawIO
from neo.core import AnalogSignal
import numpy as np
import pyabf
from scipy.signal import butter, sosfilt, sosfilt_zi, bessel, cheby1, cheby2, ellip, lfilter, firwin
from scipy.ndimage import uniform_filter1d
from joblib import Parallel, delayed
import ruptures as rpt
import scipy.signal as sig
import scipy.stats as stats
import pywt
import logging
from datetime import datetime
import time
import gc
import multiprocessing as mp
from joblib import parallel_backend
parallel_backend("loky")
from detecta import detect_cusum
from hmmlearn import hmm
from sklearn.mixture import GaussianMixture
import h5py
import json
import math
import numexpr as ne
import logging
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
from matplotlib import rc
rc('animation', html='jshtml')



logging.getLogger("qt").setLevel(logging.WARNING)

def get_hdf5_file_info_window(file_path):
    with h5py.File(file_path, 'r') as f:
        sampling_rate = f.attrs['sampling_rate']
    return sampling_rate

def load_hdf5_file(file_path):
    global sampling_rate
    with h5py.File(file_path, 'r') as f:
        selected_data = f['selected_data'][()]
        sampling_rate = f.attrs['sampling_rate']
    return selected_data, sampling_rate

def get_abf_file_info(file_path):
    """
    Returns the total number of data points, length in time, and sampling rate of an .abf file without fully loading it.
    
    Args:
        - file_path (str): Path to the .abf file.
    
    Returns:
        - tuple: A tuple containing the following elements:
            - float: Length of the file in seconds.
            - float: Sampling rate in Hz.
    """
    # Initialize AxonRawIO with the path to the .abf file
    raw_io = AxonRawIO(filename=file_path)
    
    # Parse the file header to access metadata
    raw_io.parse_header()
    
    # Get the total number of samples for the first block and segment
    # Note: This example assumes a single block and segment.
    # Adjust as necessary for files with multiple blocks or segments.
    signal_size = raw_io.get_signal_size(block_index=0, seg_index=0)
    
    # Get the sampling rate
    sampling_rate = raw_io.get_signal_sampling_rate()
    
    # Calculate the length of the file in seconds
    length_in_seconds = signal_size / sampling_rate
    return length_in_seconds, sampling_rate


def load_abf_file_nth(file_path, nth_point):
    try:
        # Create an instance of AxonRawIO
        raw_io = AxonRawIO(filename=file_path)
        # Parse the header information
        raw_io.parse_header()
        # Define the channel index you're interested in
        channel_index = 0
        # Read the signal size for the given block and segment
        signal_size = raw_io.get_signal_size(block_index=0, seg_index=0)
        # Calculate the new signal size based on the nth_point
        new_signal_size = (signal_size + nth_point - 1) // nth_point
        # Get the byte offset and data type of the signal data
        sig_dtype = raw_io._raw_data.dtype
        sig_offset = raw_io._raw_data.offset
        # Create a memory-mapped array of the signal data
        signal_data = np.memmap(file_path, dtype=sig_dtype, mode='r', offset=sig_offset, shape=(signal_size,))
        # Select every nth data point using slicing
        data = signal_data[::int(nth_point)]
        # Convert the data to a physical quantity
        data = raw_io.rescale_signal_raw_to_float(data[:, np.newaxis], dtype='float64', channel_indexes=[channel_index]).flatten()
        # Get the original sampling rate
        original_sampling_rate = raw_io.get_signal_sampling_rate()
        # Calculate the new sampling rate based on the nth_point
        sampling_rate = original_sampling_rate / nth_point
        return data, sampling_rate
    except:
        try:
            reader = neo.io.AxonIO(filename=file_path)
            block = reader.read_block(signal_group_mode='split-all')
            seg = block.segments[0]
            analogsignal = seg.analogsignals[0]
            data = analogsignal.magnitude.flatten()
            sampling_rate = analogsignal.sampling_rate.magnitude
            return data, sampling_rate
        except:
            try:
                abf = pyabf.ABF(file_path)
                data = abf.sweepY
                sampling_rate = abf.dataRate
                return data, sampling_rate
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Error")
                msg.setText("An error has occurred.")
                msg.setInformativeText(f"The selected file ({file_path}) cannot be loaded. \nContact shankar.dutt@anu.edu.au")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                return None, None


def load_abf_file(file_path):
    try:
        # Create an instance of AxonRawIO
        raw_io = AxonRawIO(filename=file_path)

        # Parse the header information
        raw_io.parse_header()

        # Define the channel index you're interested in
        channel_index = 0

        # Read the signal size for the given block and segment without specifying channel_indexes
        signal_size = raw_io.get_signal_size(block_index=0, seg_index=0)

        # Now, read the analog signal data
        # Here, we specify channel_indexes when reading the chunk to ensure we only get data for the desired channel
        data = raw_io.get_analogsignal_chunk(block_index=0, seg_index=0, i_start=0, i_stop=signal_size, channel_indexes=[channel_index])

        # Convert the chunk to a physical quantity
        data = raw_io.rescale_signal_raw_to_float(data, dtype='float64', channel_indexes=[channel_index]).flatten()

        # Get the sampling rate for the specified channel
        sampling_rate = raw_io.get_signal_sampling_rate()
        return data, sampling_rate
    
    except:
        try:
            reader = neo.io.AxonIO(filename=file_path)
            block = reader.read_block(signal_group_mode='split-all')
            seg = block.segments[0]
            analogsignal = seg.analogsignals[0]
            data = analogsignal.magnitude.flatten()
            sampling_rate = analogsignal.sampling_rate.magnitude
            return data, sampling_rate
        except:
            try:
                abf = pyabf.ABF(file_path)
                data = abf.sweepY
                sampling_rate = abf.dataRate
                return data, sampling_rate
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Error")
                msg.setText("An error has occurred.")
                msg.setInformativeText(f"The selected file ({file_path}) cannot be loaded. \nContact shankar.dutt@anu.edu.au")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                return None, None

def _thselect(data, th_type):
    def _sqtwolog(x, n):
        return np.sqrt(2 * np.log(n))
    
    def _minimaxi(x, n):
        if n <= 32:
            return 0
        else:
            return 0.3936 + 0.1829 * (np.log(n) / np.log(2))
    
    try:
        th_algo = {
            'sqtwolog': _sqtwolog,
            'minimaxi': _minimaxi,
        }[th_type]
        
        # Apply to flattened data to handle multi-level coefficients
        flat_data = np.concatenate([np.ravel(d) for d in data[1:]])
        return th_algo(flat_data, len(flat_data))
    except KeyError:
        # Fallback to sqtwolog if th_type is not recognized
        flat_data = np.concatenate([np.ravel(d) for d in data[1:]])
        return _sqtwolog(flat_data, len(flat_data))
    

def apply_low_pass_filter_window(data, cutoff_frequency,type, sampling_rate_window):
    if cutoff_frequency<sampling_rate_window/2:    
        if type == 'Butterworth':
            nyquist_rate = sampling_rate_window / 2.0
            cutoff = cutoff_frequency / nyquist_rate
            sos = butter(N=8, Wn=cutoff, btype='low', analog=False, output='sos')
            
            # Compute initial conditions for the filter
            zi = sosfilt_zi(sos) * data[0]
            
            # Apply the filter with the initial conditions
            filtered_data, _ = sosfilt(sos, data, zi=zi)
            
            return filtered_data
        elif type == 'Bessel':
            nyquist_rate = sampling_rate_window / 2.0
            cutoff = cutoff_frequency / nyquist_rate
            sos = bessel(N=8, Wn=cutoff, btype='low', analog=False, output='sos')
            
            # Compute initial conditions for the filter
            zi = sosfilt_zi(sos) * data[0]
            
            # Apply the filter with the initial conditions
            filtered_data, _ = sosfilt(sos, data, zi=zi)
            
            return filtered_data
        
        elif type == 'Wavelet':
            wavelet_type='db4'
            wavelet_level=None
            wavelet_threshold_sub_type='sqtwolog'
            wavelet_threshold_type='soft'
            w = pywt.Wavelet(wavelet_type)
            max_level = pywt.dwt_max_level(len(data), filter_len=w.dec_len)
            if wavelet_level is None:
                wavelet_level = max_level
            wcoeff = pywt.wavedec(data, w, mode='sym', level=wavelet_level)
            
            thresh = np.std(wcoeff[-1]) * _thselect(wcoeff, wavelet_threshold_sub_type)
            wcoeff[1:] = [pywt.threshold(wc, thresh, wavelet_threshold_type) for wc in wcoeff[1:]]
            
            filtered_data = pywt.waverec(wcoeff, wavelet_type, mode='sym')
            return filtered_data
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.setText("An error has occurred.")
        msg.setInformativeText(f"The selected cutoff frequency is more than sampling rate/2.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        return data
    
def exponential_weights(window_size):
    alpha = 2 / (window_size + 1)
    weights = np.exp(-alpha * np.arange(window_size))
    return weights / weights.sum()

def smooth_threshold(threshold, window_size, smoothing_index, exp_weights=None):
    window_size = 10*window_size
    if smoothing_index == 0:
        smoothed_threshold = sig.fftconvolve(threshold, np.ones(window_size) / window_size, mode='same')
    elif smoothing_index == 1:
        if exp_weights is None:
            exp_weights = exponential_weights(window_size)
        smoothed_threshold = sig.fftconvolve(threshold, exp_weights, mode='same')
    else:
        raise ValueError("Invalid smoothing method. Choose 'moving_average' or 'exponential'.")
    return smoothed_threshold
    
def calculate_rolling_stats_window(data, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate_window):
    avg_window_size_samples = int((avg_window_size_in_ms / 1000) * sampling_rate_window)
    std_window_size_samples = int((std_window_size_in_ms / 1000) * sampling_rate_window)
    
    rolling_avg = uniform_filter1d(data, size=avg_window_size_samples)
    rolling_std = np.sqrt(uniform_filter1d(data**2, size=std_window_size_samples) - uniform_filter1d(data, size=std_window_size_samples)**2)
    
    return rolling_avg, rolling_std


def find_preliminary_events_window(data, threshold_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, dips, sampling_rate_window):
    rolling_avg, rolling_std = calculate_rolling_stats_window(data, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate_window)
    
    if threshold_method == "multiplier":
        if dips == "Yes":
            threshold = rolling_avg - (threshold_multiplier * rolling_std)
        else:
            threshold = rolling_avg + (threshold_multiplier * rolling_std)
    elif threshold_method == "difference":
        if dips == "Yes":
            threshold = rolling_avg - (threshold_difference / 1000)
        else:
            threshold = rolling_avg + (threshold_difference / 1000)
    else:
        raise ValueError("Unsupported threshold_method. Use 'multiplier' or 'difference'.")
    
    
    events = []
    in_event = False
    for i in range(1, len(data)):
        if not in_event and data[i] < threshold[i] and data[i-1] >= threshold[i-1]:
            in_event = True
            event_start = i
        elif in_event and data[i] >= threshold[i] and data[i-1] < threshold[i-1]:
            event_end = i  # Mark the event end at the first crossing
            events.append((event_start, event_end))
            in_event = False
    return events


def exclude_events_and_recalculate_stats_window(data, events, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate_window):
    data_without_events = np.copy(data)
    for start, end in events:
        data_without_events[start:end] = np.nan  # Exclude event data by setting it to NaN

    # Replace NaNs with the mean of their neighboring values for a smooth transition
    nan_indices = np.where(np.isnan(data_without_events))[0]
    for idx in nan_indices:
        if idx > 0 and idx < len(data_without_events) - 1:
            data_without_events[idx] = np.nanmean(data_without_events[idx - 1:idx + 2])

    rolling_avg, rolling_std = calculate_rolling_stats_window(data, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate_window)
    return rolling_avg, rolling_std


def find_events_refined_window(data, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, min_event_width, max_event_width, dips, sampling_rate_window):
    # Step 1: Find preliminary events
    preliminary_events = find_preliminary_events_window(data, threshold_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, dips, sampling_rate_window)

    # Step 2: Recalculate statistics excluding preliminary events
    rolling_avg_refined, rolling_std_refined = exclude_events_and_recalculate_stats_window(data, preliminary_events, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate_window)

    # Step 3: Use the refined statistics to find events again
    adjusted_baseline_start = rolling_avg_refined - start_multiplier * rolling_std_refined
    adjusted_baseline_end = rolling_avg_refined - end_multiplier * rolling_std_refined

    if threshold_method == "multiplier":
        if dips == "Yes":
            threshold_refined = rolling_avg_refined - (threshold_multiplier * rolling_std_refined)
        else:
            threshold_refined = rolling_avg_refined + (threshold_multiplier * rolling_std_refined)
    elif threshold_method == "difference":
        if dips == "Yes":
            threshold_refined = rolling_avg_refined - (threshold_difference / 1000)   
        else:
            threshold_refined = rolling_avg_refined + (threshold_difference / 1000)   

    all_refined_events = []
    in_event = False
    for i in range(1, len(data)):
        if not in_event and data[i] < threshold_refined[i] and data[i-1] >= threshold_refined[i-1]:
            in_event = True
            event_start = i
            # Backtrack to refine event start
            while event_start > 0 and not (data[event_start] < adjusted_baseline_start[event_start] and data[event_start-1] >= adjusted_baseline_start[event_start-1]):
                event_start -= 1
        elif in_event and data[i] >= adjusted_baseline_end[i] and data[i-1] < adjusted_baseline_end[i-1]:
            event_end = i  # Mark the event end at the first crossing
            all_refined_events.append((event_start, event_end))
            in_event = False

    # Step 4: Filter events based on their width (duration)
    filtered_events = []
    for start, end in all_refined_events:
        event_width_in_seconds = (end - start) / sampling_rate_window
        if min_event_width <= event_width_in_seconds <= max_event_width:
            filtered_events.append((start, end))
    
    return filtered_events

def process_chunk_window_abf(file_path, desired_duration, chunk_index, chunk_size, step, channel_index, signal_size, sampling_rate, filter_type, cutoff_freq, threshold_method, dips, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference,avg_window_size_in_ms, std_window_size_in_ms, min_event_width, max_event_width, start_index):
    """
    Process a single chunk of the file.
    This function is intended to be executed in a thread pool.
    """
    adjusted_sampling_rate = sampling_rate / step
    i_start = max(int(chunk_index * chunk_size * step), int(start_index))
    i_stop = min(int((chunk_index + 1) * chunk_size * step), int(signal_size), int(start_index + desired_duration * sampling_rate))
    i_stop = min(i_stop, int(signal_size))  # Ensure not exceeding the signal size  
    
    # Initialize AxonRawIO for each worker to avoid sharing state
    raw_io = AxonRawIO(filename=file_path)
    raw_io.parse_header()
    
    raw_chunk = raw_io.get_analogsignal_chunk(block_index=0, seg_index=0, i_start=i_start, i_stop=i_stop, channel_indexes=[channel_index])
    chunk_data = raw_io.rescale_signal_raw_to_float(raw_chunk, dtype='float64', channel_indexes=[channel_index]).flatten()
    selected_chunk_data = chunk_data[::step]

    chunk_data =  apply_low_pass_filter_window(selected_chunk_data, cutoff_freq, filter_type, adjusted_sampling_rate)

    events =  find_events_refined_window(chunk_data, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, min_event_width, max_event_width, dips, adjusted_sampling_rate)
    rolling_avg_refined, rolling_std_refined = exclude_events_and_recalculate_stats_window(chunk_data, events, avg_window_size_in_ms, std_window_size_in_ms, adjusted_sampling_rate)
    return events, rolling_avg_refined, rolling_std_refined


def process_chunk_window_abf_with_data(file_path, desired_duration, chunk_index, chunk_size, step, channel_index, signal_size, sampling_rate, filter_type, cutoff_freq, threshold_method, dips, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference,avg_window_size_in_ms, std_window_size_in_ms, min_event_width, max_event_width, start_index):
    """
    Process a single chunk of the file and return events, rolling averages, rolling standard deviations, and chunk data.
    This function is intended to be executed in a thread pool.
    """
    adjusted_sampling_rate = sampling_rate / step
    i_start = max(int(chunk_index * chunk_size * step), int(start_index))
    i_stop = min(int((chunk_index + 1) * chunk_size * step), int(signal_size), int(start_index + desired_duration * sampling_rate))
    i_stop = min(i_stop, int(signal_size))  # Ensure not exceeding the signal size  
    
    # Initialize AxonRawIO for each worker to avoid sharing state
    raw_io = AxonRawIO(filename=file_path)
    raw_io.parse_header()
    
    raw_chunk = raw_io.get_analogsignal_chunk(block_index=0, seg_index=0, i_start=i_start, i_stop=i_stop, channel_indexes=[channel_index])
    chunk_data = raw_io.rescale_signal_raw_to_float(raw_chunk, dtype='float64', channel_indexes=[channel_index]).flatten()
    selected_chunk_data = chunk_data[::step]

    chunk_data =  apply_low_pass_filter_window(selected_chunk_data, cutoff_freq, filter_type, adjusted_sampling_rate)

    events =  find_events_refined_window(chunk_data, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, min_event_width, max_event_width, dips, adjusted_sampling_rate)
    rolling_avg_refined, rolling_std_refined = exclude_events_and_recalculate_stats_window(chunk_data, events, avg_window_size_in_ms, std_window_size_in_ms, adjusted_sampling_rate)
    return events, rolling_avg_refined, rolling_std_refined, chunk_data



def process_chunk_window_hdf5(file_path, dataset_name, desired_duration, chunk_index, chunk_size, step, signal_size, sampling_rate, filter_type, cutoff_freq, threshold_method, dips, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, min_event_width, max_event_width, start_index):
    """
    Process a single chunk of the HDF5 dataset.
    This function is intended to be executed in a thread pool.
    """
    adjusted_sampling_rate = sampling_rate / step
    i_start = max(chunk_index * chunk_size * step, start_index)
    i_stop = min((chunk_index + 1) * chunk_size * step, signal_size, start_index + desired_duration * sampling_rate)
    i_stop = min(i_stop, signal_size)  # Ensure not exceeding the signal size

    with h5py.File(file_path, 'r') as f:
        chunk_data = f[dataset_name][i_start:i_stop:step]

    chunk_data = apply_low_pass_filter_window(chunk_data, cutoff_freq, filter_type, adjusted_sampling_rate)

    events = find_events_refined_window(chunk_data, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, min_event_width, max_event_width, dips, adjusted_sampling_rate)
    rolling_avg_refined, rolling_std_refined = exclude_events_and_recalculate_stats_window(chunk_data, events, avg_window_size_in_ms, std_window_size_in_ms, adjusted_sampling_rate)
    return events, rolling_avg_refined, rolling_std_refined


def process_chunk_window_hdf5_with_data(file_path, dataset_name, desired_duration, chunk_index, chunk_size, step, signal_size, sampling_rate, filter_type, cutoff_freq, threshold_method, dips, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, min_event_width, max_event_width, start_index):
    """
    Process a single chunk of the HDF5 dataset.
    This function is intended to be executed in a thread pool.
    """
    adjusted_sampling_rate = sampling_rate / step
    i_start = max(chunk_index * chunk_size * step, start_index)
    i_stop = min((chunk_index + 1) * chunk_size * step, signal_size, start_index + desired_duration * sampling_rate)
    i_stop = min(i_stop, signal_size)  # Ensure not exceeding the signal size

    with h5py.File(file_path, 'r') as f:
        chunk_data = f[dataset_name][i_start:i_stop:step]

    chunk_data = apply_low_pass_filter_window(chunk_data, cutoff_freq, filter_type, adjusted_sampling_rate)

    events = find_events_refined_window(chunk_data, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, min_event_width, max_event_width, dips, adjusted_sampling_rate)
    rolling_avg_refined, rolling_std_refined = exclude_events_and_recalculate_stats_window(chunk_data, events, avg_window_size_in_ms, std_window_size_in_ms, adjusted_sampling_rate)
    return events, rolling_avg_refined, rolling_std_refined, chunk_data
    

def apply_low_pass_filter(data, cutoff_frequency, type, sampling_rate):
    if cutoff_frequency < sampling_rate / 2:
        if type == 'Butterworth':
            nyquist_rate = sampling_rate / 2.0
            cutoff = cutoff_frequency / nyquist_rate
            sos = butter(N=8, Wn=cutoff, btype='low', analog=False, output='sos')
            zi = sosfilt_zi(sos) * data[0]
            filtered_data, _ = sosfilt(sos, data, zi=zi)
            return filtered_data
        elif type == 'Bessel':
            nyquist_rate = sampling_rate / 2.0
            cutoff = cutoff_frequency / nyquist_rate
            sos = bessel(N=8, Wn=cutoff, btype='low', analog=False, output='sos')
            zi = sosfilt_zi(sos) * data[0]
            filtered_data, _ = sosfilt(sos, data, zi=zi)
            return filtered_data
        elif type == 'Chebyshev I':
            nyquist_rate = sampling_rate / 2.0
            cutoff = cutoff_frequency / nyquist_rate
            sos = cheby1(N=8, rp=0.1, Wn=cutoff, btype='low', analog=False, output='sos')
            zi = sosfilt_zi(sos) * data[0]
            filtered_data, _ = sosfilt(sos, data, zi=zi)
            return filtered_data
        elif type == 'Chebyshev II':
            nyquist_rate = sampling_rate / 2.0
            cutoff = cutoff_frequency / nyquist_rate
            sos = cheby2(N=8, rs=40, Wn=cutoff, btype='low', analog=False, output='sos')
            zi = sosfilt_zi(sos) * data[0]
            filtered_data, _ = sosfilt(sos, data, zi=zi)
            return filtered_data
        elif type == 'Elliptic':
            nyquist_rate = sampling_rate / 2.0
            cutoff = cutoff_frequency / nyquist_rate
            sos = ellip(N=8, rp=0.1, rs=40, Wn=cutoff, btype='low', analog=False, output='sos')
            zi = sosfilt_zi(sos) * data[0]
            filtered_data, _ = sosfilt(sos, data, zi=zi)
            return filtered_data
        elif type == 'FIR':
            nyquist_rate = sampling_rate / 2.0
            cutoff = cutoff_frequency / nyquist_rate
            taps = firwin(101, cutoff)
            filtered_data = lfilter(taps, 1, data)
            return filtered_data
        elif type == 'IIR':
            nyquist_rate = sampling_rate / 2.0
            cutoff = cutoff_frequency / nyquist_rate
            b, a = butter(N=8, Wn=cutoff, btype='low', analog=False)
            filtered_data = lfilter(b, a, data)
            return filtered_data
        elif type == 'Wavelet':
            wavelet_type = 'db4'
            wavelet_level = None
            wavelet_threshold_sub_type = 'sqtwolog'
            wavelet_threshold_type = 'soft'
            w = pywt.Wavelet(wavelet_type)
            max_level = pywt.dwt_max_level(len(data), filter_len=w.dec_len)
            if wavelet_level is None:
                wavelet_level = max_level
            wcoeff = pywt.wavedec(data, w, mode='sym', level=wavelet_level)
            thresh = np.std(wcoeff[-1]) * _thselect(wcoeff, wavelet_threshold_sub_type)
            wcoeff[1:] = [pywt.threshold(wc, thresh, wavelet_threshold_type) for wc in wcoeff[1:]]
            filtered_data = pywt.waverec(wcoeff, wavelet_type, mode='sym')
            return filtered_data
        elif type == 'Kalman':
            '''
            The user isn't given an option for this yet!

            process_noise:
            The process noise represents the uncertainty or variability in the system model.
            It quantifies how much the true state of the system can deviate from the predicted state based on the system model.
            In the Kalman filter, the process noise is modeled as a Gaussian distribution with zero mean and a specified covariance matrix.
            A higher process noise indicates that the system model is less accurate and allows for more significant deviations from the predicted state.
            The process noise covariance matrix is typically denoted as Q in the Kalman filter equations.

            measurement_noise:
            The measurement noise represents the uncertainty or variability in the measurements or observations of the system.
            It quantifies the expected error or noise present in the measured values.
            Like the process noise, the measurement noise is also modeled as a Gaussian distribution with zero mean and a specified covariance matrix.
            A higher measurement noise indicates that the measurements are less reliable and have more significant errors.
            The measurement noise covariance matrix is typically denoted as R in the Kalman filter equations.

            initial_state:
            The initial state represents the initial estimate of the system's state at the beginning of the Kalman filter algorithm.
            It is a vector that contains the initial values for each state variable in the system model.
            The initial state is used as the starting point for the Kalman filter's recursive estimation process.
            In the provided code, the initial state is set to a vector of zeros, assuming no prior knowledge about the system's initial state.
            
            initial_covariance:
            The initial covariance represents the uncertainty or confidence in the initial state estimate.
            It is a matrix that quantifies the initial variances and covariances of the state variables.
            A higher initial covariance indicates more uncertainty in the initial state estimate, while a lower initial covariance suggests more confidence in the initial estimate.
            The initial covariance matrix is typically denoted as P in the Kalman filter equations.
            In the provided code, the initial covariance is set to an identity matrix multiplied by a small value (1e-3), assuming a relatively low initial uncertainty.
            '''
            process_noise = 1e-4
            measurement_noise = 1e-2
            initial_state = np.zeros(2)
            initial_covariance = np.eye(2) * 1e-3
            
            num_samples = len(data)
            state_size = len(initial_state)

            state = np.zeros((state_size, num_samples))
            state[:, 0] = initial_state
            covariance = initial_covariance

            transition_matrix = np.eye(state_size)
            observation_matrix = np.ones((1, state_size))
            process_noise_covariance = np.eye(state_size) * process_noise
            measurement_noise_covariance = np.ones((1, 1)) * measurement_noise

            for t in range(1, num_samples):
                predicted_state = transition_matrix @ state[:, t-1]
                predicted_covariance = transition_matrix @ covariance @ transition_matrix.T + process_noise_covariance

                innovation = data[t] - observation_matrix @ predicted_state
                innovation_covariance = observation_matrix @ predicted_covariance @ observation_matrix.T + measurement_noise_covariance
                kalman_gain = predicted_covariance @ observation_matrix.T @ np.linalg.inv(innovation_covariance)

                state[:, t] = predicted_state + kalman_gain @ innovation
                covariance = (np.eye(state_size) - kalman_gain @ observation_matrix) @ predicted_covariance

            filtered_data = state[0, :]
            return filtered_data
        
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.setText("An error has occurred.")
        msg.setInformativeText(f"The selected cutoff frequency is more than sampling rate/2.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        return data


# def calculate_whole_std(data, mean_window_size_in_ms, sampling_rate):
#     mean_window_size_samples = int((mean_window_size_in_ms / 1000) * sampling_rate)
#     data_mean = np.mean(data)
    
#     selected_windows = []
#     for i in range(0, len(data), mean_window_size_samples):
#         window = data[i:i+mean_window_size_samples]
#         if np.mean(window) >= 0.9 * data_mean and np.mean(window) <= 1.1 * data_mean:
#             selected_windows.append(window)
    
#     selected_data = np.concatenate(selected_windows)
#     whole_std = np.std(selected_data)
    
#     return whole_std

def calculate_whole_std(data, mean_window_size_in_ms, sampling_rate):
    mean_window_size_samples = int((mean_window_size_in_ms / 1000) * sampling_rate)
    data_mean = np.mean(data)
    
    selected_windows = []
    for i in range(0, len(data), mean_window_size_samples):
        window = data[i:i+mean_window_size_samples]
        if np.mean(window) >= 0.9 * data_mean and np.mean(window) <= 1.1 * data_mean:
            selected_windows.append(window)
    
    try:
        selected_data = np.concatenate(selected_windows)
        whole_std = np.std(selected_data)
    except ValueError as e:
        #print(f"Error: {str(e)}. No windows selected for whole STD calculation.")
        whole_std = 6.0  # or any other default value or handling mechanism
    
    return whole_std



def calculate_rolling_stats(data, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate, std_calculation_method):
    avg_window_size_samples = int((avg_window_size_in_ms / 1000) * sampling_rate)
    std_window_size_samples = int((std_window_size_in_ms / 1000) * sampling_rate)
    
    rolling_avg = uniform_filter1d(data, size=avg_window_size_samples)
    
    if std_calculation_method == "Rolling STD":
        rolling_std = np.sqrt(uniform_filter1d(data**2, size=std_window_size_samples) - uniform_filter1d(data, size=std_window_size_samples)**2)
    else:  # Whole STD
        whole_std = calculate_whole_std(data, std_window_size_in_ms, sampling_rate)
        rolling_std = np.full_like(rolling_avg, whole_std)
    
    return rolling_avg, rolling_std

# def calculate_rolling_stats(data, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate):
#     avg_window_size_samples = int((avg_window_size_in_ms / 1000) * sampling_rate)
#     std_window_size_samples = int((std_window_size_in_ms / 1000) * sampling_rate)
    
#     rolling_avg = uniform_filter1d(data, size=avg_window_size_samples)
#     rolling_std = np.sqrt(uniform_filter1d(data**2, size=std_window_size_samples) - uniform_filter1d(data, size=std_window_size_samples)**2)
    
#     return rolling_avg, rolling_std


def find_preliminary_events(data, threshold_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, dips,smoothing, smoothing_index, sampling_rate,std_calculation_method):
    rolling_avg, rolling_std = calculate_rolling_stats(data, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate, std_calculation_method)
    
    if threshold_method == "multiplier":
        if dips == "Yes":
            threshold = rolling_avg - (threshold_multiplier * rolling_std)
        else:
            threshold = rolling_avg + (threshold_multiplier * rolling_std)
    elif threshold_method == "difference":
        if dips == "Yes":
            threshold = rolling_avg - (threshold_difference / 1000)
        else:
            threshold = rolling_avg + (threshold_difference / 1000)
    else:
        raise ValueError("Unsupported threshold_method. Use 'multiplier' or 'difference'.")
    if smoothing == "Yes":
        threshold = smooth_threshold(threshold,int((std_window_size_in_ms / 1000) * sampling_rate),smoothing_index)
    
    events = []
    in_event = False
    for i in range(1, len(data)):
        if not in_event and data[i] < threshold[i] and data[i-1] >= threshold[i-1]:
            in_event = True
            event_start = i
        elif in_event and data[i] >= threshold[i] and data[i-1] < threshold[i-1]:
            event_end = i  # Mark the event end at the first crossing
            events.append((event_start, event_end))
            in_event = False
    return events


def exclude_events_and_recalculate_stats(data, events, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate, std_calculation_method):
    data_without_events = np.copy(data)
    for start, end in events:
        data_without_events[start:end] = np.nan  # Exclude event data by setting it to NaN

    # Replace NaNs with the mean of their neighboring values for a smooth transition
    nan_indices = np.where(np.isnan(data_without_events))[0]
    for idx in nan_indices:
        if idx > 0 and idx < len(data_without_events) - 1:
            data_without_events[idx] = np.nanmean(data_without_events[idx - 1:idx + 2])

    rolling_avg, rolling_std = calculate_rolling_stats(data, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate, std_calculation_method)
    return rolling_avg, rolling_std


def find_events_refined(data, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, min_event_width, max_event_width, dips, smoothing, smoothing_index, sampling_rate, std_calculation_method):
    # Step 1: Find preliminary events
    preliminary_events = find_preliminary_events(data, threshold_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, dips, smoothing, smoothing_index, sampling_rate, std_calculation_method)

    # Step 2: Recalculate statistics excluding preliminary events
    rolling_avg_refined, rolling_std_refined = exclude_events_and_recalculate_stats(data, preliminary_events, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate, std_calculation_method)

    # Step 3: Use the refined statistics to find events again
    adjusted_baseline_start = rolling_avg_refined - start_multiplier * rolling_std_refined
    adjusted_baseline_end = rolling_avg_refined - end_multiplier * rolling_std_refined

    if threshold_method == "multiplier":
        if dips == "Yes":
            threshold_refined = rolling_avg_refined - (threshold_multiplier * rolling_std_refined)
        else:
            threshold_refined = rolling_avg_refined + (threshold_multiplier * rolling_std_refined)
    elif threshold_method == "difference":
        if dips == "Yes":
            threshold_refined = rolling_avg_refined - (threshold_difference / 1000)   
        else:
            threshold_refined = rolling_avg_refined + (threshold_difference / 1000)   
    if smoothing ==  "Yes":
        threshold_refined = smooth_threshold(threshold_refined,int((std_window_size_in_ms / 1000) * sampling_rate),smoothing_index)

    all_refined_events = []
    in_event = False
    for i in range(1, len(data)):
        if not in_event and data[i] < threshold_refined[i] and data[i-1] >= threshold_refined[i-1]:
            in_event = True
            event_start = i
            # Backtrack to refine event start
            while event_start > 0 and not (data[event_start] < adjusted_baseline_start[event_start] and data[event_start-1] >= adjusted_baseline_start[event_start-1]):
                event_start -= 1
        elif in_event and data[i] >= adjusted_baseline_end[i] and data[i-1] < adjusted_baseline_end[i-1]:
            event_end = i  # Mark the event end at the first crossing
            all_refined_events.append((event_start, event_end))
            in_event = False


    # Step 4: Filter events based on their width (duration)
    filtered_events = []
    for start, end in all_refined_events:
        event_width_in_seconds = (end - start) / sampling_rate
        if min_event_width <= event_width_in_seconds <= max_event_width:
            filtered_events.append((start, end))

    return filtered_events



def find_events_refined_parallel(data, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, min_event_width, max_event_width, chunk_size,  dips, sampling_rate, smoothing, smoothing_index, std_calculation_method, n_jobs):
    # Calculate the number of chunks
    n_chunks = int(np.ceil(len(data) / chunk_size))

    # Define a helper function to process each chunk
    def process_chunk(start_index, end_index):
        chunk_data = data[start_index:end_index]
        return find_events_refined(chunk_data, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, threshold_method, min_event_width, max_event_width, dips, smoothing, smoothing_index, sampling_rate, std_calculation_method)
    
    # Parallel execution
    results = Parallel(n_jobs=n_jobs)(
        delayed(process_chunk)(i * chunk_size, min((i + 1) * chunk_size, len(data)))
        for i in range(n_chunks)
    )
    
    # Combine results from all chunks
    combined_results = [event for chunk in results for event in chunk]

    # Adjust event indices based on their chunk offsets and filter out those crossing chunk boundaries
    adjusted_results = []
    for chunk_index, chunk in enumerate(results):
        chunk_start_index = chunk_index * chunk_size
        for start, end in chunk:
            if start + chunk_start_index < (chunk_index + 1) * chunk_size and end + chunk_start_index <= min((chunk_index + 1) * chunk_size, len(data)):
                adjusted_results.append((start + chunk_start_index, end + chunk_start_index))
    
    rolling_avg_refined, rolling_std_refined = calculate_rolling_stats(data, avg_window_size_in_ms, std_window_size_in_ms, sampling_rate, std_calculation_method)
    
    if threshold_method == "multiplier":
        if dips == "Yes":
            threshold_refined = rolling_avg_refined - (threshold_multiplier * rolling_std_refined)
        else:
            threshold_refined = rolling_avg_refined + (threshold_multiplier * rolling_std_refined)
    elif threshold_method == "difference":
        if dips == "Yes":
            threshold_refined = rolling_avg_refined - (threshold_difference / 1000)   
        else:
            threshold_refined = rolling_avg_refined + (threshold_difference / 1000)  
    if smoothing == "Yes":
        threshold_refined = smooth_threshold(threshold_refined,int((std_window_size_in_ms / 1000) * sampling_rate),smoothing_index)      

    return adjusted_results, rolling_avg_refined, threshold_refined



def calculate_delta_I1(l, sigma, V, i0, i01, delta_I):
    d = (i0 + np.sqrt(i0 * (i0 + (16 * l * V * sigma) / math.pi))) / (2 * V * sigma)
    d1 = (i01 + np.sqrt(i01 * (i01 + (16 * l * V * sigma) / math.pi))) / (2 * V * sigma)
    delta_G = delta_I / V
    
    term1 = (d1**2 * math.pi * sigma) / (4 * l + d1 * math.pi)
    
    sqrt_term = (4 * l * delta_G + d * math.pi * (delta_G - d * sigma))**3 * (-64 * l**2 * sigma + 4 * l * math.pi * (delta_G - 4 * d * sigma) + d * math.pi**2 * (delta_G - d * sigma))
    sqrt_term = np.where(sqrt_term >= 0, sqrt_term, np.nan)
    
    term2_numerator = (
        -d**2 * math.pi**3 * delta_G**2 +
        128 * l**3 * delta_G * sigma +
        2 * d**3 * math.pi**3 * delta_G * sigma +
        d**4 * math.pi**3 * sigma**2 -
        2 * d**2 * d1**2 * math.pi**3 * sigma**2 -
        16 * l**2 * math.pi * (delta_G**2 - 4 * d * delta_G * sigma + 2 * d1**2 * sigma**2) +
        8 * d * l * math.pi**2 * (-delta_G**2 + 2 * d * delta_G * sigma + (d**2 - 2 * d1**2) * sigma**2) -
        np.sqrt(math.pi) * np.sqrt(sqrt_term)
    )
    
    term2_denominator = (
        (4 * l + d * math.pi)**2 * sigma * (
            8 * l + np.sqrt(2 * math.pi) * np.sqrt(
                1 / ((4 * l + d * math.pi)**2 * sigma**2) * (
                    d**2 * math.pi**3 * delta_G**2 -
                    128 * l**3 * delta_G * sigma -
                    2 * d**3 * math.pi**3 * delta_G * sigma -
                    d**4 * math.pi**3 * sigma**2 +
                    2 * d**2 * d1**2 * math.pi**3 * sigma**2 +
                    16 * l**2 * math.pi * (delta_G**2 - 4 * d * delta_G * sigma + 2 * d1**2 * sigma**2) -
                    8 * d * l * math.pi**2 * (-delta_G**2 + 2 * d * delta_G * sigma + (d**2 - 2 * d1**2) * sigma**2) +
                    np.sqrt(math.pi) * np.sqrt(sqrt_term)
                )
            )
        )
    )
    
    term2 = term2_numerator / term2_denominator
    
    delta_I1 = V * (term1 + term2)
    
    return np.where(np.isnan(delta_I1), np.nan, delta_I1)



def normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean):
    normalized_signal = calculate_delta_I1(
        standard_length_nm * 10**(-9),
        standard_conductivity_S_m,
        standard_voltage_applied_mV / 1000,
        standard_open_pore_current_nA* 10**(-9),
        event_baseline_mean* 10**(-9),
        signal* 10**(-9)
    )
    return normalized_signal/10**(-9)


def analyze_event_for_CUSUM(event_signal, baseline, ML_standardisation_settings, event_time):
    standard, ML_enabled, ML_standard,  standard_power, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, sampling_rate =  ML_standardisation_settings['standard'],  ML_standardisation_settings['ML_enabled'],  ML_standardisation_settings['ML_standard'],  ML_standardisation_settings['standard_power'], ML_standardisation_settings['standard_length_nm'], ML_standardisation_settings['standard_conductivity_S_m'], ML_standardisation_settings['standard_voltage_applied_mV'], ML_standardisation_settings['standard_open_pore_current_nA'], ML_standardisation_settings['sampling_rate']

    if ML_enabled == "False":
        signal = np.abs(event_signal-baseline)    # Flip the event signal if necessary
        event_baseline_mean = np.mean(baseline)
        if standard == "Normal":
            signal = signal
        elif standard == "ΔI/I₀":
            signal = signal/event_baseline_mean
        elif standard == "(ΔI*I₀)⁰·⁵":
            signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
        elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
            signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
        elif standard == "Dutt Standardisation":
            signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
        else:
            signal = signal 

        sample_period = 1 / sampling_rate
        width = len(signal) * sample_period
        area = np.sum(signal) * sample_period
        peaks, _ = sig.find_peaks(signal)
        if len(peaks) == 0:
            return [np.nan, np.nan, np.nan, area, width, np.nan, np.nan, np.nan, np.nan]
        highest_peak = max(peaks, key=lambda peak: signal[peak])
        height = signal[highest_peak]
        fwhm_, heightatfwhm_, _, _ = sig.peak_widths(signal, [highest_peak], rel_height=0.5)
        fwhm = fwhm_[0] * sample_period
        heightatfwhm = heightatfwhm_[0]
        skew = stats.skew(signal)
        kurt = stats.kurtosis(signal)
        return [height, fwhm, heightatfwhm, area, width, skew, kurt, event_baseline_mean, event_time]
        
    else:
        if ML_standard == "Scheme 1":
            signal = np.abs(event_signal-baseline)    # Flip the event signal if necessary
            event_baseline_mean = np.mean(baseline)
            if standard == "Normal":
                signal = signal
            elif standard == "ΔI/I₀":
                signal = signal/event_baseline_mean
            elif standard == "(ΔI*I₀)⁰·⁵":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
            elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
            elif standard == "Dutt Standardisation":
                signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
            else:
                signal = signal 
            
            sample_period = 1 / sampling_rate
            width = len(signal) * sample_period
            n = 10  # Number of parts to divide the signal into
            if n>len(signal):
                n = len(signal)
            # Calculate the number of samples in each part
            samples_per_part = len(signal) // n

            # Calculate the width of each part
            part_width = width / n

            # Initialize an array to store the average values of each part
            part_averages = np.zeros(n)

            # Iterate over each part
            for i in range(n):
                start_index = i * samples_per_part
                end_index = (i + 1) * samples_per_part
                
                # Extract the samples for the current part
                part_samples = signal[start_index:end_index]
                
                # Calculate the average value of the current part
                part_averages[i] = np.mean(part_samples)

            # Create the result array in the desired form
            return np.append(part_averages, part_width)
        
        elif ML_standard == "Scheme 2":
            signal = np.abs(event_signal-baseline)   # Flip the event signal if necessary
            event_baseline_mean = np.mean(baseline)
            if standard == "Normal":
                signal = signal
            elif standard == "ΔI/I₀":
                signal = signal/event_baseline_mean
            elif standard == "(ΔI*I₀)⁰·⁵":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
            elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
            elif standard == "Dutt Standardisation":
                signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
            else:
                signal = signal 
            
            sample_period = 1 / sampling_rate
            width = len(signal) * sample_period
            n = 10  # Number of parts to divide the signal into
            if n>len(signal):
                n = len(signal)
            # Calculate the number of samples in each part
            samples_per_part = len(signal) // n

            # Calculate the width of each part
            part_width = width / n

            # Initialize an array to store the average values of each part
            part_averages = np.zeros(n)

            # Iterate over each part
            for i in range(n):
                start_index = i * samples_per_part
                end_index = (i + 1) * samples_per_part
                
                # Extract the samples for the current part
                part_samples = signal[start_index:end_index]
                
                # Calculate the average value of the current part
                part_averages[i] = np.mean(part_samples)

            area = np.sum(signal) * sample_period
            peaks, _ = sig.find_peaks(signal)
            if len(peaks) == 0:
                return np.append(part_averages, [np.nan, np.nan, np.nan, np.nan, area, width])
            highest_peak = max(peaks, key=lambda peak: signal[peak])
            height = signal[highest_peak]
            fwhm_, heightatfwhm_, _, _ = sig.peak_widths(signal, [highest_peak], rel_height=0.5)
            fwhm = fwhm_[0] * sample_period
            heightatfwhm = heightatfwhm_[0]
            return np.append(part_averages, [part_width, height, fwhm, heightatfwhm, area, width])
        
        elif ML_standard == "Scheme 3":
            signal = np.abs(event_signal-baseline)   # Flip the event signal if necessary
            event_baseline_mean = np.mean(baseline)
            if standard == "Normal":
                signal = signal
            elif standard == "ΔI/I₀":
                signal = signal/event_baseline_mean
            elif standard == "(ΔI*I₀)⁰·⁵":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
            elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
            elif standard == "Dutt Standardisation":
                signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
            else:
                signal = signal 
            
            sample_period = 1 / sampling_rate
            width = len(signal) * sample_period
            n = 10  # Number of parts to divide the signal into
            if n>len(signal):
                n = len(signal)
            # Calculate the number of samples in each part
            samples_per_part = len(signal) // n

            # Calculate the width of each part
            part_width = width / n

            # Initialize an array to store the average values of each part
            part_averages = np.zeros(n)

            # Iterate over each part
            for i in range(n):
                start_index = i * samples_per_part
                end_index = (i + 1) * samples_per_part
                
                # Extract the samples for the current part
                part_samples = signal[start_index:end_index]
                
                # Calculate the average value of the current part
                part_averages[i] = np.mean(part_samples)

            area = np.sum(signal) * sample_period
            peaks, _ = sig.find_peaks(signal)
            if len(peaks) == 0:
                return np.append(part_averages, [np.nan, np.nan, np.nan, np.nan, area, width, np.nan, np.nan])
            highest_peak = max(peaks, key=lambda peak: signal[peak])
            height = signal[highest_peak]
            fwhm_, heightatfwhm_, _, _ = sig.peak_widths(signal, [highest_peak], rel_height=0.5)
            fwhm = fwhm_[0] * sample_period
            heightatfwhm = heightatfwhm_[0]
            skew = stats.skew(signal)
            kurt = stats.kurtosis(signal)
            return np.append(part_averages, [part_width, height, fwhm, heightatfwhm, area, width, skew, kurt])
        
        elif ML_standard == "Scheme 4":
            signal = np.abs(event_signal-baseline)   # Flip the event signal if necessary
            event_baseline_mean = np.mean(baseline)
            if standard == "Normal":
                signal = signal
            elif standard == "ΔI/I₀":
                signal = signal/event_baseline_mean
            elif standard == "(ΔI*I₀)⁰·⁵":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
            elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
            elif standard == "Dutt Standardisation":
                signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
            else:
                signal = signal 
            
            sample_period = 1 / sampling_rate
            width = len(signal) * sample_period
            n = 50  # Number of parts to divide the signal into
            if n>len(signal):
                n = len(signal)
            # Calculate the number of samples in each part
            samples_per_part = len(signal) // n

            # Calculate the width of each part
            part_width = width / n

            # Initialize an array to store the average values of each part
            part_averages = np.zeros(n)

            # Iterate over each part
            for i in range(n):
                start_index = i * samples_per_part
                end_index = (i + 1) * samples_per_part
                
                # Extract the samples for the current part
                part_samples = signal[start_index:end_index]
                
                # Calculate the average value of the current part
                part_averages[i] = np.mean(part_samples)

            area = np.sum(signal) * sample_period
            peaks, _ = sig.find_peaks(signal)
            if len(peaks) == 0:
                return np.append(part_averages, [np.nan, np.nan, np.nan, np.nan, area, width, np.nan, np.nan])
            highest_peak = max(peaks, key=lambda peak: signal[peak])
            height = signal[highest_peak]
            fwhm_, heightatfwhm_, _, _ = sig.peak_widths(signal, [highest_peak], rel_height=0.5)
            fwhm = fwhm_[0] * sample_period
            heightatfwhm = heightatfwhm_[0]
            skew = stats.skew(signal)
            kurt = stats.kurtosis(signal)
            return np.append(part_averages, [part_width, height, fwhm, heightatfwhm, area, width, skew, kurt])
        
        elif ML_standard == "Scheme 5":
            signal = np.abs(event_signal-baseline)    # Flip the event signal if necessary
            event_baseline_mean = np.mean(baseline)
            if standard == "Normal":
                signal = signal
            elif standard == "ΔI/I₀":
                signal = signal/event_baseline_mean
            elif standard == "(ΔI*I₀)⁰·⁵":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
            elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
            elif standard == "Dutt Standardisation":
                signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
            else:
                signal = signal 
            
            sample_period = 1 / sampling_rate
        width = len(signal) * sample_period
        area = np.sum(signal) * sample_period
        peaks, _ = sig.find_peaks(signal)
        if len(peaks) == 0:
            return np.append(signal,[np.nan, np.nan, np.nan, area, width, np.nan, np.nan])
        highest_peak = max(peaks, key=lambda peak: signal[peak])
        height = signal[highest_peak]
        fwhm_, heightatfwhm_, _, _ = sig.peak_widths(signal, [highest_peak], rel_height=0.5)
        fwhm = fwhm_[0] * sample_period
        heightatfwhm = heightatfwhm_[0]
        skew = stats.skew(signal)
        kurt = stats.kurtosis(signal)
        return np.append(signal, [height, fwhm, heightatfwhm, area, width, skew, kurt])
  

def analyze_event(event_signal, data, rolling_avg_refined, sampling_rate, ML_standardisation_settings):
    standard, ML_enabled, ML_standard,  standard_power, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA =  ML_standardisation_settings['standard'],  ML_standardisation_settings['ML_enabled'],  ML_standardisation_settings['ML_standard'],  ML_standardisation_settings['standard_power'], ML_standardisation_settings['standard_length_nm'], ML_standardisation_settings['standard_conductivity_S_m'], ML_standardisation_settings['standard_voltage_applied_mV'], ML_standardisation_settings['standard_open_pore_current_nA']

    if ML_enabled == "False":
        event_data = data[event_signal[0]:event_signal[1]]
        event_baseline = rolling_avg_refined[event_signal[0]:event_signal[1]]
        event_baseline_mean = np.mean(event_baseline)
        #print(event_baseline_mean)
        signal = np.abs(event_data - event_baseline)  # Flip the event signal if necessary
        if standard == "Normal":
            signal = signal
        elif standard == "ΔI/I₀":
            signal = signal/event_baseline_mean
        elif standard == "(ΔI*I₀)⁰·⁵":
            signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
        elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
            signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
        elif standard == "Dutt Standardisation":
            signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
        else:
            signal = signal 

        sample_period = 1 / sampling_rate
        width = len(signal) * sample_period
        area = np.sum(signal) * sample_period
        peaks, _ = sig.find_peaks(signal)
        if len(peaks) == 0:
            return [np.nan, np.nan, np.nan, area, width, np.nan, np.nan, np.nan, np.nan]
        highest_peak = max(peaks, key=lambda peak: signal[peak])
        height = signal[highest_peak]
        fwhm_, heightatfwhm_, _, _ = sig.peak_widths(signal, [highest_peak], rel_height=0.5)
        fwhm = fwhm_[0] * sample_period
        heightatfwhm = heightatfwhm_[0]
        skew = stats.skew(signal)
        kurt = stats.kurtosis(signal)
        # Calculate the actual time of the event occurrence
        event_time = event_signal[0] / sampling_rate
        #if standard == "Dutt Standardisation":
        #    height = normalize_signal(height, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
        #    heightatfwhm = normalize_signal(heightatfwhm, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
        return [height, fwhm, heightatfwhm, area, width, skew, kurt, event_baseline_mean, event_time]
        
    else:
        if ML_standard == "Scheme 1":
            event_data = data[event_signal[0]:event_signal[1]]
            event_baseline = rolling_avg_refined[event_signal[0]:event_signal[1]]
            event_baseline_mean = np.mean(event_baseline)
            signal = np.abs(event_data - event_baseline)  # Flip the event signal if necessary
            if standard == "Normal":
                signal = signal
            elif standard == "ΔI/I₀":
                signal = signal/event_baseline_mean
            elif standard == "(ΔI*I₀)⁰·⁵":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
            elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
            elif standard == "Dutt Standardisation":
                signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
            else:
                signal = signal 
            
            sample_period = 1 / sampling_rate
            width = len(signal) * sample_period
            n = 10  # Number of parts to divide the signal into
            part_averages = np.full(n, np.nan)  

            # Calculate the number of samples in each part
            samples_per_part = len(signal) // n if n > 0 else 0

            # Calculate the number of parts that can be used based on the signal length
            num_parts = min(n, len(signal) // samples_per_part) if samples_per_part > 0 else 0

            # Calculate the width of each part based on the actual number of parts used
            part_width = width / num_parts if num_parts > 0 else width

            # Iterate over each part
            for i in range(num_parts):
                start_index = i * samples_per_part
                end_index = (i + 1) * samples_per_part
                # Extract the samples for the current part
                part_samples = signal[start_index:end_index]
                # Calculate the average value of the current part
                part_averages[i] = np.mean(part_samples)

            # Create the result array in the desired form
            return np.append(part_averages, part_width)
        
        elif ML_standard == "Scheme 2":
            event_data = data[event_signal[0]:event_signal[1]]
            event_baseline = rolling_avg_refined[event_signal[0]:event_signal[1]]
            event_baseline_mean = np.mean(event_baseline)
            signal = np.abs(event_data - event_baseline)  # Flip the event signal if necessary
            if standard == "Normal":
                signal = signal
            elif standard == "ΔI/I₀":
                signal = signal/event_baseline_mean
            elif standard == "(ΔI*I₀)⁰·⁵":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
            elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
            elif standard == "Dutt Standardisation":
                signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
            else:
                signal = signal 
            
            sample_period = 1 / sampling_rate
            width = len(signal) * sample_period
            n = 10  # Number of parts to divide the signal into
            part_averages = np.full(n, np.nan)  

            # Calculate the number of samples in each part
            samples_per_part = len(signal) // n if n > 0 else 0

            # Calculate the number of parts that can be used based on the signal length
            num_parts = min(n, len(signal) // samples_per_part) if samples_per_part > 0 else 0

            # Calculate the width of each part based on the actual number of parts used
            part_width = width / num_parts if num_parts > 0 else width

            # Iterate over each part
            for i in range(num_parts):
                start_index = i * samples_per_part
                end_index = (i + 1) * samples_per_part
                # Extract the samples for the current part
                part_samples = signal[start_index:end_index]
                # Calculate the average value of the current part
                part_averages[i] = np.mean(part_samples)

            area = np.sum(signal) * sample_period
            peaks, _ = sig.find_peaks(signal)
            if len(peaks) == 0:
                return np.full(16, np.nan)
            highest_peak = max(peaks, key=lambda peak: signal[peak])
            height = signal[highest_peak]
            fwhm_, heightatfwhm_, _, _ = sig.peak_widths(signal, [highest_peak], rel_height=0.5)
            fwhm = fwhm_[0] * sample_period
            heightatfwhm = heightatfwhm_[0]
            return np.append(part_averages, [part_width, height, fwhm, heightatfwhm, area, width])
        
        elif ML_standard == "Scheme 3":
            event_data = data[event_signal[0]:event_signal[1]]
            event_baseline = rolling_avg_refined[event_signal[0]:event_signal[1]]
            event_baseline_mean = np.mean(event_baseline)
            signal = np.abs(event_data - event_baseline)  # Flip the event signal if necessary
            if standard == "Normal":
                signal = signal
            elif standard == "ΔI/I₀":
                signal = signal/event_baseline_mean
            elif standard == "(ΔI*I₀)⁰·⁵":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
            elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
            elif standard == "Dutt Standardisation":
                signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
            else:
                signal = signal 
            
            sample_period = 1 / sampling_rate
            width = len(signal) * sample_period
            n = 10  # Number of parts to divide the signal into
            part_averages = np.full(n, np.nan)  

            # Calculate the number of samples in each part
            samples_per_part = len(signal) // n if n > 0 else 0

            # Calculate the number of parts that can be used based on the signal length
            num_parts = min(n, len(signal) // samples_per_part) if samples_per_part > 0 else 0

            # Calculate the width of each part based on the actual number of parts used
            part_width = width / num_parts if num_parts > 0 else width

            # Iterate over each part
            for i in range(num_parts):
                start_index = i * samples_per_part
                end_index = (i + 1) * samples_per_part
                # Extract the samples for the current part
                part_samples = signal[start_index:end_index]
                # Calculate the average value of the current part
                part_averages[i] = np.mean(part_samples)

            area = np.sum(signal) * sample_period
            peaks, _ = sig.find_peaks(signal)
            if len(peaks) == 0:
                return np.full(18, np.nan)
            highest_peak = max(peaks, key=lambda peak: signal[peak])
            height = signal[highest_peak]
            fwhm_, heightatfwhm_, _, _ = sig.peak_widths(signal, [highest_peak], rel_height=0.5)
            fwhm = fwhm_[0] * sample_period
            heightatfwhm = heightatfwhm_[0]
            skew = stats.skew(signal)
            kurt = stats.kurtosis(signal)
            return np.append(part_averages, [part_width, height, fwhm, heightatfwhm, area, width, skew, kurt])
        
        elif ML_standard == "Scheme 4":
            event_data = data[event_signal[0]:event_signal[1]]
            event_baseline = rolling_avg_refined[event_signal[0]:event_signal[1]]
            event_baseline_mean = np.mean(event_baseline)
            signal = np.abs(event_data - event_baseline)  # Flip the event signal if necessary
            if standard == "Normal":
                signal = signal
            elif standard == "ΔI/I₀":
                signal = signal/event_baseline_mean
            elif standard == "(ΔI*I₀)⁰·⁵":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
            elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
            elif standard == "Dutt Standardisation":
                signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
            else:
                signal = signal 
            
            sample_period = 1 / sampling_rate
            width = len(signal) * sample_period
            n = 0  # Number of parts to divide the signal into
            part_averages = np.full(n, np.nan)  

            # Calculate the number of samples in each part
            samples_per_part = len(signal) // n if n > 0 else 0

            # Calculate the number of parts that can be used based on the signal length
            num_parts = min(n, len(signal) // samples_per_part) if samples_per_part > 0 else 0

            # Calculate the width of each part based on the actual number of parts used
            part_width = width / num_parts if num_parts > 0 else width

            # Iterate over each part
            for i in range(num_parts):
                start_index = i * samples_per_part
                end_index = (i + 1) * samples_per_part
                # Extract the samples for the current part
                part_samples = signal[start_index:end_index]
                # Calculate the average value of the current part
                part_averages[i] = np.mean(part_samples)

            area = np.sum(signal) * sample_period
            peaks, _ = sig.find_peaks(signal)
            if len(peaks) == 0:
                return np.full(58, np.nan)
            highest_peak = max(peaks, key=lambda peak: signal[peak])
            height = signal[highest_peak]
            fwhm_, heightatfwhm_, _, _ = sig.peak_widths(signal, [highest_peak], rel_height=0.5)
            fwhm = fwhm_[0] * sample_period
            heightatfwhm = heightatfwhm_[0]
            skew = stats.skew(signal)
            kurt = stats.kurtosis(signal)
            return np.append(part_averages, [part_width, height, fwhm, heightatfwhm, area, width, skew, kurt])
        
        elif ML_standard == "Scheme 5":
            event_data = data[event_signal[0]:event_signal[1]]
            event_baseline = rolling_avg_refined[event_signal[0]:event_signal[1]]
            event_baseline_mean = np.mean(event_baseline)
            signal = np.abs(event_data - event_baseline)  # Flip the event signal if necessary
            if standard == "Normal":
                signal = signal
            elif standard == "ΔI/I₀":
                signal = signal/event_baseline_mean
            elif standard == "(ΔI*I₀)⁰·⁵":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**0.5
            elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
                signal = (np.abs(signal)*np.abs(event_baseline_mean))**standard_power
            elif standard == "Dutt Standardisation":
                signal = normalize_signal(signal, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
            else:
                signal = signal 
            
                sample_period = 1 / sampling_rate
                width = len(signal) * sample_period
                area = np.sum(signal) * sample_period
                peaks, _ = sig.find_peaks(signal)

                max_points = int(sampling_rate / 1000) + 8
                result = np.full(max_points, np.nan)

                if len(peaks) == 0:
                    result[-8:] = [np.nan, np.nan, np.nan, area, width, np.nan, np.nan, event_baseline_mean]
                    return result

                highest_peak = max(peaks, key=lambda peak: signal[peak])
                height = signal[highest_peak]
                fwhm_, heightatfwhm_, _, _ = sig.peak_widths(signal, [highest_peak], rel_height=0.5)
                fwhm = fwhm_[0] * sample_period
                heightatfwhm = heightatfwhm_[0]
                skew = stats.skew(signal)
                kurt = stats.kurtosis(signal)

                signal_length = min(len(signal), max_points - 8)
                result[:signal_length] = signal[:signal_length]
                result[-8:] = [height, fwhm, heightatfwhm, area, width, skew, kurt, event_baseline_mean]

                return result

def analyze_events_chunk(chunk, data, rolling_avg_refined, sampling_rate, ML_standardisation_settings):
    return [analyze_event(event_signal, data, rolling_avg_refined, sampling_rate, ML_standardisation_settings) for event_signal in chunk]

def save_chunked_event_analysis_to_npz(chunk_size, data, events, rolling_avg_refined, sampling_rate, ML_standardisation_settings):
    event_chunks = np.array_split(events, max(1, len(events) // chunk_size))
    analysis_results = Parallel(n_jobs=-1)(
        delayed(analyze_events_chunk)(chunk, data, rolling_avg_refined, sampling_rate,ML_standardisation_settings) for chunk in event_chunks
    )
    # print("Analysis results shapes:")
    # for i, chunk_result in enumerate(analysis_results):
    #     print(f"Chunk {i+1}: {[arr.shape for arr in chunk_result]}")
    flattened_results = np.array([item for sublist in analysis_results for item in sublist], dtype=np.float64)
    #flattened_results = np.concatenate(analysis_results)
    return flattened_results

def autostepfinder(data, acceptance_threshold, max_iterations=100):
    plateaus = [data]
    change_points = []

    for _ in range(max_iterations):
        best_split_idx = None
        best_reduction = 0

        for i, plateau in enumerate(plateaus):
            split_idx = find_best_split(plateau)
            if split_idx is not None:
                left_plateau, right_plateau = split_plateau(plateau, split_idx)
                reduction = np.sum((plateau - np.mean(plateau)) **2) - (
                    np.sum((left_plateau - np.mean(left_plateau))** 2) +
                    np.sum((right_plateau - np.mean(right_plateau)) ** 2)
                )
                if reduction > best_reduction:
                    best_reduction = reduction
                    best_split_idx = (i, split_idx)

        if best_split_idx is None:
            break

        plateau_idx, split_idx = best_split_idx
        left_plateau, right_plateau = split_plateau(plateaus[plateau_idx], split_idx)
        plateaus[plateau_idx] = left_plateau
        plateaus.insert(plateau_idx + 1, right_plateau)

        change_points.append(sum(len(p) for p in plateaus[:plateau_idx]) + split_idx)

        counter_plateaus = counter_fit(plateaus)
        s_score = calculate_s_score(plateaus, counter_plateaus)

        if s_score < acceptance_threshold:
            break

    change_points.sort()
    return change_points

def find_best_split(plateau):
    best_split_idx = None
    best_reduction = 0

    for i in range(1, len(plateau) - 1):
        left_plateau = plateau[:i]
        right_plateau = plateau[i:]
        left_mean = np.mean(left_plateau)
        right_mean = np.mean(right_plateau)
        reduction = np.sum((left_plateau - left_mean) **2) + np.sum((right_plateau - right_mean)** 2)

        if reduction > best_reduction:
            best_reduction = reduction
            best_split_idx = i

    return best_split_idx

def split_plateau(plateau, split_idx):
    left_plateau = plateau[:split_idx]
    right_plateau = plateau[split_idx:]
    return left_plateau, right_plateau

def counter_fit(plateaus):
    counter_plateaus = []
    for plateau in plateaus:
        split_idx = find_best_split(plateau)
        if split_idx is not None:
            left_plateau, right_plateau = split_plateau(plateau, split_idx)
            counter_plateaus.append(left_plateau)
            counter_plateaus.append(right_plateau)
        else:
            counter_plateaus.append(plateau)
    return counter_plateaus

def calculate_s_score(plateaus, counter_plateaus):
    plateaus_var = sum(np.var(plateau) for plateau in plateaus)
    counter_plateaus_var = sum(np.var(plateau) for plateau in counter_plateaus)
    s_score = counter_plateaus_var / plateaus_var
    return s_score

# def analyze_event_chunk_with_padding(event_chunk, padding, library, model, num_components, penalty, data, dips, ML_standardisation_settings):
#     chunk_results = []
#     sampling_rate = ML_standardisation_settings['sampling_rate']
#     segment_rate_threshold = ML_standardisation_settings['segment_rate_threshold']
#     first_last_segment_threshold = 0.5
#     change_of_rate_threshold = ML_standardisation_settings['change_of_rate_threshold']
#     merge_close_segments_threshold = ML_standardisation_settings['merge_close_segments_threshold']
    

#     def detect_change_points(event_data, threshold):
#         if library == "ruptures":
#             algo = rpt.Pelt(model=model).fit(event_data)
#             change_points = algo.predict(pen=penalty * threshold)
#         elif library == "detecta":
#             if model == "cusum":
#                 _, change_points, _, _ = detect_cusum(event_data, threshold=penalty * threshold, drift=0, ending=False, show=False)
#         elif library == "lmfit":
#             change_points = autostepfinder(event_data, penalty * threshold)
#         elif library == "hmm":
#             hmm_model = hmm.GaussianHMM(n_components=num_components).fit(event_data.reshape(-1, 1))
#             _, change_points = hmm_model.decode(event_data.reshape(-1, 1))
#         elif library == "gmm":
#             gmm_model = GaussianMixture(n_components=num_components).fit(event_data.reshape(-1, 1))
#             change_points = np.where(np.diff(gmm_model.predict(event_data.reshape(-1, 1))))[0]
#         else:
#             raise ValueError(f"Unsupported library: {library}")
#         return change_points

#     def calculate_adaptive_threshold(rate_of_change, is_first_segment, is_last_segment):
#         if (is_first_segment and rate_of_change < 0) or (is_last_segment and rate_of_change > 0):
#             return segment_rate_threshold
#         else:
#             return segment_rate_threshold / 2

#     def should_merge_segments(segment_data, next_segment_data, rate_of_change, next_rate_of_change, adaptive_threshold):
#         if np.sign(rate_of_change) != np.sign(next_rate_of_change):
#             return False

#         if np.abs(rate_of_change - next_rate_of_change) >= adaptive_threshold:
#             return False

#         segment_value = np.median(segment_data)
#         next_segment_value = np.median(next_segment_data)

#         if np.abs(segment_value - next_segment_value) > adaptive_threshold:
#             return False

#         return True

#     def calculate_rate_of_change(segment_start, segment_end, event_data):
#         segment_data = event_data[segment_start:segment_end]
#         if len(segment_data) < 2:
#             return 0
#         return (segment_data[-1] - segment_data[0]) / (segment_end - segment_start)

#     def calculate_segment_value(segment_data, middle_segment_data, rate_of_change, is_first_segment, is_last_segment):
#         if len(middle_segment_data) == 0 or np.all(middle_segment_data == 0):
#             return np.median(segment_data)

#         if is_last_segment:
#             return np.min(segment_data)
#         elif (is_first_segment or is_last_segment) and np.abs(rate_of_change) > first_last_segment_threshold / 3:
#             return np.min(segment_data)
#         elif np.abs(rate_of_change) > first_last_segment_threshold * 2:
#             return np.min(segment_data)
#         else:
#             return np.median(middle_segment_data)

#     def post_process_segments(event_data, cusum_segments, mean_values):
#         post_processed_segments = []
#         post_processed_mean_values = []

#         def merge_segments(segments, values, event_data):
#             merged_segments = []
#             merged_values = []

#             # Merge continuously decreasing segments at the start
#             i = 0
#             while i < len(segments) - 1:
#                 current_segment_start, current_segment_end = segments[i][0] - start, segments[i][1] - start
#                 current_value = values[i]
#                 segment_length = current_segment_end - current_segment_start

#                 # Merge small segments until we have a segment with at least 3 events
#                 while i + 1 < len(segments) and segment_length < 3:
#                     i += 1
#                     current_segment_end = segments[i][1] - start
#                     current_value = min(current_value, values[i])
#                     segment_length = current_segment_end - current_segment_start

#                 current_rate_of_change = calculate_rate_of_change(current_segment_start, current_segment_end, event_data)

#                 if np.abs(current_rate_of_change) > change_of_rate_threshold and current_rate_of_change < 0:  # Increased threshold for decreasing segments
#                     merged_segment_start = current_segment_start
#                     merged_value = current_value
#                     i += 1

#                     while i < len(segments) - 1:
#                         next_segment_start, next_segment_end = segments[i][0] - start, segments[i][1] - start
#                         next_segment_length = next_segment_end - next_segment_start

#                         # Merge small segments until we have a segment with at least 3 events
#                         while i + 1 < len(segments) and next_segment_length < 3:
#                             i += 1
#                             next_segment_end = segments[i][1] - start
#                             next_segment_length = next_segment_end - next_segment_start

#                         next_rate_of_change = calculate_rate_of_change(next_segment_start, next_segment_end, event_data)

#                         if next_rate_of_change < 0:
#                             merged_value = min(merged_value, values[i])
#                             i += 1
#                         else:
#                             break  # Stop merging if the rate of change sign changes

#                     merged_segment_end = segments[i - 1][1] - start
#                     merged_segments.append((merged_segment_start + start, merged_segment_end + start))
#                     merged_values.append(merged_value)
#                 else:
#                     merged_segments.append((current_segment_start + start, current_segment_end + start))
#                     merged_values.append(current_value)
#                     i += 1

#             # Add the last segment if it was not merged
#             if i == len(segments) - 1:
#                 merged_segments.append(segments[-1])
#                 merged_values.append(values[-1])

#             # Merge continuously increasing segments at the end
#             i = len(merged_segments) - 1
#             while i > 0:
#                 current_segment_start, current_segment_end = merged_segments[i][0] - start, merged_segments[i][1] - start
#                 current_value = merged_values[i]
#                 segment_length = current_segment_end - current_segment_start

#                 # Merge small segments until we have a segment with at least 3 events
#                 while i > 0 and segment_length < 3:
#                     i -= 1
#                     current_segment_start = merged_segments[i][0] - start
#                     current_value = min(current_value, merged_values[i])
#                     segment_length = current_segment_end - current_segment_start

#                 current_rate_of_change = calculate_rate_of_change(current_segment_start, current_segment_end, event_data)

#                 if np.abs(current_rate_of_change) > change_of_rate_threshold and current_rate_of_change > 0:  # Decreased threshold for increasing segments
#                     merged_segment_end = current_segment_end
#                     merged_value = current_value
#                     i -= 1

#                     while i > 0:
#                         prev_segment_start, prev_segment_end = merged_segments[i][0] - start, merged_segments[i][1] - start
#                         prev_segment_length = prev_segment_end - prev_segment_start

#                         # Merge small segments until we have a segment with at least 3 events
#                         while i > 0 and prev_segment_length < 3:
#                             i -= 1
#                             prev_segment_start = merged_segments[i][0] - start
#                             prev_segment_length = prev_segment_end - prev_segment_start

#                         prev_rate_of_change = calculate_rate_of_change(prev_segment_start, prev_segment_end, event_data)

#                         if prev_rate_of_change > 0:
#                             merged_value = min(merged_value, merged_values[i])
#                             i -= 1
#                         else:
#                             break  # Stop merging if the rate of change sign changes

#                     merged_segment_start = merged_segments[i + 1][0] - start
#                     merged_segments[i + 1] = (merged_segment_start + start, merged_segment_end + start)
#                     merged_values[i + 1] = merged_value
#                     del merged_segments[i + 2:]
#                     del merged_values[i + 2:]
#                 else:
#                     i -= 1


#             # Merge segments with values within 90% of each other
#             i = 0
#             while i < len(merged_segments) - 1:
#                 current_segment_start, current_segment_end = merged_segments[i][0], merged_segments[i][1]
#                 current_value = merged_values[i]

#                 next_segment_start, next_segment_end = merged_segments[i + 1][0], merged_segments[i + 1][1]
#                 next_value = merged_values[i + 1]

#                 if merge_close_segments_threshold <= current_value / next_value <= 1+(1-merge_close_segments_threshold):
#                     merged_segment_end = next_segment_end
#                     merged_value = (current_value + next_value) / 2  # Use the average of the two values
#                     merged_segments[i] = (current_segment_start, merged_segment_end)
#                     merged_values[i] = merged_value
#                     del merged_segments[i + 1]
#                     del merged_values[i + 1]
#                 else:
#                     i += 1
#             return merged_segments, merged_values

#         # print(f"Before merging: {len(cusum_segments)} segments")
#         # print(f"Cusum segments before merging: {cusum_segments}")
#         # print(f"Mean values before merging: {mean_values}")

#         for i in range(len(cusum_segments)):
#             segment_start, segment_end = cusum_segments[i][0] - start, cusum_segments[i][1] - start
#             segment_data = event_data[segment_start:segment_end]
#             segment_value = mean_values[i]

#             # Check for significant peaks or troughs within the segment
#             peaks, _ = sig.find_peaks(segment_data, prominence=first_last_segment_threshold)
#             troughs, _ = sig.find_peaks(-segment_data, prominence=first_last_segment_threshold)

#             if len(peaks) > 0 or len(troughs) > 0:
#                 # Split the segment if significant peaks or troughs are found
#                 split_points = np.sort(np.concatenate((peaks, troughs)))
#                 split_starts = [segment_start] + list(split_points + 1)
#                 split_ends = list(split_points) + [segment_end]

#                 for j in range(len(split_starts)):
#                     split_segment_start = split_starts[j]
#                     split_segment_end = split_ends[j]
#                     split_segment_data = event_data[split_segment_start:split_segment_end]

#                     if len(split_segment_data) > 0:
#                         split_segment_value = np.median(split_segment_data)
#                         post_processed_segments.append((split_segment_start + start, split_segment_end + start))
#                         post_processed_mean_values.append(split_segment_value)
#             else:
#                 post_processed_segments.append((segment_start + start, segment_end + start))
#                 post_processed_mean_values.append(segment_value)

#         post_processed_segments, post_processed_mean_values = merge_segments(cusum_segments, mean_values, event_data)

#         # print(f"After merging: {len(post_processed_segments)} segments")
#         # print(f"Cusum segments after merging: {post_processed_segments}")
#         # print(f"Mean values after merging: {post_processed_mean_values}")

#         # Check if the total number of segments is 1
#         if len(post_processed_segments) == 1:
#             segment_data = event_data[post_processed_segments[0][0] - start:post_processed_segments[0][1] - start]
#             if len(segment_data) > 0:
#                 post_processed_mean_values[0] = np.min(segment_data)

#         # Check if the rate of change of each segment is larger than 0.2
#         for i in range(len(post_processed_segments)):
#             segment_start, segment_end = post_processed_segments[i][0] - start, post_processed_segments[i][1] - start
#             #print(f"Segment {i}: start={segment_start}, end={segment_end}")  # Print segment start and end
#             segment_data = event_data[segment_start:segment_end]
#             #print(f"Segment {i} data: {segment_data}")  # Print segment data

#             if len(segment_data) > 1:
#                 segment_rate_of_change = calculate_rate_of_change(segment_start, segment_end, event_data)
#                 #print(f"Segment {i} rate of change: {segment_rate_of_change}")  # Print segment rate of change
#                 if np.abs(segment_rate_of_change) > 0.2:
#                     #print(f"Segment {i} rate of change > 0.2, setting value to min")  # Print when condition is met
#                     post_processed_mean_values[i] = np.min(segment_data)

#         return post_processed_segments, post_processed_mean_values

#     for start, end in event_chunk:
#         padded_start = max(start - padding, 0)
#         padded_end = min(end + padding, len(data))
#         padded_event_data = data[padded_start:padded_end]
#         event_data = data[start:end]

#         if len(event_data) > 1:
#             threshold = np.std(event_data) * 0.5
#             change_points = detect_change_points(event_data, threshold)

#             segments = [0] + list(change_points) + [len(event_data)]
#             mean_values = []
#             cusum_segments = []
#             segment_widths_time = []
#             segment_mean_diffs = []

#             baseline_value = np.mean(data[padded_start:start])
#             number_of_segments = len(segments) - 1


#             # print(f"Number of segments before merging: {number_of_segments}")
#             # print(f"Segments before merging: {segments}")

#             i = 0
#             is_first_segment = True
#             is_last_segment = False
#             while i < number_of_segments:
#                 segment_start, segment_end = segments[i], segments[i + 1]
#                 segment_data = event_data[segment_start:segment_end]
#                 segment_length = segment_end - segment_start

#                 # Merge small segments until we have a segment with at least 3 events
#                 while i + 1 < number_of_segments and segment_length < 3:
#                     i += 1
#                     segment_end = segments[i + 1]
#                     segment_data = event_data[segment_start:segment_end]
#                     segment_length = segment_end - segment_start

#                 if segment_length == 0:
#                     i += 1
#                     continue  # Skip zero-size segments

#                 # Calculate the middle portion of the segment based on its length
#                 if segment_length > 9:
#                     middle_start = segment_start + (segment_length - (segment_length - 4)) // 2
#                     middle_end = middle_start + (segment_length - 4)
#                 elif segment_length > 7:
#                     middle_start = segment_start + (segment_length - 5) // 2
#                     middle_end = middle_start + 5
#                 elif segment_length > 5:
#                     middle_start = segment_start + 1
#                     middle_end = segment_end - 1
#                 else:
#                     middle_start = segment_start
#                     middle_end = segment_end

#                 middle_segment_data = segment_data[middle_start - segment_start:middle_end - segment_start]

#                 # Calculate rate of change for the middle portion of the segment
#                 rate_of_change = np.mean(np.gradient(middle_segment_data))

#                 # Merge segments with similar rate of change based on middle_segment_data
#                 merge_segments = True
#                 while merge_segments and i + 1 < number_of_segments:
#                     next_segment_start, next_segment_end = segments[i + 1], segments[i + 2]
#                     next_segment_length = next_segment_end - next_segment_start
#                     next_segment_data = event_data[next_segment_start:next_segment_end]

#                     if next_segment_length > 9:
#                         next_middle_start = next_segment_start + (next_segment_length - (next_segment_length - 4)) // 2
#                         next_middle_end = next_middle_start + (next_segment_length - 4)
#                     elif next_segment_length > 7:
#                         next_middle_start = next_segment_start + (next_segment_length - 5) // 2
#                         next_middle_end = next_middle_start + 5
#                     elif next_segment_length > 5:
#                         next_middle_start = next_segment_start + 1
#                         next_middle_end = next_segment_end - 1
#                     else:
#                         next_middle_start = next_segment_start
#                         next_middle_end = next_segment_end
#                     next_middle_segment_data = next_segment_data[next_middle_start - next_segment_start:next_middle_end - next_segment_start]

#                     if len(next_middle_segment_data) < 2:  # Check if next_middle_segment_data has at least 2 elements
#                         break

#                     next_rate_of_change = np.mean(np.gradient(next_middle_segment_data))

#                     adaptive_threshold = calculate_adaptive_threshold(rate_of_change, is_first_segment, is_last_segment)

#                     if should_merge_segments(middle_segment_data, next_middle_segment_data, rate_of_change, next_rate_of_change, adaptive_threshold):
#                         i += 1
#                         segment_end = segments[i + 1]
#                         segment_data = event_data[segment_start:segment_end]
#                         segment_length = segment_end - segment_start

#                         # Update the middle portion of the merged segment
#                         if segment_length > 9:
#                             middle_start = segment_start + (segment_length - (segment_length - 4)) // 2
#                             middle_end = middle_start + (segment_length - 4)
#                         elif segment_length > 7:
#                             middle_start = segment_start + (segment_length - 5) // 2
#                             middle_end = middle_start + 5
#                         elif segment_length > 5:
#                             middle_start = segment_start + 1
#                             middle_end = segment_end - 1
#                         else:
#                             middle_start = segment_start
#                             middle_end = segment_end

#                         middle_segment_data = segment_data[middle_start - segment_start:middle_end - segment_start]
#                         rate_of_change = np.mean(np.gradient(middle_segment_data))
#                     else:
#                         merge_segments = False

#                 # Update is_first_segment and is_last_segment after merging
#                 is_first_segment = (i == 0)
#                 is_last_segment = (i == number_of_segments - 1)

#                 segment_value = calculate_segment_value(segment_data, middle_segment_data, rate_of_change, is_first_segment, is_last_segment)

#                 # print(f"Segment {i} value: {segment_value}")

#                 mean_values.append(segment_value)
#                 cusum_segments.append((segment_start + start, segment_end + start))
#                 segment_widths_time.append((segment_end - segment_start) / sampling_rate)
#                 segment_mean_diffs.append(baseline_value - segment_value)

#                 # Update the flags for the next iteration
#                 is_first_segment = False
#                 is_last_segment = (i == number_of_segments - 1)

#                 i += 1

#             # Post-processing: Split segments with significant peaks or troughs
#             cusum_segments, mean_values = post_process_segments(event_data, cusum_segments, mean_values)


#             # Calculate segment_mean_diffs and segment_widths_time after post-processing
#             segment_mean_diffs = []
#             segment_widths_time = []
#             for i, (segment_start, segment_end) in enumerate(cusum_segments):
#                 segment_data = event_data[segment_start - start:segment_end - start]
#                 segment_mean_diffs.append(baseline_value - mean_values[i])
#                 segment_widths_time.append((segment_end - segment_start) / sampling_rate)


#             # mean_values_continuous = np.zeros(len(event_data))
#             # for i, (segment_start, segment_end) in enumerate(cusum_segments):
#             #     mean_values_continuous[segment_start - start:segment_end - start] = mean_values[i]

#             mean_values_continuous = np.full(len(event_data), baseline_value)
#             for i, (segment_start, segment_end) in enumerate(cusum_segments):
#                 mean_values_continuous[segment_start - start:segment_end - start] = mean_values[i]

#             mean_values_connected_with_baseline = np.full(len(padded_event_data), baseline_value)
#             mean_values_connected_with_baseline[start - padded_start:end - padded_start] = mean_values_continuous

#             time_points_padded = np.linspace(padded_start / sampling_rate, padded_end / sampling_rate, len(padded_event_data))
#             time_points_event = np.linspace(start / sampling_rate, end / sampling_rate, len(event_data))

#             segment_info = {
#                 "number_of_segments": len(cusum_segments),
#                 "segment_mean_diffs": segment_mean_diffs,
#                 "segment_widths_time": segment_widths_time,
#                 "event_width": sum(segment_widths_time),
#             }

#             #print(segment_info)

#             event_analysis = np.append(analyze_event_for_CUSUM(event_data, baseline_value, ML_standardisation_settings, start / sampling_rate), start / sampling_rate)

#             chunk_results.append({
#                 "time_points_padded": time_points_padded,
#                 "time_points_event": time_points_event,
#                 "padded_event_data": padded_event_data,
#                 "event_time_start_end": np.array([start / sampling_rate, end / sampling_rate]),
#                 "baseline_value": baseline_value,
#                 "mean_values": mean_values,
#                 "mean_values_connected": mean_values_continuous,
#                 "mean_values_connected_with_baseline": mean_values_connected_with_baseline,
#                 "cusum_segments": cusum_segments,
#                 "segment_info": segment_info,
#                 "event_analysis": event_analysis,
#             })

#     return chunk_results    



def analyze_event_chunk_with_padding(event_chunk, padding, library, model, num_components, penalty, data, dips, ML_standardisation_settings):
    chunk_results = []
    sampling_rate = ML_standardisation_settings['sampling_rate']
    segment_rate_threshold = ML_standardisation_settings['segment_rate_threshold']
    first_last_segment_threshold = 0.5
    change_of_rate_threshold = ML_standardisation_settings['change_of_rate_threshold']
    merge_close_segments_threshold = ML_standardisation_settings['merge_close_segments_threshold']
    

    def detect_change_points(event_data, threshold):
        if library == "ruptures":
            algo = rpt.Pelt(model=model).fit(event_data)
            change_points = algo.predict(pen=penalty * threshold)
        elif library == "detecta":
            if model == "cusum":
                _, change_points, _, _ = detect_cusum(event_data, threshold=penalty * threshold, drift=0, ending=False, show=False)
        elif library == "lmfit":
            change_points = autostepfinder(event_data, penalty * threshold)
        elif library == "hmm":
            hmm_model = hmm.GaussianHMM(n_components=num_components).fit(event_data.reshape(-1, 1))
            _, change_points = hmm_model.decode(event_data.reshape(-1, 1))
        elif library == "gmm":
            gmm_model = GaussianMixture(n_components=num_components).fit(event_data.reshape(-1, 1))
            change_points = np.where(np.diff(gmm_model.predict(event_data.reshape(-1, 1))))[0]
        else:
            raise ValueError(f"Unsupported library: {library}")
        return change_points

    def calculate_adaptive_threshold(rate_of_change, is_first_segment, is_last_segment):
        if (is_first_segment and rate_of_change < 0) or (is_last_segment and rate_of_change > 0):
            return segment_rate_threshold
        else:
            return segment_rate_threshold / 2

    def should_merge_segments(segment_data, next_segment_data, rate_of_change, next_rate_of_change, adaptive_threshold):
        if np.sign(rate_of_change) != np.sign(next_rate_of_change):
            return False

        if np.abs(rate_of_change - next_rate_of_change) >= adaptive_threshold:
            return False

        segment_value = np.median(segment_data)
        next_segment_value = np.median(next_segment_data)

        if np.abs(segment_value - next_segment_value) > adaptive_threshold:
            return False

        return True

    def calculate_rate_of_change(segment_start, segment_end, event_data):
        segment_data = event_data[segment_start:segment_end]
        if len(segment_data) < 2:
            return 0
        return (segment_data[-1] - segment_data[0]) / (segment_end - segment_start)

    def calculate_segment_value(segment_data, middle_segment_data, rate_of_change, is_first_segment, is_last_segment):
        if len(middle_segment_data) == 0 or np.all(middle_segment_data == 0):
            return np.median(segment_data)

        if is_last_segment:
            return np.min(segment_data)
        elif (is_first_segment or is_last_segment) and np.abs(rate_of_change) > first_last_segment_threshold / 3:
            return np.min(segment_data)
        elif np.abs(rate_of_change) > first_last_segment_threshold * 2:
            return np.min(segment_data)
        else:
            return np.median(middle_segment_data)

    def post_process_segments(event_data, cusum_segments, mean_values):
        post_processed_segments = []
        post_processed_mean_values = []

        def merge_segments(segments, values, event_data):
            merged_segments = []
            merged_values = []

            # Merge continuously decreasing segments at the start
            i = 0
            while i < len(segments) - 1:
                current_segment_start, current_segment_end = segments[i][0] - start, segments[i][1] - start
                current_value = values[i]
                segment_length = current_segment_end - current_segment_start

                # Merge small segments until we have a segment with at least 3 events
                while i + 1 < len(segments) and segment_length < 3:
                    i += 1
                    current_segment_end = segments[i][1] - start
                    current_value = min(current_value, values[i])
                    segment_length = current_segment_end - current_segment_start

                current_rate_of_change = calculate_rate_of_change(current_segment_start, current_segment_end, event_data)

                if np.abs(current_rate_of_change) > change_of_rate_threshold and current_rate_of_change < 0:  # Increased threshold for decreasing segments
                    merged_segment_start = current_segment_start
                    merged_value = current_value
                    i += 1

                    while i < len(segments) - 1:
                        next_segment_start, next_segment_end = segments[i][0] - start, segments[i][1] - start
                        next_segment_length = next_segment_end - next_segment_start

                        # Merge small segments until we have a segment with at least 3 events
                        while i + 1 < len(segments) and next_segment_length < 3:
                            i += 1
                            next_segment_end = segments[i][1] - start
                            next_segment_length = next_segment_end - next_segment_start

                        next_rate_of_change = calculate_rate_of_change(next_segment_start, next_segment_end, event_data)

                        if next_rate_of_change < 0:
                            merged_value = min(merged_value, values[i])
                            i += 1
                        else:
                            break  # Stop merging if the rate of change sign changes

                    merged_segment_end = segments[i - 1][1] - start
                    merged_segments.append((merged_segment_start + start, merged_segment_end + start))
                    merged_values.append(merged_value)
                else:
                    merged_segments.append((current_segment_start + start, current_segment_end + start))
                    merged_values.append(current_value)
                    i += 1

            # Add the last segment if it was not merged
            if i == len(segments) - 1:
                merged_segments.append(segments[-1])
                merged_values.append(values[-1])

            # Merge continuously increasing segments at the end
            i = len(merged_segments) - 1
            while i > 0:
                current_segment_start, current_segment_end = merged_segments[i][0] - start, merged_segments[i][1] - start
                current_value = merged_values[i]
                segment_length = current_segment_end - current_segment_start

                # Merge small segments until we have a segment with at least 3 events
                while i > 0 and segment_length < 3:
                    i -= 1
                    current_segment_start = merged_segments[i][0] - start
                    current_value = min(current_value, merged_values[i])
                    segment_length = current_segment_end - current_segment_start

                current_rate_of_change = calculate_rate_of_change(current_segment_start, current_segment_end, event_data)

                if np.abs(current_rate_of_change) > change_of_rate_threshold and current_rate_of_change > 0:  # Decreased threshold for increasing segments
                    merged_segment_end = current_segment_end
                    merged_value = current_value
                    i -= 1

                    while i > 0:
                        prev_segment_start, prev_segment_end = merged_segments[i][0] - start, merged_segments[i][1] - start
                        prev_segment_length = prev_segment_end - prev_segment_start

                        # Merge small segments until we have a segment with at least 3 events
                        while i > 0 and prev_segment_length < 3:
                            i -= 1
                            prev_segment_start = merged_segments[i][0] - start
                            prev_segment_length = prev_segment_end - prev_segment_start

                        prev_rate_of_change = calculate_rate_of_change(prev_segment_start, prev_segment_end, event_data)

                        if prev_rate_of_change > 0:
                            merged_value = min(merged_value, merged_values[i])
                            i -= 1
                        else:
                            break  # Stop merging if the rate of change sign changes

                    merged_segment_start = merged_segments[i + 1][0] - start
                    merged_segments[i + 1] = (merged_segment_start + start, merged_segment_end + start)
                    merged_values[i + 1] = merged_value
                    del merged_segments[i + 2:]
                    del merged_values[i + 2:]
                else:
                    i -= 1

            # Merge segments with values within 90% of each other
            i = 0
            while i < len(merged_segments) - 1:
                current_segment_start, current_segment_end = merged_segments[i][0], merged_segments[i][1]
                current_value = merged_values[i]

                next_segment_start, next_segment_end = merged_segments[i + 1][0], merged_segments[i + 1][1]
                next_value = merged_values[i + 1]

                if merge_close_segments_threshold <= current_value / next_value <= 1+(1-merge_close_segments_threshold):
                    merged_segment_end = next_segment_end
                    merged_value = (current_value + next_value) / 2  # Use the average of the two values
                    merged_segments[i] = (current_segment_start, merged_segment_end)
                    merged_values[i] = merged_value
                    del merged_segments[i + 1]
                    del merged_values[i + 1]
                else:
                    i += 1
            return merged_segments, merged_values

        post_processed_segments, post_processed_mean_values = merge_segments(cusum_segments, mean_values, event_data)

        # Check if the total number of segments is 1
        if len(post_processed_segments) == 1:
            segment_data = event_data[post_processed_segments[0][0] - start:post_processed_segments[0][1] - start]
            if len(segment_data) > 0:
                post_processed_mean_values[0] = np.min(segment_data)

        # Check if the rate of change of each segment is larger than 0.2
        for i in range(len(post_processed_segments)):
            segment_start, segment_end = post_processed_segments[i][0] - start, post_processed_segments[i][1] - start
            segment_data = event_data[segment_start:segment_end]

            if len(segment_data) > 1:
                segment_rate_of_change = calculate_rate_of_change(segment_start, segment_end, event_data)
                if np.abs(segment_rate_of_change) > 0.2:
                    post_processed_mean_values[i] = np.min(segment_data)

        return post_processed_segments, post_processed_mean_values

    for start, end in event_chunk:
        padded_start = max(start - padding, 0)
        padded_end = min(end + padding, len(data))
        padded_event_data = data[padded_start:padded_end]
        event_data = data[start:end]

        if len(event_data) > 1:
            threshold = np.std(event_data) * 0.5
            change_points = detect_change_points(event_data, threshold)

            segments = [0] + list(change_points) + [len(event_data)]
            mean_values = []
            cusum_segments = []

            baseline_value = np.mean(data[padded_start:start])
            number_of_segments = len(segments) - 1

            i = 0
            while i < number_of_segments:
                segment_start, segment_end = segments[i], segments[i + 1]
                segment_data = event_data[segment_start:segment_end]
                segment_length = segment_end - segment_start

                # Merge small segments until we have a segment with at least 3 events
                while i + 1 < number_of_segments and segment_length < 3:
                    i += 1
                    segment_end = segments[i + 1]
                    segment_data = event_data[segment_start:segment_end]
                    segment_length = segment_end - segment_start

                if segment_length == 0:
                    i += 1
                    continue  # Skip zero-size segments

                # Calculate the middle portion of the segment based on its length
                if segment_length > 9:
                    middle_start = segment_start + (segment_length - (segment_length - 4)) // 2
                    middle_end = middle_start + (segment_length - 4)
                elif segment_length > 7:
                    middle_start = segment_start + (segment_length - 5) // 2
                    middle_end = middle_start + 5
                elif segment_length > 5:
                    middle_start = segment_start + 1
                    middle_end = segment_end - 1
                else:
                    middle_start = segment_start
                    middle_end = segment_end

                middle_segment_data = segment_data[middle_start - segment_start:middle_end - segment_start]

                # Calculate rate of change for the middle portion of the segment
                rate_of_change = np.mean(np.gradient(middle_segment_data))

                # Merge segments with similar rate of change based on middle_segment_data
                merge_segments = True
                while merge_segments and i + 1 < number_of_segments:
                    next_segment_start, next_segment_end = segments[i + 1], segments[i + 2]
                    next_segment_length = next_segment_end - next_segment_start
                    next_segment_data = event_data[next_segment_start:next_segment_end]

                    if next_segment_length > 9:
                        next_middle_start = next_segment_start + (next_segment_length - (next_segment_length - 4)) // 2
                        next_middle_end = next_middle_start + (next_segment_length - 4)
                    elif next_segment_length > 7:
                        next_middle_start = next_segment_start + (next_segment_length - 5) // 2
                        next_middle_end = next_middle_start + 5
                    elif next_segment_length > 5:
                        next_middle_start = next_segment_start + 1
                        next_middle_end = next_segment_end - 1
                    else:
                        next_middle_start = next_segment_start
                        next_middle_end = next_segment_end
                    next_middle_segment_data = next_segment_data[next_middle_start - next_segment_start:next_middle_end - next_segment_start]

                    if len(next_middle_segment_data) < 2:  # Check if next_middle_segment_data has at least 2 elements
                        break

                    next_rate_of_change = np.mean(np.gradient(next_middle_segment_data))

                    is_first_segment = (i == 0)
                    is_last_segment = (i == number_of_segments - 1)
                    adaptive_threshold = calculate_adaptive_threshold(rate_of_change, is_first_segment, is_last_segment)

                    if should_merge_segments(middle_segment_data, next_middle_segment_data, rate_of_change, next_rate_of_change, adaptive_threshold):
                        i += 1
                        segment_end = segments[i + 1]
                        segment_data = event_data[segment_start:segment_end]
                        segment_length = segment_end - segment_start

                        # Update the middle portion of the merged segment
                        if segment_length > 9:
                            middle_start = segment_start + (segment_length - (segment_length - 4)) // 2
                            middle_end = middle_start + (segment_length - 4)
                        elif segment_length > 7:
                            middle_start = segment_start + (segment_length - 5) // 2
                            middle_end = middle_start + 5
                        elif segment_length > 5:
                            middle_start = segment_start + 1
                            middle_end = segment_end - 1
                        else:
                            middle_start = segment_start
                            middle_end = segment_end

                        middle_segment_data = segment_data[middle_start - segment_start:middle_end - segment_start]
                        rate_of_change = np.mean(np.gradient(middle_segment_data))
                    else:
                        merge_segments = False

                is_first_segment = (i == 0)
                is_last_segment = (i == number_of_segments - 1)
                segment_value = calculate_segment_value(segment_data, middle_segment_data, rate_of_change, is_first_segment, is_last_segment)

                mean_values.append(segment_value)
                cusum_segments.append((segment_start + start, segment_end + start))

                i += 1

            # Post-processing: Split segments with significant peaks or troughs
            cusum_segments, mean_values = post_process_segments(event_data, cusum_segments, mean_values)

            # Calculate segment_mean_diffs and segment_widths_time after post-processing
            segment_mean_diffs = []
            segment_widths_time = []
            for i, (segment_start, segment_end) in enumerate(cusum_segments):
                segment_data = event_data[segment_start - start:segment_end - start]
                segment_mean_diffs.append(baseline_value - mean_values[i])
                segment_widths_time.append((segment_end - segment_start) / sampling_rate)

            mean_values_continuous = np.full(len(event_data), baseline_value)
            for i, (segment_start, segment_end) in enumerate(cusum_segments):
                mean_values_continuous[segment_start - start:segment_end - start] = mean_values[i]

            mean_values_connected_with_baseline = np.full(len(padded_event_data), baseline_value)
            mean_values_connected_with_baseline[start - padded_start:end - padded_start] = mean_values_continuous

            time_points_padded = np.linspace(padded_start / sampling_rate, padded_end / sampling_rate, len(padded_event_data))
            time_points_event = np.linspace(start / sampling_rate, end / sampling_rate, len(event_data))

            # Correctly identify first and last segments
            first_segment = cusum_segments[0]
            last_segment = cusum_segments[-1]

            segment_info = {
                "number_of_segments": len(cusum_segments),
                "segment_mean_diffs": segment_mean_diffs,
                "segment_widths_time": segment_widths_time,
                "event_width": sum(segment_widths_time),
                "first_segment": first_segment,
                "last_segment": last_segment
            }

            event_analysis = np.append(analyze_event_for_CUSUM(event_data, baseline_value, ML_standardisation_settings, start / sampling_rate), start / sampling_rate)

            chunk_results.append({
                "time_points_padded": time_points_padded,
                "time_points_event": time_points_event,
                "padded_event_data": padded_event_data,
                "event_time_start_end": np.array([start / sampling_rate, end / sampling_rate]),
                "baseline_value": baseline_value,
                "mean_values": mean_values,
                "mean_values_connected": mean_values_continuous,
                "mean_values_connected_with_baseline": mean_values_connected_with_baseline,
                "cusum_segments": cusum_segments,
                "segment_info": segment_info,
                "event_analysis": event_analysis,
            })

    return chunk_results

def multi_level_fitting_events(padding, chunk_size_events,library, model,num_components, penalty, data,events, dips, ML_standardisation_settings):
    event_chunks = [events[i:i + chunk_size_events] for i in range(0, len(events), chunk_size_events)]
    prepared_data_chunks = Parallel(n_jobs=-1)(
        delayed(analyze_event_chunk_with_padding)(chunk, padding,library, model,num_components,penalty,data, dips, ML_standardisation_settings) for chunk in event_chunks
    )

    # Initialize a dictionary to hold all the data to be saved
    npz_dict = {}

    # Initialize a list to collect all the event_analysis arrays
    all_event_analyses = []

    event_counter = 0
    for chunk_data in prepared_data_chunks:
        for event_data in chunk_data:
            # Construct keys for each data type
            event_key = f'EVENT_DATA_{event_counter}'
            segment_info_key = f'SEGMENT_INFO_{event_counter}'
            event_analysis_key = f'EVENT_ANALYSIS_{event_counter}'

            # Prepare the EVENT_DATA
            event_data_formatted = [
                np.array(event_data['time_points_padded'], dtype=np.float64),
                np.array(event_data['padded_event_data'], dtype=np.float64),
                np.array(event_data['event_time_start_end'], dtype=np.float64),
                np.array(event_data['mean_values_connected_with_baseline'], dtype=np.float64),
                np.full(len(event_data['padded_event_data']), event_data['baseline_value'], dtype=np.float64)
            ]

            # Save each piece of data separately to handle varying lengths
            for i, arr in enumerate(event_data_formatted):
                npz_dict[f'{event_key}_part_{i}'] = arr

            # Prepare and save SEGMENT_INFO
            segment_info_formatted = {
                'number_of_segments': np.array([event_data['segment_info']['number_of_segments']], dtype=np.float64),
                'segment_mean_diffs': np.array(event_data['segment_info']['segment_mean_diffs'], dtype=np.float64),
                'segment_widths_time': np.array(event_data['segment_info']['segment_widths_time'], dtype=np.float64),
                'event_width': np.array([event_data['segment_info']['event_width']], dtype=np.float64),
            }

            for key, value in segment_info_formatted.items():
                npz_dict[f'{segment_info_key}_{key}'] = value

            #Since event_analysis is a list, directly convert it to a numpy array
            event_analysis_array = np.array(event_data['event_analysis'], dtype=np.float64)
            npz_dict[f'EVENT_ANALYSIS_{event_counter}'] = event_analysis_array
            # Append the numpy array to the all_event_analyses list
            all_event_analyses.append(event_analysis_array)

            event_counter += 1

    # Convert the list of all event analyses into a numpy array
    all_event_analyses_array = np.array(all_event_analyses, dtype=object)

    return npz_dict, all_event_analyses_array

class FileLoadError(Exception):
    pass

class CustomNavigationToolbar(NavigationToolbar):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.setIconSize(QSize(17, 17))  # Set the icon size to 17x17 pixels

class MplWidget(QWidget):
    def __init__(self, parent=None):
        super(MplWidget, self).__init__(parent)
        self.canvas = MplCanvas()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class FittingOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fitting Options")
        self.setMinimumWidth(400)
        self.setWindowModality(Qt.WindowModality.NonModal)  # Set the dialog as non-modal

        layout = QVBoxLayout(self)

        # Create the same fitting settings as in FittingSettingsTab
        self.padding_spinbox = QSpinBox()
        self.padding_spinbox.setRange(0, 10000)
        self.padding_spinbox.setValue(100)

        self.chunk_size_for_event_fitting_spinbox = QSpinBox()
        self.chunk_size_for_event_fitting_spinbox.setRange(1, 100000)
        self.chunk_size_for_event_fitting_spinbox.setValue(30)

        self.library_combo = QComboBox()
        self.library_combo.addItems(["ruptures", "detecta", "lmfit", "hmm", "gmm"])
        self.library_combo.currentIndexChanged.connect(self.update_model_combo)

        self.model_combo = QComboBox()
        self.model_label = QLabel("Model:")

        self.num_components_spinbox = QSpinBox()
        self.num_components_spinbox.setRange(2, 10)
        self.num_components_spinbox.setValue(2)
        self.num_components_label = QLabel("Number of Components:")

        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.1, 100)
        self.threshold_spinbox.setValue(1.2)
        self.threshold_spinbox.setDecimals(2)

        self.segment_rate_threshold_spinbox = QDoubleSpinBox()
        self.segment_rate_threshold_spinbox.setRange(0.001, 100)
        self.segment_rate_threshold_spinbox.setValue(0.6)
        self.segment_rate_threshold_spinbox.setDecimals(3)

        self.change_rate_threshold_spinbox = QDoubleSpinBox()
        self.change_rate_threshold_spinbox.setRange(0.001, 100)
        self.change_rate_threshold_spinbox.setValue(0.1)
        self.change_rate_threshold_spinbox.setDecimals(3)

        self.merge_segment_threshold_spinbox = QDoubleSpinBox()
        self.merge_segment_threshold_spinbox.setRange(0.001, 100)
        self.merge_segment_threshold_spinbox.setValue(0.9)
        self.merge_segment_threshold_spinbox.setDecimals(3)

        form_layout = QFormLayout()
        form_layout.addRow("Padding (in number of samples):", self.padding_spinbox)
        form_layout.addRow("Chunk Size for Event Fitting:", self.chunk_size_for_event_fitting_spinbox)
        form_layout.addRow("Library:", self.library_combo)
        form_layout.addRow(self.model_label, self.model_combo)
        form_layout.addRow(self.num_components_label, self.num_components_spinbox)
        form_layout.addRow("Threshold:", self.threshold_spinbox)
        form_layout.addRow("Segment Rate Threshold:", self.segment_rate_threshold_spinbox)
        form_layout.addRow("Change Rate Threshold:", self.change_rate_threshold_spinbox)
        form_layout.addRow("Merge Segment Threshold:", self.merge_segment_threshold_spinbox)
        layout.addLayout(form_layout)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.update_model_combo(0)

    def update_model_combo(self, index):
        # Same as in FittingSettingsTab
        library = self.library_combo.currentText()
        self.model_combo.clear()

        if library in ["ruptures", "detecta", "lmfit"]:
            self.model_label.setVisible(True)
            self.model_combo.setVisible(True)
            self.num_components_label.setVisible(False)
            self.num_components_spinbox.setVisible(False)

            if library == "ruptures":
                self.model_combo.addItems(["l1", "l2", "rbf"])
                self.model_combo.setCurrentIndex(1)
                self.model_combo.setCurrentIndex(1)
            elif library == "detecta":
                self.model_combo.addItems(["cusum"])
            elif library == "lmfit":
                self.model_combo.addItems(["autostepfinder"])
        else:
            self.model_label.setVisible(False)
            self.model_combo.setVisible(False)
            self.num_components_label.setVisible(True)
            self.num_components_spinbox.setVisible(True)

    def closeEvent(self, event):
        # Store the current values before closing the dialog
        self.parent().fitting_settings_tab.padding_spinbox.setValue(self.padding_spinbox.value())
        self.parent().fitting_settings_tab.chunk_size_for_event_fitting_spinbox.setValue(self.chunk_size_for_event_fitting_spinbox.value())
        self.parent().fitting_settings_tab.library_combo.setCurrentText(self.library_combo.currentText())
        self.parent().fitting_settings_tab.model_combo.setCurrentText(self.model_combo.currentText())
        self.parent().fitting_settings_tab.num_components_spinbox.setValue(self.num_components_spinbox.value())
        self.parent().fitting_settings_tab.threshold_spinbox.setValue(self.threshold_spinbox.value())
        self.parent().fitting_settings_tab.segment_rate_threshold_spinbox.setValue(self.segment_rate_threshold_spinbox.value())
        self.parent().fitting_settings_tab.change_rate_threshold_spinbox.setValue(self.change_rate_threshold_spinbox.value())
        self.parent().fitting_settings_tab.merge_segment_threshold_spinbox.setValue(self.merge_segment_threshold_spinbox.value())

        super().closeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SD Data Reduction App")
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Splitter for adjustable layouts
        splitter = QSplitter(Qt.Orientation.Horizontal)
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        display_widget = QWidget()
        display_layout = QVBoxLayout(display_widget)
        
        # Splitting the layout with splitter
        splitter.addWidget(settings_widget)
        splitter.addWidget(display_widget)
        splitter.setSizes([350, 900])  # Adjusted sizes for left and right side
        
        main_layout.addWidget(splitter)
        
        # Add app name and email at the top of settings
        self.setupTopLabels(settings_layout)
        
        # Setup tabs in settings_layout
        self.setupTabs(settings_layout)
        
        # Setup the right side (display area)
        self.setupDisplayArea(display_layout)
        self.current_event_index = 0  # Starting at the first event
        self.total_events = 0
        self.sampling_rate = None
        self.save_file_path = None
        self.previous_settings = None
        self.fitting_options_dialog = FittingOptionsDialog(self)
        self.data = None



    def setupTopLabels(self, layout):
        self.app_name_label = QLabel("SD Data Reduction App")
        self.app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_name_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.email_label = QLabel("shankar.dutt@anu.edu.au")
        self.email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.app_name_label)
        layout.addWidget(self.email_label)

    def setupTabs(self, layout):
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Tabs
        self.load_options_tab = LoadOptionsTab()
        self.event_settings_tab = EventSettingsTab()
        self.fitting_settings_tab = FittingSettingsTab()
        self.ml_tab = MLTab()
        self.data_reduction_tab = DataReductionTab(self)
        
        tab_widget.addTab(self.load_options_tab, "Load Options")
        tab_widget.addTab(self.event_settings_tab, "Event Options")
        tab_widget.addTab(self.fitting_settings_tab, "Fitting Options")
        tab_widget.addTab(self.ml_tab, "ML")
        tab_widget.addTab(self.data_reduction_tab, "Multi Threshold Tester")

        #Connections Here!!
        self.load_options_tab.test_settings_btn.clicked.connect(self.on_test_settings_clicked)
        self.load_options_tab.perform_data_reduction_btn.clicked.connect(self.on_perform_data_reduction_clicked)
        self.load_options_tab.plot_data_btn.clicked.connect(self.Plot_Entire_Data)
        self.load_options_tab.save_file_path_btn.clicked.connect(self.specify_file_name)
        
    def setupDisplayArea(self, layout):
        # Vertical splitter to separate the main plot area and the information area
        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top tab widget for Analysis and Plots
        top_tab_widget = QTabWidget()
        
        # Analysis tab
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        analysis_layout.setSpacing(0)
        analysis_layout.setContentsMargins(0, 0, 0, 0)
        self.data_visualization_widget = MplWidget()
        self.data_visualization_toolbar = CustomNavigationToolbar(self.data_visualization_widget.canvas, self)
        analysis_layout.addWidget(self.data_visualization_widget)
        analysis_layout.addWidget(self.data_visualization_toolbar)
        top_tab_widget.addTab(analysis_tab, "Analysis")
        
        # Plots tab
        plots_tab = QWidget()
        plots_layout = QHBoxLayout(plots_tab)
        plots_layout.setSpacing(0)
        plots_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_widgets = []
        for i in range(2):
            plot_widget = MplWidget()
            plot_toolbar = CustomNavigationToolbar(plot_widget.canvas, self)
            plot_layout = QVBoxLayout()
            plot_layout.addWidget(plot_widget)
            plot_layout.addWidget(plot_toolbar)
            plots_layout.addLayout(plot_layout)
            self.plot_widgets.append(plot_widget)
        top_tab_widget.addTab(plots_tab, "Plots")
        
        # Bottom splitter for the table, event details, and second plot with navigation
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Widget for the table and event information
        table_and_info_widget = QWidget()
        table_and_info_layout = QVBoxLayout(table_and_info_widget)
        table_and_info_layout.setSpacing(0)
        table_and_info_layout.setContentsMargins(0, 0, 0, 0)
        self.table_widget = QTableWidget()
        self.event_info_text_edit = QTextEdit()
        self.event_info_text_edit.setReadOnly(True)
        table_and_info_layout.addWidget(self.table_widget)
        table_and_info_layout.addWidget(self.event_info_text_edit)
        
        # Widget for the second plot and navigation
        event_plot_and_navigation_widget = QWidget()
        event_plot_and_navigation_layout = QVBoxLayout(event_plot_and_navigation_widget)
        event_plot_and_navigation_layout.setSpacing(0)
        event_plot_and_navigation_layout.setContentsMargins(0, 0, 0, 0)
        self.event_visualization_widget = MplWidget()
        self.event_visualization_toolbar = CustomNavigationToolbar(self.event_visualization_widget.canvas, self)
        event_plot_and_navigation_layout.addWidget(self.event_visualization_widget)
        event_plot_and_navigation_layout.addWidget(self.event_visualization_toolbar)
        self.setupEventNavigationButtons(event_plot_and_navigation_layout)

        # Add widgets to the bottom splitter and set their sizes
        bottom_splitter.addWidget(table_and_info_widget)
        bottom_splitter.addWidget(event_plot_and_navigation_widget)
        bottom_splitter.setSizes([int(self.width() * 0.55), int(self.width() * 0.45)])
        
        # Add top tab widget and bottom splitter to the vertical splitter
        vertical_splitter.addWidget(top_tab_widget)
        vertical_splitter.addWidget(bottom_splitter)
        
        # Set the sizes of the vertical splitter. 
        vertical_splitter.setSizes([int(self.height() * 0.5), int(self.height() * 0.5)])
        
        # Finally, add the vertical splitter to the main layout
        layout.addWidget(vertical_splitter)


    def setupEventNavigationButtons(self, layout):
        # Event navigation buttons (Previous, Next, Jump To)
        event_navigation_layout = QHBoxLayout()
        event_navigation_layout.setSpacing(0)
        event_navigation_layout.setContentsMargins(0, 0, 0, 0)
        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.jump_to_label = QLabel("Jump To (index):")
        self.jump_to_spinbox = QSpinBox()
        self.jump_button = QPushButton("Jump")
        event_navigation_layout.addWidget(self.previous_button)
        event_navigation_layout.addWidget(self.next_button)
        event_navigation_layout.addWidget(self.jump_to_label)
        event_navigation_layout.addWidget(self.jump_to_spinbox)
        event_navigation_layout.addWidget(self.jump_button)
        layout.addLayout(event_navigation_layout)
        self.previous_button.clicked.connect(self.navigate_to_previous_event)
        self.next_button.clicked.connect(self.navigate_to_next_event)
        self.jump_button.clicked.connect(self.jump_to_event)

        # Create a new QHBoxLayout for the additional buttons
        additional_buttons_layout = QHBoxLayout()

        self.refit_button = QPushButton("Refit Event")
        self.fitting_options_button = QPushButton("Fitting Options")
        self.save_new_data_button = QPushButton("Save New Data")
        additional_buttons_layout.addWidget(self.refit_button)
        additional_buttons_layout.addWidget(self.fitting_options_button)
        additional_buttons_layout.addWidget(self.save_new_data_button)

        self.refit_button.clicked.connect(self.refit_current_event)
        self.fitting_options_button.clicked.connect(self.open_fitting_options_dialog)
        self.save_new_data_button.clicked.connect(self.save_new_data)

        # Add the additional buttons layout to the main layout
        layout.addLayout(additional_buttons_layout)


    def open_fitting_options_dialog(self):
        self.fitting_options_dialog.padding_spinbox.setValue(self.fitting_settings_tab.padding_spinbox.value())
        self.fitting_options_dialog.chunk_size_for_event_fitting_spinbox.setValue(self.fitting_settings_tab.chunk_size_for_event_fitting_spinbox.value())
        self.fitting_options_dialog.library_combo.setCurrentText(self.fitting_settings_tab.library_combo.currentText())
        self.fitting_options_dialog.model_combo.setCurrentText(self.fitting_settings_tab.model_combo.currentText())
        self.fitting_options_dialog.num_components_spinbox.setValue(self.fitting_settings_tab.num_components_spinbox.value())
        self.fitting_options_dialog.threshold_spinbox.setValue(self.fitting_settings_tab.threshold_spinbox.value())
        self.fitting_options_dialog.segment_rate_threshold_spinbox.setValue(self.fitting_settings_tab.segment_rate_threshold_spinbox.value())
        self.fitting_options_dialog.change_rate_threshold_spinbox.setValue(self.fitting_settings_tab.change_rate_threshold_spinbox.value())
        self.fitting_options_dialog.merge_segment_threshold_spinbox.setValue(self.fitting_settings_tab.merge_segment_threshold_spinbox.value())

        self.fitting_options_dialog.show()

    def save_new_data(self):
        # Ask the user for the file and folder path
        options = QFileDialog.Options()
        options |= QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Modified Data", "", "NumPy Files (*.npz)", options=options)

        if file_path:
            # Save the updated npz_dict with the modified fitted data
            np.savez_compressed(file_path, **self.npz_dict)
            QMessageBox.information(self, "Data Saved", f"The modified fitted data has been saved to {file_path}")

    def refit_current_event(self):
        event_index = self.current_event_index

        # Retrieve the updated fitting settings from the FittingOptionsDialog
        padding = self.fitting_options_dialog.padding_spinbox.value()
        chunk_size_events = self.fitting_options_dialog.chunk_size_for_event_fitting_spinbox.value()
        library = self.fitting_options_dialog.library_combo.currentText()
        model = self.fitting_options_dialog.model_combo.currentText()
        num_components = self.fitting_options_dialog.num_components_spinbox.value()
        penalty = self.fitting_options_dialog.threshold_spinbox.value()
        segment_rate_threshold = self.fitting_options_dialog.segment_rate_threshold_spinbox.value()
        change_of_rate_threshold = self.fitting_options_dialog.change_rate_threshold_spinbox.value()
        merge_close_segments_threshold = self.fitting_options_dialog.merge_segment_threshold_spinbox.value()

        sampling_rate = self.event_settings_tab.sampling_rate_spinbox.value() * 1000
        #print(sampling_rate)

        # Retrieve the event data and settings from npz_dict
        event_data_key = f'EVENT_DATA_{event_index}'
        event_time_start_end = self.npz_dict[f'{event_data_key}_part_2']
        start_index = int(event_time_start_end[0] * sampling_rate)
        end_index = int(event_time_start_end[1] * sampling_rate)

        

        if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
            standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
        else:
            standard = "Normal"
        if self.ml_tab.enable_ml_data_reduction_checkbox.isChecked():
            ML_enabled = "True"
            ML_tag = self.ml_tab.tag_lineedit.text()
            ML_standard = self.ml_tab.data_reduction_type_combo.currentText()
            if self.ml_tab.apply_standardisation_checkbox.isChecked():
                if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                    standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
            else:
                standard = "Normal"
        else:
            ML_enabled = "False"
            ML_standard = None
            ML_tag = None

        if self.event_settings_tab.dips_or_peaks_combo.currentText()=="Dips":
            dips = "Yes"
        else:
            dips = "No"

        ML_standardisation_settings_fitting = {
            'standard': standard,
            'ML_enabled': ML_enabled,
            'ML_standard': ML_standard,
            'standard_power': self.fitting_settings_tab.power_spinbox.value(),
            'standard_length_nm': self.fitting_settings_tab.length_spinbox.value(),
            'standard_conductivity_S_m': self.fitting_settings_tab.conductivity_spinbox.value(),
            'standard_voltage_applied_mV': self.fitting_settings_tab.voltage_spinbox.value(),
            'standard_open_pore_current_nA': self.fitting_settings_tab.open_pore_current_spinbox.value(),
            'sampling_rate': sampling_rate,
            'segment_rate_threshold': segment_rate_threshold,
            'change_of_rate_threshold': change_of_rate_threshold,
            'merge_close_segments_threshold': merge_close_segments_threshold
        }

        # Perform the refitting for the current event using the existing fitting function
        chunk_result = analyze_event_chunk_with_padding([(start_index, end_index)], padding, library, model, num_components, penalty, self.data, dips, ML_standardisation_settings_fitting)

        # Update the npz_dict with the new fitted data for the current event
        for key in list(self.npz_dict.keys()):
            if key.startswith(f'EVENT_DATA_{event_index}') or key.startswith(f'SEGMENT_INFO_{event_index}') or key.startswith(f'EVENT_ANALYSIS_{event_index}'):
                del self.npz_dict[key]

        event_data_formatted = [
            np.array(chunk_result[0]['time_points_padded'], dtype=np.float64),
            np.array(chunk_result[0]['padded_event_data'], dtype=np.float64),
            np.array(chunk_result[0]['event_time_start_end'], dtype=np.float64),
            np.array(chunk_result[0]['mean_values_connected_with_baseline'], dtype=np.float64),
            np.full(len(chunk_result[0]['padded_event_data']), chunk_result[0]['baseline_value'], dtype=np.float64)
        ]

        for i, arr in enumerate(event_data_formatted):
            self.npz_dict[f'EVENT_DATA_{event_index}_part_{i}'] = arr

        segment_info_formatted = {
            'number_of_segments': np.array([chunk_result[0]['segment_info']['number_of_segments']], dtype=np.float64),
            'segment_mean_diffs': np.array(chunk_result[0]['segment_info']['segment_mean_diffs'], dtype=np.float64),
            'segment_widths_time': np.array(chunk_result[0]['segment_info']['segment_widths_time'], dtype=np.float64),
            'event_width': np.array([chunk_result[0]['segment_info']['event_width']], dtype=np.float64),
        }

        for key, value in segment_info_formatted.items():
            self.npz_dict[f'SEGMENT_INFO_{event_index}_{key}'] = value

        event_analysis_array = np.array(chunk_result[0]['event_analysis'], dtype=np.float64)
        self.npz_dict[f'EVENT_ANALYSIS_{event_index}'] = event_analysis_array

        # Update the event plot and table with the new fitted data
        self.plot_event(event_index)
        self.update_event_info_table(event_index)

    def specify_file_name(self):
        # Step 1: Let the user select a directory with a clear instruction in the dialog title
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Save File")
        if folder_path:  # Ensure the user selected a folder
            # Step 2: Prompt the user to specify a file name
            file_name, ok = QInputDialog.getText(self, "Specify File Name", "Enter only the file name (without extension):")
            if ok and file_name:  # Ensure the user entered a file name and pressed OK
                # Combine the folder path and file name to form the full file path
                self.save_file_path = f"{folder_path}/{file_name}"
                
                # Update the QLabel to show the selected folder and file name
                selected_path = f"Selected folder: {folder_path}\nSelected file name: {file_name}"
                self.load_options_tab.selected_path_label.setText(selected_path)
                self.load_options_tab.selected_path_label.setWordWrap(True)
                self.load_options_tab.selected_path_label.setVisible(True)

    
    def on_test_settings_clicked(self):
        start_time = time.time()
        # Get selected items from the list
        selected_items = self.load_options_tab.files_list_widget.selectedItems()
        if selected_items:
            
            # Use only the first selected file
            file_path = selected_items[0].data(Qt.ItemDataRole.UserRole)

            if self.event_settings_tab.enable_window_loading.isChecked():
                if file_path.endswith('.abf'):
                    #Load the sampling rate and length of the file in seconds
                    length_in_seconds,sampling_rate = get_abf_file_info(file_path)
                    # Load data and sampling rate from the file
                    if self.event_settings_tab.enable_nth_data_point_loading.isChecked():
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Icon.Critical)
                        msg.setWindowTitle("Error")
                        msg.setText("An error has occurred.")
                        msg.setInformativeText(f"Loading of nth data point has not yet been implemented. Loading every single point.")
                        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                        msg.exec()
                        step = 1
                    else:
                        step = 1
                    
                    raw_io = AxonRawIO(filename=file_path)
                    raw_io.parse_header()
                    signal_size = raw_io.get_signal_size(block_index=0, seg_index=0)

                    if self.event_settings_tab.apply_filter_combo.currentText() == "Yes":
                        if self.event_settings_tab.filter_type_combo.currentText() == "Wavelet":
                            filter_type = "Wavelet"
                            cutoff_freq = 10000
                        else:
                            filter_type = self.event_settings_tab.low_pass_filter_type_combo.currentText()
                            cutoff_freq = self.event_settings_tab.cutoff_frequency_spinbox.value()*1000
                    if self.event_settings_tab.type_of_threshold_combo.currentText() == "ΔI":
                        threshold_method = "difference"
                    else:
                        threshold_method = "multiplier"
                    if self.event_settings_tab.dips_or_peaks_combo.currentText()=="Dips":
                        dips = "Yes"
                    else:
                        dips = "No"
                    
                    threshold_multiplier, start_multiplier, end_multiplier, threshold_difference =  self.event_settings_tab.threshold_value_multiplier_spinbox.value(),  self.event_settings_tab.start_of_event_threshold_spinbox.value(), self.event_settings_tab.end_of_event_threshold_spinbox.value(), self.event_settings_tab.threshold_value_multiplier_spinbox.value()
                    avg_window_size_in_ms, std_window_size_in_ms = self.event_settings_tab.mean_window_size_spinbox.value(), self.event_settings_tab.std_window_size_spinbox.value()
                    min_event_width, max_event_width = self.event_settings_tab.minimum_event_width_spinbox.value()/1000, self.event_settings_tab.maximum_event_width_spinbox.value()/1000
                    channel_index = 0
                    chunk_size = max(avg_window_size_in_ms,std_window_size_in_ms)*self.event_settings_tab.window_size_multiple_spinbox.value()*sampling_rate

                    start_testing_duration = self.load_options_tab.testing_duration_start_spinbox.value()
                    end_testing_duration = self.load_options_tab.testing_duration_end_spinbox.value()  # in seconds
                    desired_duration = end_testing_duration
                    start_index = int(start_testing_duration * sampling_rate)
                    start_chunk_index = int(start_index // (chunk_size * step))
                    num_chunks = int((signal_size - start_index) // (chunk_size * step)) + (0 if (signal_size - start_index) % (chunk_size * step) == 0 else 1)

                    results = Parallel(n_jobs=-1)(
                        delayed(process_chunk_window_abf_with_data)(file_path, desired_duration, chunk_index, chunk_size, step, channel_index, signal_size, sampling_rate, filter_type, cutoff_freq, threshold_method, dips, threshold_multiplier, start_multiplier, end_multiplier, threshold_difference, avg_window_size_in_ms, std_window_size_in_ms, min_event_width, max_event_width, start_index)
                        for chunk_index in range(start_chunk_index, start_chunk_index + num_chunks)
                    )

                   # Unzip the results
                    chunk_events, chunk_rolling_avgs, chunk_rolling_stds, chunk_data = zip(*results)

                    # After the parallel processing loop
                    combined_events = [event for chunk_events_tuple in chunk_events for event in chunk_events_tuple]
                    rolling_avg_refined = np.concatenate(chunk_rolling_avgs)
                    rolling_std_refined = np.concatenate(chunk_rolling_stds)
                    data = np.concatenate(chunk_data)

                    # Adjust event indices based on their chunk offsets and filter out those crossing chunk boundaries
                    adjusted_events = []
                    for chunk_index, chunk_events_tuple in enumerate(chunk_events):
                        chunk_start_index = chunk_index * chunk_size * step
                        for event in chunk_events_tuple:
                            start, end = event
                            if start + chunk_start_index < (chunk_index + 1) * chunk_size * step and end + chunk_start_index <= min((chunk_index + 1) * chunk_size * step, signal_size):
                                adjusted_events.append((start + chunk_start_index, end + chunk_start_index))

                    if threshold_method == "multiplier":
                        if dips == "Yes":
                            rolling_threshold_refined = rolling_avg_refined - (threshold_multiplier * rolling_std_refined)
                        else:
                            rolling_threshold_refined = rolling_avg_refined + (threshold_multiplier * rolling_std_refined)
                    elif threshold_method == "difference":
                        if dips == "Yes":
                            rolling_threshold_refined = rolling_avg_refined - (threshold_difference / 1000)
                        else:
                            rolling_threshold_refined = rolling_avg_refined + (threshold_difference / 1000)

                    if self.event_settings_tab.enable_std_smoothing_checkbox.isChecked():
                        rolling_threshold_refined = smooth_threshold(rolling_threshold_refined,int((std_window_size_in_ms / 1000) * sampling_rate),self.event_settings_tab.smoothing_type_dropdown.currentIndex())
                    
                    events = adjusted_events
                    end_time = time.time()
                    time_taken = end_time-start_time

                elif  file_path.endswith('.hdf5') or file_path.endswith('.h5'):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Critical)
                    msg.setWindowTitle("Error")
                    msg.setText("An error has occurred.")
                    msg.setInformativeText(f"Loading of hdf5 files has not yet been implemented with window processing. Please use the normal processing methods.")
                    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg.exec()
                    
            else:
                if file_path.endswith('.abf'):
                    #Load the sampling rate and length of the file in seconds
                    length_in_seconds,sampling_rate = get_abf_file_info(file_path)
                    # Load data and sampling rate from the file
                    if self.event_settings_tab.enable_nth_data_point_loading.isChecked():
                        data, sampling_rate = load_abf_file_nth(file_path,self.event_settings_tab.nth_data_point_spinbox.value())
                    else:
                        data, sampling_rate = load_abf_file(file_path)
                elif  file_path.endswith('.hdf5') or file_path.endswith('.h5'):
                    data,sampling_rate = load_hdf5_file(file_path)
                    length_in_seconds = len(data)/sampling_rate
                         
                if data is not None:
                    
                    # Determine the number of points to plot based on the testing duration
                    # This can be removed in main function
                    start_testing_duration = self.load_options_tab.testing_duration_start_spinbox.value()
                    end_testing_duration = self.load_options_tab.testing_duration_end_spinbox.value()  # in seconds
                    start_points = int(start_testing_duration * sampling_rate)
                    end_points = int(end_testing_duration * sampling_rate)
                    # Take the slice of data 
                    data = data[start_points:end_points]

                    # Update the EventSettingsTab with the sampling rate and file duration
                    self.event_settings_tab.sampling_rate_spinbox.setValue(sampling_rate / 1000)  # Convert to kHz
                    self.event_settings_tab.analysis_end_duration_spinbox.setValue(length_in_seconds)
                    self.event_settings_tab.analysis_end_duration_spinbox.setMaximum(length_in_seconds)
                    self.load_options_tab.testing_duration_end_spinbox.setMaximum(length_in_seconds)

                    if self.event_settings_tab.apply_filter_combo.currentText() == "Yes":
                        if self.event_settings_tab.filter_type_combo.currentText() == "Wavelet":
                            data = apply_low_pass_filter(data, 10000, "Wavelet",sampling_rate)
                        else:
                            data = apply_low_pass_filter(data, self.event_settings_tab.cutoff_frequency_spinbox.value()*1000, self.event_settings_tab.low_pass_filter_type_combo.currentText(),sampling_rate)
                    if self.event_settings_tab.type_of_threshold_combo.currentText() == "ΔI":
                        threshold_method = "difference"
                    else:
                        threshold_method = "multiplier"
                    if self.event_settings_tab.dips_or_peaks_combo.currentText()=="Dips":
                        dips = "Yes"
                        dips_for_writing = "Yes"
                    else:
                        dips = "Yes"
                        dips_for_writing = "No"
                        data_sent = ne.evaluate("data*(-1)")
                    if self.event_settings_tab.enable_std_smoothing_checkbox.isChecked():
                        enable_smoothing = "Yes"
                    else:
                        enable_smoothing = "No"
                    
                    self.data = data
                    
                    try:
                        if self.event_settings_tab.dips_or_peaks_combo.currentText()=="Dips":
                            events,rolling_avg_refined, rolling_threshold_refined = find_events_refined_parallel(data, self.event_settings_tab.threshold_value_multiplier_spinbox.value(), self.event_settings_tab.start_of_event_threshold_spinbox.value(), self.event_settings_tab.end_of_event_threshold_spinbox.value(), self.event_settings_tab.threshold_value_multiplier_spinbox.value(), self.event_settings_tab.mean_window_size_spinbox.value(), self.event_settings_tab.std_window_size_spinbox.value(), threshold_method, self.event_settings_tab.minimum_event_width_spinbox.value()/1000, self.event_settings_tab.maximum_event_width_spinbox.value()/1000, self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(), dips, sampling_rate, enable_smoothing, self.event_settings_tab.smoothing_type_dropdown.currentIndex(),self.event_settings_tab.std_calculation_method_combo.currentText(), n_jobs = -1)
                        else:
                            events,rolling_avg_refined, rolling_threshold_refined = find_events_refined_parallel(data_sent, self.event_settings_tab.threshold_value_multiplier_spinbox.value(), self.event_settings_tab.start_of_event_threshold_spinbox.value(), self.event_settings_tab.end_of_event_threshold_spinbox.value(), self.event_settings_tab.threshold_value_multiplier_spinbox.value(), self.event_settings_tab.mean_window_size_spinbox.value(), self.event_settings_tab.std_window_size_spinbox.value(), threshold_method, self.event_settings_tab.minimum_event_width_spinbox.value()/1000, self.event_settings_tab.maximum_event_width_spinbox.value()/1000, self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(), dips, sampling_rate, enable_smoothing, self.event_settings_tab.smoothing_type_dropdown.currentIndex(), self.event_settings_tab.std_calculation_method_combo.currentText(),n_jobs = -1)
                        end_time = time.time()
                        time_taken = end_time-start_time

                        if self.event_settings_tab.dips_or_peaks_combo.currentText()!="Dips":
                            rolling_avg_refined, rolling_threshold_refined = ne.evaluate("rolling_avg_refined*-1"), ne.evaluate("rolling_threshold_refined *-1")
                    except:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Icon.Critical)
                        msg.setWindowTitle("Error")
                        msg.setText("An error has occurred.")
                        msg.setInformativeText(f"I cannot extract any events from the selected file ({file_path}) within the selected duration. \nContact shankar.dutt@anu.edu.au")
                        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                        msg.exec()

            if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
            else:
                standard = "Normal"
            if self.ml_tab.enable_ml_data_reduction_checkbox.isChecked():
                ML_enabled = "True"
                ML_tag = self.ml_tab.tag_lineedit.text()
                ML_standard = self.ml_tab.data_reduction_type_combo.currentText()
                if self.ml_tab.apply_standardisation_checkbox.isChecked():
                    if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                        standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
                else:
                    standard = "Normal"
            else:
                ML_enabled = "False"
                ML_standard = None
                ML_tag = None
            
            settings = {
                    "file_name": file_path,
                    "sampling_rate": sampling_rate,
                    "start_testing_duration": start_testing_duration,
                    "end_testing_duration": end_testing_duration,
                    "threshold_method": threshold_method,
                    "dips": dips_for_writing,
                    "low_pass_filter_applied": self.event_settings_tab.apply_filter_combo.currentText(),
                    "low_pass_filter_cutoff": self.event_settings_tab.cutoff_frequency_spinbox.value() * 1000,
                    "low_pass_filter_type": self.event_settings_tab.low_pass_filter_type_combo.currentText(),
                    "threshold_value_multiplier": self.event_settings_tab.threshold_value_multiplier_spinbox.value(),
                    "start_of_event_threshold": self.event_settings_tab.start_of_event_threshold_spinbox.value(),
                    "end_of_event_threshold": self.event_settings_tab.end_of_event_threshold_spinbox.value(),
                    "mean_window_size": self.event_settings_tab.mean_window_size_spinbox.value(),
                    "std_window_size": self.event_settings_tab.std_window_size_spinbox.value(),
                    "minimum_event_width": self.event_settings_tab.minimum_event_width_spinbox.value() / 1000,
                    "maximum_event_width": self.event_settings_tab.maximum_event_width_spinbox.value() / 1000,
                    "chunk_size_for_event_detection": self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(),
                    "standard": standard,
                    "ML_enabled": ML_enabled,
                    "ML_tag": ML_tag,
                    "ML_standard": ML_standard,
                    'standard_power' : self.fitting_settings_tab.power_spinbox.value(),
                    'standard_length_nm' : self.fitting_settings_tab.length_spinbox.value(),
                    'standard_conductivity_S_m' : self.fitting_settings_tab.conductivity_spinbox.value(),
                    'standard_voltage_applied_mV' : self.fitting_settings_tab.voltage_spinbox.value(),
                    'standard_open_pore_current_nA' : self.fitting_settings_tab.open_pore_current_spinbox.value()
                }

            # Update information
            duration_tested = end_testing_duration - start_testing_duration
            self.update_file_info(file_path, length_in_seconds, len(events), time_taken, file_path, duration_tested, settings, test = "True")
            # Plot the data
            self.plot_events(events, data, rolling_avg_refined, rolling_threshold_refined, sampling_rate)
            # Event Fitting
            if self.load_options_tab.level_fitting_combo.currentText() == "Yes":

                if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                    standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
                else:
                    standard = "Normal"
                if self.ml_tab.enable_ml_data_reduction_checkbox.isChecked():
                    ML_enabled = "True"
                    ML_tag = self.ml_tab.tag_lineedit.text()
                    ML_standard = self.ml_tab.data_reduction_type_combo.currentText()
                    if self.ml_tab.apply_standardisation_checkbox.isChecked():
                        if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                            standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
                    else:
                        standard = "Normal"
                else:
                    ML_enabled = "False"
                    ML_standard = None
                    ML_tag = None

                ML_standardisation_settings = {
                    'standard' : standard,
                    'ML_enabled' : ML_enabled,
                    'ML_standard' : ML_standard,
                    'standard_power' : self.fitting_settings_tab.power_spinbox.value(),
                    'standard_length_nm' : self.fitting_settings_tab.length_spinbox.value(),
                    'standard_conductivity_S_m' : self.fitting_settings_tab.conductivity_spinbox.value(),
                    'standard_voltage_applied_mV' : self.fitting_settings_tab.voltage_spinbox.value(),
                    'standard_open_pore_current_nA' : self.fitting_settings_tab.open_pore_current_spinbox.value(),
                    'sampling_rate' : sampling_rate,
                    'segment_rate_threshold' : self.fitting_settings_tab.segment_rate_threshold_spinbox.value(),
                    'change_of_rate_threshold': self.fitting_settings_tab.change_rate_threshold_spinbox.value(),
                    'merge_close_segments_threshold': self.fitting_settings_tab.merge_segment_threshold_spinbox.value()
                }

                if self.event_settings_tab.dips_or_peaks_combo.currentText()=="Dips":
                    self.npz_dict, event_analysis_array = multi_level_fitting_events(self.fitting_settings_tab.padding_spinbox.value(), self.fitting_settings_tab.chunk_size_for_event_fitting_spinbox.value(),self.fitting_settings_tab.library_combo.currentText(),self.fitting_settings_tab.model_combo.currentText(),self.fitting_settings_tab.num_components_spinbox.value(), self.fitting_settings_tab.threshold_spinbox.value(), data, events, dips,ML_standardisation_settings)
                else:
                    self.npz_dict, event_analysis_array = multi_level_fitting_events(self.fitting_settings_tab.padding_spinbox.value(), self.fitting_settings_tab.chunk_size_for_event_fitting_spinbox.value(),self.fitting_settings_tab.library_combo.currentText(),self.fitting_settings_tab.model_combo.currentText(),self.fitting_settings_tab.num_components_spinbox.value(), self.fitting_settings_tab.threshold_spinbox.value(), data_sent, events, dips,ML_standardisation_settings)
                X =[np.array(sublist, dtype=np.float64) for sublist in event_analysis_array]
                if len(self.npz_dict)>10:
                    self.total_events = len(self.npz_dict) // 10  
                    self.jump_to_spinbox.setMaximum(self.total_events - 1)
                    self.jump_to_spinbox.setValue(0)
                    self.current_event_index = 0
                    self.plot_event(0)
                    self.update_event_info_table(0)


    def process_single_file_multi_threshold(self,file_path, threshold_type, threshold_value):
        start_time = time.time()
        if file_path.endswith('.abf'):
            #Load the sampling rate and length of the file in seconds
            length_in_seconds,sampling_rate = get_abf_file_info(file_path)
            if self.event_settings_tab.enable_nth_data_point_loading.isChecked():
                data, sampling_rate = load_abf_file_nth(file_path,self.event_settings_tab.nth_data_point_spinbox.value())
            else:
                data, sampling_rate = load_abf_file(file_path)
        elif file_path.endswith('.hdf5') or file_path.endswith('.h5'):
            data,sampling_rate = load_hdf5_file(file_path)
            length_in_seconds = len(data)/sampling_rate

        if data is not None:
            if self.event_settings_tab.analysis_start_duration_spinbox.value() > 0:
                if self.event_settings_tab.enable_analysis_time_specific.isChecked():
                    start_testing_duration = self.event_settings_tab.analysis_start_duration_spinbox.value()
                    start_points = int(start_testing_duration * sampling_rate)
                else:
                    start_testing_duration = 0
                    start_points = 0
            else:
                start_testing_duration = 0
                start_points = 0
            if self.event_settings_tab.analysis_end_duration_spinbox.value() > 0:
                if self.event_settings_tab.enable_analysis_time_specific.isChecked():
                    end_testing_duration = self.event_settings_tab.analysis_end_duration_spinbox.value()
                    end_points = int(end_testing_duration * sampling_rate)
                else:
                    end_testing_duration = length_in_seconds
                    end_points = int(end_testing_duration * sampling_rate)
            else:
                end_points = int(length_in_seconds * sampling_rate)
                end_testing_duration = length_in_seconds

            # Take the slice of data 
            data = data[start_points:end_points]

            #Update the EventSettingsTab with the sampling rate and file duration
            self.event_settings_tab.sampling_rate_spinbox.setValue(sampling_rate / 1000)  # Convert to kHz
            self.event_settings_tab.analysis_end_duration_spinbox.setMaximum(length_in_seconds)
            self.load_options_tab.testing_duration_end_spinbox.setMaximum(length_in_seconds)
            file_duration = length_in_seconds

            if self.event_settings_tab.apply_filter_combo.currentText() == "Yes":
                if self.event_settings_tab.filter_type_combo.currentText() == "Wavelet":
                    data = apply_low_pass_filter(data, 10000, "Wavelet",sampling_rate)
                else:
                    data = apply_low_pass_filter(data, self.event_settings_tab.cutoff_frequency_spinbox.value()*1000, self.event_settings_tab.low_pass_filter_type_combo.currentText(),sampling_rate)
            if self.event_settings_tab.type_of_threshold_combo.currentText() == "ΔI":
                threshold_method = "difference"
            else:
                threshold_method = "multiplier"
            if self.event_settings_tab.dips_or_peaks_combo.currentText()=="Dips":
                dips = "Yes"
            else:
                dips = "Yes"
                data = ne.evaluate("data*(-1)")
            if self.event_settings_tab.enable_std_smoothing_checkbox.isChecked():
                enable_smoothing = "Yes"
            else:
                enable_smoothing = "No"
            try:
                self.data = data
                # events,rolling_avg_refined, rolling_threshold_refined = find_events_refined_parallel(data, self.event_settings_tab.threshold_value_multiplier_spinbox.value(), self.event_settings_tab.start_of_event_threshold_spinbox.value(), self.event_settings_tab.end_of_event_threshold_spinbox.value(), self.event_settings_tab.threshold_value_multiplier_spinbox.value(), self.event_settings_tab.mean_window_size_spinbox.value(), self.event_settings_tab.std_window_size_spinbox.value(), threshold_method, self.event_settings_tab.minimum_event_width_spinbox.value()/1000, self.event_settings_tab.maximum_event_width_spinbox.value()/1000, self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(), dips, sampling_rate, enable_smoothing, self.event_settings_tab.smoothing_type_dropdown.currentIndex(), n_jobs = -1)

                if threshold_type == "std multiplier":
                    events, rolling_avg_refined, rolling_threshold_refined = find_events_refined_parallel(
                        data, threshold_value, self.event_settings_tab.start_of_event_threshold_spinbox.value(),
                        self.event_settings_tab.end_of_event_threshold_spinbox.value(), threshold_value,
                        self.event_settings_tab.mean_window_size_spinbox.value(),
                        self.event_settings_tab.std_window_size_spinbox.value(), "multiplier",
                        self.event_settings_tab.minimum_event_width_spinbox.value() / 1000,
                        self.event_settings_tab.maximum_event_width_spinbox.value() / 1000,
                        self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(),
                        dips, sampling_rate, enable_smoothing, self.event_settings_tab.smoothing_type_dropdown.currentIndex(),self.event_settings_tab.std_calculation_method_combo.currentText(),
                        n_jobs=-1
                    )
                else:  # difference
                    events, rolling_avg_refined, rolling_threshold_refined = find_events_refined_parallel(
                        data, threshold_value, self.event_settings_tab.start_of_event_threshold_spinbox.value(),
                        self.event_settings_tab.end_of_event_threshold_spinbox.value(), threshold_value,
                        self.event_settings_tab.mean_window_size_spinbox.value(),
                        self.event_settings_tab.std_window_size_spinbox.value(), "difference",
                        self.event_settings_tab.minimum_event_width_spinbox.value() / 1000,
                        self.event_settings_tab.maximum_event_width_spinbox.value() / 1000,
                        self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(),
                        dips, sampling_rate, enable_smoothing, self.event_settings_tab.smoothing_type_dropdown.currentIndex(),self.event_settings_tab.std_calculation_method_combo.currentText(),
                        n_jobs=-1
                    )
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Error")
                msg.setText("An error has occurred.")
                msg.setInformativeText(f"I cannot extract any events from the selected file ({file_path}). Change your settings or \nContact shankar.dutt@anu.edu.au")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
            
            if len(events)<1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("No Events Detected!")
                msg.setText("No Events Detected!")
                msg.setInformativeText(f"I cannot extract any events from the selected file ({file_path}). Change your settings or \nContact shankar.dutt@anu.edu.au")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
            else:               
                if self.load_options_tab.save_event_chk.isChecked():
                    # Organize the event information
                    event_info = {
                        'sampling_rate': sampling_rate,
                        'events': [],
                    }

                    for idx, (start, end) in enumerate(events):
                        event_data = data[start:end]
                        event_baseline = rolling_avg_refined[start:end]
                        event_info_data = {
                            'event_id': idx,
                            'start_time': start / sampling_rate,
                            'end_time': end / sampling_rate,
                            'event_data': event_data-event_baseline,
                            'baseline_value': np.mean(event_baseline)
                        }
                        event_info['events'].append(event_info_data)

                    date_time_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                    if self.save_file_path is not None:
                        np.savez_compressed(self.save_file_path + '_' + str(np.round(threshold_value,2))+ '_' + date_time_str + '.event_data', 
                                            sampling_rate=event_info['sampling_rate'],
                                            events=event_info['events'])
                                            
                    else:
                        file_path, _ = os.path.splitext(file_path)
                        np.savez_compressed(file_path + '_' + str(np.round(threshold_value,2)) + '_' + date_time_str + '.event_data',
                                            sampling_rate=event_info['sampling_rate'],
                                            events=event_info['events'])
                                            
                    
                if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                    standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
                else:
                    standard = "Normal"
                if self.ml_tab.enable_ml_data_reduction_checkbox.isChecked():
                    ML_enabled = "True"
                    ML_tag = self.ml_tab.tag_lineedit.text()
                    ML_standard = self.ml_tab.data_reduction_type_combo.currentText()
                    if self.ml_tab.apply_standardisation_checkbox.isChecked():
                        if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                            standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
                    else:
                        standard = "Normal"
                else:
                    ML_enabled = "False"
                    ML_standard = None
                    ML_tag = None

                ML_standardisation_settings = {
                    'standard' : standard,
                    'ML_enabled' : ML_enabled,
                    'ML_standard' : ML_standard,
                    'standard_power' : self.fitting_settings_tab.power_spinbox.value(),
                    'standard_length_nm' : self.fitting_settings_tab.length_spinbox.value(),
                    'standard_conductivity_S_m' : self.fitting_settings_tab.conductivity_spinbox.value(),
                    'standard_voltage_applied_mV' : self.fitting_settings_tab.voltage_spinbox.value(),
                    'standard_open_pore_current_nA' : self.fitting_settings_tab.open_pore_current_spinbox.value(),
                    'sampling_rate' : sampling_rate,
                    'segment_rate_threshold' : self.fitting_settings_tab.segment_rate_threshold_spinbox.value(),
                    'change_of_rate_threshold':self.fitting_settings_tab.change_rate_threshold_spinbox.value(),
                    'merge_close_segments_threshold': self.fitting_settings_tab.merge_segment_threshold_spinbox.value()
                }

                settings = {
                    "file_name": file_path,
                    "sampling_rate": sampling_rate,
                    "start_testing_duration": start_testing_duration,
                    "end_testing_duration": end_testing_duration,
                    "threshold_method": threshold_method,
                    "dips": dips,
                    "low_pass_filter_applied": self.event_settings_tab.apply_filter_combo.currentText(),
                    "low_pass_filter_cutoff": self.event_settings_tab.cutoff_frequency_spinbox.value() * 1000,
                    "low_pass_filter_type": self.event_settings_tab.low_pass_filter_type_combo.currentText(),
                    "threshold_value_multiplier": self.event_settings_tab.threshold_value_multiplier_spinbox.value(),
                    "start_of_event_threshold": self.event_settings_tab.start_of_event_threshold_spinbox.value(),
                    "end_of_event_threshold": self.event_settings_tab.end_of_event_threshold_spinbox.value(),
                    "mean_window_size": self.event_settings_tab.mean_window_size_spinbox.value(),
                    "std_window_size": self.event_settings_tab.std_window_size_spinbox.value(),
                    "minimum_event_width": self.event_settings_tab.minimum_event_width_spinbox.value() / 1000,
                    "maximum_event_width": self.event_settings_tab.maximum_event_width_spinbox.value() / 1000,
                    "chunk_size_for_event_detection": self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(),
                    "standard": standard,
                    "ML_enabled": ML_enabled,
                    "ML_tag": ML_tag,
                    "ML_standard": ML_standard,
                    'standard_power' : self.fitting_settings_tab.power_spinbox.value(),
                    'standard_length_nm' : self.fitting_settings_tab.length_spinbox.value(),
                    'standard_conductivity_S_m' : self.fitting_settings_tab.conductivity_spinbox.value(),
                    'standard_voltage_applied_mV' : self.fitting_settings_tab.voltage_spinbox.value(),
                    'standard_open_pore_current_nA' : self.fitting_settings_tab.open_pore_current_spinbox.value()
                }

                # Serialize the settings dictionary to a JSON string
                settings = json.dumps(settings)

                # Event Fitting
                if self.load_options_tab.level_fitting_combo.currentText() == "Yes":   
                    self.npz_dict, event_analysis_array = multi_level_fitting_events(self.fitting_settings_tab.padding_spinbox.value(), self.fitting_settings_tab.chunk_size_for_event_fitting_spinbox.value(),self.fitting_settings_tab.library_combo.currentText(),self.fitting_settings_tab.model_combo.currentText(),self.fitting_settings_tab.num_components_spinbox.value(), self.fitting_settings_tab.threshold_spinbox.value(), data, events, dips, ML_standardisation_settings)
                    X =[np.array(sublist, dtype=np.float64) for sublist in event_analysis_array]
                    end_time = time.time()
                    time_taken = end_time-start_time

                    # Update information
                    if len(self.npz_dict)>10:
                        date_time_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                        if self.save_file_path is not None:
                            file_123 = self.save_file_path+'_'+date_time_str
                            np.savez_compressed(self.save_file_path+ '_' + str(np.round(threshold_value,2))+'_'+date_time_str+'.event_fitting', **self.npz_dict)
                            if ML_enabled == "True":
                                np.savez_compressed(self.save_file_path+ '_' + str(np.round(threshold_value,2))+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                            else:
                                np.savez_compressed(self.save_file_path+ '_' + str(np.round(threshold_value,2))+'_'+date_time_str+'.dataset', settings=settings, X=X)
                        else:
                            file_path, _ = os.path.splitext(file_path)
                            file_123 = file_path+'_'+date_time_str
                            np.savez_compressed(file_path+ '_' + str(np.round(threshold_value,2))+'_'+date_time_str+'.event_fitting', **self.npz_dict)
                            if ML_enabled == "True":
                                np.savez_compressed(file_path+ '_' + str(np.round(threshold_value,2))+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                            else:
                                np.savez_compressed(file_path+ '_' + str(np.round(threshold_value,2))+'_'+date_time_str+'.dataset', settings=settings, X=X)
                        
                        duration_tested = end_testing_duration - start_testing_duration
                        self.update_file_info(file_path, file_duration, len(events),time_taken, file_123, duration_tested, settings, test = "False")
                        self.total_events = len(self.npz_dict) // 10  # Assuming 10 parts per event
                        self.jump_to_spinbox.setMaximum(self.total_events - 1)
                        self.jump_to_spinbox.setValue(0)
                        self.current_event_index = 0
                        self.plot_event(0)
                        self.update_event_info_table(0)
                        
                else:
                    self.npz_dict = [ ]
                    X = save_chunked_event_analysis_to_npz(self.fitting_settings_tab.chunk_size_for_peak_fitting_spinbox.value(),data,events, rolling_avg_refined, sampling_rate, ML_standardisation_settings)
                    date_time_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                    if self.save_file_path is not None:
                        file_123 = self.save_file_path+'_'+date_time_str
                        if ML_enabled == "True":
                            np.savez_compressed(self.save_file_path+ '_' + str(np.round(threshold_value,2))+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                        else:
                            np.savez_compressed(self.save_file_path+ '_' + str(np.round(threshold_value,2))+'_'+date_time_str+'.dataset', settings=settings, X=X)
                    else:
                        file_path, _ = os.path.splitext(file_path)
                        file_123 = file_path+'_'+date_time_str
                        if ML_enabled == "True":
                            np.savez_compressed(file_path+ '_' + str(np.round(threshold_value,2))+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                        else:
                            np.savez_compressed(file_path+ '_' + str(np.round(threshold_value,2))+'_'+date_time_str+'.dataset', settings=settings, X=X)
                    self.jump_to_spinbox.setMaximum(0)
                    self.jump_to_spinbox.setValue(0)
                    self.current_event_index = 0
                    end_time = time.time()
                    time_taken = end_time-start_time
                    # Update information
                    duration_tested = end_testing_duration - start_testing_duration
                    self.update_file_info(file_path, file_duration, len(events),time_taken, file_123, duration_tested, settings, test = "False")

                if self.event_settings_tab.enable_plots.isChecked():
                    # Assuming X is already defined and populated with your event data as described
                    
                    if ML_enabled == "False":
                        dI = np.array([x[0] for x in X]) 
                        dt = np.array([x[4] for x in X])*1e3 
                    else:
                        if ML_standard == "Scheme 2" or ML_standard == "Scheme 3":
                            dI = np.array([x[11] for x in X])  
                            dt = np.array([x[15] for x in X])*1e3 
                        elif ML_standard == "Scheme 4":
                            dI = np.array([x[51] for x in X]) 
                            dt = np.array([x[55] for x in X])*1e3  
                        else:
                            dI = np.array([x[0] for x in X]) 
                            dt = np.array([x[4] for x in X])*1e3 

                    if ML_standard == "Scheme 1" or ML_standard == "Scheme 2" or ML_standard == "Scheme 3" or ML_enabled == "False":

                        dt =  dt[~np.isnan(dI)]
                        dI =  dI[~np.isnan(dI)]
                        

                        # Plotting the histogram of dI on the first canvas
                        self.plot_widgets[0].canvas.axes.clear()  # Clear existing plot
                        self.plot_widgets[0].canvas.axes.hist(dI, bins=100, color='blue', alpha=0.7)  # Adjust 'bins' as necessary
                        self.plot_widgets[0].canvas.axes.set_title(f'Histogram of dI | Counts:{len(dI)} | Threshold: {np.round(threshold_value,2)}')
                        self.plot_widgets[0].canvas.axes.set_xlabel('dI (nA)')
                        self.plot_widgets[0].canvas.axes.set_ylabel('Frequency')
                        self.plot_widgets[0].canvas.draw()  # Redraw the canvas

                        # Save the histogram plot
                        date_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        plot_title = f'Histogram of dI | Counts:{len(dI)} | Threshold: {np.round(threshold_value,2)}'
                        if self.save_file_path is not None:
                            filename = f"{self.save_file_path}_dI_{str(np.round(threshold_value,2))}_{date_time_str}.png"
                        else:
                            file_path, _ = os.path.splitext(file_path)
                            filename = f"{file_path}_dI_{str(np.round(threshold_value,2))}_{date_time_str}.png"
                        self.plot_widgets[0].canvas.figure.savefig(filename, dpi=300, transparent=True)

                        # Plotting the scatter plot of dI vs log(dt*1e3) on the second canvas
                        #log_dt = np.log(np.array(dt) * 1e3)  # Calculate the logarithm of dt*1e3
                        log_dt = np.log(dt)  # Calculate the logarithm of dt*1e3
                        self.plot_widgets[1].canvas.axes.clear()
                        self.plot_widgets[1].canvas.axes.scatter(log_dt, dI, color='red', alpha=0.5, s = 2)  # Plot dI vs. log(dt*1e3)
                        self.plot_widgets[1].canvas.axes.set_title('Scatter Plot of ΔI vs. log(Δt*1e3)| Threshold: {np.round(threshold_value,2)}')
                        self.plot_widgets[1].canvas.axes.set_ylabel('ΔI (nA)')
                        self.plot_widgets[1].canvas.axes.set_xlabel('log(Δt (ms))')
                        self.plot_widgets[1].canvas.draw()  
                        # Save the scatter plot
                        plot_title = 'Scatter_Plot_of_dI_vs_log_dt_{str(np.round(threshold_value,2))'
                        if self.save_file_path is not None:
                            filename = f"{self.save_file_path}_{plot_title}_{date_time_str}.png"
                        else:
                            file_path, _ = os.path.splitext(file_path)
                            filename = f"{file_path}_{plot_title}_{date_time_str}.png"
                        self.plot_widgets[1].canvas.figure.savefig(filename, dpi=300, transparent=True)

                    # Store the data for each threshold
                    if not hasattr(self, 'dI_data'):
                        self.dI_data = []
                        self.log_dt_data = []
                    self.dI_data.append(dI)
                    self.log_dt_data.append(np.log(dt))

                    # Store the threshold value
                    if not hasattr(self, 'std_values'):
                        self.std_values = []
                    self.std_values.append(threshold_value)
                    
        return events 


    def process_single_file(self,file_path):
        start_time = time.time()
        if file_path.endswith('.abf'):
            #Load the sampling rate and length of the file in seconds
            length_in_seconds,sampling_rate = get_abf_file_info(file_path)
            if self.event_settings_tab.enable_nth_data_point_loading.isChecked():
                data, sampling_rate = load_abf_file_nth(file_path,self.event_settings_tab.nth_data_point_spinbox.value())
            else:
                data, sampling_rate = load_abf_file(file_path)
        elif file_path.endswith('.hdf5') or file_path.endswith('.h5'):
            data,sampling_rate = load_hdf5_file(file_path)
            length_in_seconds = len(data)/sampling_rate

        if data is not None:
            if self.event_settings_tab.analysis_start_duration_spinbox.value() > 0:
                if self.event_settings_tab.enable_analysis_time_specific.isChecked():
                    start_testing_duration = self.event_settings_tab.analysis_start_duration_spinbox.value()
                    start_points = int(start_testing_duration * sampling_rate)
                else:
                    start_testing_duration = 0
                    start_points = 0
            else:
                start_testing_duration = 0
                start_points = 0
            if self.event_settings_tab.analysis_end_duration_spinbox.value() > 0:
                if self.event_settings_tab.enable_analysis_time_specific.isChecked():
                    end_testing_duration = self.event_settings_tab.analysis_end_duration_spinbox.value()
                    end_points = int(end_testing_duration * sampling_rate)
                else:
                    end_testing_duration = length_in_seconds
                    end_points = int(end_testing_duration * sampling_rate)
            else:
                end_points = int(length_in_seconds * sampling_rate)
                end_testing_duration = length_in_seconds

            # Take the slice of data 
            data = data[start_points:end_points]

            #Update the EventSettingsTab with the sampling rate and file duration
            self.event_settings_tab.sampling_rate_spinbox.setValue(sampling_rate / 1000)  # Convert to kHz
            self.event_settings_tab.analysis_end_duration_spinbox.setMaximum(length_in_seconds)
            self.load_options_tab.testing_duration_end_spinbox.setMaximum(length_in_seconds)
            file_duration = length_in_seconds

            if self.event_settings_tab.apply_filter_combo.currentText() == "Yes":
                if self.event_settings_tab.filter_type_combo.currentText() == "Wavelet":
                    data = apply_low_pass_filter(data, 10000, "Wavelet",sampling_rate)
                else:
                    data = apply_low_pass_filter(data, self.event_settings_tab.cutoff_frequency_spinbox.value()*1000, self.event_settings_tab.low_pass_filter_type_combo.currentText(),sampling_rate)
            if self.event_settings_tab.type_of_threshold_combo.currentText() == "ΔI":
                threshold_method = "difference"
            else:
                threshold_method = "multiplier"
            if self.event_settings_tab.dips_or_peaks_combo.currentText()=="Dips":
                dips = "Yes"
            else:
                #dips = "No"
                dips = "Yes"
                data = ne.evaluate("data*(-1)")
            if self.event_settings_tab.enable_std_smoothing_checkbox.isChecked():
                enable_smoothing = "Yes"
            else:
                enable_smoothing = "No"
            try:
                self.data = data
                events,rolling_avg_refined, rolling_threshold_refined = find_events_refined_parallel(data, self.event_settings_tab.threshold_value_multiplier_spinbox.value(), self.event_settings_tab.start_of_event_threshold_spinbox.value(), self.event_settings_tab.end_of_event_threshold_spinbox.value(), self.event_settings_tab.threshold_value_multiplier_spinbox.value(), self.event_settings_tab.mean_window_size_spinbox.value(), self.event_settings_tab.std_window_size_spinbox.value(), threshold_method, self.event_settings_tab.minimum_event_width_spinbox.value()/1000, self.event_settings_tab.maximum_event_width_spinbox.value()/1000, self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(), dips, sampling_rate, enable_smoothing, self.event_settings_tab.smoothing_type_dropdown.currentIndex(),self.event_settings_tab.std_calculation_method_combo.currentText(), n_jobs = -1)
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Error")
                msg.setText("An error has occurred.")
                msg.setInformativeText(f"I cannot extract any events from the selected file ({file_path}). Change your settings or \nContact shankar.dutt@anu.edu.au")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
            
            if len(events)<1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("No Events Detected!")
                msg.setText("No Events Detected!")
                msg.setInformativeText(f"I cannot extract any events from the selected file ({file_path}). Change your settings or \nContact shankar.dutt@anu.edu.au")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
            else:               
                if self.load_options_tab.save_event_chk.isChecked():
                    # Organize the event information
                    event_info = {
                        'sampling_rate': sampling_rate,
                        'events': [],
                    }

                    for idx, (start, end) in enumerate(events):
                        event_data = data[start:end]
                        event_baseline = rolling_avg_refined[start:end]
                        event_info_data = {
                            'event_id': idx,
                            'start_time': start / sampling_rate,
                            'end_time': end / sampling_rate,
                            'event_data': event_data-event_baseline,
                            'baseline_value': np.mean(event_baseline)
                        }
                        event_info['events'].append(event_info_data)

                    date_time_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                    if self.save_file_path is not None:
                        np.savez_compressed(self.save_file_path + '_' + date_time_str + '.event_data', 
                                            sampling_rate=event_info['sampling_rate'],
                                            events=event_info['events'])
                                            
                    else:
                        file_path, _ = os.path.splitext(file_path)
                        np.savez_compressed(file_path + '_' + date_time_str + '.event_data',
                                            sampling_rate=event_info['sampling_rate'],
                                            events=event_info['events'])
                                            
                    
                if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                    standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
                else:
                    standard = "Normal"
                if self.ml_tab.enable_ml_data_reduction_checkbox.isChecked():
                    ML_enabled = "True"
                    ML_tag = self.ml_tab.tag_lineedit.text()
                    ML_standard = self.ml_tab.data_reduction_type_combo.currentText()
                    if self.ml_tab.apply_standardisation_checkbox.isChecked():
                        if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                            standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
                    else:
                        standard = "Normal"
                else:
                    ML_enabled = "False"
                    ML_standard = None
                    ML_tag = None

                ML_standardisation_settings = {
                    'standard' : standard,
                    'ML_enabled' : ML_enabled,
                    'ML_standard' : ML_standard,
                    'standard_power' : self.fitting_settings_tab.power_spinbox.value(),
                    'standard_length_nm' : self.fitting_settings_tab.length_spinbox.value(),
                    'standard_conductivity_S_m' : self.fitting_settings_tab.conductivity_spinbox.value(),
                    'standard_voltage_applied_mV' : self.fitting_settings_tab.voltage_spinbox.value(),
                    'standard_open_pore_current_nA' : self.fitting_settings_tab.open_pore_current_spinbox.value(),
                    'sampling_rate' : sampling_rate,
                    'segment_rate_threshold' : self.fitting_settings_tab.segment_rate_threshold_spinbox.value(),
                    'change_of_rate_threshold':self.fitting_settings_tab.change_rate_threshold_spinbox.value(),
                    'merge_close_segments_threshold': self.fitting_settings_tab.merge_segment_threshold_spinbox.value()
                }

                settings = {
                    "file_name": file_path,
                    "sampling_rate": sampling_rate,
                    "start_testing_duration": start_testing_duration,
                    "end_testing_duration": end_testing_duration,
                    "threshold_method": threshold_method,
                    "dips": dips,
                    "low_pass_filter_applied": self.event_settings_tab.apply_filter_combo.currentText(),
                    "low_pass_filter_cutoff": self.event_settings_tab.cutoff_frequency_spinbox.value() * 1000,
                    "low_pass_filter_type": self.event_settings_tab.low_pass_filter_type_combo.currentText(),
                    "threshold_value_multiplier": self.event_settings_tab.threshold_value_multiplier_spinbox.value(),
                    "start_of_event_threshold": self.event_settings_tab.start_of_event_threshold_spinbox.value(),
                    "end_of_event_threshold": self.event_settings_tab.end_of_event_threshold_spinbox.value(),
                    "mean_window_size": self.event_settings_tab.mean_window_size_spinbox.value(),
                    "std_window_size": self.event_settings_tab.std_window_size_spinbox.value(),
                    "minimum_event_width": self.event_settings_tab.minimum_event_width_spinbox.value() / 1000,
                    "maximum_event_width": self.event_settings_tab.maximum_event_width_spinbox.value() / 1000,
                    "chunk_size_for_event_detection": self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(),
                    "standard": standard,
                    "ML_enabled": ML_enabled,
                    "ML_tag": ML_tag,
                    "ML_standard": ML_standard,
                    'standard_power' : self.fitting_settings_tab.power_spinbox.value(),
                    'standard_length_nm' : self.fitting_settings_tab.length_spinbox.value(),
                    'standard_conductivity_S_m' : self.fitting_settings_tab.conductivity_spinbox.value(),
                    'standard_voltage_applied_mV' : self.fitting_settings_tab.voltage_spinbox.value(),
                    'standard_open_pore_current_nA' : self.fitting_settings_tab.open_pore_current_spinbox.value()
                }

                # Serialize the settings dictionary to a JSON string
                settings = json.dumps(settings)

                # Event Fitting
                if self.load_options_tab.level_fitting_combo.currentText() == "Yes":   
                    self.npz_dict, event_analysis_array = multi_level_fitting_events(self.fitting_settings_tab.padding_spinbox.value(), self.fitting_settings_tab.chunk_size_for_event_fitting_spinbox.value(),self.fitting_settings_tab.library_combo.currentText(),self.fitting_settings_tab.model_combo.currentText(),self.fitting_settings_tab.num_components_spinbox.value(), self.fitting_settings_tab.threshold_spinbox.value(), data, events, dips, ML_standardisation_settings)
                    X =[np.array(sublist, dtype=np.float64) for sublist in event_analysis_array]
                    end_time = time.time()
                    time_taken = end_time-start_time

                    # Update information
                    if len(self.npz_dict)>10:
                        date_time_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                        if self.save_file_path is not None:
                            file_123 = self.save_file_path+'_'+date_time_str
                            np.savez_compressed(self.save_file_path+'_'+date_time_str+'.event_fitting', **self.npz_dict)
                            if ML_enabled == "True":
                                np.savez_compressed(self.save_file_path+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                            else:
                                np.savez_compressed(self.save_file_path+'_'+date_time_str+'.dataset', settings=settings, X=X)
                        else:
                            file_path, _ = os.path.splitext(file_path)
                            file_123 = file_path+'_'+date_time_str
                            np.savez_compressed(file_path+'_'+date_time_str+'.event_fitting', **self.npz_dict)
                            if ML_enabled == "True":
                                np.savez_compressed(file_path+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                            else:
                                np.savez_compressed(file_path+'_'+date_time_str+'.dataset', settings=settings, X=X)
                        
                        duration_tested = end_testing_duration - start_testing_duration
                        self.update_file_info(file_path, file_duration, len(events),time_taken, file_123, duration_tested, settings, test = "False")
                        self.total_events = len(self.npz_dict) // 10  # Assuming 10 parts per event
                        self.jump_to_spinbox.setMaximum(self.total_events - 1)
                        self.jump_to_spinbox.setValue(0)
                        self.current_event_index = 0
                        self.plot_event(0)
                        self.update_event_info_table(0)
                        
                else:
                    self.npz_dict = [ ]
                    X = save_chunked_event_analysis_to_npz(self.fitting_settings_tab.chunk_size_for_peak_fitting_spinbox.value(),data,events, rolling_avg_refined, sampling_rate, ML_standardisation_settings)
                    date_time_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                    if self.save_file_path is not None:
                        file_123 = self.save_file_path+'_'+date_time_str
                        if ML_enabled == "True":
                            np.savez_compressed(self.save_file_path+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                        else:
                            np.savez_compressed(self.save_file_path+'_'+date_time_str+'.dataset', settings=settings, X=X)
                    else:
                        file_path, _ = os.path.splitext(file_path)
                        file_123 = file_path+'_'+date_time_str
                        if ML_enabled == "True":
                            np.savez_compressed(file_path+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                        else:
                            np.savez_compressed(file_path+'_'+date_time_str+'.dataset', settings=settings, X=X)
                    self.jump_to_spinbox.setMaximum(0)
                    self.jump_to_spinbox.setValue(0)
                    self.current_event_index = 0
                    end_time = time.time()
                    time_taken = end_time-start_time
                    # Update information
                    duration_tested = end_testing_duration - start_testing_duration
                    self.update_file_info(file_path, file_duration, len(events),time_taken, file_123, duration_tested, settings, test = "False")

                if self.event_settings_tab.enable_plots.isChecked():
                    # Assuming X is already defined and populated with your event data as described
                    
                    if ML_enabled == "False":
                        dI = np.array([x[0] for x in X]) 
                        dt = np.array([x[4] for x in X])*1e3 
                    else:
                        if ML_standard == "Scheme 2" or ML_standard == "Scheme 3":
                            dI = np.array([x[11] for x in X])  
                            dt = np.array([x[15] for x in X])*1e3 
                        elif ML_standard == "Scheme 4":
                            dI = np.array([x[51] for x in X]) 
                            dt = np.array([x[55] for x in X])*1e3  
                        else:
                            dI = np.array([x[0] for x in X]) 
                            dt = np.array([x[4] for x in X])*1e3 

                    if ML_standard == "Scheme 1" or ML_standard == "Scheme 2" or ML_standard == "Scheme 3" or ML_enabled == "False":

                        dt =  dt[~np.isnan(dI)]
                        dI =  dI[~np.isnan(dI)]
                        

                        # Plotting the histogram of dI on the first canvas
                        self.plot_widgets[0].canvas.axes.clear()  # Clear existing plot
                        self.plot_widgets[0].canvas.axes.hist(dI, bins=100, color='blue', alpha=0.7)  # Adjust 'bins' as necessary
                        self.plot_widgets[0].canvas.axes.set_title(f'Histogram of dI | Counts:{len(dI)}')
                        self.plot_widgets[0].canvas.axes.set_xlabel('dI (nA)')
                        self.plot_widgets[0].canvas.axes.set_ylabel('Frequency')
                        self.plot_widgets[0].canvas.draw()  # Redraw the canvas

                        # Save the histogram plot
                        date_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        plot_title = f'Histogram of dI | Counts:{len(dI)}'
                        if self.save_file_path is not None:
                            filename = f"{self.save_file_path}_dI_{date_time_str}.png"
                        else:
                            file_path, _ = os.path.splitext(file_path)
                            filename = f"{file_path}_dI_{date_time_str}.png"
                        self.plot_widgets[0].canvas.figure.savefig(filename, dpi=300, transparent=True)

                        # Plotting the scatter plot of dI vs log(dt*1e3) on the second canvas
                        #log_dt = np.log(np.array(dt) * 1e3)  # Calculate the logarithm of dt*1e3
                        log_dt = np.log(dt)  # Calculate the logarithm of dt*1e3
                        self.plot_widgets[1].canvas.axes.clear()
                        self.plot_widgets[1].canvas.axes.scatter(log_dt, dI, color='red', alpha=0.5, s = 2)  # Plot dI vs. log(dt*1e3)
                        self.plot_widgets[1].canvas.axes.set_title('Scatter Plot of ΔI vs. log(Δt*1e3)')
                        self.plot_widgets[1].canvas.axes.set_ylabel('ΔI (nA)')
                        self.plot_widgets[1].canvas.axes.set_xlabel('log(Δt (ms))')
                        self.plot_widgets[1].canvas.draw()  
                        # Save the scatter plot
                        plot_title = 'Scatter_Plot_of_dI_vs_log_dt'
                        if self.save_file_path is not None:
                            filename = f"{self.save_file_path}_{plot_title}_{date_time_str}.png"
                        else:
                            file_path, _ = os.path.splitext(file_path)
                            filename = f"{file_path}_{plot_title}_{date_time_str}.png"
                        self.plot_widgets[1].canvas.figure.savefig(filename, dpi=300, transparent=True)
                    


                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Icon.Information)
                msgBox.setWindowTitle("Success")
                msgBox.setText("Data Reduction performed successfully!")
                msgBox.setInformativeText(f"Number of Events Detected: {len(events)}")
                msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
                msgBox.exec()
    

    def process_multiple_files(self,file_path):
        start_time = time.time()
        # Load data and sampling rate from the file
        #Load the sampling rate and length of the file in seconds

        if file_path.endswith('.abf'):

            length_in_seconds,sampling_rate = get_abf_file_info(file_path)
            if self.event_settings_tab.enable_nth_data_point_loading.isChecked():
                data, sampling_rate = load_abf_file_nth(file_path,self.event_settings_tab.nth_data_point_spinbox.value())
            else:
                data, sampling_rate = load_abf_file(file_path)
        elif  file_path.endswith('.hdf5') or file_path.endswith('.h5'):
                data,sampling_rate = load_hdf5_file(file_path)
                length_in_seconds = len(data)/sampling_rate

        if data is not None:
            if self.event_settings_tab.analysis_start_duration_spinbox.value() > 0:
                if self.event_settings_tab.enable_analysis_time_specific.isChecked():
                    start_testing_duration = self.event_settings_tab.analysis_start_duration_spinbox.value()
                    start_points = int(start_testing_duration * sampling_rate)
                else:
                    start_testing_duration = 0
                    start_points = 0
            else:
                start_testing_duration = 0
                start_points = 0
            if self.event_settings_tab.analysis_end_duration_spinbox.value() > 0:
                if self.event_settings_tab.enable_analysis_time_specific.isChecked():
                    end_testing_duration = self.event_settings_tab.analysis_end_duration_spinbox.value()
                    end_points = int(end_testing_duration * sampling_rate)
                else:
                    end_testing_duration = length_in_seconds
                    end_points = int(end_testing_duration * sampling_rate)
            else:
                end_points = int(length_in_seconds * sampling_rate)
                end_testing_duration = length_in_seconds

            # Take the slice of data 
            data = data[start_points:end_points]

            #Update the EventSettingsTab with the sampling rate and file duration
            self.event_settings_tab.sampling_rate_spinbox.setValue(sampling_rate / 1000)  # Convert to kHz
            self.event_settings_tab.analysis_end_duration_spinbox.setMaximum(length_in_seconds)
            self.load_options_tab.testing_duration_end_spinbox.setMaximum(length_in_seconds)
            file_duration = length_in_seconds

            if self.event_settings_tab.apply_filter_combo.currentText() == "Yes":
                if self.event_settings_tab.filter_type_combo.currentText() == "Wavelet":
                    data = apply_low_pass_filter(data, 10000, "Wavelet",sampling_rate)
                else:
                    data = apply_low_pass_filter(data, self.event_settings_tab.cutoff_frequency_spinbox.value()*1000, self.event_settings_tab.low_pass_filter_type_combo.currentText(),sampling_rate)
            if self.event_settings_tab.type_of_threshold_combo.currentText() == "ΔI":
                threshold_method = "difference"
            else:
                threshold_method = "multiplier"
            if self.event_settings_tab.dips_or_peaks_combo.currentText()=="Dips":
                dips = "Yes"
            else:
                dips = "Yes"
                data = ne.evaluate("data*(-1)")
                
            if self.event_settings_tab.enable_std_smoothing_checkbox.isChecked():
                enable_smoothing = "Yes"
            else:
                enable_smoothing = "No"
            try:
                events,rolling_avg_refined, rolling_threshold_refined = find_events_refined_parallel(data, self.event_settings_tab.threshold_value_multiplier_spinbox.value(), self.event_settings_tab.start_of_event_threshold_spinbox.value(), self.event_settings_tab.end_of_event_threshold_spinbox.value(), self.event_settings_tab.threshold_value_multiplier_spinbox.value(), self.event_settings_tab.mean_window_size_spinbox.value(), self.event_settings_tab.std_window_size_spinbox.value(), threshold_method, self.event_settings_tab.minimum_event_width_spinbox.value()/1000, self.event_settings_tab.maximum_event_width_spinbox.value()/1000, self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(), dips, sampling_rate, enable_smoothing, self.event_settings_tab.smoothing_type_dropdown.currentIndex(),self.event_settings_tab.std_calculation_method_combo.currentText(), n_jobs = -1)
            except:
                pass
            if self.load_options_tab.save_event_chk.isChecked():
                try:
                    # Organize the event information
                    event_info = {
                        'sampling_rate': sampling_rate,
                        'events': []
                    }

                    for idx, (start, end) in enumerate(events):
                        event_data = data[start:end]
                        event_baseline = rolling_avg_refined[start:end]
                        event_info_data = {
                            'event_id': idx,
                            'start_time': start / sampling_rate,
                            'end_time': end / sampling_rate,
                            'event_data': event_data,
                            'baseline_value': np.mean(event_baseline)
                        }
                        event_info['events'].append(event_info_data)

                    date_time_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                    if self.save_file_path is not None:
                        np.savez_compressed(self.save_file_path + '_' + date_time_str + '.event_data', 
                                            sampling_rate=event_info['sampling_rate'],
                                            events=event_info['events'])
                    else:
                        file_path, _ = os.path.splitext(file_path)
                        np.savez_compressed(file_path + '_' + date_time_str + '.event_data',
                                            sampling_rate=event_info['sampling_rate'],
                                            events=event_info['events'])
                except:
                    pass
            try:
                if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                    standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
                else:
                    standard = "Normal"
                if self.ml_tab.enable_ml_data_reduction_checkbox.isChecked():
                    ML_enabled = "True"
                    ML_tag = self.ml_tab.tag_lineedit.text()
                    ML_standard = self.ml_tab.data_reduction_type_combo.currentText()
                    if self.ml_tab.apply_standardisation_checkbox.isChecked():
                        if self.fitting_settings_tab.enable_standardisation_checkbox.isChecked():
                            standard = self.fitting_settings_tab.standardisation_type_combo.currentText()
                    else:
                        standard = "Normal"
                else:
                    ML_enabled = "False"
                    ML_standard = None
                    ML_tag = None

                ML_standardisation_settings = {
                    'standard' : standard,
                    'ML_enabled' : ML_enabled,
                    'ML_standard' : ML_standard,
                    'standard_power' : self.fitting_settings_tab.power_spinbox.value(),
                    'standard_length_nm' : self.fitting_settings_tab.length_spinbox.value(),
                    'standard_conductivity_S_m' : self.fitting_settings_tab.conductivity_spinbox.value(),
                    'standard_voltage_applied_mV' : self.fitting_settings_tab.voltage_spinbox.value(),
                    'standard_open_pore_current_nA' : self.fitting_settings_tab.open_pore_current_spinbox.value(),
                    'sampling_rate' : sampling_rate,
                    'segment_rate_threshold' : self.fitting_settings_tab.segment_rate_threshold_spinbox.value(),
                    'change_of_rate_threshold':self.fitting_settings_tab.change_rate_threshold_spinbox.value(),
                    'merge_close_segments_threshold': self.fitting_settings_tab.merge_segment_threshold_spinbox.value()
                }

                settings = {
                    "file_name": file_path,
                    "sampling_rate": sampling_rate,
                    "start_testing_duration": start_testing_duration,
                    "end_testing_duration": end_testing_duration,
                    "threshold_method": threshold_method,
                    "dips": dips,
                    "low_pass_filter_applied": self.event_settings_tab.apply_filter_combo.currentText(),
                    "low_pass_filter_cutoff": self.event_settings_tab.cutoff_frequency_spinbox.value() * 1000,
                    "low_pass_filter_type": self.event_settings_tab.low_pass_filter_type_combo.currentText(),
                    "threshold_value_multiplier": self.event_settings_tab.threshold_value_multiplier_spinbox.value(),
                    "start_of_event_threshold": self.event_settings_tab.start_of_event_threshold_spinbox.value(),
                    "end_of_event_threshold": self.event_settings_tab.end_of_event_threshold_spinbox.value(),
                    "mean_window_size": self.event_settings_tab.mean_window_size_spinbox.value(),
                    "std_window_size": self.event_settings_tab.std_window_size_spinbox.value(),
                    "minimum_event_width": self.event_settings_tab.minimum_event_width_spinbox.value() / 1000,
                    "maximum_event_width": self.event_settings_tab.maximum_event_width_spinbox.value() / 1000,
                    "chunk_size_for_event_detection": self.fitting_settings_tab.chunk_size_for_event_detection_spinbox.value(),
                    "standard": standard,
                    "ML_enabled": ML_enabled,
                    "ML_tag": ML_tag,
                    "ML_standard": ML_standard,
                    'standard_power' : self.fitting_settings_tab.power_spinbox.value(),
                    'standard_length_nm' : self.fitting_settings_tab.length_spinbox.value(),
                    'standard_conductivity_S_m' : self.fitting_settings_tab.conductivity_spinbox.value(),
                    'standard_voltage_applied_mV' : self.fitting_settings_tab.voltage_spinbox.value(),
                    'standard_open_pore_current_nA' : self.fitting_settings_tab.open_pore_current_spinbox.value()
                }

                # Serialize the settings dictionary to a JSON string
                settings = json.dumps(settings)

                # Event Fitting
                if self.load_options_tab.level_fitting_combo.currentText() == "Yes":    
                    self.npz_dict, event_analysis_array = multi_level_fitting_events(self.fitting_settings_tab.padding_spinbox.value(), self.fitting_settings_tab.chunk_size_for_event_fitting_spinbox.value(),self.fitting_settings_tab.library_combo.currentText(),self.fitting_settings_tab.model_combo.currentText(),self.fitting_settings_tab.num_components_spinbox.value(), self.fitting_settings_tab.threshold_spinbox.value(), data, events, dips, ML_standardisation_settings)
                    X =[np.array(sublist, dtype=np.float64) for sublist in event_analysis_array]
                    end_time = time.time()
                    time_taken = end_time-start_time
                    # Update information
                    if len(self.npz_dict)>10:
                        date_time_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

                        if self.save_file_path is not None:
                            file_123 = self.save_file_path+'_'+date_time_str
                            np.savez_compressed(self.save_file_path+'_'+date_time_str+'.event_fitting', **self.npz_dict)
                            if ML_enabled == "True":
                                np.savez_compressed(self.save_file_path+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                            else:
                                np.savez_compressed(self.save_file_path+'_'+date_time_str+'.dataset', settings=settings, X=X)
                        else:
                            file_path, _ = os.path.splitext(file_path)
                            file_123 = file_path+'_'+date_time_str
                            np.savez_compressed(file_path+'_'+date_time_str+'.event_fitting', **self.npz_dict)
                            if ML_enabled == "True":
                                np.savez_compressed(file_path+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                            else:
                                np.savez_compressed(file_path+'_'+date_time_str+'.dataset', settings=settings, X=X)

                        duration_tested = end_testing_duration - start_testing_duration
                        self.update_file_info(file_path, file_duration, len(events),time_taken, file_123, duration_tested, settings, test = "False")
                        if self.event_settings_tab.enable_plots.isChecked():
                            if ML_enabled == "False":
                                dI = np.array([x[0] for x in X]) 
                                dt = np.array([x[4] for x in X])*1e3 
                            else:
                                if ML_standard == "Scheme 2" or ML_standard == "Scheme 3":
                                    dI = np.array([x[11] for x in X])  
                                    dt = np.array([x[15] for x in X])*1e3 
                                elif ML_standard == "Scheme 4":
                                    dI = np.array([x[51] for x in X]) 
                                    dt = np.array([x[55] for x in X])*1e3  
                                else:
                                    dI = np.array([x[0] for x in X]) 
                                    dt = np.array([x[4] for x in X])*1e3 

                            if ML_standard == "Scheme 1" or ML_standard == "Scheme 2" or ML_standard == "Scheme 3" or ML_enabled == "False":

                                dt =  dt[~np.isnan(dI)]
                                dI =  dI[~np.isnan(dI)]
                                
                            
                                # Plotting the histogram of dI on the first canvas
                                self.plot_widgets[0].canvas.axes.clear()  # Clear existing plot
                                self.plot_widgets[0].canvas.axes.hist(dI, bins=100, color='blue', alpha=0.7)  # Adjust 'bins' as necessary
                                self.plot_widgets[0].canvas.axes.set_title('Histogram of dI')
                                self.plot_widgets[0].canvas.axes.set_xlabel('dI (nA)')
                                self.plot_widgets[0].canvas.axes.set_ylabel('Frequency')
                                self.plot_widgets[0].canvas.draw()  # Redraw the canvas

                                # Save the histogram plot
                                date_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                                plot_title = 'Histogram_of_dI'
                                if self.save_file_path is not None:
                                    filename = f"{self.save_file_path}_{plot_title}_{date_time_str}.png"
                                else:
                                    file_path, _ = os.path.splitext(file_path)
                                    filename = f"{file_path}_{plot_title}_{date_time_str}.png"
                                self.plot_widgets[0].canvas.figure.savefig(filename, dpi=300, transparent=True)

                                # Plotting the scatter plot of dI vs log(dt*1e3) on the second canvas
                                #log_dt = np.log(np.array(dt) * 1e3)  # Calculate the logarithm of dt*1e3
                                log_dt = np.log(dt)  # Calculate the logarithm of dt*1e3
                                self.plot_widgets[1].canvas.axes.clear()
                                self.plot_widgets[1].canvas.axes.scatter(log_dt, dI, color='red', alpha=0.5, s = 2)  # Plot dI vs. log(dt*1e3)
                                self.plot_widgets[1].canvas.axes.set_title('Scatter Plot of ΔI vs. log(Δt*1e3)')
                                self.plot_widgets[1].canvas.axes.set_ylabel('ΔI (nA)')
                                self.plot_widgets[1].canvas.axes.set_xlabel('log(Δt (ms))')
                                self.plot_widgets[1].canvas.draw()  
                                # Save the scatter plot
                                plot_title = 'Scatter_Plot_of_dI_vs_log_dt'
                                if self.save_file_path is not None:
                                    filename = f"{self.save_file_path}_{plot_title}_{date_time_str}.png"
                                else:
                                    file_path, _ = os.path.splitext(file_path)
                                    filename = f"{file_path}_{plot_title}_{date_time_str}.png"
                                self.plot_widgets[1].canvas.figure.savefig(filename, dpi=300, transparent=True)
                        
                        del self.npz_dict,X
                else:
                    self.npz_dict = [ ]
                    X = save_chunked_event_analysis_to_npz(self.fitting_settings_tab.chunk_size_for_peak_fitting_spinbox.value(),data,events, rolling_avg_refined, sampling_rate, ML_standardisation_settings)
                    date_time_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

                    if self.save_file_path is not None:
                        file_123 = self.save_file_path+'_'+date_time_str
                        if ML_enabled == "True":
                            np.savez_compressed(self.save_file_path+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                        else:
                            np.savez_compressed(self.save_file_path+'_'+date_time_str+'.dataset', settings=settings, X=X)
                    else:
                        file_path, _ = os.path.splitext(file_path)
                        file_123 = file_path+'_'+date_time_str
                        if ML_enabled == "True":
                            np.savez_compressed(file_path+'_'+date_time_str+'.MLdataset',settings=settings, X=X)
                        else:
                            np.savez_compressed(file_path+'_'+date_time_str+'.dataset', settings=settings, X=X)
                    end_time = time.time()
                    time_taken = end_time-start_time
                    # Update information
                    duration_tested = end_testing_duration - start_testing_duration
                    self.update_file_info(file_path, file_duration, len(events),time_taken, file_123, duration_tested, settings, test = "False")
                    if self.event_settings_tab.enable_plots.isChecked():
                        # Assuming X is already defined and populated with your event data as described
                        if ML_enabled == "False":
                            dI = np.array([x[0] for x in X]) 
                            dt = np.array([x[4] for x in X])*1e3 
                        else:
                            if ML_standard == "Scheme 2" or ML_standard == "Scheme 3":
                                dI = np.array([x[11] for x in X])  
                                dt = np.array([x[15] for x in X])*1e3 
                            elif ML_standard == "Scheme 4":
                                dI = np.array([x[51] for x in X]) 
                                dt = np.array([x[55] for x in X])*1e3  
                            else:
                                dI = np.array([x[0] for x in X]) 
                                dt = np.array([x[4] for x in X])*1e3 

                        if ML_standard == "Scheme 1" or ML_standard == "Scheme 2" or ML_standard == "Scheme 3" or ML_enabled == "False":

                            dt =  dt[~np.isnan(dI)]
                            dI =  dI[~np.isnan(dI)]
                            
                        
                            # Plotting the histogram of dI on the first canvas
                            self.plot_widgets[0].canvas.axes.clear()  # Clear existing plot
                            self.plot_widgets[0].canvas.axes.hist(dI, bins=100, color='blue', alpha=0.7)  # Adjust 'bins' as necessary
                            self.plot_widgets[0].canvas.axes.set_title(f'Histogram of dI | Counts:{len(dI)}')
                            self.plot_widgets[0].canvas.axes.set_xlabel('dI (nA)')
                            self.plot_widgets[0].canvas.axes.set_ylabel('Frequency')
                            self.plot_widgets[0].canvas.draw()  # Redraw the canvas

                            # Save the histogram plot
                            date_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                            plot_title = f'Histogram of dI | Counts:{len(dI)}'
                            if self.save_file_path is not None:
                                filename = f"{self.save_file_path}_dI_{date_time_str}.png"
                            else:
                                file_path, _ = os.path.splitext(file_path)
                                filename = f"{file_path}_dI_{date_time_str}.png"
                            self.plot_widgets[0].canvas.figure.savefig(filename, dpi=300, transparent=True)

                            # Plotting the scatter plot of dI vs log(dt*1e3) on the second canvas
                            #log_dt = np.log(np.array(dt) * 1e3)  # Calculate the logarithm of dt*1e3
                            log_dt = np.log(dt)  # Calculate the logarithm of dt*1e3
                            self.plot_widgets[1].canvas.axes.clear()
                            self.plot_widgets[1].canvas.axes.scatter(log_dt, dI, color='red', alpha=0.5, s = 2)  # Plot dI vs. log(dt*1e3)
                            self.plot_widgets[1].canvas.axes.set_title('Scatter Plot of ΔI vs. log(Δt*1e3)')
                            self.plot_widgets[1].canvas.axes.set_ylabel('ΔI (nA)')
                            self.plot_widgets[1].canvas.axes.set_xlabel('log(Δt (ms))')
                            self.plot_widgets[1].canvas.draw()  
                            # Save the scatter plot
                            plot_title = 'Scatter_Plot_of_dI_vs_log_dt'
                            if self.save_file_path is not None:
                                filename = f"{self.save_file_path}_{plot_title}_{date_time_str}.png"
                            else:
                                file_path, _ = os.path.splitext(file_path)
                                filename = f"{file_path}_{plot_title}_{date_time_str}.png"
                            self.plot_widgets[1].canvas.figure.savefig(filename, dpi=300, transparent=True)
                del X
            except:
                pass
            del data

    def on_perform_data_reduction_clicked(self):

        # Get selected items from the list
        selected_items = self.load_options_tab.files_list_widget.selectedItems()       
        
        if selected_items:
            files = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
            if len(files) > 1:
                # Show custom dialog for multiple files
                dialog = ProcessingDialog(self)
                dialog.show()

                # Process events to ensure the dialog is displayed
                QApplication.processEvents()

                for  file_path in files:
                    self.process_multiple_files(file_path)
                    gc.collect()

                # Close the dialog when done
                dialog.close()

                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Icon.Information)
                msgBox.setWindowTitle("Success")
                msgBox.setText("Data Reduction performed successfully!")
                msgBox.setInformativeText(f"Number of Files Processed: {len(files)}\n Due to the fact that multiple files were processed, we are not displaying any events.")
                msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
                msgBox.exec()
            else:
                # Show custom dialog for single file
                dialog = ProcessingDialog(self)
                dialog.show()

                # Process events to ensure the message box is displayed
                QApplication.processEvents()

                # Process the single file
                self.process_single_file(files[0])

                # Close the dialog when done
                dialog.close()
                    

    def plot_event(self, event_index):
        try:
            # Retrieve event data from your npz_dict using the event_index
            event_data_key = f'EVENT_DATA_{event_index}'
            segment_info_key = f'SEGMENT_INFO_{event_index}'
            
            # Retrieve data from npz_dict
            time_points_padded = self.npz_dict[f'{event_data_key}_part_0']
            padded_event_data = self.npz_dict[f'{event_data_key}_part_1']
            event_time_start_end = self.npz_dict[f'{event_data_key}_part_2']
            mean_values_connected_with_baseline = self.npz_dict[f'{event_data_key}_part_3']
            
            # Clear the current plot
            self.event_visualization_widget.canvas.figure.clear()
            ax = self.event_visualization_widget.canvas.figure.add_subplot(111)

            # Plot the event data
            ax.plot(time_points_padded, padded_event_data, label='Event Data')
                
            # Highlight event start and end
            ax.axvline(x=event_time_start_end[0], color='g', linestyle='--', label='Event Start')
            ax.axvline(x=event_time_start_end[1], color='g', linestyle='--', label='Event End')
            
            # Plot mean values connected with baseline
            ax.plot(time_points_padded, mean_values_connected_with_baseline, label='Mean Values with Baseline', color='red', linestyle='--')
            
            # Set x-axis and y-axis limits based on the data
            # ax.set_xlim(time_points_padded[0], time_points_padded[-1])
            # ax.set_ylim(min(padded_event_data.min(), mean_values_connected_with_baseline.min()),
            #             max(padded_event_data.max(), mean_values_connected_with_baseline.max()))
            
            # Add labels and legend
            ax.set_xlabel('Time')
            ax.set_ylabel('Amplitude')
            #ax.legend()

            self.event_visualization_widget.canvas.figure.tight_layout()
            self.event_visualization_widget.canvas.draw()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText("An error has occurred.")
            msg.setInformativeText(f"No fitted events found!")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            

    # def update_event_info_table(self, event_index):
    #     try:
    #         segment_info_key = f'SEGMENT_INFO_{event_index}'
    #         number_of_segments = int(self.npz_dict[f'{segment_info_key}_number_of_segments'][0])
    #         segment_mean_diffs = self.npz_dict[f'{segment_info_key}_segment_mean_diffs']
    #         segment_widths_time = self.npz_dict[f'{segment_info_key}_segment_widths_time']
    #         event_width = self.npz_dict[f'{segment_info_key}_event_width'][0]

    #         # Adjust row count to include segments + extra rows for event info
    #         self.table_widget.setRowCount(number_of_segments + 3)  # Corrected row count
    #         self.table_widget.setColumnCount(3)
    #         self.table_widget.setHorizontalHeaderLabels(["Segment #", "ΔI (nA)", "Width (μs)"])

    #         # Fill segment rows
    #         for i in range(number_of_segments):
    #             self.table_widget.setItem(i, 0, QTableWidgetItem(str(i + 1)))
    #             self.table_widget.setItem(i, 1, QTableWidgetItem(f"{segment_mean_diffs[i]:.3g}"))
    #             self.table_widget.setItem(i, 2, QTableWidgetItem(f"{segment_widths_time[i]*1e6:.3g}"))

    #         # Insert an empty row as a separator
    #         # Corrected by removing setSpan, simply leaving an empty row for visual separation
    #         separator_index = number_of_segments
    #         self.table_widget.setItem(separator_index, 0, QTableWidgetItem(""))
    #         self.table_widget.setItem(separator_index, 1, QTableWidgetItem(""))
    #         self.table_widget.setItem(separator_index, 2, QTableWidgetItem(""))

    #         # Event Number Row
    #         event_number_index = number_of_segments + 1
    #         self.table_widget.setItem(event_number_index, 0, QTableWidgetItem("Event Index"))
    #         self.table_widget.setItem(event_number_index, 1, QTableWidgetItem(""))  # Adjust if you want the number in a different column
    #         self.table_widget.setItem(event_number_index, 2, QTableWidgetItem(f"{event_index}"))

    #         # Event Width Row
    #         event_width_index = number_of_segments + 2
    #         self.table_widget.setItem(event_width_index, 0, QTableWidgetItem("Event Width (μs)"))
    #         self.table_widget.setItem(event_width_index, 1, QTableWidgetItem(""))  # Adjust if you want the width in a different column
    #         self.table_widget.setItem(event_width_index, 2, QTableWidgetItem(f"{event_width*1e6:.3g}"))

    #         # Adjusting appearance
    #         self.table_widget.resizeColumnsToContents()
    #     except:
    #         pass

    def update_event_info_table(self, event_index):
        try:
            segment_info_key = f'SEGMENT_INFO_{event_index}'
            number_of_segments = int(self.npz_dict[f'{segment_info_key}_number_of_segments'][0])
            segment_mean_diffs = self.npz_dict[f'{segment_info_key}_segment_mean_diffs']
            segment_widths_time = self.npz_dict[f'{segment_info_key}_segment_widths_time']
            event_width = self.npz_dict[f'{segment_info_key}_event_width'][0]

            # Retrieve the baseline value
            event_data_key = f'EVENT_DATA_{event_index}'
            baseline_value = self.npz_dict[f'{event_data_key}_part_4'][0]

            # Calculate the actual segment means
            segment_means = baseline_value - segment_mean_diffs

            # Adjust row count to include segments + extra rows for event info
            self.table_widget.setRowCount(number_of_segments + 3)
            self.table_widget.setColumnCount(4)
            self.table_widget.setHorizontalHeaderLabels(["Segment #", "Mean (nA)", "ΔI (nA)", "Width (μs)"])

            # Fill segment rows
            for i in range(number_of_segments):
                self.table_widget.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.table_widget.setItem(i, 1, QTableWidgetItem(f"{segment_means[i]:.3g}"))
                self.table_widget.setItem(i, 2, QTableWidgetItem(f"{segment_mean_diffs[i]:.3g}"))
                self.table_widget.setItem(i, 3, QTableWidgetItem(f"{segment_widths_time[i]*1e6:.3g}"))

            # Insert an empty row as a separator
            separator_index = number_of_segments
            self.table_widget.setItem(separator_index, 0, QTableWidgetItem(""))
            self.table_widget.setItem(separator_index, 1, QTableWidgetItem(""))
            self.table_widget.setItem(separator_index, 2, QTableWidgetItem(""))
            self.table_widget.setItem(separator_index, 3, QTableWidgetItem(""))

            # Event Number Row
            event_number_index = number_of_segments + 1
            self.table_widget.setItem(event_number_index, 0, QTableWidgetItem("Event Index"))
            self.table_widget.setItem(event_number_index, 1, QTableWidgetItem(""))
            self.table_widget.setItem(event_number_index, 2, QTableWidgetItem(""))
            self.table_widget.setItem(event_number_index, 3, QTableWidgetItem(f"{event_index}"))

            # Event Width Row
            event_width_index = number_of_segments + 2
            self.table_widget.setItem(event_width_index, 0, QTableWidgetItem("Event Width (μs)"))
            self.table_widget.setItem(event_width_index, 1, QTableWidgetItem(""))
            self.table_widget.setItem(event_width_index, 2, QTableWidgetItem(""))
            self.table_widget.setItem(event_width_index, 3, QTableWidgetItem(f"{event_width*1e6:.3g}"))

            # Adjusting appearance
            self.table_widget.resizeColumnsToContents()
        except:
            pass
                  
       
    def Plot_Entire_Data(self):
        selected_items = self.load_options_tab.files_list_widget.selectedItems()
        if selected_items:
            # Use only the first selected file
            file_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
            if file_path.endswith('.abf'):
                # Load data and sampling rate from the file
                if self.event_settings_tab.enable_nth_data_point_loading.isChecked():
                    data, sampling_rate = load_abf_file_nth(file_path,self.event_settings_tab.nth_data_point_spinbox.value())
                else:
                    data, sampling_rate = load_abf_file(file_path)
            elif  file_path.endswith('.hdf5') or file_path.endswith('.h5'):
                data,sampling_rate = load_hdf5_file(file_path)
                length_in_seconds = len(data)/sampling_rate
            
            if data is not None:
                time_axis = np.arange(len(data)) / sampling_rate

                if self.event_settings_tab.apply_filter_combo.currentText() == "Yes":
                    if self.event_settings_tab.filter_type_combo.currentText() == "Wavelet":
                        data = apply_low_pass_filter(data, 10000, "Wavelet", sampling_rate)
                    else:
                        data = apply_low_pass_filter(data, self.event_settings_tab.cutoff_frequency_spinbox.value()*1000, self.event_settings_tab.low_pass_filter_type_combo.currentText(), sampling_rate)
                

                # Clear the current figure and plot the new data
                self.data_visualization_widget.canvas.axes.clear()
                self.data_visualization_widget.canvas.axes.plot(time_axis, data, label='Signal', linewidth=0.5)
                self.data_visualization_widget.canvas.axes.set_xlabel('Time (s)')
                self.data_visualization_widget.canvas.axes.set_ylabel('Current (nA)')

                #Adjust Limits
                self.data_visualization_widget.canvas.axes.set_xlim(min(time_axis), max(time_axis))

                # Adjust layout
                self.data_visualization_widget.canvas.figure.tight_layout()

                self.data_visualization_widget.canvas.draw()

                self.event_settings_tab.sampling_rate_spinbox.setValue(sampling_rate / 1000)  # Convert to kHz

                file_duration = len(data) / sampling_rate

                self.event_settings_tab.analysis_end_duration_spinbox.setValue(file_duration)

    def plot_events(self, events, data, rolling_avg_refined, rolling_std_refined, sampling_rate):
        time_axis = np.arange(len(data)) / sampling_rate
        self.data_visualization_widget.canvas.axes.clear()

        # Plot the main signal
        self.data_visualization_widget.canvas.axes.plot(time_axis, data, label='Signal', linewidth=0.5)
        # Plot the rolling average (baseline)
        self.data_visualization_widget.canvas.axes.plot(time_axis, rolling_avg_refined, label='Baseline', color='orange')
        # Plot the rolling standard deviation (threshold)
        self.data_visualization_widget.canvas.axes.plot(time_axis, rolling_std_refined, label='Threshold', color='green', linestyle='--')

        # Highlight events, but limit to the first 20 for performance
        events_to_highlight = events[:20]  # Only highlight the first 20 events
        for start, end in events_to_highlight:
            # Calculate the bottom and height for the rectangle
            bottom = min(data)
            height = max(data) - bottom
            # Add a rectangle patch for the event duration
            self.data_visualization_widget.canvas.axes.add_patch(patches.Rectangle(
                (start / sampling_rate, bottom),  # (x, y)
                (end - start) / sampling_rate,    # width
                height,                           # height
                color='yellow', alpha=0.5))       # rectangle color and transparency

        if len(events) > 20:
            # If more than 20 events, show a message box to the user
            if not hasattr(self, 'events_message_shown') or not self.events_message_shown:
                # If more than 20 events and the message hasn't been shown before
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText("We are highlighting the first 20 events only for performance reasons.")
                msg.setInformativeText("Contact shankar.dutt@anu.edu.au for any further changes.")
                msg.setWindowTitle("Notice")

                # Add a checkbox to the message box for muting future messages
                mute_checkbox = QCheckBox("Mute future messages")
                msg.setCheckBox(mute_checkbox)

                msg.exec()

                # Update the flag to indicate that the message has been shown
                self.events_message_shown = True

                # Check if the user has chosen to mute future messages
                if mute_checkbox.isChecked():
                    self.events_message_muted = True

            elif not hasattr(self, 'events_message_muted') or not self.events_message_muted:
                # If the message has been shown before but not muted
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText("We are highlighting the first 20 events only for performance reasons.")
                msg.setInformativeText("Contact shankar.dutt@anu.edu.au for any further changes.")
                msg.setWindowTitle("Notice")

                # Add a checkbox to the message box for muting future messages
                mute_checkbox = QCheckBox("Mute future messages")
                msg.setCheckBox(mute_checkbox)

                msg.exec()

                # Check if the user has chosen to mute future messages
                if mute_checkbox.isChecked():
                    self.events_message_muted = True

        # Set labels and title
        self.data_visualization_widget.canvas.axes.set_xlabel('Time (s)')
        self.data_visualization_widget.canvas.axes.set_ylabel('Current (nA)')
        self.data_visualization_widget.canvas.axes.set_title('Signal with Identified Events')
        self.data_visualization_widget.canvas.axes.legend(loc='lower right')

        # Set x-axis limits to minimum and maximum of the time axis
        self.data_visualization_widget.canvas.axes.set_xlim(min(time_axis), max(time_axis))

        # Adjust layout
        self.data_visualization_widget.canvas.figure.tight_layout()

        # Refresh the canvas to display the updated plot
        self.data_visualization_widget.canvas.draw()

    def navigate_to_previous_event(self):
        if self.current_event_index > 0:
            self.current_event_index -= 1
            self.plot_event(self.current_event_index)
            self.update_event_info_table(self.current_event_index)
        else:
            QMessageBox.information(self, "Navigation", "Already at the first event.")

    def navigate_to_next_event(self):
        if self.current_event_index < self.total_events - 1:
            self.current_event_index += 1
            self.plot_event(self.current_event_index)
            self.update_event_info_table(self.current_event_index)
        else:
            QMessageBox.information(self, "Navigation", "Already at the last event.")

    def jump_to_event(self):
        jump_index = self.jump_to_spinbox.value()
        if 0 <= jump_index < self.total_events:
            self.current_event_index = jump_index
            self.plot_event(self.current_event_index)
            self.update_event_info_table(self.current_event_index)
        else:
            QMessageBox.warning(self, "Invalid Event Number", "The specified event number is out of bounds.")

    def update_file_info(self, file_name, file_duration, event_count, time_taken, file_path, duration_tested, settings, test):
        # Get the current date and time
        now = datetime.now()
        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

        if test == "True":
            if self.previous_settings is not None and self.previous_settings.get('file_name') == file_name:
                # Check if settings have changed
                changed_settings = []
                for key, value in settings.items():
                    if key != 'file_name' and value != self.previous_settings[key]:
                        changed_settings.append(f"{key.replace('_', ' ').title()} -> Changed from {self.previous_settings[key]} to {value}")

                if changed_settings:
                    info_text = (
                        f"TEST SETTINGS ON THE FOLLOWING FILE\n\n"
                        #f"File Information:\n\n"
                        #f"Path: {file_name}\n\n"
                        f"Detected Events: {event_count}\n"
                        f"Time taken for Analysis: {round(time_taken, 3)} s\n"
                        f"Changed Settings:\n"
                        f"{chr(10).join(changed_settings)}\n"  # Use chr(10) instead of '\n'
                        f"_________________________________________________________________________________"
                    )
                else:
                    info_text = ""
            else:
                # Create the information text for test settings
                info_text = (
                    f"TEST SETTINGS ON THE FOLLOWING FILE\n\n"
                    f"File Information:\n\n"
                    f"Path: {file_name}\n\n"
                    f"File Duration: {file_duration:.2f} seconds\n"
                    f"Duration Tested: {duration_tested:.2f} seconds\n"
                    f"Detected Events: {event_count}\n"
                    f"Date and Time of Analysis: {date_time_str}\n"
                    f"Time taken for Analysis: {round(time_taken, 3)} s\n"
                    f"_________________________________________________________________________________\n\n"
                    f"Settings:\n"
                    f"Filter applied: {settings['low_pass_filter_applied']} \n"
                    f"If Lowpass, Type of Filter applied: {settings['low_pass_filter_type']} \n"
                    f"Low Pass Filter Cutoff: {settings['low_pass_filter_cutoff']} Hz\n"
                    f"Event Start Prominence Threshold: {settings['start_of_event_threshold']:.2f} nA\n"
                    f"Event End Prominence Threshold: {settings['end_of_event_threshold']:.2f} nA\n"
                    f"Sampling Rate: {settings['sampling_rate']:.2f} Hz\n"
                    f"Threshold Method: {settings['threshold_method']} \n"
                    f"Threshold Value: {settings['threshold_value_multiplier']} \n"
                    f"Dips: {settings['dips']}\n"
                    f"_________________________________________________________________________________"
                )

                # Update the previous settings
            self.previous_settings = settings.copy()
        else:
            # Create the information text for actual analysis
            info_text = (
                f"File Information:\n\n"
                f"Path: {file_name}\n\n"
                f"File Duration: {file_duration:.2f} seconds\n"
                f"Duration Tested: {duration_tested:.2f} seconds\n"
                f"Detected Events: {event_count}\n"
                f"Date and Time of Analysis: {date_time_str}\n"
                f"Time taken for Analysis: {round(time_taken, 3)} s\n"
                f"File Saved to: {file_path}\n"
                f"_________________________________________________________________________________\n\n"
            )

        # Ensure the cursor is at the end and append the new information text
        self.event_info_text_edit.moveCursor(QTextCursor.MoveOperation.End)
        self.event_info_text_edit.append(info_text)

    def generate_plot_animation(self, file_path):
        if hasattr(self, 'dI_data') and hasattr(self, 'log_dt_data'):
            # Get the axes limits from the data corresponding to the smallest threshold value
            dI_min = np.min(self.dI_data[0])
            dI_max = np.max(self.dI_data[0])
            log_dt_min = np.min(self.log_dt_data[0])
            log_dt_max = np.max(self.log_dt_data[0])

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            def animate(i):
                ax1.clear()
                ax2.clear()

                # Plot histogram of dI
                ax1.hist(self.dI_data[i], bins=100, color='blue', alpha=0.7)
                ax1.set_title(f'Histogram of dI | Counts: {len(self.dI_data[i])} | Threshold: {np.round(self.std_values[i], 2)}')
                ax1.set_xlabel('dI (nA)')
                ax1.set_ylabel('Frequency')
                ax1.set_xlim(dI_min, dI_max)

                # Plot scatter plot of dI vs log(dt*1e3)
                ax2.scatter(self.log_dt_data[i], self.dI_data[i], color='red', alpha=0.5, s=2)
                ax2.set_title(f'Scatter Plot of ΔI vs. log(Δt*1e3) | Threshold: {np.round(self.std_values[i], 2)}')
                ax2.set_xlabel('log(Δt (ms))')
                ax2.set_ylabel('ΔI (nA)')
                ax2.set_xlim(log_dt_min, log_dt_max)
                ax2.set_ylim(dI_min, dI_max)

            ani = animation.FuncAnimation(fig, animate, frames=len(self.dI_data), interval=200, repeat_delay=1000)
            plt.tight_layout()
            plt.show()

            # Save the animation as a GIF file using PillowWriter
            date_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            if self.save_file_path is not None:
                filename = f"{self.save_file_path}_plot_animation_{date_time_str}.gif"
            else:
                file_path_without_ext, _ = os.path.splitext(file_path)
                filename = f"{file_path_without_ext}_plot_animation_{date_time_str}.gif"
            
            # Set up the writer for saving the animation
            writer = animation.PillowWriter(fps=2)
            ani.save(filename, writer=writer)

class MLTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("Data Reduction for ML")
        group_layout = QFormLayout(group)
        
        self.enable_ml_data_reduction_checkbox = QCheckBox("Enable ML Data Reduction")
        self.enable_ml_data_reduction_checkbox.stateChanged.connect(self.toggle_ml_widgets)
        group_layout.addRow(self.enable_ml_data_reduction_checkbox)
        
        self.tag_label = QLabel("Tag:")
        self.tag_lineedit = QLineEdit()
        self.tag_lineedit.setText("BSA")
        group_layout.addRow(self.tag_label, self.tag_lineedit)
        
        self.apply_standardisation_checkbox = QCheckBox("Apply Standardisation?")
        self.apply_standardisation_checkbox.stateChanged.connect(self.toggle_standardisation_label)
        group_layout.addRow(self.apply_standardisation_checkbox)
        
        self.standardisation_label = QLabel("Please choose standardisation settings in the Fitting Options tab. If not chosen, results may not be correct.")
        self.standardisation_label.setWordWrap(True)
        self.standardisation_label.setVisible(False)
        group_layout.addRow(self.standardisation_label)
        
        self.data_reduction_type_label = QLabel("Type of Data Reduction:")
        self.data_reduction_type_combo = QComboBox()
        self.data_reduction_type_combo.addItems(["Scheme 1", "Scheme 2", "Scheme 3", "Scheme 4", "Scheme 5"])
        group_layout.addRow(self.data_reduction_type_label, self.data_reduction_type_combo)
        
        self.scheme_table = QTableWidget()
        self.scheme_table.setRowCount(5)
        self.scheme_table.setColumnCount(2)
        self.scheme_table.setHorizontalHeaderLabels(["Feature Extraction Scheme", "Features/Details"])
        self.scheme_table.setItem(0, 0, QTableWidgetItem("Scheme 1"))
        self.scheme_table.setItem(0, 1, QTableWidgetItem("Δi1, Δi2, … Δi10, Δt0/10"))
        self.scheme_table.setItem(1, 0, QTableWidgetItem("Scheme 2"))
        self.scheme_table.setItem(1, 1, QTableWidgetItem("Δi1, Δi2, … Δi10, Δt0/10, Δtfwhm, area, Δifwhm, Δimax"))
        self.scheme_table.setItem(2, 0, QTableWidgetItem("Scheme 3"))
        self.scheme_table.setItem(2, 1, QTableWidgetItem("Δi1, Δi2, … Δi10, Δt0/10, Δtfwhm, area, Δifwhm, Δimax , skew, kurtosis"))
        self.scheme_table.setItem(3, 0, QTableWidgetItem("Scheme 4"))
        self.scheme_table.setItem(3, 1, QTableWidgetItem("Δi1, Δi2, … Δi50, Δt0/50, Δtfwhm, area, Δifwhm, Δimax , skew, kurtosis"))
        self.scheme_table.setItem(4, 0, QTableWidgetItem("Scheme 5"))
        self.scheme_table.setItem(4, 1, QTableWidgetItem("Full signal, Δtfwhm, area, Δifwhm, Δimax , skew, kurtosis"))
        self.scheme_table.resizeColumnsToContents()
        group_layout.addRow(self.scheme_table)
        
        layout.addWidget(group)
        
        self.ml_widgets = [self.tag_label, self.tag_lineedit, self.apply_standardisation_checkbox, self.data_reduction_type_label, self.data_reduction_type_combo, self.scheme_table]
        self.toggle_ml_widgets()
        
    def toggle_ml_widgets(self):
        for widget in self.ml_widgets:
            widget.setVisible(self.enable_ml_data_reduction_checkbox.isChecked())
        
    def toggle_standardisation_label(self):
        self.standardisation_label.setVisible(self.apply_standardisation_checkbox.isChecked())
        

class LoadOptionsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Adjust margins as needed

        # Scroll Area Setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        
        # Button to select folder
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.selectFolder)
        
        # Include subfolders checkbox
        self.include_subfolders_chk = QCheckBox("Include Subfolders")
        
        # List widget to display .abf files
        self.files_list_widget = QListWidget()
        self.files_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        # Path display
        self.folder_path_label = QLabel(" ")
        self.folder_path_label.setWordWrap(True)

        # Select All checkbox
        self.select_all_chk = QCheckBox("Select All")
        self.select_all_chk.stateChanged.connect(self.selectAllFiles)
        self.select_all_chk.setTristate(False)
        
        # Testing duration setup with new layout structure
        testing_duration_main_layout = QVBoxLayout()  # Main vertical layout for the testing duration section

        # Label for Testing Duration, centered
        testing_duration_label = QLabel("Testing Duration")
        testing_duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        testing_duration_main_layout.addWidget(testing_duration_label)

        testing_duration_start_layout = QHBoxLayout()
        start_label = QLabel("Start:")
        testing_duration_start_layout.addWidget(start_label)  # Add Start label

        self.testing_duration_start_spinbox = QDoubleSpinBox()  # Make it an attribute of the class
        self.testing_duration_start_spinbox.setRange(0, 10000)  # Example range
        self.testing_duration_start_spinbox.setValue(0.000)  # Example start value
        self.testing_duration_start_spinbox.setDecimals(3)
        self.testing_duration_start_spinbox.setSuffix(" s")  # Unit
        testing_duration_start_layout.addWidget(self.testing_duration_start_spinbox)

        # Horizontal layout for End Duration label and spinbox
        testing_duration_end_layout = QHBoxLayout()
        end_label = QLabel("End:")
        testing_duration_end_layout.addWidget(end_label)  # Add End label

        self.testing_duration_end_spinbox = QDoubleSpinBox()  # Make it an attribute of the class
        self.testing_duration_end_spinbox.setRange(0, 10000)  # Example range
        self.testing_duration_end_spinbox.setValue(1.000)  # Example end value
        self.testing_duration_end_spinbox.setDecimals(3)
        self.testing_duration_end_spinbox.setSuffix(" s")  # Unit
        testing_duration_end_layout.addWidget(self.testing_duration_end_spinbox)

        # Adding the start and end layouts to the main vertical layout
        testing_duration_main_layout.addLayout(testing_duration_start_layout)
        testing_duration_main_layout.addLayout(testing_duration_end_layout)
        
        # Save Event Data
        self.save_event_chk = QCheckBox("Save Events individually for Clustering")
        self.save_event_chk.setTristate(False)
        testing_duration_main_layout.addWidget(self.save_event_chk)

        # Level Fitting DropDown
        level_fitting_layout = QHBoxLayout()
        level_fitting_layout.addWidget(QLabel("Do you want Level Fitting?"))
        self.level_fitting_combo = QComboBox()
        self.level_fitting_combo.addItems(["Yes", "No"])
        self.level_fitting_combo.setCurrentText("No")  # Default to "No"
        level_fitting_layout.addWidget(self.level_fitting_combo)


        self.test_settings_btn = QPushButton("Test Settings on File")
        #Create the Plot Data button 
        self.plot_data_btn = QPushButton("Plot Data")

        self.perform_data_reduction_btn = QPushButton("Perform Data Reduction")
        self.save_file_path_btn = QPushButton("Specify File Name (Saved Data)")

        self.selected_path_label = QLabel()
        self.selected_path_label.setWordWrap(True)
        self.selected_path_label.setVisible(False)  # Initially hidden
        

        #Adjust the layout to place the new button to the left of the Test Settings on File button
        button_layout = QHBoxLayout()  # Create a horizontal layout
        button_layout.addWidget(self.plot_data_btn)  # Add the Plot Data button first
        button_layout.addWidget(self.test_settings_btn)  # Then add the Test Settings on File button


        #Adjust the layout to place the new button to the left of the Test Settings on File button
        button_layout_2 = QHBoxLayout()  # Create a horizontal layout
        button_layout_2.addWidget(self.save_file_path_btn)  # Add the Plot Data button first
        button_layout_2.addWidget(self.perform_data_reduction_btn)  # Then add the Test Settings on File button

        #Adjust the layout to place the new button to the left of the Test Settings on File button
        button_layout_3 = QHBoxLayout()  # Create a horizontal layout
        button_layout_3.addWidget(self.selected_path_label)  # Add the selected path label
        
        # Adding widgets to layout
        scroll_layout.addWidget(self.select_folder_btn)
        scroll_layout.addWidget(self.include_subfolders_chk)
        scroll_layout.addWidget(self.folder_path_label)
        scroll_layout.addWidget(self.files_list_widget)
        scroll_layout.addWidget(self.select_all_chk)
        scroll_layout.addLayout(testing_duration_main_layout)
        scroll_layout.addLayout(level_fitting_layout)
        scroll_layout.addLayout(button_layout)
        scroll_layout.addLayout(button_layout_2)
        scroll_layout.addLayout(button_layout_3)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
    def selectFolder(self):
        options = QFileDialog.Option.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Select Folder", "", options=options)
        if directory:
            # Set text with word wrap for long paths
            self.folder_path_label.setText(f"Selected folder: {directory}")
            self.populateFileList(directory, self.include_subfolders_chk.isChecked())

    def populateFileList(self, directory, include_subfolders):
        self.files_list_widget.clear()  # Clear the existing list
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.abf') or file.endswith('.hdf5')or file.endswith('.h5'):
                    # Get the relative path
                    rel_path = os.path.relpath(os.path.join(root, file), start=directory)
                    item = QListWidgetItem(rel_path)  # Create a new QListWidgetItem
                    item.setData(Qt.ItemDataRole.UserRole, os.path.join(root, file))  # Store the full path
                    self.files_list_widget.addItem(item)  # Add the item to the list
            if not include_subfolders:
                # If we don't want to include subfolders, break after the first iteration
                break

    def selectAllFiles(self):
        is_checked = self.select_all_chk.isChecked()  # Directly check if the checkbox is checked
        for index in range(self.files_list_widget.count()):
            item = self.files_list_widget.item(index)
            item.setSelected(is_checked)

class EventSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Adjust margins as needed

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_area.setWidget(scroll_widget)      

        # Group 1: File settings
        file_settings_group = QGroupBox("File Settings")
        file_settings_layout = QFormLayout(file_settings_group)
        self.sampling_rate_spinbox = QDoubleSpinBox()
        self.sampling_rate_spinbox.setRange(1, 100000)  # 
        self.sampling_rate_spinbox.setValue(200)  # Default value
        self.sampling_rate_spinbox.setSuffix(" kHz")  # Unit
        self.analysis_start_duration_spinbox = QDoubleSpinBox()
        self.analysis_start_duration_spinbox.setRange(0, 100000)
        self.analysis_start_duration_spinbox.setValue(0)  # Default value
        self.analysis_start_duration_spinbox.setDecimals(3)
        self.analysis_start_duration_spinbox.setSuffix(" s")  # Unit
        self.analysis_end_duration_spinbox = QDoubleSpinBox()
        self.analysis_end_duration_spinbox.setRange(0, 100000)
        self.analysis_end_duration_spinbox.setValue(0)  # Default value
        self.analysis_end_duration_spinbox.setDecimals(3)
        self.analysis_end_duration_spinbox.setSuffix(" s")  # Unit
        self.dips_or_peaks_combo = QComboBox()
        self.dips_or_peaks_combo.addItems(["Dips","Peaks"])
        self.dips_or_peaks_combo.setCurrentIndex(0) #Default to "Dips"

        

        self.enable_nth_data_point_loading = QCheckBox("Enable Nth Data Point Loading")
        self.enable_nth_data_point_loading.stateChanged.connect(self.toggle_nth_data_point_loading_widgets)
        
        file_settings_layout.addRow("Sampling Rate:", self.sampling_rate_spinbox)
        file_settings_layout.addRow("Analysis Start Duration:", self.analysis_start_duration_spinbox)
        file_settings_layout.addRow("Analysis End Duration:", self.analysis_end_duration_spinbox)
        file_settings_layout.addRow("Dips or Peaks:", self.dips_or_peaks_combo)
        self.enable_analysis_time_specific = QCheckBox("Enable Analysis between the time specified above")
        file_settings_layout.addRow(self.enable_analysis_time_specific)
        file_settings_layout.addRow(self.enable_nth_data_point_loading)
        
    

        self.nth_data_point_spinbox = QDoubleSpinBox()
        self.nth_data_point_spinbox.setRange(1,1000)
        self.nth_data_point_spinbox.setValue(10)
        self.nth_data_point_label = QLabel("Load every nth point:")
        file_settings_layout.addRow(self.nth_data_point_label,self.nth_data_point_spinbox)
        self.nth_data_point_loading_widgets = [self.nth_data_point_spinbox,self.nth_data_point_label]
        self.toggle_nth_data_point_loading_widgets()


        self.enable_window_loading = QCheckBox("Enable Window Loading")
        self.enable_window_loading.stateChanged.connect(self.toggle_window_loading_widgets)
        #file_settings_layout.addRow(self.enable_window_loading)
        self.window_size_multiple_spinbox = QDoubleSpinBox()
        self.window_size_multiple_spinbox.setRange(1,1000)
        self.window_size_multiple_spinbox.setValue(10)
        self.window_size_multiple_label = QLabel("Multiple of avg/std Window Size(whichever is higher):")
        
        #Hiding the Window Loading Option

        #file_settings_layout.addRow(self.window_size_multiple_label, self.window_size_multiple_spinbox)

        
        #self.window_loading_widgets = [self.window_size_multiple_label, self.window_size_multiple_spinbox]
        #self.toggle_window_loading_widgets()

        self.enable_plots = QCheckBox("Enable Plots after Data Reduction")
        self.enable_plots.setChecked(True)  # Set the checkbox checked by default
        self.enable_plots.stateChanged.connect(self.toggle_enable_plots_widgets)
        file_settings_layout.addRow(self.enable_plots)
        self.enable_plots_label = QLabel("NOTE: This option only works when you reduce single file!")
        file_settings_layout.addRow(self.enable_plots_label)
        self.enable_plots_widgets = [self.enable_plots_label]
        self.toggle_enable_plots_widgets()

        self.save_plots = QCheckBox("Save Plots after Data Reduction")
        self.save_plots.setChecked(True)  # Set the checkbox checked by default
        self.save_plots.stateChanged.connect(self.toggle_enable_plots_widgets)
        file_settings_layout.addRow(self.save_plots)
        


        # Group 2: Low Pass Filter
        filtering_group = QGroupBox("Filtering Options")
        filtering_layout = QFormLayout(filtering_group)

        self.apply_filter_combo = QComboBox()
        self.apply_filter_combo.addItems(["Yes", "No"])
        self.apply_filter_combo.setCurrentIndex(0)  # Default to "Yes"
        filtering_layout.addRow("Apply Filter:", self.apply_filter_combo)

        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems(["Low Pass Filter", "Wavelet"])
        self.filter_type_combo.setCurrentIndex(0)  # Default to "Low Pass Filter"
        filtering_layout.addRow("Filter Type:", self.filter_type_combo)

        # Labels for additional options
        self.type_of_low_pass_filter_label = QLabel("Type of Low Pass Filter:")
        self.low_pass_filter_type_combo = QComboBox()
        self.low_pass_filter_type_combo.addItems(["Bessel", "Butterworth", "Chebyshev I", "Chebyshev II", "Elliptic", "FIR", "IIR"])
        self.low_pass_filter_type_combo.setCurrentIndex(1)  # Default to "Butterworth"

        self.cutoff_frequency_label = QLabel("Cutoff Frequency:")
        self.cutoff_frequency_spinbox = QDoubleSpinBox()
        self.cutoff_frequency_spinbox.setRange(1, 5000)  # Example range, adjust as needed
        self.cutoff_frequency_spinbox.setValue(35)
        self.cutoff_frequency_spinbox.setSuffix(" kHz")

        # Add labels and widgets but hide them initially
        filtering_layout.addRow(self.type_of_low_pass_filter_label, self.low_pass_filter_type_combo)
        filtering_layout.addRow(self.cutoff_frequency_label, self.cutoff_frequency_spinbox)

        self.low_pass_filter_type_combo.hide()
        self.cutoff_frequency_spinbox.hide()
        self.type_of_low_pass_filter_label.hide()
        self.cutoff_frequency_label.hide()

        def update_filter_options():
            # Show or hide low pass filter options based on the filter type selection
            if self.filter_type_combo.currentText() == "Low Pass Filter":
                self.low_pass_filter_type_combo.show()
                self.cutoff_frequency_spinbox.show()
                self.type_of_low_pass_filter_label.show()
                self.cutoff_frequency_label.show()
            else:
                self.low_pass_filter_type_combo.hide()
                self.cutoff_frequency_spinbox.hide()
                self.type_of_low_pass_filter_label.hide()
                self.cutoff_frequency_label.hide()

        self.filter_type_combo.currentTextChanged.connect(update_filter_options)

        # Initial call to ensure the UI is correctly set up for the default selection
        update_filter_options()

        # Group 3: Thresholds - Dynamic adjustment for threshold value will be implemented in its handler
        thresholds_group = QGroupBox("Thresholds")
        thresholds_layout = QFormLayout(thresholds_group)
        self.type_of_threshold_combo = QComboBox()
        self.type_of_threshold_combo.addItems(["ΔI", "std multiplier"])
        self.type_of_threshold_combo.setCurrentIndex(1)  # Set the second index as default

        self.std_calculation_method_combo = QComboBox()
        self.std_calculation_method_combo.addItems(["Rolling STD", "Whole STD"])
        self.std_calculation_method_combo.setCurrentIndex(0)  # Default to "Rolling STD"
        self.std_calculation_method_label = QLabel("Method of STD Calculation:")
        self.std_calculation_method_combo.currentTextChanged.connect(self.update_std_calculation_method)

        self.threshold_value_multiplier_spinbox = QDoubleSpinBox()
        # Default values and ranges set dynamically in a handler
        self.start_of_event_threshold_spinbox = QDoubleSpinBox()
        self.start_of_event_threshold_spinbox.setValue(0.1)  # Default value
        self.end_of_event_threshold_spinbox = QDoubleSpinBox()
        self.end_of_event_threshold_spinbox.setValue(0.1)  # Default value
        thresholds_layout.addRow("Type of Threshold:", self.type_of_threshold_combo)


        thresholds_layout.addRow(self.std_calculation_method_label, self.std_calculation_method_combo)
        # Hide the combo box initially
        self.std_calculation_method_label.setVisible(False)
        self.std_calculation_method_combo.setVisible(False)

        thresholds_layout.addRow("Threshold Value/Multiplier:", self.threshold_value_multiplier_spinbox)
        thresholds_layout.addRow("Start of Event Threshold:", self.start_of_event_threshold_spinbox)
        thresholds_layout.addRow("End of Event Threshold:", self.end_of_event_threshold_spinbox)

        # Handlers for dynamic value adjustments
        self.type_of_threshold_combo.currentTextChanged.connect(self.updateThresholdValueRange)
        self.updateThresholdValueRange(self.type_of_threshold_combo.currentText())  # Initial update

        # Group 4: Window Sizes
        window_sizes_group = QGroupBox("Window Sizes")
        window_sizes_layout = QFormLayout(window_sizes_group)

        self.mean_window_size_spinbox = QDoubleSpinBox()
        self.mean_window_size_spinbox.setRange(0.1, 10000)  # Min and max
        self.mean_window_size_spinbox.setValue(10)  # Default value
        self.mean_window_size_spinbox.setSuffix(" ms")  # Unit

        self.std_window_size_label = QLabel("Std Window Size:")
        self.std_window_size_spinbox = QDoubleSpinBox()
        self.std_window_size_spinbox.setRange(0.1, 10000)  # Min and max
        self.std_window_size_spinbox.setValue(250)  # Default value
        self.std_window_size_spinbox.setSuffix(" ms")  # Unit

        self.enable_std_smoothing_checkbox = QCheckBox("Enable Std Smoothing")
        self.enable_std_smoothing_checkbox.setChecked(False)
        self.enable_std_smoothing_checkbox.stateChanged.connect(lambda state: self.update_std_smoothing_options(state))

        self.smoothing_type_label = QLabel("Type of smoothing:")
        self.smoothing_type_dropdown = QComboBox()
        self.smoothing_type_dropdown.addItems(["Moving Mean Smoothing", "Exponential Smoothing"])
        self.smoothing_type_dropdown.setCurrentIndex(1)

        window_sizes_layout.addRow("Mean Window Size:", self.mean_window_size_spinbox)
        window_sizes_layout.addRow(self.std_window_size_label, self.std_window_size_spinbox)
        window_sizes_layout.addRow(self.enable_std_smoothing_checkbox)
        window_sizes_layout.addRow(self.smoothing_type_label, self.smoothing_type_dropdown)

        self.smoothing_type_label.setVisible(False)
        self.smoothing_type_dropdown.setVisible(False)

        # Group 5: Min, Max Event Widths
        event_widths_group = QGroupBox("Min, Max Event Widths")
        event_widths_layout = QFormLayout(event_widths_group)
        self.minimum_event_width_spinbox = QDoubleSpinBox()
        self.minimum_event_width_spinbox.setRange(0.000001, 100)  # Min and max
        self.minimum_event_width_spinbox.setDecimals(6)  # Increase precision for small values
        self.minimum_event_width_spinbox.setValue(0.001)  # Default value
        self.minimum_event_width_spinbox.setSuffix(" ms")  # Unit
        self.maximum_event_width_spinbox = QDoubleSpinBox()
        self.maximum_event_width_spinbox.setRange(1e-3, 10000)  # Min and max
        self.maximum_event_width_spinbox.setDecimals(6)  # Allow precision for large values
        self.maximum_event_width_spinbox.setValue(3)  # Default value
        self.maximum_event_width_spinbox.setSuffix(" ms")  # Unit
        event_widths_layout.addRow("Minimum Event Width:", self.minimum_event_width_spinbox)
        event_widths_layout.addRow("Maximum Event Width:", self.maximum_event_width_spinbox)

        # Adjusting layout for all groups to ensure alignment
        self.adjustGroupLayout(file_settings_group)
        self.adjustGroupLayout(filtering_group)  # Explicit adjustment might help
        self.adjustGroupLayout(thresholds_group)
        self.adjustGroupLayout(window_sizes_group)
        self.adjustGroupLayout(event_widths_group)

        # Add all groups to the main layout
        scroll_layout.addWidget(file_settings_group)
        scroll_layout.addWidget(filtering_group)
        scroll_layout.addWidget(thresholds_group)
        scroll_layout.addWidget(window_sizes_group)
        scroll_layout.addWidget(event_widths_group)
        layout.addWidget(scroll_area)


    def update_std_calculation_method(self, method):
        if method == "Whole STD":
            self.enable_std_smoothing_checkbox.setChecked(False)
            self.enable_std_smoothing_checkbox.setVisible(False)
            self.std_window_size_label.setText("Window Size for data selection:")
            self.std_window_size_spinbox.setValue(100)  # Set default value for Whole STD
            self.mean_window_size_spinbox.setValue(5)
        else:  # Rolling STD
            self.enable_std_smoothing_checkbox.setVisible(True)
            self.std_window_size_label.setText("Std Window Size:")
            self.std_window_size_spinbox.setValue(250)  # Set default value for Rolling STD
            self.mean_window_size_spinbox.setValue(10)
    
    def update_std_smoothing_options(self, state):
        if state == 2:
            self.smoothing_type_label.setVisible(True)
            self.smoothing_type_dropdown.setVisible(True)
            self.std_window_size_spinbox.setValue(10)  # Reset to default value
        else:
            self.smoothing_type_label.setVisible(False)
            self.smoothing_type_dropdown.setVisible(False)
            self.std_window_size_spinbox.setValue(250)  # Reset to default value

    def toggle_nth_data_point_loading_widgets(self):
        for widget in self.nth_data_point_loading_widgets:
            widget.setVisible(self.enable_nth_data_point_loading.isChecked())
    
    def toggle_window_loading_widgets(self):
        for widget in self.window_loading_widgets:
            widget.setVisible(self.enable_window_loading.isChecked())

    def toggle_enable_plots_widgets(self):
        for widget in self.enable_plots_widgets:
            widget.setVisible(self.enable_plots.isChecked())

    def updateThresholdValueRange(self, threshold_type):
        if threshold_type == "ΔI":
            self.threshold_value_multiplier_spinbox.setRange(100, 20000)
            self.threshold_value_multiplier_spinbox.setValue(2000)
            self.threshold_value_multiplier_spinbox.setSuffix(" pA")  # Unit
            self.std_calculation_method_label.setVisible(False)  # Hide the label
            self.std_calculation_method_combo.setVisible(False)  # Hide the combo box
        else:  # std multiplier
            self.threshold_value_multiplier_spinbox.setRange(1, 20)
            self.threshold_value_multiplier_spinbox.setValue(4)
            self.threshold_value_multiplier_spinbox.setSuffix(" ")  # Unit
            self.std_calculation_method_label.setVisible(True)  # Show the label
            self.std_calculation_method_combo.setVisible(True)  # Show the combo bo

    
    def adjustGroupLayout(self, group_box):
        group_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout = group_box.layout()
        if layout:
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align content to the left
            
            for i in range(layout.count()):
                item = layout.itemAt(i).widget()
                if item:
                    item.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)            

class FittingSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Adjust margins as needed

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_area.setWidget(scroll_widget)

        # Setting groups
        settings_group = QGroupBox("Fitting Settings")
        settings_layout = QFormLayout(settings_group)
        scroll_layout.addWidget(settings_group)

        self.padding_spinbox = QSpinBox()
        self.padding_spinbox.setRange(0, 10000)  # Min and max values
        self.padding_spinbox.setValue(100)  # Default value

        self.chunk_size_for_event_detection_spinbox = QSpinBox()
        self.chunk_size_for_event_detection_spinbox.setRange(1, 1000000000)  # Min and max values
        self.chunk_size_for_event_detection_spinbox.setValue(4000000)  # Default value

        self.chunk_size_for_event_fitting_spinbox = QSpinBox()
        self.chunk_size_for_event_fitting_spinbox.setRange(1, 100000)  # Min and max values
        self.chunk_size_for_event_fitting_spinbox.setValue(30)  # Default value

        self.chunk_size_for_peak_fitting_spinbox = QSpinBox()
        self.chunk_size_for_peak_fitting_spinbox.setRange(1, 100000)  # Min and max values
        self.chunk_size_for_peak_fitting_spinbox.setValue(30)  # Default value

        self.library_combo = QComboBox()
        self.library_combo.addItems(["ruptures",  "detecta", "lmfit", "hmm", "gmm"])
        self.library_combo.currentIndexChanged.connect(self.update_model_combo)

        self.model_combo = QComboBox()
        self.model_label = QLabel("Model:")

        self.num_components_spinbox = QSpinBox()
        self.num_components_spinbox.setRange(2, 10)  # Min and max values
        self.num_components_spinbox.setValue(2)  # Default value
        self.num_components_label = QLabel("Number of Components:")

        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.1, 100)  # Min and max values
        self.threshold_spinbox.setValue(1.2)  # Default value
        self.threshold_spinbox.setDecimals(2)  # Allows for fractional thresholds


        self.segment_rate_threshold_spinbox = QDoubleSpinBox()
        self.segment_rate_threshold_spinbox.setRange(0.001, 100)  # Min and max values
        self.segment_rate_threshold_spinbox.setValue(0.6)  # Default value
        self.segment_rate_threshold_spinbox.setDecimals(3)  # Allows for fractional thresholds

        self.change_rate_threshold_spinbox = QDoubleSpinBox()
        self.change_rate_threshold_spinbox.setRange(0.001, 100)  # Min and max values
        self.change_rate_threshold_spinbox.setValue(0.1)  # Default value
        self.change_rate_threshold_spinbox.setDecimals(3)  # Allows for fractional thresholds

        self.merge_segment_threshold_spinbox = QDoubleSpinBox()
        self.merge_segment_threshold_spinbox.setRange(0.001, 100)  # Min and max values
        self.merge_segment_threshold_spinbox.setValue(0.9)  # Default value
        self.merge_segment_threshold_spinbox.setDecimals(3)  # Allows for fractional thresholds

        settings_layout.addRow("Padding (in number of samples):", self.padding_spinbox)
        settings_layout.addRow("Chunk Size for Event Detection:", self.chunk_size_for_event_detection_spinbox)
        settings_layout.addRow("Chunk Size for Event Fitting:", self.chunk_size_for_event_fitting_spinbox)
        settings_layout.addRow("Chunk Size for Peak Fitting:", self.chunk_size_for_peak_fitting_spinbox)
        settings_layout.addRow("Library:", self.library_combo)
        settings_layout.addRow(self.model_label, self.model_combo)
        settings_layout.addRow(self.num_components_label, self.num_components_spinbox)
        settings_layout.addRow("Threshold:", self.threshold_spinbox)
        settings_layout.addRow("Segment Rate Threshold:", self.segment_rate_threshold_spinbox)
        settings_layout.addRow("Change Rate Threshold:", self.change_rate_threshold_spinbox)
        settings_layout.addRow("Merge Segment Threshold:", self.merge_segment_threshold_spinbox)

        layout.addWidget(scroll_area)

        standardisation_group = QGroupBox("Standardisation during Data Reduction")
        group_layout = QFormLayout(standardisation_group)
        scroll_layout.addWidget(standardisation_group)

        self.enable_standardisation_checkbox = QCheckBox("Enable Standardisation")
        self.enable_standardisation_checkbox.stateChanged.connect(self.toggle_standardisation_widgets)
        group_layout.addRow(self.enable_standardisation_checkbox)

        self.standardisation_type_label = QLabel("Which Standardisation to use:")
        self.standardisation_type_combo = QComboBox()
        self.standardisation_type_combo.addItems(["ΔI/I₀", "(ΔI*I₀)⁰·⁵", "(ΔI*I₀)ᵖᵒʷᵉʳ", "Dutt Standardisation"])
        self.standardisation_type_combo.currentIndexChanged.connect(self.update_standardisation_explanation)
        group_layout.addRow(self.standardisation_type_label, self.standardisation_type_combo)

        self.standardisation_explanation_label = QLabel()
        self.standardisation_explanation_label.setWordWrap(True)
        group_layout.addRow(self.standardisation_explanation_label)

        self.power_label = QLabel("Power:")
        self.power_spinbox = QDoubleSpinBox()
        self.power_spinbox.setRange(0.01, 10)
        self.power_spinbox.setValue(0.5)
        self.power_spinbox.setSingleStep(0.01)
        self.power_label.setVisible(False)
        self.power_spinbox.setVisible(False)
        group_layout.addRow(self.power_label, self.power_spinbox)

        self.length_label = QLabel("Length of the nanopore (L) (nm):")
        self.length_spinbox = QDoubleSpinBox()
        self.length_spinbox.setRange(1, 100)
        self.length_spinbox.setValue(7)
        self.length_spinbox.setSingleStep(0.1)
        self.length_label.setVisible(False)
        self.length_spinbox.setVisible(False)
        group_layout.addRow(self.length_label, self.length_spinbox)

        self.conductivity_label = QLabel("σ (Conductivity of the solution) (S/m):")
        self.conductivity_spinbox = QDoubleSpinBox()
        self.conductivity_spinbox.setRange(0.1, 100)
        self.conductivity_spinbox.setValue(10.5)
        self.conductivity_spinbox.setSingleStep(0.1)
        self.conductivity_label.setVisible(False)
        self.conductivity_spinbox.setVisible(False)
        group_layout.addRow(self.conductivity_label, self.conductivity_spinbox)

        self.voltage_label = QLabel("V (Voltage Applied) (mV):")
        self.voltage_spinbox = QDoubleSpinBox()
        self.voltage_spinbox.setRange(10, 2000)
        self.voltage_spinbox.setValue(400)
        self.voltage_spinbox.setSingleStep(1)
        self.voltage_label.setVisible(False)
        self.voltage_spinbox.setVisible(False)
        group_layout.addRow(self.voltage_label, self.voltage_spinbox)

        self.open_pore_current_label = QLabel("I₀ (Open Pore Current) (nA):")
        self.open_pore_current_spinbox = QDoubleSpinBox()
        self.open_pore_current_spinbox.setRange(-500, 500)
        self.open_pore_current_spinbox.setValue(25)
        self.open_pore_current_spinbox.setSingleStep(0.1)
        self.open_pore_current_label.setVisible(False)
        self.open_pore_current_spinbox.setVisible(False)
        group_layout.addRow(self.open_pore_current_label, self.open_pore_current_spinbox)

        check_values_group = QGroupBox("Check Values")
        check_values_layout = QFormLayout(check_values_group)
        scroll_layout.addWidget(check_values_group)

        self.delta_i_label = QLabel("ΔI (Change in Current) (nA):")
        self.delta_i_spinbox = QDoubleSpinBox()
        self.delta_i_spinbox.setRange(-500, 500)
        self.delta_i_spinbox.setValue(1)
        self.delta_i_spinbox.setSingleStep(0.1)
        check_values_layout.addRow(self.delta_i_label, self.delta_i_spinbox)

        self.check_values_button = QPushButton("Check Values")
        self.check_values_button.clicked.connect(self.check_values)
        check_values_layout.addRow(self.check_values_button)

        self.check_values_result_label = QLabel()
        check_values_layout.addRow(self.check_values_result_label)

        self.check_values_group = check_values_group
        self.check_values_group.setVisible(False)

        layout.addWidget(scroll_area)

        self.standardisation_widgets = [
            self.standardisation_type_label,
            self.standardisation_type_combo,
            self.standardisation_explanation_label,
            self.power_label,
            self.power_spinbox,
            self.length_label,
            self.length_spinbox,
            self.conductivity_label,
            self.conductivity_spinbox,
            self.voltage_label,
            self.voltage_spinbox,
            self.open_pore_current_label,
            self.open_pore_current_spinbox
        ]
        self.toggle_standardisation_widgets()

        self.update_model_combo(0)  # Initialize the model combo based on the default library
        self.update_standardisation_explanation(0)

    def check_values(self):
        l = self.length_spinbox.value()*10**(-9)
        delta_i = self.delta_i_spinbox.value()*10**(-9)
        v = self.voltage_spinbox.value()/1000
        sigma = self.conductivity_spinbox.value()
        i0 = self.open_pore_current_spinbox.value()*10**(-9)

        d = i0 + (i0 * (i0 + 16 * l * v * sigma / np.pi)) ** 0.5 / (2 * v * sigma)
        condition = sigma > (4 * l * delta_i / v + d * np.pi * delta_i / v) / (d ** 2 * np.pi)
        condition1  = delta_i<i0

        if condition and condition1:
            self.check_values_result_label.setText("The entered values should work and you will get a good standardisation.")
        else:
            self.check_values_result_label.setText("The entered values will not work. Something is wrong!")
        self.check_values_result_label.setWordWrap(True)


    def update_model_combo(self, index):
        library = self.library_combo.currentText()
        self.model_combo.clear()

        if library in ["ruptures", "detecta",  "lmfit"]:
            self.model_label.setVisible(True)
            self.model_combo.setVisible(True)
            self.num_components_label.setVisible(False)
            self.num_components_spinbox.setVisible(False)

            if library == "ruptures":
                self.model_combo.addItems(["l1", "l2", "rbf"])
                self.model_combo.setCurrentIndex(1)
                self.model_combo.setCurrentIndex(1)
            elif library == "detecta":
                self.model_combo.addItems(["cusum"])
            elif library == "lmfit":
                self.model_combo.addItems(["autostepfinder"])
        else:
            self.model_label.setVisible(False)
            self.model_combo.setVisible(False)
            self.num_components_label.setVisible(True)
            self.num_components_spinbox.setVisible(True)

    def toggle_standardisation_widgets(self):
        enabled = self.enable_standardisation_checkbox.isChecked()
        for widget in self.standardisation_widgets:
            widget.setVisible(enabled)

        if enabled:
            self.update_standardisation_explanation(self.standardisation_type_combo.currentIndex())
        else:
            self.power_label.setVisible(False)
            self.power_spinbox.setVisible(False)
            self.length_label.setVisible(False)
            self.length_spinbox.setVisible(False)
            self.conductivity_label.setVisible(False)
            self.conductivity_spinbox.setVisible(False)
            self.voltage_label.setVisible(False)
            self.voltage_spinbox.setVisible(False)
            self.open_pore_current_label.setVisible(False)
            self.open_pore_current_spinbox.setVisible(False)
            self.check_values_group.setVisible(False)

    def update_standardisation_explanation(self, index):
        self.power_label.setVisible(index == 2)
        self.power_spinbox.setVisible(index == 2)
        self.length_label.setVisible(index == 3)
        self.length_spinbox.setVisible(index == 3)
        self.conductivity_label.setVisible(index == 3)
        self.conductivity_spinbox.setVisible(index == 3)
        self.voltage_label.setVisible(index == 3)
        self.voltage_spinbox.setVisible(index == 3)
        self.open_pore_current_label.setVisible(index == 3)
        self.open_pore_current_spinbox.setVisible(index == 3)
        self.check_values_group.setVisible(index == 3)


        if index == 0:
            self.standardisation_explanation_label.setText("ΔI<sub>new</sub> = ΔI/I<sub>0</sub>")
        elif index == 1:
            self.standardisation_explanation_label.setText("ΔI<sub>new</sub> = (ΔI*I<sub>0</sub>)<sup>0.5</sup>")
        elif index == 2:
            self.standardisation_explanation_label.setText("ΔI<sub>new</sub> = (ΔI*I<sub>0</sub>)<sup>power</sup><br>"
                                                        "Beware of using this option as some parts of ΔI<sub>new</sub> would be favoured as compared to others with changing values of power. "
                                                        "Also beware of the units as except for power = 0.5, the units are not nA.")
        elif index == 3:
            self.standardisation_explanation_label.setText("Fo more information on this, talk with Shankar Dutt (shankar.dutt@anu.edu.au)")
        elif index == 4:
            explanation = "According to Kowalczyk Model:<br>" \
                        "I<sub>0</sub> = σ*V*(4*L/(π*d<sup>2</sup>)+1/d)<sup>(-1)</sup><br>" \
                        " <br>"\
                        "ΔI = I<sub>0</sub>-(1*V*σ)/((1.27324*L)/(-1* d<sub>bio</sub><sup>2</sup>+(0.25*(I<sub>0</sub>+(I<sub>0</sub>*(I<sub>0</sub>+5.09296*L*V*σ)) <br>"\
                        "<sup>0.5</sup>)<sup>2</sup>)/(V<sup>2</sup> *σ<sup>2</sup>))+1/((-1* d<sub>bio</sub><sup>2</sup>+(0.25*(I<sub>0</sub>+(I<sub>0</sub>* (I<sub>0</sub>+5.09296*L*V*σ))<sup>0.5</sup>)<sup>2</sup>)/(V<sup>2</sup>*σ<sup>2</sup>))<sup>0.5</sup>)<br>" \
                        "<br> "\
                        "ΔI<sub>new</sub> = ΔI*(I<sub>0_new</sub>-(1*V*σ)/(2.50663/(((3.14159*I<sub>0_new</sub><sup>2</sup>+8*I<sub>0_new</sub>*L*V*σ-6.28319*d<sub>bio</sub><sup>2</sup>*V<sup>2</sup>*σ<sup>2</sup>+ <br>" \
                        "1.77245*I<sub>0_new</sub>*(I<sub>0_new</sub>*(3.14159*I<sub>0_new</sub>+16*L*V*σ))<sup>0.5</sup>)/(V<sup>2</sup>*σ<sup>2</sup>))<sup>0.5</sup>)+(1.27324*L)/ <br>" \
                        "(-1*d<sub>bio</sub><sup>2</sup>+ (0.25*(I<sub>0_new</sub>+(I<sub>0_new</sub>*(I<sub>0_new</sub>+5.09296*L*V*σ))<sup>0.5</sup>)<sup>2</sup>)/(V<sup>2</sup> <br> " \
                        "*σ<sup>2</sup>))))/(I<sub>0</sub>-(1*V*σ)/(2.50663*/(((3.14159*I<sub>0</sub><sup>2</sup>+ 8*I<sub>0</sub>*L*V*σ-6.28319*d<sub>bio</sub><sup>2</sup>*V<sup>2</sup>*σ<sup>2</sup>+ <br> "\
                        "1.77245*I<sub>0</sub>*(I<sub>0</sub>*(3.14159*I<sub>0</sub>+16*L*V*σ))<sup>0.5</sup>)/(V<sup>2</sup>*σ<sup>2</sup>))<sup>0.5</sup>)+(1.27324*L)/(-1*d<sub>bio</sub><sup>2</sup>+ <br> "\
                        "(0.25*(i0+(I<sub>0</sub>*(I<sub>0</sub>+5.09296*L*V*σ))<sup>0.5</sup>)<sup>2</sup>)/(V<sup>2</sup>*σ<sup>2</sup>))))"
            self.standardisation_explanation_label.setText(explanation)


class DataReductionTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Data Reduction with Different Thresholds")
        group_layout = QFormLayout(group)

        self.threshold_type_combo = QComboBox()
        self.threshold_type_combo.addItems(["std multiplier", "ΔI"])
        self.threshold_type_combo.currentTextChanged.connect(self.update_threshold_range)
        group_layout.addRow("Type of Threshold:", self.threshold_type_combo)

        self.start_threshold_spinbox = QDoubleSpinBox()
        self.start_threshold_spinbox.setRange(0.1, 100000)
        self.start_threshold_spinbox.setValue(3)
        self.start_threshold_spinbox.setSingleStep(0.1)
        group_layout.addRow("Start Threshold Value/Multiplier:", self.start_threshold_spinbox)

        self.end_threshold_spinbox = QDoubleSpinBox()
        self.end_threshold_spinbox.setRange(0.1, 100000)
        self.end_threshold_spinbox.setValue(4)
        self.end_threshold_spinbox.setSingleStep(0.1)
        group_layout.addRow("End Threshold Value/Multiplier:", self.end_threshold_spinbox)

        self.num_steps_spinbox = QSpinBox()
        self.num_steps_spinbox.setRange(1, 100)
        self.num_steps_spinbox.setValue(20)
        group_layout.addRow("Number of Steps:", self.num_steps_spinbox)

        self.settings_label = QLabel("All other settings are the same as set in different tabs")
        self.settings_label.setWordWrap(True)
        group_layout.addRow(self.settings_label)

        self.perform_data_reduction_button = QPushButton("Perform Data Reduction")
        self.perform_data_reduction_button.clicked.connect(self.perform_data_reduction)
        group_layout.addRow(self.perform_data_reduction_button)

        layout.addWidget(group)

    def update_threshold_range(self, threshold_type):
        if threshold_type == "std multiplier":
            self.start_threshold_spinbox.setRange(0.1, 100)
            self.start_threshold_spinbox.setValue(3)
            self.start_threshold_spinbox.setSuffix(" ")  # Unit
            self.start_threshold_spinbox.setSingleStep(0.1)
            self.end_threshold_spinbox.setRange(0.1, 100)
            self.end_threshold_spinbox.setValue(5)
            self.end_threshold_spinbox.setSuffix(" ")  # Unit
            self.end_threshold_spinbox.setSingleStep(0.1)
        else:  # difference
            self.start_threshold_spinbox.setRange(100, 100000)
            self.start_threshold_spinbox.setValue(1000)
            self.start_threshold_spinbox.setSuffix(" pA")  # Unit
            self.start_threshold_spinbox.setSingleStep(100)
            self.end_threshold_spinbox.setRange(100, 100000)
            self.end_threshold_spinbox.setValue(3000)
            self.end_threshold_spinbox.setSuffix(" pA")  # Unit
            self.end_threshold_spinbox.setSingleStep(100)

    def perform_data_reduction(self):
        std_values = []
        event_counts = []
        selected_items = self.main_window.load_options_tab.files_list_widget.selectedItems()
        if selected_items:
            file_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
            threshold_type = self.threshold_type_combo.currentText()
            start_threshold = self.start_threshold_spinbox.value()
            end_threshold = self.end_threshold_spinbox.value()
            num_steps = self.num_steps_spinbox.value()

            step_size = (end_threshold - start_threshold) / (num_steps - 1)

            dialog = ProcessingDialog(self)
            dialog.show()
            QApplication.processEvents()

            for i in range(num_steps):
                threshold_value = start_threshold + i * step_size
                events = self.main_window.process_single_file_multi_threshold(file_path, threshold_type, threshold_value)
                std_values.append(threshold_value)
                event_counts.append(len(events))

            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Information)
            msgBox.setWindowTitle("Success")
            msgBox.setText("Data Reduction performed successfully!")
            msgBox.setInformativeText(f"Number of Events Detected: {len(events)}")
            msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
            msgBox.exec()

            dialog.close()

            # Create and show the event count graph
            graph_dialog = EventCountGraph(std_values, event_counts, self)
            graph_dialog.exec()

            # Generate and save the plot animation
            self.main_window.generate_plot_animation(file_path)

class EventCountGraph(QDialog):
    def __init__(self, std_values, event_counts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Number of Events vs. STD Values | SD Data Reduction App")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout(self)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        ax = self.figure.add_subplot(111)
        ax.plot(std_values, event_counts, marker='o')
        ax.set_xlabel("STD Values")
        ax.set_ylabel("Number of Events")
        ax.set_title("Number of Events vs. STD Values")
        ax.grid(True)

        layout.addWidget(self.canvas)

        self.save_button = QPushButton("Save Graph")
        self.save_button.clicked.connect(self.save_graph)
        layout.addWidget(self.save_button)

    def save_graph(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "PNG Files (*.png);;All Files (*)", options=options)
        if file_name:
            self.figure.savefig(file_name)
            QMessageBox.information(self, "Graph Saved", f"The graph has been saved to {file_name}")

class ProcessingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SD Data Reduction App")
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()
        self.label = QLabel("Please wait, Data Reduction is in progress...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)



class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)



def main():
    app = QApplication(sys.argv)

    app.setStyle(QStyleFactory.create('Fusion'))  # Use Fusion or other available styles
    # Customize the palette for a darker, more modern look
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)


    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()