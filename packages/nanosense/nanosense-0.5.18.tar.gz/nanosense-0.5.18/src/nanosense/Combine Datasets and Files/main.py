import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QCheckBox, QComboBox, QListWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QStyleFactory, QInputDialog, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont
import numpy as np
import h5py
from neo.rawio import AxonRawIO
import pyabf


class SDCombineDatasets(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SD Combine Datasets/Files")
        self.resize(500, 700)

        # Create widgets
        self.app_name_label = QLabel("SD Combine Datasets/Files")
        self.app_name_label.setAlignment(Qt.AlignCenter)
        self.app_name_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.email_label = QLabel("shankar.dutt@anu.edu.au")
        self.email_label.setAlignment(Qt.AlignCenter)
        self.select_folder_button = QPushButton("Select Folder")
        self.include_subfolders_checkbox = QCheckBox("Include Subfolders")
        self.extension_dropdown = QComboBox()
        self.extension_dropdown.addItems([".dataset.npz", ".MLdataset.npz", ".abf", ".h5", ".event_data.npz", ".event_fitting.npz"])
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.select_all_checkbox = QCheckBox("Select All")
        self.same_duration_checkbox = QCheckBox("Files have the same duration")
        self.same_duration_checkbox.setChecked(True)  # Set checked by default
        self.folder_path_label = QLabel()
        self.folder_path_label.setWordWrap(True)
        self.combine_datasets_button = QPushButton("Combine Datasets/Files")

        # Create layouts
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.app_name_label)
        main_layout.addWidget(self.email_label)
        main_layout.addWidget(self.select_folder_button)
        main_layout.addWidget(self.include_subfolders_checkbox)
        main_layout.addWidget(self.extension_dropdown)
        main_layout.addWidget(self.file_list)
        main_layout.addWidget(self.select_all_checkbox)
        main_layout.addWidget(self.same_duration_checkbox)
        main_layout.addWidget(self.folder_path_label)
        main_layout.addWidget(self.combine_datasets_button)

        self.setLayout(main_layout)

        # Connect signals and slots
        self.select_folder_button.clicked.connect(self.select_folder)
        self.select_all_checkbox.stateChanged.connect(self.select_all)
        self.combine_datasets_button.clicked.connect(self.combine_datasets)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.file_list.clear()
            self.folder_path_label.setText(f"Selected Folder: {folder_path}")
            extension = self.extension_dropdown.currentText()
            if self.include_subfolders_checkbox.isChecked():
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        if file.endswith(extension):
                            file_path = os.path.relpath(os.path.join(root, file), folder_path)
                            self.file_list.addItem(file_path)
            else:
                for file in os.listdir(folder_path):
                    if file.endswith(extension):
                        self.file_list.addItem(file)

    def select_all(self, state):
        is_checked = self.select_all_checkbox.isChecked()
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            item.setSelected(is_checked)

    def read_abf_file(self, file_path):
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
            abf = pyabf.ABF(file_path)
            data = abf.sweepY
            sampling_rate = abf.dataRate
            return data, sampling_rate

    def combine_datasets(self):
        selected_files = [self.file_list.item(i).text() for i in range(self.file_list.count()) if self.file_list.item(i).isSelected()]
        if selected_files:
            if self.select_all_checkbox.isChecked():
                selected_files.sort()  # Sort files by name if all files are selected
            else:
                selected_indexes = self.file_list.selectedIndexes()
                selected_files = [self.file_list.item(index.row()).text() for index in selected_indexes]  # Preserve user's selection order

            extension = self.extension_dropdown.currentText()
            folder_path = self.folder_path_label.text().replace("Selected Folder: ", "")

            if extension in [".dataset.npz", ".MLdataset.npz"]:
                self.combine_npz_datasets(selected_files, folder_path, extension)
            elif extension in [".abf", ".h5"]:
                self.combine_abf_h5_datasets(selected_files, folder_path, extension)
            elif extension == ".event_data.npz":
                self.combine_event_data_npz(selected_files, folder_path)
            elif extension == ".event_fitting.npz":
                self.combine_event_fitting_npz(selected_files, folder_path)
        else:
            QMessageBox.warning(self, "Warning", "No files selected.")


    def combine_event_fitting_npz(self, selected_files, folder_path):
        combined_npz_dict = {}
        all_event_analyses = []
        event_counter = 0

        file_lengths = []
        if self.same_duration_checkbox.isChecked():
            file_length, ok = QInputDialog.getInt(self, "File Duration", "Enter the duration of each file in seconds:")
            if ok:
                file_lengths = [file_length] * len(selected_files)
            else:
                QMessageBox.warning(self, "Warning", "File duration not provided. Skipping combination.")
                return
        else:
            for file_path in selected_files:
                file_length, ok = QInputDialog.getInt(self, "File Duration", f"Enter the duration of file '{file_path}' in seconds:")
                if ok:
                    file_lengths.append(file_length)
                else:
                    QMessageBox.warning(self, "Warning", "File duration not provided. Skipping file.")
                    return

        cumulative_time = 0
        for file_path, file_length in zip(selected_files, file_lengths):
            full_path = os.path.join(folder_path, file_path)
            with np.load(full_path, allow_pickle=True) as data:
                for key, value in data.items():
                    if key.startswith('EVENT_DATA_'):
                        event_num = int(key.split('_')[2])
                        new_key = f'EVENT_DATA_{event_counter}'
                        if key.endswith('_part_2'):  # This is the event_time_start_end array
                            value = value + cumulative_time
                        combined_npz_dict[f'{new_key}{key[key.rfind("_"):]}'] = value
                    elif key.startswith('SEGMENT_INFO_'):
                        event_num = int(key.split('_')[2])
                        new_key = f'SEGMENT_INFO_{event_counter}'
                        combined_npz_dict[f'{new_key}{key[key.rfind("_"):]}'] = value
                    elif key.startswith('EVENT_ANALYSIS_'):
                        event_num = int(key.split('_')[2])
                        new_key = f'EVENT_ANALYSIS_{event_counter}'
                        adjusted_value = value.copy()
                        adjusted_value[-1] += cumulative_time  # Adjust the last element (start time)
                        combined_npz_dict[new_key] = adjusted_value
                        all_event_analyses.append(adjusted_value)
                    event_counter += 1
            cumulative_time += file_length

        if combined_npz_dict:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Combined Event Fitting Data", "", "NumPy Files (*.event_fitting.npz)")
            if save_path:
                if not save_path.endswith('.event_fitting.npz'):
                    save_path += '.event_fitting.npz'
                np.savez_compressed(save_path, **combined_npz_dict)
                
                # Save the combined event analyses as a separate file
                analysis_save_path = save_path.replace('.event_fitting.npz', '.event_analysis.npz')
                np.savez_compressed(analysis_save_path, event_analyses=np.array(all_event_analyses, dtype=object))
                
                QMessageBox.information(self, "Success", "Event fitting data files combined successfully.")
        else:
            QMessageBox.warning(self, "Warning", "No valid event fitting data files to combine.")

    def combine_event_data_npz(self, selected_files, folder_path):
        combined_events = []
        sampling_rate = None
        event_id_offset = 0
        cumulative_time = 0

        file_lengths = []
        if self.same_duration_checkbox.isChecked():
            file_length, ok = QInputDialog.getInt(self, "File Duration", "Enter the duration of each file in seconds:")
            if ok:
                file_lengths = [file_length] * len(selected_files)
            else:
                QMessageBox.warning(self, "Warning", "File duration not provided. Skipping combination.")
                return
        else:
            for file_path in selected_files:
                file_length, ok = QInputDialog.getInt(self, "File Duration", f"Enter the duration of file '{file_path}' in seconds:")
                if ok:
                    file_lengths.append(file_length)
                else:
                    QMessageBox.warning(self, "Warning", "File duration not provided. Skipping file.")
                    return

        for file_path, file_length in zip(selected_files, file_lengths):
            full_path = os.path.join(folder_path, file_path)
            with np.load(full_path, allow_pickle=True) as data:
                if sampling_rate is None:
                    sampling_rate = data['sampling_rate']
                elif sampling_rate != data['sampling_rate']:
                    QMessageBox.warning(self, "Warning", f"File {file_path} has a different sampling rate. Skipping.")
                    continue

                events = data['events']
                for event in events:
                    adjusted_event = event.copy()
                    adjusted_event['event_id'] += event_id_offset
                    adjusted_event['start_time'] += cumulative_time
                    adjusted_event['end_time'] += cumulative_time
                    combined_events.append(adjusted_event)

            event_id_offset = len(combined_events)
            cumulative_time += file_length

        if combined_events:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Combined Event Data", "", "NumPy Files (*.event_data.npz)")
            if save_path:
                if not save_path.endswith('.event_data.npz'):
                    save_path += '.event_data.npz'
                np.savez_compressed(save_path, sampling_rate=sampling_rate, events=combined_events)
                QMessageBox.information(self, "Success", "Event data files combined successfully.")
        else:
            QMessageBox.warning(self, "Warning", "No valid event data files to combine.")

    def combine_npz_datasets(self, selected_files, folder_path, extension):
        file_lengths = []
        if self.same_duration_checkbox.isChecked():
            file_length, ok = QInputDialog.getInt(self, "File Duration", "Enter the duration of each file in seconds:")
            if ok:
                file_lengths = [file_length] * len(selected_files)
            else:
                QMessageBox.warning(self, "Warning", "File duration not provided. Skipping combination.")
                return
        else:
            for file_path in selected_files:
                file_length, ok = QInputDialog.getInt(self, "File Duration", f"Enter the duration of file '{file_path}' in seconds:")
                if ok:
                    file_lengths.append(file_length)
                else:
                    QMessageBox.warning(self, "Warning", "File duration not provided. Skipping file.")
                    return

        combined_data = None
        settings_file = None
        cumulative_time = 0
        for file_path, file_length in zip(selected_files, file_lengths):
            full_path = os.path.join(folder_path, file_path)
            with np.load(full_path) as data:
                if combined_data is None:
                    combined_data = data['X']
                else:
                    try:
                        data_x = data['X']
                        data_x[:, 8] += cumulative_time  # Add cumulative time to event_time
                        combined_data = np.concatenate((combined_data, data_x))
                    except:
                        print(f"Cannot save file: {file_path}")
                if settings_file is None:
                    settings_file = data['settings']
            cumulative_time += file_length

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Combined Dataset", "", f"NumPy Files (*{extension})")
        if save_path:
            if not save_path.endswith(extension):
                save_path += extension
            np.savez(save_path, X=combined_data, settings=settings_file)
            QMessageBox.information(self, "Success", "Datasets/Files combined successfully.")

    def combine_abf_h5_datasets(self, selected_files, folder_path, extension):
        combined_data = []
        sampling_rate = None

        for file_path in selected_files:
            full_path = os.path.join(folder_path, file_path)
            if extension == ".abf":
                data, file_sampling_rate = self.read_abf_file(full_path)
            elif extension == ".h5":
                with h5py.File(full_path, 'r') as f:
                    data = f['selected_data'][:]
                    file_sampling_rate = f.attrs['sampling_rate']
            
            combined_data.append(data)
            
            if sampling_rate is None:
                sampling_rate = file_sampling_rate
            elif sampling_rate != file_sampling_rate:
                QMessageBox.warning(self, "Warning", "Files have different sampling rates. Proceeding with combination, but please be cautious with the results.")

        # Combine the data
        combined_data = np.concatenate(combined_data)

        # Save as .h5 file
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Combined Dataset", "", "HDF5 Files (*.h5)")
        if save_path:
            if not save_path.endswith('.h5'):
                save_path += '.h5'
            with h5py.File(save_path, 'w') as f:
                f.create_dataset('selected_data', data=combined_data)
                f.attrs['sampling_rate'] = sampling_rate
            QMessageBox.information(self, "Success", "Datasets combined successfully and saved as .h5 file.")

if __name__ == '__main__':
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

    window = SDCombineDatasets()
    window.show()
    sys.exit(app.exec())