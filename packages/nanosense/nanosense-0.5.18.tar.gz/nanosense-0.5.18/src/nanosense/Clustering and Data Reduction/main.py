import os
import numpy as np
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                               QPushButton, QCheckBox, QListWidget, QFileDialog, QTabWidget,
                               QComboBox, QDoubleSpinBox, QGroupBox, QFormLayout, QLineEdit,
                               QTableWidget, QTableWidgetItem, QScrollArea, QSpinBox, QRadioButton,QListWidgetItem, QStyleFactory, QMessageBox,
                               QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, AgglomerativeClustering, AffinityPropagation, MeanShift
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score
from joblib import Parallel, delayed
from tqdm import tqdm
import multiprocessing as mp
import math
import scipy.stats as stats
import scipy.signal as sig
from datetime import datetime 
from scipy.ndimage import uniform_filter1d



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


def standardize_events(events, standard, event_baseline_mean, standard_power, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA):
    standardized_events = []
    
    for event in events:
        if standard == "Normal":
            standardized_event = event
        elif standard == "ΔI/I₀":
            standardized_event = event / event_baseline_mean
        elif standard == "(ΔI*I₀)⁰·⁵":
            standardized_event = (np.abs(event) * np.abs(event_baseline_mean)) ** 0.5
        elif standard == "(ΔI*I₀)ᵖᵒʷᵉʳ":
            standardized_event = (np.abs(event) * np.abs(event_baseline_mean)) ** standard_power
        elif standard == "Dutt Standardisation":
            standardized_event = normalize_signal(event, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA, event_baseline_mean)
        else:
            standardized_event = event
        
        standardized_events.append(standardized_event)
    
    return standardized_events

def analyze_event(event_signal, event_baseline_mean, sampling_rate, ML_standardisation_settings):
    standard, ML_enabled, ML_standard,  standard_power, standard_length_nm, standard_conductivity_S_m, standard_voltage_applied_mV, standard_open_pore_current_nA =  ML_standardisation_settings['standard'],  ML_standardisation_settings['ML_enabled'],  ML_standardisation_settings['ML_standard'],  ML_standardisation_settings['standard_power'], ML_standardisation_settings['standard_length_nm'], ML_standardisation_settings['standard_conductivity_S_m'], ML_standardisation_settings['standard_voltage_applied_mV'], ML_standardisation_settings['standard_open_pore_current_nA']

    if ML_enabled == "False":
        signal = np.abs(event_signal)

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
            signal = np.abs(event_signal)
            
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
            signal = np.abs(event_signal)

            
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

            signal = np.abs(event_signal)
            
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
            signal = np.abs(event_signal)
            
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

            signal = np.abs(event_signal)
            
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
            
def analyze_events_chunk(chunk, data, sampling_rate, ML_standardisation_settings):
    return [analyze_event(event['event_data'], event['baseline_value'], sampling_rate, ML_standardisation_settings) for event in chunk]

def save_chunked_event_analysis_to_npz(chunk_size, data, events, sampling_rate, ML_standardisation_settings):
    event_chunks = np.array_split(events, max(1, len(events) // chunk_size))
    analysis_results = Parallel(n_jobs=-1)(
        delayed(analyze_events_chunk)(chunk, data, sampling_rate, ML_standardisation_settings) for chunk in event_chunks
    )

    flattened_results = np.array([item for sublist in analysis_results for item in sublist], dtype=np.float64)
    return flattened_results

def process_chunk(data_chunk, algorithm, num_clusters_determination, num_clusters_spinbox_value,
                  max_clusters_silhouette_spinbox_value, max_clusters_db_spinbox_value,
                  threshold_spinbox_value, covariance_type_combo_value, linkage_combo_value,
                  damping_spinbox_value, bandwidth_spinbox_value):
    
    # Convert data_chunk to a NumPy array
    data_chunk = np.array(data_chunk)

    # Remove NaN values from the data chunk
    data_chunk = data_chunk[~np.isnan(data_chunk).any(axis=1), :]

    # Check if data_chunk has any samples after removing NaN values
    if data_chunk.shape[0] == 0:
        return np.array([]), None

    if algorithm == "K-Means Clustering":
        if num_clusters_determination == "Manual":
            num_clusters = min(num_clusters_spinbox_value, data_chunk.shape[0])
        elif num_clusters_determination == "Silhouette Method":
            max_clusters = min(max_clusters_silhouette_spinbox_value, data_chunk.shape[0])
            best_score = -1
            best_num_clusters = 2
            for num_clusters in range(2, max_clusters + 1):
                if num_clusters >= data_chunk.shape[0]:
                    break
                kmeans = KMeans(n_clusters=num_clusters, n_init='auto')
                labels = kmeans.fit_predict(data_chunk)
                if len(np.unique(labels)) < 2:
                    continue
                score = silhouette_score(data_chunk, labels)
                if score > best_score:
                    best_score = score
                    best_num_clusters = num_clusters
            num_clusters = min(best_num_clusters, data_chunk.shape[0] - 1)
        elif num_clusters_determination == "Davies-Bouldin Index":
            max_clusters = min(max_clusters_db_spinbox_value, data_chunk.shape[0])
            best_score = float('inf')
            best_num_clusters = 2
            for num_clusters in range(2, max_clusters + 1):
                if num_clusters >= data_chunk.shape[0]:
                    break
                kmeans = KMeans(n_clusters=num_clusters, n_init='auto')
                labels = kmeans.fit_predict(data_chunk)
                if len(np.unique(labels)) < 2:
                    continue
                score = davies_bouldin_score(data_chunk, labels)
                if score < best_score:
                    best_score = score
                    best_num_clusters = num_clusters
            num_clusters = min(best_num_clusters, data_chunk.shape[0] - 1)
        else:  # Threshold
            threshold = threshold_spinbox_value
            max_clusters = min(20, data_chunk.shape[0])
            num_clusters = 2
            
            # Calculate the maximum distance between any two data points
            max_distance_data = 0
            for i in range(data_chunk.shape[0]):
                for j in range(i+1, data_chunk.shape[0]):
                    distance = np.linalg.norm(data_chunk[i] - data_chunk[j])
                    if distance > max_distance_data:
                        max_distance_data = distance
            
            while num_clusters < max_clusters:
                kmeans = KMeans(n_clusters=num_clusters, n_init='auto')
                labels = kmeans.fit_predict(data_chunk)
                centroids = kmeans.cluster_centers_
                
                max_distance_centroid = 0
                for i in range(data_chunk.shape[0]):
                    distance = np.linalg.norm(data_chunk[i] - centroids[labels[i]])
                    if distance > max_distance_centroid:
                        max_distance_centroid = distance
                
                if max_distance_centroid <= threshold * max_distance_data:
                    break
                
                num_clusters += 1
            
            if num_clusters == max_clusters:
                print("Threshold not satisfied. Using maximum number of clusters.")
        
        if num_clusters > 0:
            kmeans = KMeans(n_clusters=num_clusters, n_init='auto')
            labels = kmeans.fit_predict(data_chunk)
            centroids = kmeans.cluster_centers_
        else:
            labels = np.array([])
            centroids = None
        
        return labels, centroids


    elif algorithm == "GMM":
        if num_clusters_determination == "Manual":
            num_components = num_clusters_spinbox_value
            num_components = min(num_components, data_chunk.shape[0])
        elif num_clusters_determination == "Silhouette Method":
            max_clusters = max_clusters_silhouette_spinbox_value
            max_clusters = min(max_clusters, data_chunk.shape[0])
            best_score = -1
            best_num_components = 2
            for num_components in range(2, max_clusters + 1):
                gmm = GaussianMixture(n_components=num_components, covariance_type=covariance_type_combo_value)
                labels = gmm.fit_predict(data_chunk)
                if len(np.unique(labels)) < 2:
                    continue
                score = silhouette_score(data_chunk, labels)
                if score > best_score:
                    best_score = score
                    best_num_components = num_components
        elif num_clusters_determination == "Davies-Bouldin Index":
            max_clusters = max_clusters_db_spinbox_value
            max_clusters = min(max_clusters, data_chunk.shape[0])
            best_score = float('inf')
            best_num_components = 2
            for num_components in range(2, max_clusters + 1):
                gmm = GaussianMixture(n_components=num_components, covariance_type=covariance_type_combo_value)
                labels = gmm.fit_predict(data_chunk)
                if len(np.unique(labels)) < 2:
                    continue
                score = davies_bouldin_score(data_chunk, labels)
                if score < best_score:
                    best_score = score
                    best_num_components = num_components
        else:  # Threshold
            threshold = threshold_spinbox_value
            max_clusters = 20
            num_components = 2
            
            # Calculate the maximum distance between any two data points
            max_distance_data = 0
            for i in range(data_chunk.shape[0]):
                for j in range(i+1, data_chunk.shape[0]):
                    distance = np.linalg.norm(data_chunk[i] - data_chunk[j])
                    if distance > max_distance_data:
                        max_distance_data = distance
            
            while num_components < max_clusters:
                gmm = GaussianMixture(n_components=num_components, covariance_type=covariance_type_combo_value)
                labels = gmm.fit_predict(data_chunk)
                centroids = gmm.means_
                
                max_distance_centroid = 0
                for i in range(data_chunk.shape[0]):
                    distance = np.linalg.norm(data_chunk[i] - centroids[labels[i]])
                    if distance > max_distance_centroid:
                        max_distance_centroid = distance
                
                if max_distance_centroid <= threshold * max_distance_data:
                    break
                
                num_components += 1
            
            if num_components == max_clusters:
                print("Threshold not satisfied. Using maximum number of components.")

        best_num_components = min(num_components, data_chunk.shape[0])

        if best_num_components > 0:
            gmm = GaussianMixture(n_components=best_num_components, covariance_type=covariance_type_combo_value)
            labels = gmm.fit_predict(data_chunk)
        else:
            labels = np.array([])

        return labels, None

    elif algorithm == "Hierarchical Clustering":
        linkage = linkage_combo_value
        if num_clusters_determination == "Manual":
            num_clusters = num_clusters_spinbox_value
            num_clusters = min(num_clusters, data_chunk.shape[0])
            hierarchical = AgglomerativeClustering(n_clusters=num_clusters, linkage=linkage)
            labels = hierarchical.fit_predict(data_chunk)
            return labels, None
        else:
            if num_clusters_determination == "Silhouette Method":
                max_clusters = max_clusters_silhouette_spinbox_value
                max_clusters = min(max_clusters, data_chunk.shape[0])
                best_score = -1
                best_num_clusters = 2
                for num_clusters in range(2, max_clusters + 1):
                    if num_clusters >= data_chunk.shape[0]:
                        break
                    hierarchical = AgglomerativeClustering(n_clusters=num_clusters, linkage=linkage)
                    labels = hierarchical.fit_predict(data_chunk)
                    if len(np.unique(labels)) < 2:
                        continue
                    score = silhouette_score(data_chunk, labels)
                    if score > best_score:
                        best_score = score
                        best_num_clusters = num_clusters
                best_num_clusters = min(best_num_clusters, data_chunk.shape[0] - 1)
            elif num_clusters_determination == "Davies-Bouldin Index":
                max_clusters = max_clusters_db_spinbox_value
                max_clusters = min(max_clusters, data_chunk.shape[0])
                best_score = float('inf')
                best_num_clusters = 2
                for num_clusters in range(2, max_clusters + 1):
                    if num_clusters >= data_chunk.shape[0]:
                        break
                    hierarchical = AgglomerativeClustering(n_clusters=num_clusters, linkage=linkage)
                    labels = hierarchical.fit_predict(data_chunk)
                    if len(np.unique(labels)) < 2:
                        continue
                    score = davies_bouldin_score(data_chunk, labels)
                    if score < best_score:
                        best_score = score
                        best_num_clusters = num_clusters
                best_num_clusters = min(best_num_clusters, data_chunk.shape[0] - 1)
            else:  # Threshold
                threshold = threshold_spinbox_value
                max_clusters = max_clusters_silhouette_spinbox_value
                max_clusters = min(max_clusters, data_chunk.shape[0])
                num_clusters = 2
                best_num_clusters = num_clusters  # Initialize best_num_clusters
                while num_clusters < max_clusters:
                    hierarchical = AgglomerativeClustering(n_clusters=num_clusters, linkage=linkage)
                    labels = hierarchical.fit_predict(data_chunk)
                    if len(np.unique(labels)) < 2:
                        num_clusters += 1
                        continue
                    score = silhouette_score(data_chunk, labels)
                    if score >= threshold:
                        best_num_clusters = num_clusters
                        break
                    num_clusters += 1

        if best_num_clusters > 0:
            hierarchical = AgglomerativeClustering(n_clusters=best_num_clusters, linkage=linkage)
            labels = hierarchical.fit_predict(data_chunk)
        else:
            labels = np.array([])

        return labels, None

    elif algorithm == "Affinity Propagation":
        damping = damping_spinbox_value
        affinity = AffinityPropagation(damping=damping, max_iter = 2000)
        labels = affinity.fit_predict(data_chunk)

        return labels, None

    elif algorithm == "Mean Shift":
        bandwidth = bandwidth_spinbox_value
        mean_shift = MeanShift(bandwidth=bandwidth)
        labels = mean_shift.fit_predict(data_chunk)

        return labels, None

class SDEventClusteringApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SD Event Clustering and Data Reduction App")
        self.setGeometry(100, 100, 1200, 800)
        self.data = None
        self.events_data = {}

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 7)

        # Left side
        self.title_label = QLabel('SD Event Clustering and Data Reduction App')
        self.title_label.setFont(QFont('Arial', 23, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label = QLabel('shankar.dutt@anu.edu.au')
        self.subtitle_label.setFont(QFont('Arial', 15, QFont.Weight.Bold))
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.title_label)
        left_layout.addWidget(self.subtitle_label)

        self.tabs = QTabWidget()
        left_layout.addWidget(self.tabs)

        # Load files tab
        load_files_tab = QWidget()
        load_files_layout = QVBoxLayout(load_files_tab)

        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.include_subfolders_chk = QCheckBox("Include Subfolders")
        self.files_list_widget = QListWidget()
        #self.files_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.files_list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.folder_path_label = QLabel(" ")
        self.folder_path_label.setWordWrap(True)
        load_files_layout.addWidget(self.select_folder_btn)
        load_files_layout.addWidget(self.include_subfolders_chk)
        load_files_layout.addWidget(self.files_list_widget)
        load_files_layout.addWidget(self.folder_path_label)

        self.perform_clustering_btn = QPushButton("Perform Clustering")
        self.perform_clustering_btn.clicked.connect(self.perform_clustering)
        self.perform_clustering_data_reduction_btn = QPushButton("Perform Clustering and Data Reduction")
        self.perform_clustering_data_reduction_btn.clicked.connect(self.perform_clustering_data_reduction)
        load_files_layout.addWidget(self.perform_clustering_btn)
        load_files_layout.addWidget(self.perform_clustering_data_reduction_btn)

        self.tabs.addTab(load_files_tab, "Load Files")

        # Clustering settings tab
        clustering_settings_tab = QWidget()
        clustering_settings_layout = QVBoxLayout(clustering_settings_tab)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        clustering_settings_layout.addWidget(scroll_area)

        # Alignment and Padding Settings
        alignment_padding_group = QGroupBox("Alignment and Padding Settings")
        alignment_padding_layout = QFormLayout(alignment_padding_group)

        # Alignment method
        self.alignment_method_label = QLabel("Alignment Method:")
        self.alignment_method_combo = QComboBox()
        self.alignment_method_combo.addItems(["Maximum", "Minimum", "Center"])
        self.alignment_method_combo.setCurrentIndex(1)
        alignment_padding_layout.addRow(self.alignment_method_label, self.alignment_method_combo)

        # Padding method
        self.padding_method_label = QLabel("Padding Method:")
        self.padding_method_combo = QComboBox()
        self.padding_method_combo.addItems(["NaN", "Zero"])
        self.padding_method_combo.setCurrentIndex(1)
        alignment_padding_layout.addRow(self.padding_method_label, self.padding_method_combo)

        scroll_layout.addWidget(alignment_padding_group)

        # Clustering Algorithm Group
        algorithm_group = QGroupBox("Clustering Algorithm")
        algorithm_layout = QFormLayout(algorithm_group)
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["K-Means Clustering", "GMM", "Hierarchical Clustering",
                                    "Affinity Propagation", "Mean Shift"])
        self.algorithm_combo.currentIndexChanged.connect(self.update_algorithm_settings)
        algorithm_layout.addRow("Algorithm:", self.algorithm_combo)
        scroll_layout.addWidget(algorithm_group)

        self.settings_group = QGroupBox("Clustering Settings")
        self.settings_layout = QFormLayout(self.settings_group)


        # K-Means settings
        self.kmeans_max_clusters_label = QLabel("Max Clusters (K-Means):")
        self.kmeans_max_clusters_spinbox = QSpinBox()
        self.kmeans_max_clusters_spinbox.setRange(2, 1000)
        self.kmeans_max_clusters_spinbox.setValue(20)
        self.settings_layout.addRow(self.kmeans_max_clusters_label, self.kmeans_max_clusters_spinbox)

        # GMM settings
        self.gmm_max_clusters_label = QLabel("Max Clusters (GMM):")
        self.gmm_max_clusters_spinbox = QSpinBox()
        self.gmm_max_clusters_spinbox.setRange(2, 1000)
        self.gmm_max_clusters_spinbox.setValue(20)
        self.settings_layout.addRow(self.gmm_max_clusters_label, self.gmm_max_clusters_spinbox)

        # Hierarchical Clustering settings
        self.hierarchical_max_clusters_label = QLabel("Max Clusters (Hierarchical):")
        self.hierarchical_max_clusters_spinbox = QSpinBox()
        self.hierarchical_max_clusters_spinbox.setRange(2, 1000)
        self.hierarchical_max_clusters_spinbox.setValue(20)
        self.settings_layout.addRow(self.hierarchical_max_clusters_label, self.hierarchical_max_clusters_spinbox)
        self.hierarchical_max_clusters_label.setVisible(False)
        self.hierarchical_max_clusters_spinbox.setVisible(False)

        # Number of clusters determination
        self.num_clusters_determination_label = QLabel("Number of Clusters Determination:")
        self.num_clusters_determination_combo = QComboBox()
        self.num_clusters_determination_combo.addItems(["Manual", "Silhouette Method", "Davies-Bouldin Index", "Threshold"])
        self.num_clusters_determination_combo.currentIndexChanged.connect(self.update_num_clusters_determination)
        self.settings_layout.addRow(self.num_clusters_determination_label, self.num_clusters_determination_combo)

        # Manual number of clusters
        self.num_clusters_label = QLabel("Number of Clusters:")
        self.num_clusters_spinbox = QSpinBox()
        self.num_clusters_spinbox.setRange(1, 1000)
        self.num_clusters_spinbox.setValue(5)
        self.num_clusters_label.setVisible(False)
        self.num_clusters_spinbox.setVisible(False)
        self.settings_layout.addRow(self.num_clusters_label, self.num_clusters_spinbox)

        # Silhouette Method settings
        self.max_clusters_silhouette_label = QLabel("Max Clusters (Silhouette):")
        self.max_clusters_silhouette_spinbox = QSpinBox()
        self.max_clusters_silhouette_spinbox.setRange(2, 1000)
        self.max_clusters_silhouette_spinbox.setValue(20)
        self.max_clusters_silhouette_label.setVisible(False)
        self.max_clusters_silhouette_spinbox.setVisible(False)
        self.settings_layout.addRow(self.max_clusters_silhouette_label, self.max_clusters_silhouette_spinbox)

        # Davies-Bouldin Index settings
        self.max_clusters_db_label = QLabel("Max Clusters (Davies-Bouldin):")
        self.max_clusters_db_spinbox = QSpinBox()
        self.max_clusters_db_spinbox.setRange(2, 1000)
        self.max_clusters_db_spinbox.setValue(20)
        self.max_clusters_db_label.setVisible(False)
        self.max_clusters_db_spinbox.setVisible(False)
        self.settings_layout.addRow(self.max_clusters_db_label, self.max_clusters_db_spinbox)

        # Threshold settings
        self.threshold_label = QLabel("Threshold:")
        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.1, 1.0)
        self.threshold_spinbox.setSingleStep(0.05)
        self.threshold_spinbox.setValue(0.85)
        self.threshold_label.setVisible(False)
        self.threshold_spinbox.setVisible(False)
        self.settings_layout.addRow(self.threshold_label, self.threshold_spinbox)

        # GMM settings
        self.covariance_type_label = QLabel("Covariance Type:")
        self.covariance_type_combo = QComboBox()
        self.covariance_type_combo.addItems(["full", "tied", "diag", "spherical"])
        self.covariance_type_label.setVisible(False)
        self.covariance_type_combo.setVisible(False)
        self.settings_layout.addRow(self.covariance_type_label, self.covariance_type_combo)

        # Affinity Propagation settings
        self.damping_label = QLabel("Damping:")
        self.damping_spinbox = QDoubleSpinBox()
        self.damping_spinbox.setRange(0.5, 1.0)
        self.damping_spinbox.setSingleStep(0.05)
        self.damping_spinbox.setValue(0.5)
        self.damping_label.setVisible(False)
        self.damping_spinbox.setVisible(False)
        self.settings_layout.addRow(self.damping_label, self.damping_spinbox)

        # Mean Shift settings
        self.bandwidth_label = QLabel("Bandwidth:")
        self.bandwidth_spinbox = QDoubleSpinBox()
        self.bandwidth_spinbox.setRange(0.1, 1000.0)
        self.bandwidth_spinbox.setSingleStep(0.1)
        self.bandwidth_spinbox.setValue(100.0)
        self.bandwidth_label.setVisible(False)
        self.bandwidth_spinbox.setVisible(False)
        self.settings_layout.addRow(self.bandwidth_label, self.bandwidth_spinbox)

        # Hierarchical Clustering settings
        self.linkage_label = QLabel("Linkage:")
        self.linkage_combo = QComboBox()
        self.linkage_combo.addItems(["ward", "complete", "average", "single"])
        self.linkage_label.setVisible(False)
        self.linkage_combo.setVisible(False)
        self.settings_layout.addRow(self.linkage_label, self.linkage_combo)

        scroll_layout.addWidget(self.settings_group)

        self.tabs.addTab(clustering_settings_tab, "Clustering Settings")

        # Data reduction settings tab
        data_reduction_settings_tab = QWidget()
        data_reduction_settings_layout = QVBoxLayout(data_reduction_settings_tab)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        data_reduction_settings_layout.addWidget(scroll_area)

        normal_reduction_group = QGroupBox("Standardisation")
        normal_reduction_layout = QFormLayout(normal_reduction_group)
        self.enable_standardisation_checkbox = QCheckBox("Enable Standardisation")
        self.enable_standardisation_checkbox.stateChanged.connect(self.toggle_standardisation_widgets)
        normal_reduction_layout.addWidget(self.enable_standardisation_checkbox)
        self.standardisation_type_label = QLabel("Which Standardisation to use:")
        self.standardisation_type_combo = QComboBox()
        self.standardisation_type_combo.addItems(["ΔI/I₀", "(ΔI*I₀)⁰·⁵", "(ΔI*I₀)ᵖᵒʷᵉʳ", "Dutt Standardisation"])
        self.standardisation_type_combo.currentIndexChanged.connect(self.update_standardisation_explanation)
        normal_reduction_layout.addRow(self.standardisation_type_label, self.standardisation_type_combo)
        self.standardisation_explanation_label = QLabel()
        self.standardisation_explanation_label.setWordWrap(True)
        normal_reduction_layout.addRow(self.standardisation_explanation_label)
        self.power_label = QLabel("Power:")
        self.power_spinbox = QDoubleSpinBox()
        self.power_spinbox.setRange(0.01, 10)
        self.power_spinbox.setValue(0.5)
        self.power_spinbox.setSingleStep(0.01)
        self.power_label.setVisible(False)
        self.power_spinbox.setVisible(False)
        normal_reduction_layout.addRow(self.power_label, self.power_spinbox)
        self.length_label = QLabel("Length of the nanopore (L) (nm):")
        self.length_spinbox = QDoubleSpinBox()
        self.length_spinbox.setRange(1, 100)
        self.length_spinbox.setValue(7)
        self.length_spinbox.setSingleStep(0.1)
        self.length_label.setVisible(False)
        self.length_spinbox.setVisible(False)
        normal_reduction_layout.addRow(self.length_label, self.length_spinbox)
        self.conductivity_label = QLabel("σ (Conductivity of the solution) (S/m):")
        self.conductivity_spinbox = QDoubleSpinBox()
        self.conductivity_spinbox.setRange(0.1, 100)
        self.conductivity_spinbox.setValue(10.5)
        self.conductivity_spinbox.setSingleStep(0.1)
        self.conductivity_label.setVisible(False)
        self.conductivity_spinbox.setVisible(False)
        normal_reduction_layout.addRow(self.conductivity_label, self.conductivity_spinbox)
        self.voltage_label = QLabel("V (Voltage Applied) (mV):")
        self.voltage_spinbox = QDoubleSpinBox()
        self.voltage_spinbox.setRange(10, 2000)
        self.voltage_spinbox.setValue(400)
        self.voltage_spinbox.setSingleStep(1)
        self.voltage_label.setVisible(False)
        self.voltage_spinbox.setVisible(False)
        normal_reduction_layout.addRow(self.voltage_label, self.voltage_spinbox)
        self.open_pore_current_label = QLabel("I₀ (Open Pore Current) (nA):")
        self.open_pore_current_spinbox = QDoubleSpinBox()
        self.open_pore_current_spinbox.setRange(-500, 500)
        self.open_pore_current_spinbox.setValue(25)
        self.open_pore_current_spinbox.setSingleStep(0.1)
        self.open_pore_current_label.setVisible(False)
        self.open_pore_current_spinbox.setVisible(False)
        normal_reduction_layout.addRow(self.open_pore_current_label, self.open_pore_current_spinbox)
        scroll_layout.addWidget(normal_reduction_group)

        self.check_values_group = QGroupBox("Check Values")
        self.check_values_layout = QFormLayout(self.check_values_group)
        self.delta_i_label = QLabel("ΔI (Change in Current) (nA):")
        self.delta_i_spinbox = QDoubleSpinBox()
        self.delta_i_spinbox.setRange(-500, 500)
        self.delta_i_spinbox.setValue(1)
        self.delta_i_spinbox.setSingleStep(0.1)
        self.check_values_layout.addRow(self.delta_i_label, self.delta_i_spinbox)
        self.check_values_button = QPushButton("Check Values")
        self.check_values_button.clicked.connect(self.check_values)
        self.check_values_layout.addRow(self.check_values_button)
        self.check_values_result_label = QLabel()
        self.check_values_layout.addRow(self.check_values_result_label)
        self.check_values_group.setVisible(False)
        scroll_layout.addWidget(self.check_values_group)

        ml_reduction_group = QGroupBox("ML Data Reduction")
        ml_reduction_layout = QFormLayout(ml_reduction_group)
        self.enable_ml_data_reduction_checkbox = QCheckBox("Enable ML Data Reduction")
        self.enable_ml_data_reduction_checkbox.stateChanged.connect(self.toggle_ml_widgets)
        ml_reduction_layout.addWidget(self.enable_ml_data_reduction_checkbox)
        self.tag_label = QLabel("Tag:")
        self.tag_lineedit = QLineEdit()
        self.tag_lineedit.setText("BSA")
        ml_reduction_layout.addRow(self.tag_label, self.tag_lineedit)
        self.data_reduction_type_label = QLabel("Type of Data Reduction:")
        self.data_reduction_type_combo = QComboBox()
        self.data_reduction_type_combo.addItems(["Scheme 1", "Scheme 2", "Scheme 3", "Scheme 4", "Scheme 5"])
        ml_reduction_layout.addRow(self.data_reduction_type_label, self.data_reduction_type_combo)
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
        ml_reduction_layout.addRow(self.scheme_table)
        scroll_layout.addWidget(ml_reduction_group)

        self.tabs.addTab(data_reduction_settings_tab, "Data Reduction Settings")

        # Right side
        self.canvas = FigureCanvas(plt.Figure(figsize=(15, 6)))
        self.ax = self.canvas.figure.subplots()
        right_layout.addWidget(self.canvas)

        toolbar = NavigationToolbar(self.canvas, self)
        right_layout.addWidget(toolbar)

        self.result_text = QLabel()
        self.result_text.setWordWrap(True)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.result_text)
        right_layout.addWidget(scroll_area)

        self.standardisation_widgets = [
            self.standardisation_type_label, self.standardisation_type_combo,
            self.standardisation_explanation_label, self.power_label, self.power_spinbox,
            self.length_label, self.length_spinbox, self.conductivity_label, self.conductivity_spinbox,
            self.voltage_label, self.voltage_spinbox, self.open_pore_current_label,
            self.open_pore_current_spinbox, self.check_values_group
        ]
        self.toggle_standardisation_widgets()

        self.ml_widgets = [self.tag_label, self.tag_lineedit, self.data_reduction_type_label,
                           self.data_reduction_type_combo, self.scheme_table]
        self.toggle_ml_widgets()

        self.update_algorithm_settings(0)

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
                                                           "Beware of using this option as some parts of ΔI<sub>new</sub> "
                                                           "would be favoured as compared to others with changing values "
                                                           "of power. Also beware of the units as except for power = 0.5, "
                                                           "the units are not nA.")
        elif index == 3:
            self.standardisation_explanation_label.setText("For more information on this, talk with Shankar Dutt "
                                                           "(shankar.dutt@anu.edu.au)")

    def check_values(self):
        l = self.length_spinbox.value() * 10**(-9)
        delta_i = self.delta_i_spinbox.value() * 10**(-9)
        v = self.voltage_spinbox.value() / 1000
        sigma = self.conductivity_spinbox.value()
        i0 = self.open_pore_current_spinbox.value() * 10**(-9)
        d = i0 + (i0 * (i0 + 16 * l * v * sigma / np.pi)) ** 0.5 / (2 * v * sigma)
        condition = sigma > (4 * l * delta_i / v + d * np.pi * delta_i / v) / (d ** 2 * np.pi)
        condition1 = delta_i < i0
        if condition and condition1:
            self.check_values_result_label.setText("The entered values should work, and you will get a good standardisation.")
        else:
            self.check_values_result_label.setText("The entered values will not work. Something is wrong!")
        self.check_values_result_label.setWordWrap(True)

    def toggle_ml_widgets(self):
        for widget in self.ml_widgets:
            widget.setVisible(self.enable_ml_data_reduction_checkbox.isChecked())

    def update_algorithm_settings(self, index):
        if index == 0:  # K-Means
            self.num_clusters_label.setVisible(False)
            self.num_clusters_spinbox.setVisible(False)
            self.covariance_type_label.setVisible(False)
            self.covariance_type_combo.setVisible(False)
            self.damping_label.setVisible(False)
            self.damping_spinbox.setVisible(False)
            self.bandwidth_label.setVisible(False)
            self.bandwidth_spinbox.setVisible(False)
            self.linkage_label.setVisible(False)
            self.linkage_combo.setVisible(False)
            self.kmeans_max_clusters_label.setVisible(True)
            self.kmeans_max_clusters_spinbox.setVisible(True)
            self.gmm_max_clusters_label.setVisible(False)
            self.gmm_max_clusters_spinbox.setVisible(False)
            self.hierarchical_max_clusters_label.setVisible(False)
            self.hierarchical_max_clusters_spinbox.setVisible(False)
            self.num_clusters_label.setVisible(self.num_clusters_determination_combo.currentIndex() == 0)
            self.num_clusters_spinbox.setVisible(self.num_clusters_determination_combo.currentIndex() == 0)
            self.kmeans_max_clusters_label.setVisible(False)
            self.kmeans_max_clusters_spinbox.setVisible(False)
        elif index == 1:  # GMM
            self.num_clusters_label.setVisible(False)
            self.num_clusters_spinbox.setVisible(False)
            self.covariance_type_label.setVisible(True)
            self.covariance_type_combo.setVisible(True)
            self.damping_label.setVisible(False)
            self.damping_spinbox.setVisible(False)
            self.bandwidth_label.setVisible(False)
            self.bandwidth_spinbox.setVisible(False)
            self.linkage_label.setVisible(False)
            self.linkage_combo.setVisible(False)
            self.kmeans_max_clusters_label.setVisible(False)
            self.kmeans_max_clusters_spinbox.setVisible(False)
            self.gmm_max_clusters_label.setVisible(True)
            self.gmm_max_clusters_spinbox.setVisible(True)
            self.hierarchical_max_clusters_label.setVisible(False)
            self.hierarchical_max_clusters_spinbox.setVisible(False)
        elif index == 2:  # Hierarchical Clustering
            self.num_clusters_label.setVisible(False)
            self.num_clusters_spinbox.setVisible(False)
            self.covariance_type_label.setVisible(False)
            self.covariance_type_combo.setVisible(False)
            self.damping_label.setVisible(False)
            self.damping_spinbox.setVisible(False)
            self.bandwidth_label.setVisible(False)
            self.bandwidth_spinbox.setVisible(False)
            self.linkage_label.setVisible(True)
            self.linkage_combo.setVisible(True)
            self.kmeans_max_clusters_label.setVisible(False)
            self.kmeans_max_clusters_spinbox.setVisible(False)
            self.gmm_max_clusters_label.setVisible(False)
            self.gmm_max_clusters_spinbox.setVisible(False)
            self.hierarchical_max_clusters_label.setVisible(False)
            self.hierarchical_max_clusters_spinbox.setVisible(False)
            self.num_clusters_determination_label.setVisible(True)
            self.num_clusters_determination_combo.setVisible(True)
            self.num_clusters_label.setVisible(self.num_clusters_determination_combo.currentIndex() == 0)
            self.num_clusters_spinbox.setVisible(self.num_clusters_determination_combo.currentIndex() == 0)
        elif index == 3:  # Affinity Propagation
            self.num_clusters_label.setVisible(False)
            self.num_clusters_spinbox.setVisible(False)
            self.covariance_type_label.setVisible(False)
            self.covariance_type_combo.setVisible(False)
            self.damping_label.setVisible(True)
            self.damping_spinbox.setVisible(True)
            self.bandwidth_label.setVisible(False)
            self.bandwidth_spinbox.setVisible(False)
            self.linkage_label.setVisible(False)
            self.linkage_combo.setVisible(False)
            self.num_clusters_determination_label.setVisible(False)
            self.num_clusters_determination_combo.setVisible(False)
        elif index == 4:  # Mean Shift
            self.num_clusters_label.setVisible(False)
            self.num_clusters_spinbox.setVisible(False)
            self.covariance_type_label.setVisible(False)
            self.covariance_type_combo.setVisible(False)
            self.damping_label.setVisible(False)
            self.damping_spinbox.setVisible(False)
            self.bandwidth_label.setVisible(True)
            self.bandwidth_spinbox.setVisible(True)
            self.linkage_label.setVisible(False)
            self.linkage_combo.setVisible(False)
            self.num_clusters_determination_label.setVisible(False)
            self.num_clusters_determination_combo.setVisible(False)

    def update_num_clusters_determination(self, index):
        self.num_clusters_label.setVisible(index == 0)
        self.num_clusters_spinbox.setVisible(index == 0)
        self.max_clusters_silhouette_label.setVisible(index == 1)
        self.max_clusters_silhouette_spinbox.setVisible(index == 1)
        self.max_clusters_db_label.setVisible(index == 2)
        self.max_clusters_db_spinbox.setVisible(index == 2)
        self.threshold_label.setVisible(index == 3)
        self.threshold_spinbox.setVisible(index == 3)

        # Hide the "Max Clusters (K-Means)", "Max Clusters (GMM)", and "Max Clusters (Hierarchical)" spinboxes for all cluster determination methods
        self.kmeans_max_clusters_label.setVisible(False)
        self.kmeans_max_clusters_spinbox.setVisible(False)
        self.gmm_max_clusters_label.setVisible(False)
        self.gmm_max_clusters_spinbox.setVisible(False)
        self.hierarchical_max_clusters_label.setVisible(False)
        self.hierarchical_max_clusters_spinbox.setVisible(False)

    def select_folder(self):
        options = QFileDialog.Option.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Select Folder", "", options=options)
        if directory:
            self.folder_path_label.setText(f"Selected folder: {directory}")
            self.populate_file_list(directory, self.include_subfolders_chk.isChecked())

    def populate_file_list(self, directory, include_subfolders):
        self.files_list_widget.clear()
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.event_data.npz'):
                    rel_path = os.path.relpath(os.path.join(root, file), start=directory)
                    item = QListWidgetItem(rel_path)
                    item.setData(Qt.ItemDataRole.UserRole, os.path.join(root, file))
                    self.files_list_widget.addItem(item)
            if not include_subfolders:
                break

    def load_data(self):
        self.events_data = {}  # Clear events_data before loading new data
        events_data = self.data['events']

        for event_counter, event_data in enumerate(events_data):
            start_time = event_data['start_time']
            end_time = event_data['end_time']
            event_signal = event_data['event_data']  # Use 'event_data' key instead of 'data'
            event_baseline_mean = event_data['baseline_value']

            self.events_data[event_counter] = {
                'event_id': event_data['event_id'],
                'start_time': start_time,
                'end_time': end_time,
                'event_data': event_signal,
                'baseline_value': event_baseline_mean
            }

        self.sampling_rate = self.data['sampling_rate'].item()
        print(f"Total events loaded: {len(self.events_data)}")

    def perform_clustering(self):
        self.data = {}
        self.events_data = {}  # Initialize events_data
        selected_files = [item.data(Qt.ItemDataRole.UserRole) for item in self.files_list_widget.selectedItems()]
        if not selected_files:
            # No files selected, display an error message or take appropriate action
            QMessageBox.warning(self, "No File Selected", "No file was selected.")
            return

        file_path = selected_files[0]  # Use only the first selected file
        npz_data = np.load(file_path, allow_pickle=True)
        self.data = {key: npz_data[key] for key in npz_data}

        self.load_data()
    
        # Subtract the baseline value from the main data for each event
        #for event_data in self.events_data.values():
        #    event_data['event_data'] -= event_data['baseline_value']

        #print(event_data['baseline_value'])
        
        if self.enable_standardisation_checkbox.isChecked():
            # Perform standardization on each event's data
            standard = self.standardisation_type_combo.currentText()
            standard_power = self.power_spinbox.value()
            standard_length_nm = self.length_spinbox.value()
            standard_conductivity_S_m = self.conductivity_spinbox.value()
            standard_voltage_applied_mV = self.voltage_spinbox.value()
            standard_open_pore_current_nA = self.open_pore_current_spinbox.value()


            for event_data in self.events_data.values():
                event_data['event_data'] = standardize_events(
                    [event_data['event_data']],
                    standard,
                    event_data['baseline_value'],
                    standard_power,
                    standard_length_nm,
                    standard_conductivity_S_m,
                    standard_voltage_applied_mV,
                    standard_open_pore_current_nA
                )[0]

        # Check if self.events_data is empty
        if not self.events_data:
            print("No valid event data found.")
            return

        # Determine the maximum length of the events
        max_length = max(len(event_data['event_data']) for event_data in self.events_data.values())

        # Find the alignment index for each event
        alignment_indices = []
        for event_data in self.events_data.values():
            if self.alignment_method_combo.currentText() == "Maximum":
                alignment_index = np.argmax(event_data['event_data'])
            elif self.alignment_method_combo.currentText() == "Minimum":
                alignment_index = np.argmin(event_data['event_data'])
            else:  # Center alignment
                alignment_index = len(event_data['event_data']) // 2
            alignment_indices.append(alignment_index)

        # Determine the maximum alignment index
        max_alignment_index = max(alignment_indices)

        # Align the events and pad the shorter events
        aligned_data = []
        for event_index, event_data in enumerate(self.events_data.values()):
            event_length = len(event_data['event_data'])
            
            if self.padding_method_combo.currentText() == "NaN":
                aligned_event = np.full(max_length + max_alignment_index, np.nan)
            else:  # Zero padding
                aligned_event = np.zeros(max_length + max_alignment_index)
            
            if self.alignment_method_combo.currentText() == "Maximum":
                alignment_index = np.argmax(event_data['event_data'])
            elif self.alignment_method_combo.currentText() == "Minimum":
                alignment_index = np.argmin(event_data['event_data'])
            else:  # Center alignment
                alignment_index = len(event_data['event_data']) // 2
            
            start_index = max_alignment_index - alignment_index
            end_index = start_index + event_length
            aligned_event[start_index:end_index] = event_data['event_data']
            
            aligned_data.append(aligned_event)
            
        data = np.array(aligned_data)
        aligned_data = data

        #print(f"Total events after alignment: {len(aligned_data)}")

        algorithm = self.algorithm_combo.currentText()
        num_clusters_determination = self.num_clusters_determination_combo.currentText()

        num_chunks = mp.cpu_count()  # Number of CPU cores
        chunk_size = len(aligned_data) // num_chunks
        data_chunks = [aligned_data[i:i + chunk_size] for i in range(0, len(aligned_data), chunk_size)]

        # Create a progress bar
        progress_bar = tqdm(total=len(data_chunks), desc="Clustering Progress", unit="chunk")

        # Process the data chunks in parallel using joblib
        results = Parallel(n_jobs=num_chunks)(delayed(process_chunk)(
            chunk, algorithm, num_clusters_determination,
            self.num_clusters_spinbox.value(), self.max_clusters_silhouette_spinbox.value(),
            self.max_clusters_db_spinbox.value(), np.abs(1-self.threshold_spinbox.value()),
            self.covariance_type_combo.currentText(), self.linkage_combo.currentText(),
            self.damping_spinbox.value(), 
            self.bandwidth_spinbox.value()
        ) for chunk in data_chunks)

        # Update the progress bar
        progress_bar.update(len(data_chunks))
        progress_bar.close()

        # Combine the results from all chunks
        labels_list = [result[0] for result in results]
        centroids_list = [result[1] for result in results if result[1] is not None]

        if labels_list:
            labels = np.concatenate(labels_list)
        else:
            labels = np.array([])

        if centroids_list:
            centroids = np.vstack(centroids_list)
        else:
            centroids = None

        # Convert aligned_data to a NumPy array
        aligned_data = np.array(aligned_data)

        # print(f"Length of aligned_data: {len(aligned_data)}")
        # print(f"Length of labels: {len(labels)}")

        if len(labels) != len(aligned_data):
            # Assign a default label to the events with missing labels
            missing_labels = np.full(len(aligned_data) - len(labels), -1)
            labels = np.concatenate((labels, missing_labels))

        # Remove samples with NaN values from aligned_data
        nan_mask = np.isnan(aligned_data).any(axis=1)
        aligned_data_no_nan = aligned_data[~nan_mask]
        labels_no_nan = labels[~nan_mask]

        # Update the plot and display the results based on the selected algorithm
        self.ax.clear()
        unique_labels = np.unique(labels)
        colors = plt.colormaps['tab20b'](np.linspace(0, 1, len(unique_labels)))
        if len(aligned_data) < 1000:
            alpha_small = 0.05
        elif len(aligned_data) < 5000:
            alpha_small = 0.025
        else:
            alpha_small = 0.01
        for i, label in enumerate(unique_labels):
            cluster_mask = (labels == label)
            cluster_data = aligned_data[cluster_mask]
            for event in cluster_data:
                self.ax.plot(event, alpha=alpha_small, color=colors[i])
            if centroids is not None and i < len(centroids):
                centroid = centroids[i]
                self.ax.plot(centroid, alpha=0.9, color=colors[i], linewidth=2, label=f"Cluster {label}")

        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Amplitude')
        self.ax.set_title(f'{algorithm} Clustering')
        self.ax.grid(True)
        self.ax.legend(loc='best')  # Add a legend to the plot

        if algorithm == "K-Means Clustering":
            if centroids is not None:
                centroids = np.vstack(centroids)
            self.ax.set_title(f"K-Means Clustering")
            if len(np.unique(labels_no_nan)) < 2:
                self.result_text.setText(f"Clustering Algorithm: K-Means\n"
                                        f"All data points are assigned to a single cluster.")
            else:
                self.result_text.setText(f"Clustering Algorithm: K-Means\n"
                                        f"Silhouette Score: {silhouette_score(aligned_data_no_nan, labels_no_nan):.2f}\n"
                                        f"Davies-Bouldin Index: {davies_bouldin_score(aligned_data_no_nan, labels_no_nan):.2f}")
        elif algorithm == "GMM":
            self.ax.set_title(f"GMM Clustering (covariance_type={self.covariance_type_combo.currentText()})")
            if len(np.unique(labels_no_nan)) < 2:
                self.result_text.setText(f"Clustering Algorithm: GMM\n"
                                        f"Covariance Type: {self.covariance_type_combo.currentText()}\n"
                                        f"All data points are assigned to a single cluster.")
            else:
                self.result_text.setText(f"Clustering Algorithm: GMM\n"
                                        f"Covariance Type: {self.covariance_type_combo.currentText()}\n"
                                        f"Silhouette Score: {silhouette_score(aligned_data_no_nan, labels_no_nan):.2f}\n"
                                        f"Davies-Bouldin Index: {davies_bouldin_score(aligned_data_no_nan, labels_no_nan):.2f}")
        elif algorithm == "Hierarchical Clustering":
            self.ax.set_title(f"Hierarchical Clustering (linkage={self.linkage_combo.currentText()})")
            if len(np.unique(labels)) < 2:
                self.result_text.setText(f"Clustering Algorithm: Hierarchical\n"
                                        f"Linkage: {self.linkage_combo.currentText()}\n"
                                        f"All data points are assigned to a single cluster.")
            else:
                self.result_text.setText(f"Clustering Algorithm: Hierarchical\n"
                                        f"Linkage: {self.linkage_combo.currentText()}\n"
                                        f"Silhouette Score: {silhouette_score(aligned_data, labels):.2f}\n"
                                        f"Davies-Bouldin Index: {davies_bouldin_score(aligned_data, labels):.2f}")
        elif algorithm == "Affinity Propagation":
            self.ax.set_title(f"Affinity Propagation (damping={self.damping_spinbox.value()}, )")
            if len(np.unique(labels)) < 2:
                self.result_text.setText(f"Clustering Algorithm: Affinity Propagation\n"
                                        f"Damping: {self.damping_spinbox.value()}\n"
                                        
                                        f"All data points are assigned to a single cluster.")
            else:
                self.result_text.setText(f"Clustering Algorithm: Affinity Propagation\n"
                                        f"Damping: {self.damping_spinbox.value()}\n"
                                        
                                        f"Silhouette Score: {silhouette_score(aligned_data, labels):.2f}\n"
                                        f"Davies-Bouldin Index: {davies_bouldin_score(aligned_data, labels):.2f}")
        elif algorithm == "Mean Shift":
            self.ax.set_title(f"Mean Shift (bandwidth={self.bandwidth_spinbox.value()})")
            if len(np.unique(labels)) < 2:
                self.result_text.setText(f"Clustering Algorithm: Mean Shift\n"
                                        f"Bandwidth: {self.bandwidth_spinbox.value()}\n"
                                        f"All data points are assigned to a single cluster.")
            else:
                self.result_text.setText(f"Clustering Algorithm: Mean Shift\n"
                                        f"Bandwidth: {self.bandwidth_spinbox.value()}\n"
                                        f"Silhouette Score: {silhouette_score(aligned_data, labels):.2f}\n"
                                        f"Davies-Bouldin Index: {davies_bouldin_score(aligned_data, labels):.2f}")

        self.canvas.draw()

        # Display cluster information
        unique_labels = np.unique(labels)
        num_clusters = len(unique_labels)

        cluster_info = ""
        for label in unique_labels:
            cluster_mask = (labels == label)
            cluster_data = aligned_data[cluster_mask]
            cluster_size = len(cluster_data)
            cluster_centroid = np.mean(cluster_data, axis=0)

            cluster_info += f"Cluster {label}:\n"
            cluster_info += f"  Size: {cluster_size}\n"
            cluster_info += f"  Centroid: {cluster_centroid}\n\n"

        self.result_text.setText(self.result_text.text() + "\n\nCluster Information:\n" + cluster_info)

    def perform_clustering_data_reduction(self):
        self.data = {}
        self.events_data = {}  # Initialize events_data
        selected_files = [item.data(Qt.ItemDataRole.UserRole) for item in self.files_list_widget.selectedItems()]
        if not selected_files:
            # No files selected, display an error message or take appropriate action
            print("No file selected.")
            return

        file_path = selected_files[0]  # Use only the first selected file
        npz_data = np.load(file_path, allow_pickle=True)
        self.data = {key: npz_data[key] for key in npz_data}

        self.load_data()
        
        # Subtract the baseline value from the main data for each event
        #for event_data in self.events_data.values():
        #    event_data['event_data'] -= event_data['baseline_value']

        if self.enable_standardisation_checkbox.isChecked():
            # Perform standardization on each event's data
            standard = self.standardisation_type_combo.currentText()
            standard_power = self.power_spinbox.value()
            standard_length_nm = self.length_spinbox.value()
            standard_conductivity_S_m = self.conductivity_spinbox.value()
            standard_voltage_applied_mV = self.voltage_spinbox.value()
            standard_open_pore_current_nA = self.open_pore_current_spinbox.value()

            for event_data in self.events_data.values():
                event_data['event_data'] = standardize_events(
                    [event_data['event_data']],
                    standard,
                    event_data['baseline_value'],
                    standard_power,
                    standard_length_nm,
                    standard_conductivity_S_m,
                    standard_voltage_applied_mV,
                    standard_open_pore_current_nA
                )[0]

        # Check if self.events_data is empty
        if not self.events_data:
            print("No valid event data found.")
            return

        # Determine the maximum length of the events
        max_length = max(len(event_data['event_data']) for event_data in self.events_data.values())

        # Find the alignment index for each event
        alignment_indices = []
        for event_data in self.events_data.values():
            if self.alignment_method_combo.currentText() == "Maximum":
                alignment_index = np.argmax(event_data['event_data'])
            else:  # Minimum alignment
                alignment_index = np.argmin(event_data['event_data'])
            alignment_indices.append(alignment_index)

        # Determine the maximum alignment index
        max_alignment_index = max(alignment_indices)

        # Align the events and pad the shorter events
        aligned_data = []
        for event_index, event_data in enumerate(self.events_data.values()):
            event_length = len(event_data['event_data'])
            
            if self.padding_method_combo.currentText() == "NaN":
                aligned_event = np.full(max_length + max_alignment_index, np.nan)
            else:  # Zero padding
                aligned_event = np.zeros(max_length + max_alignment_index)
            
            if self.alignment_method_combo.currentText() == "Maximum":
                alignment_index = np.argmax(event_data['event_data'])
            else:  # Minimum alignment
                alignment_index = np.argmin(event_data['event_data'])
            
            start_index = max_alignment_index - alignment_index
            end_index = start_index + event_length
            aligned_event[start_index:end_index] = event_data['event_data']
            
            aligned_data.append(aligned_event)

        aligned_data = np.array(aligned_data)

        algorithm = self.algorithm_combo.currentText()
        num_clusters_determination = self.num_clusters_determination_combo.currentText()

        num_chunks = mp.cpu_count()  # Number of CPU cores
        chunk_size = len(aligned_data) // num_chunks
        data_chunks = [aligned_data[i:i + chunk_size] for i in range(0, len(aligned_data), chunk_size)]

        # Create a progress bar
        progress_bar = tqdm(total=len(data_chunks), desc="Clustering Progress", unit="chunk")

        # Process the data chunks in parallel using joblib
        results = Parallel(n_jobs=num_chunks)(delayed(process_chunk)(
            chunk, algorithm, num_clusters_determination,
            self.num_clusters_spinbox.value(), self.max_clusters_silhouette_spinbox.value(),
            self.max_clusters_db_spinbox.value(), np.abs(1-self.threshold_spinbox.value()),
            self.covariance_type_combo.currentText(), self.linkage_combo.currentText(),
            self.damping_spinbox.value(), 
            self.bandwidth_spinbox.value()
        ) for chunk in data_chunks)

        # Update the progress bar
        progress_bar.update(len(data_chunks))
        progress_bar.close()

        # Combine the results from all chunks
        labels_list = [result[0] for result in results]
        centroids_list = [result[1] for result in results if result[1] is not None]

        if labels_list:
            labels = np.concatenate(labels_list)
        else:
            labels = np.array([])

        if centroids_list:
            centroids = np.vstack(centroids_list)
        else:
            centroids = None

        # Convert aligned_data to a NumPy array
        aligned_data = np.array(aligned_data)

        print(f"Length of aligned_data: {len(aligned_data)}")
        print(f"Length of labels: {len(labels)}")

        if len(labels) != len(aligned_data):
            # Assign a default label to the events with missing labels
            missing_labels = np.full(len(aligned_data) - len(labels), -1)
            labels = np.concatenate((labels, missing_labels))

        # Remove samples with NaN values from aligned_data
        nan_mask = np.isnan(aligned_data).any(axis=1)
        aligned_data_no_nan = aligned_data[~nan_mask]
        labels_no_nan = labels[~nan_mask]

        # Update the plot and display the results based on the selected algorithm
        self.ax.clear()
        unique_labels = np.unique(labels)
        colors = plt.colormaps['tab20b'](np.linspace(0, 1, len(unique_labels)))
        if len(aligned_data) < 1000:
            alpha_small = 0.05
        elif len(aligned_data) < 5000:
            alpha_small = 0.025
        else:
            alpha_small = 0.01
        for i, label in enumerate(unique_labels):
            cluster_mask = (labels == label)
            cluster_data = aligned_data[cluster_mask]
            for event in cluster_data:
                self.ax.plot(event, alpha=alpha_small, color=colors[i])
            if centroids is not None and i < len(centroids):
                centroid = centroids[i]
                self.ax.plot(centroid, alpha=0.9, color=colors[i], linewidth=2, label=f"Cluster {label}")

        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Amplitude')
        self.ax.set_title(f'{algorithm} Clustering')
        self.ax.grid(True)
        self.ax.legend(loc='best')  # Add a legend to the plot

        if algorithm == "K-Means Clustering":
            if centroids is not None:
                centroids = np.vstack(centroids)
            self.ax.set_title(f"K-Means Clustering")
            if len(np.unique(labels_no_nan)) < 2:
                self.result_text.setText(f"Clustering Algorithm: K-Means\n"
                                        f"All data points are assigned to a single cluster.")
            else:
                self.result_text.setText(f"Clustering Algorithm: K-Means\n"
                                        f"Silhouette Score: {silhouette_score(aligned_data_no_nan, labels_no_nan):.2f}\n"
                                        f"Davies-Bouldin Index: {davies_bouldin_score(aligned_data_no_nan, labels_no_nan):.2f}")
        elif algorithm == "GMM":
            self.ax.set_title(f"GMM Clustering (covariance_type={self.covariance_type_combo.currentText()})")
            if len(np.unique(labels_no_nan)) < 2:
                self.result_text.setText(f"Clustering Algorithm: GMM\n"
                                        f"Covariance Type: {self.covariance_type_combo.currentText()}\n"
                                        f"All data points are assigned to a single cluster.")
            else:
                self.result_text.setText(f"Clustering Algorithm: GMM\n"
                                        f"Covariance Type: {self.covariance_type_combo.currentText()}\n"
                                        f"Silhouette Score: {silhouette_score(aligned_data_no_nan, labels_no_nan):.2f}\n"
                                        f"Davies-Bouldin Index: {davies_bouldin_score(aligned_data_no_nan, labels_no_nan):.2f}")
        elif algorithm == "Hierarchical Clustering":
            self.ax.set_title(f"Hierarchical Clustering (linkage={self.linkage_combo.currentText()})")
            if len(np.unique(labels)) < 2:
                self.result_text.setText(f"Clustering Algorithm: Hierarchical\n"
                                        f"Linkage: {self.linkage_combo.currentText()}\n"
                                        f"All data points are assigned to a single cluster.")
            else:
                self.result_text.setText(f"Clustering Algorithm: Hierarchical\n"
                                        f"Linkage: {self.linkage_combo.currentText()}\n"
                                        f"Silhouette Score: {silhouette_score(aligned_data, labels):.2f}\n"
                                        f"Davies-Bouldin Index: {davies_bouldin_score(aligned_data, labels):.2f}")
        elif algorithm == "Affinity Propagation":
            self.ax.set_title(f"Affinity Propagation (damping={self.damping_spinbox.value()}, )")
            if len(np.unique(labels)) < 2:
                self.result_text.setText(f"Clustering Algorithm: Affinity Propagation\n"
                                        f"Damping: {self.damping_spinbox.value()}\n"
                                        f"All data points are assigned to a single cluster.")
            else:
                self.result_text.setText(f"Clustering Algorithm: Affinity Propagation\n"
                                        f"Damping: {self.damping_spinbox.value()}\n"
                                        f"Silhouette Score: {silhouette_score(aligned_data, labels):.2f}\n"
                                        f"Davies-Bouldin Index: {davies_bouldin_score(aligned_data, labels):.2f}")
        elif algorithm == "Mean Shift":
            self.ax.set_title(f"Mean Shift (bandwidth={self.bandwidth_spinbox.value()})")
            if len(np.unique(labels)) < 2:
                self.result_text.setText(f"Clustering Algorithm: Mean Shift\n"
                                        f"Bandwidth: {self.bandwidth_spinbox.value()}\n"
                                        f"All data points are assigned to a single cluster.")
            else:
                self.result_text.setText(f"Clustering Algorithm: Mean Shift\n"
                                        f"Bandwidth: {self.bandwidth_spinbox.value()}\n"
                                        f"Silhouette Score: {silhouette_score(aligned_data, labels):.2f}\n"
                                        f"Davies-Bouldin Index: {davies_bouldin_score(aligned_data, labels):.2f}")

        self.canvas.draw()

        # Display cluster information
        unique_labels = np.unique(labels)
        num_clusters = len(unique_labels)

        cluster_info = ""
        for label in unique_labels:
            cluster_mask = (labels == label)
            cluster_data = aligned_data[cluster_mask]
            cluster_size = len(cluster_data)
            cluster_centroid = np.mean(cluster_data, axis=0)

            cluster_info += f"Cluster {label}:\n"
            cluster_info += f"  Size: {cluster_size}\n"
            cluster_info += f"  Centroid: {cluster_centroid}\n\n"

        self.result_text.setText(self.result_text.text() + "\n\nCluster Information:\n" + cluster_info)

        # Retrieve the selected standardization and ML_Standard settings from the Data Reduction Settings tab
        standard = self.standardisation_type_combo.currentText()
        ML_enabled = self.enable_ml_data_reduction_checkbox.isChecked()
        ML_standard = self.data_reduction_type_combo.currentText()
        standard_power = self.power_spinbox.value()
        standard_length_nm = self.length_spinbox.value()
        standard_conductivity_S_m = self.conductivity_spinbox.value()
        standard_voltage_applied_mV = self.voltage_spinbox.value()
        standard_open_pore_current_nA = self.open_pore_current_spinbox.value()

        ML_standardisation_settings = {
            'standard': standard,
            'ML_enabled': str(ML_enabled),
            'ML_standard': ML_standard,
            'standard_power': standard_power,
            'standard_length_nm': standard_length_nm,
            'standard_conductivity_S_m': standard_conductivity_S_m,
            'standard_voltage_applied_mV': standard_voltage_applied_mV,
            'standard_open_pore_current_nA': standard_open_pore_current_nA
        }

        unique_labels = np.unique(labels)
        sampling_rate = self.sampling_rate

        # Get the directory of the first selected file
        if selected_files:
            file_path = selected_files[0]
            file_directory = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            file_name_without_extension, _ = os.path.splitext(file_name)
            file_name_without_extension, _ = os.path.splitext(file_name_without_extension)
        else:
            file_directory = ""
            file_name = ""
        
        for label in unique_labels:
            cluster_mask = (labels == label)
            cluster_data = aligned_data[cluster_mask]
            cluster_events = [self.events_data[i] for i in range(len(labels)) if labels[i] == label]

            reduced_data = save_chunked_event_analysis_to_npz(
                30,
                cluster_data,
                cluster_events,
                self.sampling_rate,
                ML_standardisation_settings
            )

            # Save the reduced data for the current cluster
            date_time_str = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
            file_name = f"{file_name_without_extension}_cluster_{label}_{date_time_str}"
            if ML_enabled:
                file_name += ".MLdataset"
            else:
                file_name += ".dataset"

            save_file_path = os.path.join(file_directory, file_name)
            np.savez_compressed(save_file_path, settings=ML_standardisation_settings, X=reduced_data)

        QMessageBox.information(self, "Data Reduction", "Data reduction and saving completed.")

if __name__ == "__main__":
    app = QApplication([])
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

    window = SDEventClusteringApp()
    window.showMaximized()
    app.exec()