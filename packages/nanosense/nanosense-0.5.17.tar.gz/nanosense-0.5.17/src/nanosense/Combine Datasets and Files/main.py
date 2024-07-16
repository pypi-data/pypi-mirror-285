import sys 
import os 
from PySide6 .QtWidgets import QApplication ,QWidget ,QLabel ,QPushButton ,QCheckBox ,QComboBox ,QListWidget ,QVBoxLayout ,QHBoxLayout ,QFileDialog ,QMessageBox ,QStyleFactory ,QInputDialog ,QDialog 
from PySide6 .QtCore import Qt 
from PySide6 .QtGui import QPalette ,QColor ,QFont 
import numpy as np 
import h5py 
from neo .rawio import AxonRawIO 
import pyabf 

class SDCombineDatasets (QWidget ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("SD Combine Datasets/Files")
        self .resize (500 ,700 )


        self .app_name_label =QLabel ("SD Combine Datasets/Files")
        self .app_name_label .setAlignment (Qt .AlignCenter )
        self .app_name_label .setFont (QFont ("Arial",16 ,QFont .Bold ))
        self .email_label =QLabel ("shankar.dutt@anu.edu.au")
        self .email_label .setAlignment (Qt .AlignCenter )
        self .select_folder_button =QPushButton ("Select Folder")
        self .include_subfolders_checkbox =QCheckBox ("Include Subfolders")
        self .extension_dropdown =QComboBox ()
        self .extension_dropdown .addItems ([".dataset.npz",".MLdataset.npz",".abf",".h5"])
        self .file_list =QListWidget ()
        self .file_list .setSelectionMode (QListWidget .SelectionMode .MultiSelection )
        self .select_all_checkbox =QCheckBox ("Select All")
        self .same_duration_checkbox =QCheckBox ("Files have the same duration")
        self .same_duration_checkbox .setChecked (True )
        self .folder_path_label =QLabel ()
        self .folder_path_label .setWordWrap (True )
        self .combine_datasets_button =QPushButton ("Combine Datasets/Files")


        main_layout =QVBoxLayout ()
        main_layout .addWidget (self .app_name_label )
        main_layout .addWidget (self .email_label )
        main_layout .addWidget (self .select_folder_button )
        main_layout .addWidget (self .include_subfolders_checkbox )
        main_layout .addWidget (self .extension_dropdown )
        main_layout .addWidget (self .file_list )
        main_layout .addWidget (self .select_all_checkbox )
        main_layout .addWidget (self .same_duration_checkbox )
        main_layout .addWidget (self .folder_path_label )
        main_layout .addWidget (self .combine_datasets_button )

        self .setLayout (main_layout )


        self .select_folder_button .clicked .connect (self .select_folder )
        self .select_all_checkbox .stateChanged .connect (self .select_all )
        self .combine_datasets_button .clicked .connect (self .combine_datasets )

    def select_folder (self ):
        folder_path =QFileDialog .getExistingDirectory (self ,"Select Folder")
        if folder_path :
            self .file_list .clear ()
            self .folder_path_label .setText (f"Selected Folder: {folder_path}")
            extension =self .extension_dropdown .currentText ()
            if self .include_subfolders_checkbox .isChecked ():
                for root ,dirs ,files in os .walk (folder_path ):
                    for file in files :
                        if file .endswith (extension ):
                            file_path =os .path .relpath (os .path .join (root ,file ),folder_path )
                            self .file_list .addItem (file_path )
            else :
                for file in os .listdir (folder_path ):
                    if file .endswith (extension ):
                        self .file_list .addItem (file )

    def select_all (self ,state ):
        is_checked =self .select_all_checkbox .isChecked ()
        for index in range (self .file_list .count ()):
            item =self .file_list .item (index )
            item .setSelected (is_checked )

    def read_abf_file (self ,file_path ):
        try :

            raw_io =AxonRawIO (filename =file_path )


            raw_io .parse_header ()


            channel_index =0 


            signal_size =raw_io .get_signal_size (block_index =0 ,seg_index =0 )



            data =raw_io .get_analogsignal_chunk (block_index =0 ,seg_index =0 ,i_start =0 ,i_stop =signal_size ,channel_indexes =[channel_index ])


            data =raw_io .rescale_signal_raw_to_float (data ,dtype ='float64',channel_indexes =[channel_index ]).flatten ()


            sampling_rate =raw_io .get_signal_sampling_rate ()
            return data ,sampling_rate 
        except :
            abf =pyabf .ABF (file_path )
            data =abf .sweepY 
            sampling_rate =abf .dataRate 
            return data ,sampling_rate 

    def combine_datasets (self ):
        selected_files =[self .file_list .item (i ).text ()for i in range (self .file_list .count ())if self .file_list .item (i ).isSelected ()]
        if selected_files :
            if self .select_all_checkbox .isChecked ():
                selected_files .sort ()
            else :
                selected_indexes =self .file_list .selectedIndexes ()
                selected_files =[self .file_list .item (index .row ()).text ()for index in selected_indexes ]

            extension =self .extension_dropdown .currentText ()
            folder_path =self .folder_path_label .text ().replace ("Selected Folder: ","")

            if extension in [".dataset.npz",".MLdataset.npz"]:
                self .combine_npz_datasets (selected_files ,folder_path ,extension )
            elif extension in [".abf",".h5"]:
                self .combine_abf_h5_datasets (selected_files ,folder_path ,extension )
        else :
            QMessageBox .warning (self ,"Warning","No files selected.")

    def combine_npz_datasets (self ,selected_files ,folder_path ,extension ):
        file_lengths =[]
        if self .same_duration_checkbox .isChecked ():
            file_length ,ok =QInputDialog .getInt (self ,"File Duration","Enter the duration of each file in seconds:")
            if ok :
                file_lengths =[file_length ]*len (selected_files )
            else :
                QMessageBox .warning (self ,"Warning","File duration not provided. Skipping combination.")
                return 
        else :
            for file_path in selected_files :
                file_length ,ok =QInputDialog .getInt (self ,"File Duration",f"Enter the duration of file '{file_path}' in seconds:")
                if ok :
                    file_lengths .append (file_length )
                else :
                    QMessageBox .warning (self ,"Warning","File duration not provided. Skipping file.")
                    return 

        combined_data =None 
        settings_file =None 
        cumulative_time =0 
        for file_path ,file_length in zip (selected_files ,file_lengths ):
            full_path =os .path .join (folder_path ,file_path )
            with np .load (full_path )as data :
                if combined_data is None :
                    combined_data =data ['X']
                else :
                    try :
                        data_x =data ['X']
                        data_x [:,8 ]+=cumulative_time 
                        combined_data =np .concatenate ((combined_data ,data_x ))
                    except :
                        print (f"Cannot save file: {file_path}")
                if settings_file is None :
                    settings_file =data ['settings']
            cumulative_time +=file_length 

        save_path ,_ =QFileDialog .getSaveFileName (self ,"Save Combined Dataset","",f"NumPy Files (*{extension})")
        if save_path :
            if not save_path .endswith (extension ):
                save_path +=extension 
            np .savez (save_path ,X =combined_data ,settings =settings_file )
            QMessageBox .information (self ,"Success","Datasets/Files combined successfully.")

    def combine_abf_h5_datasets (self ,selected_files ,folder_path ,extension ):
        combined_data =[]
        sampling_rate =None 

        for file_path in selected_files :
            full_path =os .path .join (folder_path ,file_path )
            if extension ==".abf":
                data ,file_sampling_rate =self .read_abf_file (full_path )
            elif extension ==".h5":
                with h5py .File (full_path ,'r')as f :
                    data =f ['selected_data'][:]
                    file_sampling_rate =f .attrs ['sampling_rate']

            combined_data .append (data )

            if sampling_rate is None :
                sampling_rate =file_sampling_rate 
            elif sampling_rate !=file_sampling_rate :
                QMessageBox .warning (self ,"Warning","Files have different sampling rates. Proceeding with combination, but please be cautious with the results.")


        combined_data =np .concatenate (combined_data )


        save_path ,_ =QFileDialog .getSaveFileName (self ,"Save Combined Dataset","","HDF5 Files (*.h5)")
        if save_path :
            if not save_path .endswith ('.h5'):
                save_path +='.h5'
            with h5py .File (save_path ,'w')as f :
                f .create_dataset ('selected_data',data =combined_data )
                f .attrs ['sampling_rate']=sampling_rate 
            QMessageBox .information (self ,"Success","Datasets combined successfully and saved as .h5 file.")

if __name__ =='__main__':
    app =QApplication (sys .argv )
    app .setStyle (QStyleFactory .create ('Fusion'))


    palette =QPalette ()
    palette .setColor (QPalette .ColorRole .Window ,QColor (53 ,53 ,53 ))
    palette .setColor (QPalette .ColorRole .WindowText ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .Base ,QColor (25 ,25 ,25 ))
    palette .setColor (QPalette .ColorRole .AlternateBase ,QColor (53 ,53 ,53 ))
    palette .setColor (QPalette .ColorRole .ToolTipBase ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .ToolTipText ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .Text ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .Button ,QColor (53 ,53 ,53 ))
    palette .setColor (QPalette .ColorRole .ButtonText ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .BrightText ,Qt .GlobalColor .red )
    palette .setColor (QPalette .ColorRole .Link ,QColor (42 ,130 ,218 ))
    palette .setColor (QPalette .ColorRole .Highlight ,QColor (42 ,130 ,218 ))
    palette .setColor (QPalette .ColorRole .HighlightedText ,Qt .GlobalColor .black )
    app .setPalette (palette )

    window =SDCombineDatasets ()
    window .show ()
    sys .exit (app .exec ())