import sys 
from PySide6 .QtWidgets import QApplication ,QMainWindow ,QWidget ,QHBoxLayout ,QVBoxLayout ,QPushButton ,QCheckBox ,QListWidget ,QLabel ,QFileDialog ,QLineEdit ,QMessageBox ,QListWidgetItem ,QSplitter ,QGroupBox ,QFormLayout ,QComboBox ,QSpinBox ,QStyleFactory 
from PySide6 .QtCore import Qt 
from PySide6 .QtGui import QPalette ,QColor 
import os 
import numpy as np 
from neo .rawio import AxonRawIO 
from scipy .ndimage import uniform_filter1d 
import matplotlib 
from matplotlib .backends .backend_qtagg import FigureCanvasQTAgg ,NavigationToolbar2QT 
from matplotlib .figure import Figure 
import h5py 
from scipy .signal import butter ,bessel ,cheby1 ,cheby2 ,ellip ,firwin ,lfilter ,sosfilt ,sosfilt_zi 

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

def calculate_rolling_stats (data ,sampling_rate ,avg_window_size_in_ms ):
    avg_window_size_samples =int ((avg_window_size_in_ms /1000 )*sampling_rate )
    rolling_avg =uniform_filter1d (data ,size =avg_window_size_samples )
    return rolling_avg 

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

class MainWindow (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("SD ABF File Plotter and Selector App")
        self .setGeometry (100 ,100 ,1200 ,800 )

        self .data =None 
        self .sampling_rate =None 
        self .time =None 
        self .selected_regions =None 
        self .segment_widgets =[]
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


        self .app_name_label =QLabel ("SD ABF File Plotter and Selector App")
        self .app_name_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        self .app_name_label .setStyleSheet ("font-size: 22px; font-weight: bold;")
        self .email_label =QLabel ("shankar.dutt@anu.edu.au")
        self .email_label .setAlignment (Qt .AlignmentFlag .AlignCenter )

        self .select_folder_btn =QPushButton ("Select Folder")
        self .select_folder_btn .clicked .connect (self .select_folder )

        self .include_subfolders_chk =QCheckBox ("Include Subfolders")

        self .files_list_widget =QListWidget ()
        self .files_list_widget .setSelectionMode (QListWidget .SelectionMode .MultiSelection )

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


        right_splitter =QSplitter (Qt .Orientation .Vertical )
        right_layout .addWidget (right_splitter )

        top_right_widget =QWidget ()
        top_right_layout =QVBoxLayout ()
        top_right_widget .setLayout (top_right_layout )

        bottom_right_widget =QWidget ()
        bottom_right_layout =QVBoxLayout ()
        bottom_right_widget .setLayout (bottom_right_layout )

        right_splitter .addWidget (top_right_widget )
        right_splitter .addWidget (bottom_right_widget )


        self .canvas =MplCanvas (self ,width =5 ,height =4 ,dpi =100 )
        top_right_layout .addWidget (self .canvas )

        self .mpl_toolbar =NavigationToolbar2QT (self .canvas ,self )
        top_right_layout .addWidget (self .mpl_toolbar )


        bottom_right_widget =QWidget ()
        bottom_right_layout =QHBoxLayout ()
        bottom_right_widget .setLayout (bottom_right_layout )
        right_splitter .addWidget (bottom_right_widget )

        self .calculate_avg_group =QGroupBox ("Calculate and Plot Avg")
        self .calculate_avg_layout =QFormLayout ()
        self .calculate_avg_group .setLayout (self .calculate_avg_layout )

        self .calculate_avg_chk =QCheckBox ("Calculate and Plot Avg")
        self .calculate_avg_chk .stateChanged .connect (self .toggle_avg_window_size )

        self .avg_window_size_label =QLabel ("Avg Window Size (ms):")
        self .avg_window_size_input =QLineEdit ("10")

        self .avg_window_size_input .editingFinished .connect (self .update_plot )

        self .update_plot_btn =QPushButton ("Update Plot")

        self .update_plot_btn .clicked .connect (self .update_plot )

        self .calculate_avg_layout .addRow (self .calculate_avg_chk )
        self .calculate_avg_layout .addRow (self .avg_window_size_label ,self .avg_window_size_input )
        self .calculate_avg_layout .addRow (self .update_plot_btn )

        self .threshold_group =QGroupBox ("Select Regions within Threshold")
        self .threshold_layout =QFormLayout ()
        self .threshold_group .setLayout (self .threshold_layout )

        self .threshold_chk =QCheckBox ("Select Regions within Threshold")
        self .threshold_chk .stateChanged .connect (self .toggle_threshold_input )

        self .threshold_value_label =QLabel ("Value for selecting regions(pA):")
        self .threshold_value_input =QSpinBox ()
        self .threshold_value_input .setRange (0 ,1000000 )
        self .threshold_value_input .setValue (0 )
        self .threshold_value_input .setEnabled (False )
        self .threshold_value_input .editingFinished .connect (self .update_plot )

        self .threshold_label =QLabel ("Threshold (% of the value above):")
        self .threshold_input =QLineEdit ("75")
        self .threshold_input .setEnabled (False )
        self .threshold_input .editingFinished .connect (self .update_plot )

        self .threshold_layout .addRow (self .threshold_chk )
        self .threshold_layout .addRow (self .threshold_value_label ,self .threshold_value_input )
        self .threshold_layout .addRow (self .threshold_label ,self .threshold_input )

        self .select_segments_group =QGroupBox ("Select Segments")
        self .select_segments_layout =QVBoxLayout ()
        self .select_segments_group .setLayout (self .select_segments_layout )

        self .select_segments_chk =QCheckBox ("Select Segments")
        self .select_segments_chk .stateChanged .connect (self .toggle_select_segments )

        self .segment_dropdown =QComboBox ()
        self .segment_dropdown .setEnabled (False )

        self .delete_segment_btn =QPushButton ("Delete Segment")
        self .delete_segment_btn .setEnabled (False )
        self .delete_segment_btn .clicked .connect (self .delete_segment )

        self .select_segments_layout .addWidget (self .select_segments_chk )
        self .select_segments_layout .addWidget (self .segment_dropdown )
        self .select_segments_layout .addWidget (self .delete_segment_btn )

        bottom_right_layout .addWidget (self .calculate_avg_group )
        bottom_right_layout .addWidget (self .threshold_group )
        bottom_right_layout .addWidget (self .select_segments_group )

        bottom_button_layout =QHBoxLayout ()
        bottom_right_layout .addLayout (bottom_button_layout )

        self .save_btn =QPushButton ("Save Selected Data")
        self .save_btn .clicked .connect (self .save_selected_data )
        bottom_button_layout .addWidget (self .save_btn )

        self .raw_data =[]

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
            file_path =selected_items [0 ].data (Qt .ItemDataRole .UserRole )
            if file_path .endswith ('.abf'):
                self .raw_data ,self .sampling_rate ,self .time =load_abf_file (file_path )
            elif file_path .endswith ('.hdf5')or file_path .endswith ('.h5'):
                self .raw_data ,self .sampling_rate ,self .time =load_hdf5_file (file_path )

            self .data =self .raw_data .copy ()

            if self .low_pass_filter_chk .isChecked ():
                filter_type =self .filter_type_dropdown .currentText ()
                cutoff_frequency =self .cutoff_frequency_spinbox .value ()*1000 

                if self .sampling_rate <=cutoff_frequency *2 :
                    QMessageBox .warning (self ,"Error","The selected cutoff frequency is too high for the sampling rate.")
                    return 

                self .data =self .apply_low_pass_filter (self .data ,cutoff_frequency ,filter_type ,self .sampling_rate )


            self .canvas .axes .clear ()
            self .segments .clear ()
            self .segment_dropdown .clear ()


            nth_element =self .nth_element_spinbox .value ()


            self .canvas .axes .plot (self .time [::nth_element ],self .data [::nth_element ],linewidth =0.5 )
            self .canvas .axes .set_xlabel ('Time (s)')
            self .canvas .axes .set_ylabel ('Current (nA)')
            self .canvas .axes .set_xlim ([min (self .time ),max (self .time )])
            self .canvas .figure .tight_layout ()
            self .canvas .draw ()


            self .calculate_avg_chk .setChecked (False )
            self .threshold_chk .setChecked (False )
            self .select_segments_chk .setChecked (False )

    def update_plot (self ):
        if self .data is not None :
            nth_element =self .nth_element_spinbox .value ()
            if not self .canvas .axes .lines :
                self .canvas .axes .plot (self .time [::nth_element ],self .data [::nth_element ],linewidth =0.5 )
                self .canvas .axes .set_xlabel ('Time (s)')
                self .canvas .axes .set_ylabel ('Current (nA)')
                self .canvas .axes .set_xlim ([min (self .time ),max (self .time )])
                self .canvas .figure .tight_layout ()

            show_rolling_avg =self .calculate_avg_chk .isChecked ()
            if show_rolling_avg :
                avg_window_size_in_ms =float (self .avg_window_size_input .text ())
                rolling_avg =calculate_rolling_stats (self .data ,self .sampling_rate ,avg_window_size_in_ms )
                if len (self .canvas .axes .lines )>1 :
                    self .canvas .axes .lines [1 ].set_data (self .time ,rolling_avg )
                else :
                    self .canvas .axes .plot (self .time ,rolling_avg ,linewidth =2 )
            else :
                if len (self .canvas .axes .lines )>1 :
                    self .canvas .axes .lines [1 ].remove ()

            show_threshold =self .threshold_chk .isChecked ()
            if show_threshold :
                threshold_percentage =float (self .threshold_input .text ())/100 
                if self .data is not None :
                    if self .threshold_value_input .value ()==0 :
                        self .threshold_value_input .setValue (int (np .mean (self .data )*1000 ))
                    threshold_value =self .threshold_value_input .value ()/1000 
                    avg_window_size_in_ms =float (self .avg_window_size_input .text ())
                    rolling_avg =calculate_rolling_stats (self .data ,self .sampling_rate ,avg_window_size_in_ms )
                    threshold_lower =threshold_value -(threshold_value *(1 -threshold_percentage ))
                    threshold_upper =threshold_value +(threshold_value *(1 -threshold_percentage ))

                    self .selected_regions =np .where ((rolling_avg >=threshold_lower )&(rolling_avg <=threshold_upper ))[0 ]


                    threshold_lines =[line for line in self .canvas .axes .lines if line .get_color ()=='r']
                    for line in threshold_lines :
                        line .remove ()
                    threshold_spans =[patch for patch in self .canvas .axes .patches if patch .get_facecolor ()==(1.0 ,0.0 ,0.0 ,0.3 )]
                    for span in threshold_spans :
                        span .remove ()


                    for region_start ,region_end in self .find_contiguous_regions (self .selected_regions ):
                        start_time =self .time [region_start ]
                        end_time =self .time [region_end ]
                        self .canvas .axes .axvline (x =start_time ,color ='r',linestyle ='-',linewidth =0.5 )
                        self .canvas .axes .axvline (x =end_time ,color ='r',linestyle ='-',linewidth =0.5 )
                        self .canvas .axes .axvspan (start_time ,end_time ,alpha =0.3 ,color ='red')
            else :

                threshold_lines =[line for line in self .canvas .axes .lines if line .get_color ()=='r']
                for line in threshold_lines :
                    line .remove ()
                threshold_spans =[patch for patch in self .canvas .axes .patches if patch .get_facecolor ()==(1.0 ,0.0 ,0.0 ,0.3 )]
                for span in threshold_spans :
                    span .remove ()

            show_segments =self .select_segments_chk .isChecked ()
            if show_segments :
                while len (self .canvas .axes .lines )>2 :
                    self .canvas .axes .lines [2 ].remove ()
                for start_time ,end_time in self .segments :
                    self .canvas .axes .axvline (x =start_time ,color ='g',linestyle ='-',linewidth =0.5 )
                    self .canvas .axes .axvline (x =end_time ,color ='g',linestyle ='-',linewidth =0.5 )
                    self .canvas .axes .axvspan (start_time ,end_time ,alpha =0.3 ,color ='green')
            else :
                segment_lines =[line for line in self .canvas .axes .lines if line .get_color ()=='g']
                for line in segment_lines :
                    line .remove ()
                segment_patches =[patch for patch in self .canvas .axes .patches if patch .get_facecolor ()==(0.0 ,0.5019607843137255 ,0.0 ,0.3 )]
                for patch in segment_patches :
                    patch .remove ()

            self .canvas .draw ()



    def find_contiguous_regions (self ,data ):
        contiguous_regions =[]
        data =np .sort (data )
        start_index =data [0 ]
        prev_index =start_index 
        for i in range (1 ,len (data )):
            if data [i ]>prev_index +1 :
                contiguous_regions .append ((start_index ,prev_index ))
                start_index =data [i ]
            prev_index =data [i ]
        contiguous_regions .append ((start_index ,data [-1 ]))
        return contiguous_regions 

    def toggle_avg_window_size (self ,state ):
        self .avg_window_size_input .setEnabled (state ==Qt .CheckState .Checked .value )
        self .update_plot_btn .setEnabled (state ==Qt .CheckState .Checked .value )
        self .update_plot ()

    def toggle_threshold_input (self ,state ):
        self .threshold_input .setEnabled (state ==Qt .CheckState .Checked .value )
        self .threshold_value_input .setEnabled (state ==Qt .CheckState .Checked .value )
        self .select_segments_chk .setChecked (False )
        self .update_plot ()

    def toggle_select_segments (self ,state ):
        if state ==Qt .CheckState .Checked .value :
            segment_widget =SegmentWidget ()
            segment_widget .add_button .clicked .connect (lambda :self .add_segment (segment_widget ))
            self .segment_widgets .append (segment_widget )
            self .select_segments_layout .insertWidget (self .select_segments_layout .count ()-2 ,segment_widget )
            segment_widget .show ()
            self .segment_dropdown .setEnabled (True )
            self .delete_segment_btn .setEnabled (True )
        else :
            while self .segment_widgets :
                segment_widget =self .segment_widgets .pop ()
                self .select_segments_layout .removeWidget (segment_widget )
                segment_widget .deleteLater ()
            self .segments .clear ()
            self .segment_dropdown .clear ()
            self .segment_dropdown .setEnabled (False )
            self .delete_segment_btn .setEnabled (False )

        self .threshold_chk .setChecked (False )
        self .update_plot ()

    def add_segment (self ,segment_widget ):
        start_time =float (segment_widget .start_input .text ())
        end_time =float (segment_widget .end_input .text ())
        self .segments .append ((start_time ,end_time ))
        segment_label =f"Segment: {start_time} - {end_time}"
        self .segment_dropdown .addItem (segment_label )
        index =self .segment_dropdown .count ()-1 
        self .segment_dropdown .setItemData (index ,segment_widget )
        self .update_plot ()

    def delete_segment (self ):
        if self .segment_dropdown .count ()>0 :
            index =self .segment_dropdown .currentIndex ()
            self .segments .pop (index )
            segment_label =self .segment_dropdown .itemText (index )
            self .segment_dropdown .removeItem (index )
            for i in range (self .select_segments_layout .count ()):
                widget =self .select_segments_layout .itemAt (i ).widget ()
                if isinstance (widget ,QLabel )and widget .text ()==segment_label :
                    self .select_segments_layout .removeWidget (widget )
                    widget .deleteLater ()
                    break 


            segment_lines =[line for line in self .canvas .axes .lines if line .get_color ()=='g']
            for line in segment_lines :
                line .remove ()
            segment_patches =[patch for patch in self .canvas .axes .patches if patch .get_facecolor ()==(0.0 ,0.5019607843137255 ,0.0 ,0.3 )]
            for patch in segment_patches :
                patch .remove ()


            for start_time ,end_time in self .segments :
                self .canvas .axes .axvline (x =start_time ,color ='g',linestyle ='-',linewidth =0.5 )
                self .canvas .axes .axvline (x =end_time ,color ='g',linestyle ='-',linewidth =0.5 )
                self .canvas .axes .axvspan (start_time ,end_time ,alpha =0.3 ,color ='green')

            self .canvas .draw ()

    def save_selected_data (self ):
        if self .data is not None :

            if self .threshold_chk .isChecked ():
                selected_data =[]
                for region_start ,region_end in self .find_contiguous_regions (self .selected_regions ):
                    start_index =np .searchsorted (self .time ,self .time [region_start ])
                    end_index =np .searchsorted (self .time ,self .time [region_end ])
                    selected_data .append (self .raw_data [start_index :end_index +1 ])
                selected_data =np .concatenate (selected_data )
            elif self .select_segments_chk .isChecked ():
                selected_data =[]
                for start_time ,end_time in self .segments :
                    start_index =np .searchsorted (self .time ,start_time )
                    end_index =np .searchsorted (self .time ,end_time )
                    selected_data .append (self .raw_data [start_index :end_index +1 ])
                selected_data =np .concatenate (selected_data )
            else :
                QMessageBox .warning (self ,"Warning","No data selected.")
                return 

            file_dialog =QFileDialog ()
            file_dialog .setDefaultSuffix ("h5")
            file_path ,_ =file_dialog .getSaveFileName (self ,"Save Selected Data","","HDF5 Files (*.h5)")

            if file_path :
                with h5py .File (file_path ,'w')as f :
                    f .create_dataset ('selected_data',data =selected_data )
                    f .attrs ['sampling_rate']=self .sampling_rate 
                QMessageBox .information (self ,"Success","Raw data saved successfully.")


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