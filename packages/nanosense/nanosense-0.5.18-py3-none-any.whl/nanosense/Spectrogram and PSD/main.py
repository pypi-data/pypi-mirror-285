import sys 
from PySide6 .QtWidgets import QApplication ,QMainWindow ,QWidget ,QHBoxLayout ,QVBoxLayout ,QPushButton ,QCheckBox ,QListWidget ,QLabel ,QFileDialog ,QLineEdit ,QMessageBox ,QListWidgetItem ,QSplitter ,QGroupBox ,QFormLayout ,QComboBox ,QSpinBox ,QTabWidget ,QDoubleSpinBox ,QGridLayout ,QStyleFactory 
from PySide6 .QtCore import Qt 
from PySide6 .QtGui import QIcon ,QFont ,QAction ,QPalette ,QColor 
import os 
import numpy as np 
from neo .rawio import AxonRawIO 
import matplotlib 
from matplotlib .backends .backend_qtagg import FigureCanvasQTAgg ,NavigationToolbar2QT 
from matplotlib .figure import Figure 
import h5py 
from scipy .signal import butter ,bessel ,cheby1 ,cheby2 ,ellip ,firwin ,lfilter ,sosfilt ,sosfilt_zi ,welch ,spectrogram 

matplotlib .use ('Qt5Agg')

class MplCanvas (FigureCanvasQTAgg ):
    def __init__ (self ,parent =None ,width =5 ,height =4 ,dpi =100 ):
        fig =Figure (figsize =(width ,height ),dpi =dpi )
        self .axes =fig .add_subplot (111 )
        fig .tight_layout ()
        super ().__init__ (fig )

def load_abf_file (file_path ):

    raw_io =AxonRawIO (filename =file_path )


    raw_io .parse_header ()


    channel_index =0 


    signal_size =raw_io .get_signal_size (block_index =0 ,seg_index =0 )



    data =raw_io .get_analogsignal_chunk (block_index =0 ,seg_index =0 ,i_start =0 ,i_stop =signal_size ,channel_indexes =[channel_index ])


    data =raw_io .rescale_signal_raw_to_float (data ,dtype ='float64',channel_indexes =[channel_index ]).flatten ()


    sampling_rate =raw_io .get_signal_sampling_rate ()


    time =np .arange (len (data ))/sampling_rate 

    return data ,sampling_rate ,time 

def load_hdf5_file (file_path ):
    with h5py .File (file_path ,'r')as f :
        selected_data =f ['selected_data'][()]
        sampling_rate =f .attrs ['sampling_rate']
        time =np .arange (len (selected_data ))/sampling_rate 
    return selected_data ,sampling_rate ,time 

class SegmentWidget (QWidget ):
    def __init__ (self ,parent =None ):
        super ().__init__ (parent )
        layout =QHBoxLayout ()
        self .setLayout (layout )

        self .start_label =QLabel ("Start (s):")
        self .start_input =QLineEdit ()
        self .end_label =QLabel ("End (s):")
        self .end_input =QLineEdit ()
        self .add_button =QPushButton ("Add Segment")

        layout .addWidget (self .start_label )
        layout .addWidget (self .start_input )
        layout .addWidget (self .end_label )
        layout .addWidget (self .end_input )
        layout .addWidget (self .add_button )

class SettingsWidget (QWidget ):
    def __init__ (self ,parent =None ):
        super ().__init__ (parent )
        layout =QGridLayout ()
        self .setLayout (layout )

        self .nperseg_psd_spinbox =QSpinBox ()
        self .nperseg_psd_spinbox .setRange (1 ,1000000 )
        self .nperseg_psd_spinbox .setValue (100000 )
        layout .addWidget (QLabel ("nperseg (PSD):"),0 ,0 )
        layout .addWidget (self .nperseg_psd_spinbox ,0 ,1 )

        self .noverlap_psd_spinbox =QSpinBox ()
        self .noverlap_psd_spinbox .setRange (0 ,1000000 )
        self .noverlap_psd_spinbox .setValue (128 )
        layout .addWidget (QLabel ("noverlap (PSD):"),0 ,2 )
        layout .addWidget (self .noverlap_psd_spinbox ,0 ,3 )

        self .scaling_psd_combobox =QComboBox ()
        self .scaling_psd_combobox .addItems (['density','spectrum'])
        layout .addWidget (QLabel ("scaling (PSD):"),1 ,0 )
        layout .addWidget (self .scaling_psd_combobox ,1 ,1 )

        self .nperseg_spectrogram_spinbox =QSpinBox ()
        self .nperseg_spectrogram_spinbox .setRange (1 ,1000000 )
        self .nperseg_spectrogram_spinbox .setValue (100000 )
        layout .addWidget (QLabel ("nperseg (Spectrogram):"),1 ,2 )
        layout .addWidget (self .nperseg_spectrogram_spinbox ,1 ,3 )

        self .return_onesided_spectrogram_checkbox =QCheckBox ()
        self .return_onesided_spectrogram_checkbox .setChecked (True )
        layout .addWidget (QLabel ("return_onesided (Spectrogram):"),2 ,0 )
        layout .addWidget (self .return_onesided_spectrogram_checkbox ,2 ,1 )

        self .plot_spectrogram_combobox =QComboBox ()
        self .plot_spectrogram_combobox .addItems (['pcolormesh','imshow'])
        layout .addWidget (QLabel ("Plot (Spectrogram):"),2 ,2 )
        layout .addWidget (self .plot_spectrogram_combobox ,2 ,3 )


class MainWindow (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("SD Spectrogram and PSD Plotter")
        self .setGeometry (100 ,100 ,1200 ,800 )

        self .data =None 
        self .sampling_rate =None 
        self .time =None 
        self .segments =[]

        main_splitter =QSplitter (Qt .Orientation .Horizontal )

        left_widget =QWidget ()
        left_layout =QVBoxLayout ()
        left_widget .setLayout (left_layout )

        right_widget =QWidget ()
        right_layout =QVBoxLayout ()
        right_widget .setLayout (right_layout )

        main_splitter .addWidget (left_widget )
        main_splitter .addWidget (right_widget )
        main_splitter .setSizes ([300 ,900 ])

        self .setCentralWidget (main_splitter )

        nth_element_layout =QHBoxLayout ()


        self .app_name_label =QLabel ("SD Spectrogram and PSD Plotter")
        self .app_name_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        self .app_name_label .setStyleSheet ("font-size: 22px; font-weight: bold;")
        self .email_label =QLabel ("shankar.dutt@anu.edu.au")
        self .email_label .setAlignment (Qt .AlignmentFlag .AlignCenter )

        self .select_folder_btn =QPushButton ("Select Folder")
        self .select_folder_btn .clicked .connect (self .select_folder )

        self .include_subfolders_chk =QCheckBox ("Include Subfolders")

        self .files_list_widget =QListWidget ()
        self .files_list_widget .setSelectionMode (QListWidget .SelectionMode .ExtendedSelection )

        self .folder_path_label =QLabel (" ")
        self .folder_path_label .setWordWrap (True )

        self .nth_element_label =QLabel ("Plot nth element:")
        self .nth_element_spinbox =QSpinBox ()
        self .nth_element_spinbox .setMinimum (1 )
        self .nth_element_spinbox .setMaximum (1000 )
        self .nth_element_spinbox .setValue (1 )

        nth_element_layout .addWidget (self .nth_element_label )
        nth_element_layout .addWidget (self .nth_element_spinbox )

        self .low_pass_filter_chk =QCheckBox ("Apply Low Pass Filter")
        self .low_pass_filter_chk .stateChanged .connect (self .toggle_low_pass_filter )

        self .filter_type_label =QLabel ("Filter Type:")
        self .filter_type_dropdown =QComboBox ()
        self .filter_type_dropdown .addItems (["Butterworth","Bessel","Chebyshev I","Chebyshev II","Elliptic","FIR","IIR"])
        self .filter_type_dropdown .setEnabled (False )

        self .cutoff_frequency_label =QLabel ("Cutoff Frequency (kHz):")
        self .cutoff_frequency_spinbox =QSpinBox ()
        self .cutoff_frequency_spinbox .setRange (1 ,1000 )
        self .cutoff_frequency_spinbox .setValue (10 )
        self .cutoff_frequency_spinbox .setEnabled (False )

        self .plot_btn =QPushButton ("Plot Selected File")
        self .plot_btn .clicked .connect (self .plot_selected_file )

        left_layout .addWidget (self .app_name_label )
        left_layout .addWidget (self .email_label )
        left_layout .addWidget (self .select_folder_btn )
        left_layout .addWidget (self .include_subfolders_chk )
        left_layout .addWidget (self .files_list_widget )
        left_layout .addWidget (self .folder_path_label )
        left_layout .addLayout (nth_element_layout )
        left_layout .addWidget (self .low_pass_filter_chk )
        left_layout .addWidget (self .filter_type_label )
        left_layout .addWidget (self .filter_type_dropdown )
        left_layout .addWidget (self .cutoff_frequency_label )
        left_layout .addWidget (self .cutoff_frequency_spinbox )
        left_layout .addWidget (self .plot_btn )


        self .tab_widget =QTabWidget ()
        right_layout .addWidget (self .tab_widget )

        self .plots_tab =QWidget ()
        self .plots_tab_layout =QVBoxLayout ()
        self .plots_tab .setLayout (self .plots_tab_layout )
        self .tab_widget .addTab (self .plots_tab ,"Plots")

        self .psd_tab =QWidget ()
        self .psd_canvas =MplCanvas (self ,width =8 ,height =6 ,dpi =100 )
        self .psd_toolbar =NavigationToolbar2QT (self .psd_canvas ,self )
        psd_layout =QVBoxLayout ()
        psd_layout .addWidget (self .psd_canvas )
        psd_layout .addWidget (self .psd_toolbar )
        self .psd_tab .setLayout (psd_layout )
        self .tab_widget .addTab (self .psd_tab ,"PSD")

        self .spectrogram_tab =QWidget ()
        self .spectrogram_tab_layout =QVBoxLayout ()
        self .spectrogram_tab .setLayout (self .spectrogram_tab_layout )
        self .tab_widget .addTab (self .spectrogram_tab ,"Spectrogram")

        bottom_layout =QHBoxLayout ()
        self .plot_spectrogram_btn =QPushButton ("Plot Spectrogram")
        self .plot_spectrogram_btn .clicked .connect (self .plot_spectrogram )
        self .plot_psd_btn =QPushButton ("Plot PSD")
        self .plot_psd_btn .clicked .connect (self .plot_psd )
        bottom_layout .addWidget (self .plot_spectrogram_btn )
        bottom_layout .addWidget (self .plot_psd_btn )
        right_layout .addLayout (bottom_layout )

        self .settings_group =QGroupBox ("Settings")
        self .settings_layout =QVBoxLayout ()
        self .settings_group .setLayout (self .settings_layout )
        self .settings_widget =SettingsWidget ()
        self .settings_layout .addWidget (self .settings_widget )
        right_layout .addWidget (self .settings_group )

        self .plot_tabs ={}
        self .spectrogram_tabs ={}
        self .plots_tab_widget =QTabWidget ()
        self .plots_tab_layout .addWidget (self .plots_tab_widget )

        self .spectrogram_tab_widget =QTabWidget ()
        self .spectrogram_tab_layout .addWidget (self .spectrogram_tab_widget )

    def toggle_low_pass_filter (self ,state ):
        self .filter_type_dropdown .setEnabled (state ==Qt .CheckState .Checked .value )
        self .cutoff_frequency_spinbox .setEnabled (state ==Qt .CheckState .Checked .value )

    def select_folder (self ):
        options =QFileDialog .Option .ShowDirsOnly 
        directory =QFileDialog .getExistingDirectory (self ,"Select Folder","",options =options )
        if directory :
            self .folder_path_label .setText (f"Selected folder: {directory}")
            self .populate_file_list (directory ,self .include_subfolders_chk .isChecked ())

    def apply_low_pass_filter (self ,data ,cutoff_frequency ,type ,sampling_rate ):
        if type =='Butterworth':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            sos =butter (N =8 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
            zi =sosfilt_zi (sos )*data [0 ]
            filtered_data ,_ =sosfilt (sos ,data ,zi =zi )
            return filtered_data 
        elif type =='Bessel':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            sos =bessel (N =8 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
            zi =sosfilt_zi (sos )*data [0 ]
            filtered_data ,_ =sosfilt (sos ,data ,zi =zi )
            return filtered_data 
        elif type =='Chebyshev I':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            sos =cheby1 (N =8 ,rp =0.1 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
            zi =sosfilt_zi (sos )*data [0 ]
            filtered_data ,_ =sosfilt (sos ,data ,zi =zi )
            return filtered_data 
        elif type =='Chebyshev II':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            sos =cheby2 (N =8 ,rs =40 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
            zi =sosfilt_zi (sos )*data [0 ]
            filtered_data ,_ =sosfilt (sos ,data ,zi =zi )
            return filtered_data 
        elif type =='Elliptic':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            sos =ellip (N =8 ,rp =0.1 ,rs =40 ,Wn =cutoff ,btype ='low',analog =False ,output ='sos')
            zi =sosfilt_zi (sos )*data [0 ]
            filtered_data ,_ =sosfilt (sos ,data ,zi =zi )
            return filtered_data 
        elif type =='FIR':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            taps =firwin (101 ,cutoff )
            filtered_data =lfilter (taps ,1 ,data )
            return filtered_data 
        elif type =='IIR':
            nyquist_rate =sampling_rate /2.0 
            cutoff =cutoff_frequency /nyquist_rate 
            b ,a =butter (N =8 ,Wn =cutoff ,btype ='low',analog =False )
            filtered_data =lfilter (b ,a ,data )
            return filtered_data 

    def populate_file_list (self ,directory ,include_subfolders ):
        self .files_list_widget .clear ()
        for root ,dirs ,files in os .walk (directory ):
            for file in files :
                if file .endswith ('.abf')or file .endswith ('.hdf5')or file .endswith ('.h5'):
                    rel_path =os .path .relpath (os .path .join (root ,file ),start =directory )
                    item =QListWidgetItem (rel_path )
                    item .setData (Qt .ItemDataRole .UserRole ,os .path .join (root ,file ))
                    self .files_list_widget .addItem (item )
            if not include_subfolders :
                break 

    def plot_selected_file (self ):
        selected_items =self .files_list_widget .selectedItems ()
        if selected_items :
            self .data_dict ={}
            self .sampling_rate_dict ={}
            self .time_dict ={}


            for file_path in self .plot_tabs :
                self .plot_tabs [file_path ]['segments'].clear ()
                self .plot_tabs [file_path ]['segment_dropdown'].clear ()
                self .plot_tabs [file_path ]['segment_dropdown'].setEnabled (False )
                self .plot_tabs [file_path ]['delete_segment_btn'].setEnabled (False )

            for item in selected_items :
                file_path =item .data (Qt .ItemDataRole .UserRole )
                if file_path .endswith ('.abf'):
                    data ,sampling_rate ,time =load_abf_file (file_path )
                elif file_path .endswith ('.hdf5')or file_path .endswith ('.h5'):
                    data ,sampling_rate ,time =load_hdf5_file (file_path )

                if self .low_pass_filter_chk .isChecked ():
                    filter_type =self .filter_type_dropdown .currentText ()
                    cutoff_frequency =self .cutoff_frequency_spinbox .value ()*1000 

                    if sampling_rate <=cutoff_frequency *2 :
                        QMessageBox .warning (self ,"Error","The selected cutoff frequency is too high for the sampling rate.")
                        continue 

                    data =self .apply_low_pass_filter (data ,cutoff_frequency ,filter_type ,sampling_rate )

                self .data_dict [file_path ]=data 
                self .sampling_rate_dict [file_path ]=sampling_rate 
                self .time_dict [file_path ]=time 

                if file_path not in self .plot_tabs :
                    plot_tab =QWidget ()
                    plot_layout =QVBoxLayout ()
                    plot_tab .setLayout (plot_layout )

                    canvas =MplCanvas (self ,width =8 ,height =6 ,dpi =100 )
                    mpl_toolbar =NavigationToolbar2QT (canvas ,self )

                    canvas_layout =QVBoxLayout ()
                    canvas_layout .addWidget (canvas )
                    canvas_layout .addWidget (mpl_toolbar )

                    select_segments_group =QGroupBox ("Select Segments")
                    select_segments_layout =QGridLayout ()
                    select_segments_group .setLayout (select_segments_layout )

                    segment_widget =SegmentWidget ()
                    segment_widget .add_button .clicked .connect (lambda _ ,f =file_path :self .add_segment (f ))
                    select_segments_layout .addWidget (segment_widget ,0 ,0 ,1 ,2 )

                    segment_dropdown =QComboBox ()
                    segment_dropdown .setEnabled (False )
                    select_segments_layout .addWidget (segment_dropdown ,1 ,0 )

                    delete_segment_btn =QPushButton ("Delete Segment")
                    delete_segment_btn .setEnabled (False )
                    delete_segment_btn .clicked .connect (lambda _ ,f =file_path :self .delete_segment (f ))
                    select_segments_layout .addWidget (delete_segment_btn ,1 ,1 )

                    plot_layout .addLayout (canvas_layout )
                    plot_layout .addWidget (select_segments_group )

                    self .plot_tabs [file_path ]={
                    'tab':plot_tab ,
                    'canvas':canvas ,
                    'segment_widget':segment_widget ,
                    'segment_dropdown':segment_dropdown ,
                    'delete_segment_btn':delete_segment_btn ,
                    'segments':[]
                    }


                    file_name =os .path .basename (file_path )
                    self .plots_tab_widget .addTab (plot_tab ,file_name )


                nth_element =self .nth_element_spinbox .value ()


                self .plot_tabs [file_path ]['canvas'].axes .clear ()
                self .plot_tabs [file_path ]['canvas'].axes .plot (time [::nth_element ],data [::nth_element ],linewidth =0.5 )
                self .plot_tabs [file_path ]['canvas'].axes .set_xlabel ('Time (s)')
                self .plot_tabs [file_path ]['canvas'].axes .set_ylabel ('Current (nA)')
                self .plot_tabs [file_path ]['canvas'].axes .set_xlim ([min (time ),max (time )])
                self .plot_tabs [file_path ]['canvas'].figure .tight_layout ()
                self .plot_tabs [file_path ]['canvas'].draw ()

    def add_segment (self ,file_path ):
        start_time =float (self .plot_tabs [file_path ]['segment_widget'].start_input .text ())
        end_time =float (self .plot_tabs [file_path ]['segment_widget'].end_input .text ())
        self .plot_tabs [file_path ]['segments'].append ((start_time ,end_time ))
        segment_label =f"Segment: {start_time} - {end_time}"
        self .plot_tabs [file_path ]['segment_dropdown'].addItem (segment_label )
        self .plot_tabs [file_path ]['segment_dropdown'].setEnabled (True )
        self .plot_tabs [file_path ]['delete_segment_btn'].setEnabled (True )
        self .update_plot (file_path )

    def delete_segment (self ,file_path ):
        if self .plot_tabs [file_path ]['segment_dropdown'].count ()>0 :
            index =self .plot_tabs [file_path ]['segment_dropdown'].currentIndex ()
            self .plot_tabs [file_path ]['segments'].pop (index )
            self .plot_tabs [file_path ]['segment_dropdown'].removeItem (index )
            if self .plot_tabs [file_path ]['segment_dropdown'].count ()==0 :
                self .plot_tabs [file_path ]['segment_dropdown'].setEnabled (False )
                self .plot_tabs [file_path ]['delete_segment_btn'].setEnabled (False )
            self .update_plot (file_path )

    def update_plot (self ,file_path ):
        data =self .data_dict [file_path ]
        time =self .time_dict [file_path ]

        self .plot_tabs [file_path ]['canvas'].axes .clear ()
        nth_element =self .nth_element_spinbox .value ()
        self .plot_tabs [file_path ]['canvas'].axes .plot (time [::nth_element ],data [::nth_element ],linewidth =0.5 )
        self .plot_tabs [file_path ]['canvas'].axes .set_xlabel ('Time (s)')
        self .plot_tabs [file_path ]['canvas'].axes .set_ylabel ('Current (nA)')
        self .plot_tabs [file_path ]['canvas'].axes .set_xlim ([min (time ),max (time )])

        segment_lines =[line for line in self .plot_tabs [file_path ]['canvas'].axes .lines if line .get_color ()=='g']
        for line in segment_lines :
            line .remove ()
        segment_patches =[patch for patch in self .plot_tabs [file_path ]['canvas'].axes .patches if patch .get_facecolor ()==(0.0 ,0.5019607843137255 ,0.0 ,0.3 )]
        for patch in segment_patches :
            patch .remove ()

        for start_time ,end_time in self .plot_tabs [file_path ]['segments']:
            self .plot_tabs [file_path ]['canvas'].axes .axvline (x =start_time ,color ='g',linestyle ='-',linewidth =0.5 )
            self .plot_tabs [file_path ]['canvas'].axes .axvline (x =end_time ,color ='g',linestyle ='-',linewidth =0.5 )
            self .plot_tabs [file_path ]['canvas'].axes .axvspan (start_time ,end_time ,alpha =0.3 ,color ='green')

        self .plot_tabs [file_path ]['canvas'].draw ()


    def plot_spectrogram (self ):
        if self .data_dict :
            for file_path ,data in self .data_dict .items ():
                sampling_rate =self .sampling_rate_dict [file_path ]
                time =self .time_dict [file_path ]

                if file_path not in self .spectrogram_tabs :
                    spectrogram_tab =QWidget ()
                    spectrogram_layout =QVBoxLayout ()
                    spectrogram_tab .setLayout (spectrogram_layout )

                    spectrogram_canvas =MplCanvas (self ,width =8 ,height =6 ,dpi =100 )
                    spectrogram_toolbar =NavigationToolbar2QT (spectrogram_canvas ,self )
                    spectrogram_layout .addWidget (spectrogram_canvas )
                    spectrogram_layout .addWidget (spectrogram_toolbar )

                    self .spectrogram_tabs [file_path ]={
                    'tab':spectrogram_tab ,
                    'canvas':spectrogram_canvas ,
                    'colorbar':None 
                    }


                    file_name =os .path .basename (file_path )
                    self .spectrogram_tab_widget .addTab (spectrogram_tab ,file_name )

                spectrogram_canvas =self .spectrogram_tabs [file_path ]['canvas']
                spectrogram_canvas .axes .clear ()


                if self .spectrogram_tabs [file_path ]['colorbar']is None :
                    self .spectrogram_tabs [file_path ]['colorbar']=spectrogram_canvas .figure .colorbar (None ,ax =spectrogram_canvas .axes )

                segments =self .plot_tabs [file_path ]['segments']

                for start_time ,end_time in segments :
                    start_index =np .searchsorted (time ,start_time )
                    end_index =np .searchsorted (time ,end_time )


                    end_index =min (end_index ,len (time )-1 )

                    segment_data =data [start_index :end_index +1 ]
                    segment_time =time [start_index :end_index +1 ]-time [start_index ]


                    nperseg =self .settings_widget .nperseg_spectrogram_spinbox .value ()
                    return_onesided =self .settings_widget .return_onesided_spectrogram_checkbox .isChecked ()
                    plot_type =self .settings_widget .plot_spectrogram_combobox .currentText ()


                    freq ,time ,Sxx =spectrogram (segment_data ,fs =sampling_rate ,nperseg =nperseg ,return_onesided =return_onesided )


                    Sxx_db =10 *np .log10 (Sxx )


                    if plot_type =='pcolormesh':
                        im =spectrogram_canvas .axes .pcolormesh (time +segment_time [0 ],freq ,Sxx_db ,shading ='gouraud',cmap ='viridis')
                    elif plot_type =='imshow':
                        im =spectrogram_canvas .axes .imshow (Sxx_db ,extent =[segment_time [0 ],segment_time [-1 ],freq [0 ],freq [-1 ]],aspect ='auto',cmap ='viridis',origin ='lower')

                    spectrogram_canvas .axes .set_xlabel ('Time (s)')
                    spectrogram_canvas .axes .set_ylabel ('Frequency (Hz)')
                    spectrogram_canvas .axes .set_xlim ([segment_time [0 ],segment_time [-1 ]])
                    spectrogram_canvas .figure .tight_layout ()


                    self .spectrogram_tabs [file_path ]['colorbar'].mappable =im 
                    self .spectrogram_tabs [file_path ]['colorbar'].set_label ('Magnitude (dB)')

                spectrogram_canvas .draw ()
                self .tab_widget .setCurrentWidget (self .spectrogram_tabs [file_path ]['tab'])


    def plot_psd (self ):
        if self .data_dict :
            self .psd_canvas .axes .clear ()

            for file_path ,data in self .data_dict .items ():
                sampling_rate =self .sampling_rate_dict [file_path ]
                time =self .time_dict [file_path ]

                segments =self .plot_tabs [file_path ]['segments']

                for start_time ,end_time in segments :
                    start_index =np .searchsorted (time ,start_time )
                    end_index =np .searchsorted (time ,end_time )
                    segment_data =data [start_index :end_index +1 ]

                    freq ,psd_na2hz =self .calculate_psd (segment_data ,sampling_rate )
                    self .psd_canvas .axes .loglog (freq ,psd_na2hz ,linewidth =0.5 ,label =f"{os.path.basename(file_path)} - [{start_time}, {end_time}]")

            self .psd_canvas .axes .set_xlabel ('Frequency (Hz)')
            self .psd_canvas .axes .set_ylabel ('PSD (A^2/Hz)')
            self .psd_canvas .axes .set_xlim ([0.1 ,max (self .sampling_rate_dict .values ())])
            self .psd_canvas .axes .legend ()
            self .psd_canvas .figure .tight_layout ()
            self .psd_canvas .draw ()

    def calculate_psd (self ,data ,sampling_rate ):

        nperseg =self .settings_widget .nperseg_psd_spinbox .value ()
        noverlap =self .settings_widget .noverlap_psd_spinbox .value ()
        scaling =self .settings_widget .scaling_psd_combobox .currentText ()

        freq ,psd =welch (data ,fs =sampling_rate ,nperseg =nperseg ,noverlap =noverlap ,scaling =scaling )
        psd_na2hz =psd 
        return freq ,psd_na2hz 

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
    window =MainWindow ()
    window .showMaximized ()
    sys .exit (app .exec ())