from PySide6 .QtWidgets import (QMainWindow ,QApplication ,QVBoxLayout ,QHBoxLayout ,
QLabel ,QTabWidget ,QWidget ,QMenuBar ,QFileDialog ,QPushButton ,
QRadioButton ,QButtonGroup ,QSlider ,QSpinBox ,QGroupBox ,QGridLayout ,QComboBox ,QMessageBox ,QCheckBox ,
QTableWidget ,QTableWidgetItem ,QHeaderView ,QGridLayout ,QSplitter ,QVBoxLayout ,QScrollArea ,QStyleFactory )
from PySide6 .QtGui import QIcon ,QFont ,QAction ,QPalette ,QColor 
from PySide6 .QtCore import Qt 
from PySide6 import QtWidgets 
import numpy as np 
from PySide6 .QtCore import QTimer 
from sklearn .mixture import GaussianMixture 
from matplotlib .colors import LogNorm 
import sys 
import os 
import numpy as np 
import json 
from matplotlib .backends .backend_qtagg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib .backends .backend_qtagg import NavigationToolbar2QT as NavigationToolbar 
from matplotlib .figure import Figure 
import matplotlib .pyplot as plt 
import seaborn as sns 
from scipy import stats 
from typing import List 
from matplotlib .colors import PowerNorm 
import matplotlib .gridspec as gridspec 
import matplotlib .pyplot as plt 
import matplotlib .cm as cm 
import scipy 
from sklearn .decomposition import PCA 
import seaborn as sns 
from matplotlib .ticker import NullFormatter 
from scipy .stats import gaussian_kde 
import pandas as pd 
from scipy .signal import find_peaks 
from scipy .stats import norm 
import scipy .stats 
from sklearn .mixture import GaussianMixture 
from tabulate import tabulate 
from matplotlib .colors import Normalize 


MAX_FILES =11 

colorlist =['orange','red','green','blue','lime','navy','teal','olive','maroon','darkcyan','silver','gray']

cmaps =plt .colormaps ()


def plot_pairwise_matplotlib (ax ,data ):
    features =['height','fwhm','heightatfwhm','area','basewidth','skew','kurt']
    df =pd .DataFrame (data ,columns =features )
    num_features =len (features )

    for i in range (num_features ):
        for j in range (num_features ):
            if i ==j :

                ax [i ,j ].hist (df [features [i ]],bins =50 ,edgecolor ='k',color ='gray')
            else :

                ax [i ,j ].scatter (df [features [j ]],df [features [i ]],s =1 ,alpha =0.5 )

            if i ==num_features -1 :
                ax [i ,j ].set_xlabel (features [j ])
            if j ==0 :
                ax [i ,j ].set_ylabel (features [i ])

def remove_nan_arrays (X ):

    X_filtered =X [~np .isnan (X ).any (axis =1 )]


    num_removed =X .shape [0 ]-X_filtered .shape [0 ]

    return X_filtered ,num_removed 

class MainApp (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()


        self .setWindowTitle ("SD Nanopore Data Visualisation Tool")



        main_widget =QWidget (self )
        self .setCentralWidget (main_widget )
        main_layout =QHBoxLayout (main_widget )


        self .left_part =QWidget (self )
        self .right_part =QWidget (self )

        self .left_layout =QVBoxLayout (self .left_part )
        self .right_layout =QVBoxLayout (self .right_part )

        main_layout .addWidget (self .left_part ,1 )
        main_layout .addWidget (self .right_part ,6 )





        self .showMaximized ()


        title_label =QLabel ("SD Nanopore Data Visualisation Tool",self )
        author_label =QLabel ("shankar.dutt@anu.edu.au",self )
        title_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        author_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        title_label .setFont (QFont ('Arial',30 ))
        author_label .setFont (QFont ('Arial',20 ))

        self .left_layout .addWidget (title_label )
        self .left_layout .addWidget (author_label )


        self .left_tabs =QTabWidget ()
        self .right_tabs =QTabWidget ()

        self .left_layout .addWidget (self .left_tabs )
        self .right_layout .addWidget (self .right_tabs )


        self .toolbar1 =QWidget ()
        self .toolbar2 =QWidget ()


        scroll_area1 =QScrollArea ()
        scroll_area2 =QScrollArea ()


        scroll_area1 .setWidgetResizable (True )
        scroll_area2 .setWidgetResizable (True )


        scroll_area1 .setWidget (self .toolbar1 )
        scroll_area2 .setWidget (self .toolbar2 )


        self .left_tabs .addTab (scroll_area1 ,"Toolbars 1")
        self .left_tabs .addTab (scroll_area2 ,"Toolbars 2")


        self .plots_tab =QWidget ()
        self .pairwise_plots_tab =QWidget ()
        self .box_plots_tab =QWidget ()
        self .pca_corr_tab =QWidget ()
        self .time_series_tab =QWidget ()


        self .right_tabs .addTab (self .plots_tab ,"Plots")
        self .right_tabs .addTab (self .pairwise_plots_tab ,"Pairwise plots")
        self .right_tabs .addTab (self .box_plots_tab ,"Box plots and Statistics")
        self .right_tabs .addTab (self .pca_corr_tab ,"PCA and Correlation Matrix")
        self .right_tabs .addTab (self .time_series_tab ,"Time Series")


        self .folder_path =None 
        self .file_path =None 
        self .data =None 


        self .create_menu_bar ()
        self .create_toolbar1_options ()
        self .create_toolbar2_options ()

        self .create_plots_tab ()
        self .create_pairwise_plots_tab ()
        self .create_box_plots_tab ()
        self .create_pca_corr_tab ()
        self .create_time_series_tab ()




    def create_menu_bar (self ):
        menu_bar =QMenuBar (self )

        file_menu =menu_bar .addMenu ('File')
        view_menu =menu_bar .addMenu ('View')
        help_menu =menu_bar .addMenu ('Help')

        select_folder_action =QAction ('Select Folder',self )
        select_folder_action .triggered .connect (self .select_folder )

        select_file_action =QAction ('Select File',self )
        select_file_action .triggered .connect (self .select_file )

        exit_action =QAction ('Exit',self )
        exit_action .triggered .connect (self .close )

        file_menu .addAction (select_folder_action )
        file_menu .addAction (select_file_action )
        file_menu .addAction (exit_action )

        about_action =QAction ('About',self )
        about_action .triggered .connect (self .about )
        help_menu .addAction (about_action )
        self .setMenuBar (menu_bar )

    def create_toolbar1_options (self ):

        toolbar1_layout =QVBoxLayout (self .toolbar1 )

        select_folder_button =QPushButton ('Select Folder',self )
        select_file_button =QPushButton ('Select File',self )


        self .toolbar1 .layout ().addWidget (select_folder_button )
        self .toolbar1 .layout ().addWidget (select_file_button )
        select_folder_button .clicked .connect (self .select_folder )
        select_file_button .clicked .connect (self .select_file )


        standardisation_used_box =QGroupBox ("Choose which standarisation are you using")
        standardisation_used_layout =QVBoxLayout (standardisation_used_box )



        density_plot_box =QGroupBox ("Choose method for plotting the density plot")
        density_plot_layout =QVBoxLayout (density_plot_box )



        third_plot_box =QGroupBox ("Choose what to plot to show in the 3rd (2_1) graph and time series")
        third_plot_layout =QVBoxLayout (third_plot_box )


        density_plot_option_box =QGroupBox ("Choose what to plot to show in the Density Graph")
        density_plot_option_layout =QVBoxLayout (density_plot_option_box )


        density_component_box =QGroupBox ("Choose number of components for GMM fitting")
        density_component_layout =QVBoxLayout (density_component_box )



        gaussian_component_box =QGroupBox ("Gaussian Fitting")
        gaussian_component_layout =QVBoxLayout (gaussian_component_box )


        self .standardisation_used_combo_box =QComboBox ()
        self .standardisation_used_combo_box .addItems (['ΔI','(ΔI*I0)**0.1','(ΔI*I0)**0.5','ΔI/I0'])
        self .standardisation_used_combo_box .setCurrentIndex (0 )
        standardisation_used_layout .addWidget (self .standardisation_used_combo_box )


        self .gmm_button =QRadioButton ("GMM")
        self .hist2d_button =QRadioButton ("Hist2D")
        density_plot_button_group =QButtonGroup (self )
        density_plot_button_group .addButton (self .gmm_button )
        density_plot_button_group .addButton (self .hist2d_button )
        self .gmm_button .setChecked (True )



        self .dI_plot_button =QRadioButton ("ΔI")
        self .dt_plot_button =QRadioButton ("Δt")
        third_plot_button_group =QButtonGroup (self )
        third_plot_button_group .addButton (self .dI_plot_button )
        third_plot_button_group .addButton (self .dt_plot_button )
        self .dI_plot_button .setChecked (True )



        self .density_dI_plot_button =QRadioButton ("ΔI vs Δt")
        self .density_area_plot_button =QRadioButton ("Area vs Δt")
        density_plot_option_group =QButtonGroup (self )
        density_plot_option_group .addButton (self .density_dI_plot_button )
        density_plot_option_group .addButton (self .density_area_plot_button )
        self .density_area_plot_button .setChecked (True )


        self .num_components_spin_box =QSpinBox ()
        self .num_components_spin_box .setRange (1 ,10 )
        self .num_components_spin_box .setValue (4 )



        self .density_show_checkbox =QCheckBox ("Calculate Density",self )
        self .density_show_checkbox .setChecked (True )


        self .gaussian_show_checkbox =QCheckBox ("Show Gaussian Fitting",self )
        self .gaussian_show_checkbox .setChecked (False )


        self .gaussian_fitting_label =QLabel ("How to determine number of components?")



        self .gaussian_fitting_combo_box =QComboBox ()
        self .gaussian_fitting_combo_box .addItems (['Automatic','Given by User (Choose below)'])
        self .gaussian_fitting_combo_box .setCurrentIndex (0 )


        self .gaussian_components_label =QLabel ("If not automatic, Choose number of components")


        self .gaussian_components_spin_box =QSpinBox ()
        self .gaussian_components_spin_box .setRange (1 ,10 )
        self .gaussian_components_spin_box .setValue (3 )


        density_plot_layout .addWidget (self .density_show_checkbox )
        density_plot_layout .addWidget (self .gmm_button )
        density_plot_layout .addWidget (self .hist2d_button )



        third_plot_layout .addWidget (self .dI_plot_button )
        third_plot_layout .addWidget (self .dt_plot_button )




        density_plot_option_layout .addWidget (self .density_dI_plot_button )
        density_plot_option_layout .addWidget (self .density_area_plot_button )


        density_component_layout .addWidget (self .num_components_spin_box )




        gaussian_component_layout .addWidget (self .gaussian_show_checkbox )


        gaussian_component_layout .addWidget (self .gaussian_fitting_label )


        gaussian_component_layout .addWidget (self .gaussian_fitting_combo_box )


        gaussian_component_layout .addWidget (self .gaussian_components_label )


        gaussian_component_layout .addWidget (self .gaussian_components_spin_box )

        current_type_box_layout =QVBoxLayout ()
        dwell_time_box_layout =QVBoxLayout ()



        current_type_box =QGroupBox ("Choose type of drop in current")
        dwell_time_box =QGroupBox ("Choose type of dwell time")



        current_type_box .setLayout (current_type_box_layout )
        dwell_time_box .setLayout (dwell_time_box_layout )



        self .delta_I_button =QRadioButton ("ΔI")
        self .delta_I_fwhm_button =QRadioButton ("ΔI(fwhm)")
        current_type_button_group =QButtonGroup (self )
        current_type_button_group .addButton (self .delta_I_button )
        current_type_button_group .addButton (self .delta_I_fwhm_button )
        self .delta_I_button .setChecked (True )


        self .delta_t_button =QRadioButton ("Δt")
        self .delta_t_fwhm_button =QRadioButton ("Δt(fwhm)")
        dwell_time_button_group =QButtonGroup (self )
        dwell_time_button_group .addButton (self .delta_t_button )
        dwell_time_button_group .addButton (self .delta_t_fwhm_button )
        self .delta_t_button .setChecked (True )


        self .time_diff_spin_box =QSpinBox ()
        self .time_diff_spin_box .setRange (0 ,10000 )
        self .time_diff_spin_box .setValue (7 )


        current_type_box_layout .addWidget (self .delta_I_button )
        current_type_box_layout .addWidget (self .delta_I_fwhm_button )
        dwell_time_box_layout .addWidget (self .delta_t_button )
        dwell_time_box_layout .addWidget (self .delta_t_fwhm_button )

        toolbar1_layout .addWidget (standardisation_used_box )


        toolbar1_layout .addWidget (current_type_box )
        toolbar1_layout .addWidget (dwell_time_box )


        toolbar1_layout .addWidget (density_plot_box )
        toolbar1_layout .addWidget (third_plot_box )
        toolbar1_layout .addWidget (density_plot_option_box )
        toolbar1_layout .addWidget (density_component_box )
        toolbar1_layout .addWidget (gaussian_component_box )
        self .standardisation_used_combo_box .currentIndexChanged .connect (self .create_plots )
        self .standardisation_used_combo_box .currentIndexChanged .connect (self .update_time_series )
        self .delta_I_button .toggled .connect (self .create_plots )
        self .delta_I_fwhm_button .toggled .connect (self .create_plots )
        self .delta_t_button .toggled .connect (self .create_plots )
        self .delta_t_fwhm_button .toggled .connect (self .create_plots )
        self .dI_plot_button .toggled .connect (self .create_plots )
        self .dt_plot_button .toggled .connect (self .create_plots )
        self .dI_plot_button .toggled .connect (self .update_time_series )
        self .dt_plot_button .toggled .connect (self .update_time_series )
        self .delta_t_button .toggled .connect (self .create_density_plot )
        self .delta_t_fwhm_button .toggled .connect (self .create_density_plot )
        self .gmm_button .toggled .connect (self .create_density_plot )
        self .hist2d_button .toggled .connect (self .create_density_plot )
        self .delta_I_button .toggled .connect (self .update_time_series )
        self .delta_I_fwhm_button .toggled .connect (self .update_time_series )

        self .num_components_spin_box .valueChanged .connect (self .create_density_plot )
        self .density_area_plot_button .toggled .connect (self .create_density_plot )
        self .density_dI_plot_button .toggled .connect (self .create_density_plot )

        self .gaussian_show_checkbox .toggled .connect (self .create_plots )
        self .gaussian_fitting_combo_box .currentIndexChanged .connect (self .create_plots )
        self .gaussian_components_spin_box .valueChanged .connect (self .create_plots )

        self .gaussian_show_checkbox .toggled .connect (self .update_time_series )
        self .gaussian_fitting_combo_box .currentIndexChanged .connect (self .update_time_series )
        self .gaussian_components_spin_box .valueChanged .connect (self .update_time_series )



    def select_folder (self ):
        folder =QFileDialog .getExistingDirectory (self ,"Select Folder")

        if folder :
            self .folder_path =folder 


            data_list =[]
            for dirpath ,dirnames ,filenames in os .walk (folder ):
                for filename in filenames :
                    if filename .endswith ('.dataset.npz'):
                        file_path =os .path .join (dirpath ,filename )
                        file_data =self .read_file (file_path )
                        if file_data is not None :
                            data_list .append (file_data )

            if data_list :
                self .data =np .concatenate (data_list )
                self .create_plots ()
                if self .density_show_checkbox .isChecked ():
                    self .create_density_plot ()
                self .update_box_plots_and_statistics ()
                self .update_pca_and_corr_matrix ()
                self .update_time_series ()
                self .populate_pairwise_plots ()

    def select_file (self ):
        file ,_ =QFileDialog .getOpenFileName (self ,"Select File","","Numpy files (*.dataset.npz)")

        if file :
            self .file_path =file 
            self .data =self .read_file (file )
            self .create_plots ()
            if self .density_show_checkbox .isChecked ():
                self .create_density_plot ()
            self .update_box_plots_and_statistics ()
            self .update_pca_and_corr_matrix ()
            self .update_time_series ()
            self .populate_pairwise_plots ()

    def read_file (self ,file ):
        try :
            with np .load (file )as data :
                X =data ['X']





                X ,nan_count =remove_nan_arrays (X )
                if nan_count >0 :
                    print (f"Total Number of nan_counts: {nan_count}")
                return X 
        except Exception as e :
            QMessageBox .warning (self ,"Error",str (e ))
            return None 


    def about (self ):
        QMessageBox .about (self ,"About SD Nanopore Data Visualisation Tool",
        "Version: 0.1\n\nThis application is a tool for visualise .npz data files generated from Nanosense.\n\n"
        "Author: Shankar Dutt\nEmail: shankar.dutt@anu.edu.au")

    def create_toolbar2_options (self ):
        toolbar2_layout =QVBoxLayout (self .toolbar2 )

        colormap_box_layout =QVBoxLayout ()
        normalization_box_layout =QVBoxLayout ()
        plot_type_normalised_density_box_layout =QVBoxLayout ()
        contrast_box_layout =QVBoxLayout ()
        power_box_layout =QVBoxLayout ()
        bin_box_layout =QVBoxLayout ()
        time_diff_box_layout =QVBoxLayout ()



        colormap_box =QGroupBox ("Choose colormap for the plots")
        normalization_box =QGroupBox ("Choose normalization method for the plots")
        plot_type_normalised_density_box =QGroupBox ("Choose plot type for 2x1 plot")
        contrast_box =QGroupBox ("Adjust contrast of the density plot")
        power_box =QGroupBox ("Value of Power*10, i.e. 2 actually means 0.2")
        bin_box =QGroupBox ("Number of Bins")
        time_diff_box =QGroupBox ("Choose time difference between files")


        colormap_box .setLayout (colormap_box_layout )
        normalization_box .setLayout (normalization_box_layout )
        plot_type_normalised_density_box .setLayout (plot_type_normalised_density_box_layout )
        contrast_box .setLayout (contrast_box_layout )
        power_box .setLayout (power_box_layout )
        bin_box .setLayout (bin_box_layout )
        time_diff_box .setLayout (time_diff_box_layout )


        self .colormap_combo_box =QComboBox ()
        self .colormap_combo_box .addItems (cmaps )
        self .colormap_combo_box .setCurrentIndex (7 )


        self .linear_button =QRadioButton ("Linear")
        self .power_button =QRadioButton ("Power")
        self .linear_button .setChecked (True )



        self .counts_button =QRadioButton ("Counts")
        self .normalised_density_button =QRadioButton ("Normalised Density")
        self .counts_button .setChecked (True )


        self .power_spin_box =QSpinBox ()
        self .power_spin_box .setRange (0 ,100 )
        self .power_spin_box .setValue (2 )




        colormap_box_layout .addWidget (self .colormap_combo_box )
        normalization_box_layout .addWidget (self .linear_button )
        normalization_box_layout .addWidget (self .power_button )
        plot_type_normalised_density_box_layout .addWidget (self .counts_button )
        plot_type_normalised_density_box_layout .addWidget (self .normalised_density_button )



        power_box_layout .addWidget (self .power_spin_box )


        self .min_contrast_label =QLabel ("Minimum Contrast")
        self .min_contrast_slider =QSlider (Qt .Orientation .Horizontal )
        self .min_contrast_slider .setRange (0 ,1000 )
        self .min_contrast_slider .setValue (0 )


        self .max_contrast_label =QLabel ("Maximum Contrast")
        self .max_contrast_slider =QSlider (Qt .Orientation .Horizontal )
        self .max_contrast_slider .setRange (1 ,2000 )
        self .max_contrast_slider .setValue (1000 )

        self .min_contrast_slider .valueChanged .connect (self .update_contrast )
        self .max_contrast_slider .valueChanged .connect (self .update_contrast )


        self .min_contrast_spin_box =QSpinBox ()
        self .max_contrast_spin_box =QSpinBox ()
        self .min_range_label =QLabel ("Minimum Range of the sliders")
        self .min_contrast_spin_box .setRange (0 ,1000000 )
        self .min_contrast_spin_box .setValue (0 )
        self .max_range_label =QLabel ("Maximum Range of the sliders")
        self .max_contrast_spin_box .setRange (1 ,1000000 )
        self .max_contrast_spin_box .setValue (1 )


        self .min_contrast_spin_box .valueChanged .connect (lambda value :self .min_contrast_slider .setMinimum (value *1000 ))
        self .max_contrast_spin_box .valueChanged .connect (lambda value :self .min_contrast_slider .setMaximum (value *1000 ))
        self .min_contrast_spin_box .valueChanged .connect (lambda value :self .max_contrast_slider .setMinimum (value *1000 ))
        self .max_contrast_spin_box .valueChanged .connect (lambda value :self .max_contrast_slider .setMaximum (value *1000 ))


        self .big_plot_bins =QSpinBox ()
        self .big_plot_bins .setRange (10 ,1000 )
        self .big_plot_bins .setValue (100 )


        self .small_plot_bins =QSpinBox ()
        self .small_plot_bins .setRange (10 ,1000 )
        self .small_plot_bins .setValue (100 )


        self .markersize =QSpinBox ()
        self .markersize .setRange (1 ,1000 )
        self .markersize .setValue (10 )



        self .big_bin_label =QLabel ("Number of bins for plot 2x1 in Plots Tab")
        self .small_bin_label =QLabel ("Number of bins for small histograms in Plots Tab")
        self .markersize_label =QLabel ("Size of the marker for plots 1x1 and 2x2 in Plots Tab")


        bin_box_layout .addWidget (self .big_bin_label )
        bin_box_layout .addWidget (self .big_plot_bins )
        bin_box_layout .addWidget (self .small_bin_label )
        bin_box_layout .addWidget (self .small_plot_bins )
        bin_box_layout .addWidget (self .markersize_label )
        bin_box_layout .addWidget (self .markersize )


        contrast_box_layout .addWidget (self .min_contrast_label )
        contrast_box_layout .addWidget (self .min_contrast_slider )
        contrast_box_layout .addWidget (self .max_contrast_label )
        contrast_box_layout .addWidget (self .max_contrast_slider )
        contrast_box_layout .addWidget (self .min_range_label )
        contrast_box_layout .addWidget (self .min_contrast_spin_box )
        contrast_box_layout .addWidget (self .max_range_label )
        contrast_box_layout .addWidget (self .max_contrast_spin_box )

        time_diff_box_layout .addWidget (self .time_diff_spin_box )


        toolbar2_layout .addWidget (plot_type_normalised_density_box )
        toolbar2_layout .addWidget (colormap_box )
        toolbar2_layout .addWidget (normalization_box )
        toolbar2_layout .addWidget (power_box )
        toolbar2_layout .addWidget (contrast_box )
        toolbar2_layout .addWidget (bin_box )
        toolbar2_layout .addWidget (time_diff_box )


        self .counts_button .toggled .connect (self .create_plots )
        self .normalised_density_button .toggled .connect (self .create_plots )
        self .linear_button .toggled .connect (self .update_density_plot )
        self .power_button .toggled .connect (self .update_density_plot )
        self .power_spin_box .valueChanged .connect (self .update_density_plot )
        self .colormap_combo_box .currentIndexChanged .connect (self .update_density_plot )
        self .big_plot_bins .valueChanged .connect (self .create_plots )
        self .small_plot_bins .valueChanged .connect (self .create_plots )
        self .markersize .valueChanged .connect (self .create_plots )
        self .small_plot_bins .valueChanged .connect (self .create_density_plot )
        self .time_diff_spin_box .valueChanged .connect (self .update_time_series )


    def create_plots_tab (self ):
        plots_layout =QGridLayout (self .plots_tab )


        self .figure_11 =Figure (constrained_layout =True )
        self .figure_12 =Figure (constrained_layout =True )
        self .figure_21 =Figure (constrained_layout =True )
        self .figure_22 =Figure (constrained_layout =True )

        self .canvas_11 =FigureCanvas (self .figure_11 )
        self .canvas_12 =FigureCanvas (self .figure_12 )
        self .canvas_21 =FigureCanvas (self .figure_21 )
        self .canvas_22 =FigureCanvas (self .figure_22 )


        gs_11 =gridspec .GridSpec (4 ,4 ,figure =self .figure_11 )
        self .plot_11 =self .figure_11 .add_subplot (gs_11 [1 :,:-1 ])
        self .hist_11_top =self .figure_11 .add_subplot (gs_11 [0 ,:-1 ],sharex =self .plot_11 )
        self .hist_11_right =self .figure_11 .add_subplot (gs_11 [1 :,-1 ],sharey =self .plot_11 )
        self .hist_11_top .tick_params (axis ='x',which ='both',bottom =False ,labelbottom =False )
        self .plot_11 .tick_params (axis ='x',which ='both',bottom =True ,labelbottom =True )

        self .hist_11_right .tick_params (axis ='y',which ='both',left =False ,labelleft =False )
        self .plot_11 .tick_params (axis ='y',which ='both',left =True ,labelleft =True )
        gs_11 .update (wspace =0.02 ,hspace =0.02 )

        gs_12 =gridspec .GridSpec (4 ,3 ,width_ratios =[4 ,1.3 ,0.15 ],figure =self .figure_12 )
        self .plot_12 =self .figure_12 .add_subplot (gs_12 [1 :,0 ])
        self .hist_12_top =self .figure_12 .add_subplot (gs_12 [0 ,0 ],sharex =self .plot_12 )
        self .hist_12_right =self .figure_12 .add_subplot (gs_12 [1 :,1 ],sharey =self .plot_12 )
        self .colorbar_12_ax =self .figure_12 .add_subplot (gs_12 [1 :,2 ])
        self .hist_12_top .tick_params (axis ='x',which ='both',bottom =False ,labelbottom =False )
        self .plot_12 .tick_params (axis ='x',which ='both',bottom =True ,labelbottom =True )
        self .hist_12_right .tick_params (axis ='y',which ='both',left =False ,labelleft =False )
        self .plot_12 .tick_params (axis ='y',which ='both',left =True ,labelleft =True )
        self .plot_12 .grid (False )
        gs_12 .update (wspace =0.02 ,hspace =0.02 )


        self .plot_21 =self .figure_21 .add_subplot (111 )


        gs_22 =gridspec .GridSpec (4 ,4 ,figure =self .figure_22 )
        self .plot_22 =self .figure_22 .add_subplot (gs_22 [1 :,:-1 ])
        self .hist_22_top =self .figure_22 .add_subplot (gs_22 [0 ,:-1 ],sharex =self .plot_22 )
        self .hist_22_right =self .figure_22 .add_subplot (gs_22 [1 :,-1 ],sharey =self .plot_22 )
        self .hist_22_top .tick_params (axis ='x',which ='both',bottom =False ,labelbottom =False )
        self .plot_22 .tick_params (axis ='x',which ='both',bottom =True ,labelbottom =True )

        self .hist_22_right .tick_params (axis ='y',which ='both',left =False ,labelleft =False )
        self .plot_22 .tick_params (axis ='y',which ='both',left =True ,labelleft =True )
        gs_22 .update (wspace =0.02 ,hspace =0.02 )




        toolbar_11 =NavigationToolbar (self .canvas_11 ,self )
        toolbar_12 =NavigationToolbar (self .canvas_12 ,self )
        toolbar_21 =NavigationToolbar (self .canvas_21 ,self )
        toolbar_22 =NavigationToolbar (self .canvas_22 ,self )


        plots_layout .addWidget (self .canvas_11 ,0 ,0 )
        plots_layout .addWidget (toolbar_11 ,1 ,0 )
        plots_layout .addWidget (self .canvas_12 ,0 ,1 )
        plots_layout .addWidget (toolbar_12 ,1 ,1 )
        plots_layout .addWidget (self .canvas_21 ,2 ,0 )
        plots_layout .addWidget (toolbar_21 ,3 ,0 )
        plots_layout .addWidget (self .canvas_22 ,2 ,1 )
        plots_layout .addWidget (toolbar_22 ,3 ,1 )


    def create_plots (self ):
        if self .data is None :
            return 

        X =self .data 

        if self .delta_I_button .isChecked ():
            delta_I =X [:,0 ]*1e3 
        else :
            delta_I =X [:,2 ]*1e3 
        if self .delta_t_button .isChecked ():
            delta_t =X [:,4 ]*1e3 
        else :
            delta_t =X [:,1 ]*1e3 

        area =X [:,3 ]

        markersize_defined =self .markersize .value ()
        markersize_defined =markersize_defined /10 


        if self .standardisation_used_combo_box .currentText ()=='ΔI':
            standard_label ='ΔI (pA)'
        elif self .standardisation_used_combo_box .currentText ()=='(ΔI*I0)**0.1':
            standard_label ='$(ΔI \u00D7 I_0)^{0.1}$'
        elif self .standardisation_used_combo_box .currentText ()=='(ΔI*I0)**0.5':
            standard_label ='$(ΔI \u00D7 I_0)^{0.5}$'
        elif self .standardisation_used_combo_box .currentText ()=='ΔI/I0':
            standard_label ='$ΔI/I_0$'
        else :
            standard_label ='ΔI (pA)'




        def adjust_limits (data ):

            return data .min ()-(data .max ()-data .min ())/20 ,data .max ()+(data .max ()-data .min ())/20 


        self .plot_11 .clear ()
        self .hist_11_top .clear ()
        self .hist_11_right .clear ()
        sns .scatterplot (x =np .log (delta_t ),y =delta_I ,ax =self .plot_11 ,legend =False ,edgecolor =None ,s =markersize_defined ,alpha =0.5 )
        self .plot_11 .set_xlabel ('log(Δt (ms))',fontsize =14 )
        self .plot_11 .set_ylabel (standard_label ,fontsize =14 )
        self .plot_11 .set_xlim (*adjust_limits (np .log (delta_t )))
        self .plot_11 .set_ylim (*adjust_limits (delta_I ))
        if self .gaussian_show_checkbox .isChecked ():
            x =np .log (delta_t )

            x_values =np .linspace (x .min (),x .max (),1000 )
            kde_values =sns .kdeplot (x ,bw_adjust =0.5 ,gridsize =1000 ).get_lines ()[0 ].get_ydata ()
            plt .close ()

            if self .gaussian_fitting_combo_box .currentText ()=='Automatic':

                kde_peaks ,_ =find_peaks (kde_values ,distance =70 ,height =0.01 )

            else :
                kde_peaks =np .zeros (self .gaussian_components_spin_box .value ())


            gmm =GaussianMixture (n_components =len (kde_peaks ),random_state =0 ).fit (x .reshape (-1 ,1 ))
            gmm_scores =gmm .score_samples (x_values .reshape (-1 ,1 ))


            gmm_components =[weights *norm .pdf (x_values ,loc =mean ,scale =np .sqrt (covariance ))
            for weights ,mean ,covariance in zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ])]
            sns .histplot (x ,bins =self .small_plot_bins .value (),kde =False ,color ='#A9A9A9',stat ="density",label ='Histogram',ax =self .hist_11_top ,linewidth =0 )
            for i ,component in enumerate (gmm_components ):
                self .hist_11_top .plot (x_values ,component ,'--',label =f'Component {i+1}')
            self .hist_11_top .plot (x_values ,np .sum (gmm_components ,axis =0 ),'b-',label ='Combined GMM Fit')
            y_max =self .hist_11_top .get_ylim ()[1 ]
            for mean in gmm .means_ :

                self .hist_11_top .text (mean [0 ],y_max *0.95 ,f'{mean[0]:.2f}')


            x =delta_I 
            x_values =np .linspace (x .min (),x .max (),1000 )
            kde_values =sns .kdeplot (y =x ,bw_adjust =0.5 ,gridsize =1000 ).get_lines ()[0 ].get_xdata ()
            plt .close ()

            if self .gaussian_fitting_combo_box .currentText ()=='Automatic':

                kde_peaks ,_ =find_peaks (kde_values ,distance =200 )
            else :
                kde_peaks =np .zeros (self .gaussian_components_spin_box .value ())


            gmm =GaussianMixture (n_components =len (kde_peaks ),random_state =0 ).fit (x .reshape (-1 ,1 ))
            gmm_scores =gmm .score_samples (x_values .reshape (-1 ,1 ))


            gmm_components =[weights *norm .pdf (x_values ,loc =mean ,scale =np .sqrt (covariance ))
            for weights ,mean ,covariance in zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ])]

            sns .histplot (y =x ,bins =self .small_plot_bins .value (),kde =False ,color ='#A9A9A9',stat ="density",ax =self .hist_11_right ,linewidth =0 )
            for i ,component in enumerate (gmm_components ):
                self .hist_11_right .plot (component ,x_values ,'--',label =f'Component {i+1}')
            self .hist_11_right .plot (np .sum (gmm_components ,axis =0 ),x_values ,'b-',label ='Combined GMM Fit',linewidth =2 )

            x_max =self .hist_11_right .get_xlim ()[1 ]
            for mean in gmm .means_ :
                self .hist_11_right .text (x_max *0.95 ,mean [0 ],f'{mean[0]:.2f}')


        else :
            self .hist_11_top .hist (np .log (delta_t ),edgecolor =None ,bins =self .small_plot_bins .value (),linewidth =0 ,density =True )

            self .hist_11_right .hist (delta_I ,edgecolor =None ,bins =self .small_plot_bins .value (),linewidth =0 ,orientation ='horizontal',density =True )
            sns .kdeplot (np .log (delta_t ),ax =self .hist_11_top )


            ax_temp =sns .kdeplot (delta_I )


            lines =ax_temp .get_lines ()
            data_x =lines [0 ].get_xdata ()
            data_y =lines [0 ].get_ydata ()


            plt .close (ax_temp .figure )


            self .hist_11_right .plot (data_y ,data_x )



        self .plot_22 .clear ()
        self .hist_22_top .clear ()
        self .hist_22_right .clear ()
        sns .scatterplot (x =np .log (delta_t ),y =area ,ax =self .plot_22 ,legend =False ,edgecolor =None ,s =markersize_defined ,alpha =0.5 )
        self .plot_22 .set_xlabel ('log(Δt (ms))',fontsize =14 )
        self .plot_22 .set_ylabel ('Area',fontsize =14 )
        self .plot_22 .set_xlim (*adjust_limits (np .log (delta_t )))
        self .plot_22 .set_ylim (*adjust_limits (area ))
        self .hist_22_top .hist (np .log (delta_t ),edgecolor =None ,bins =self .small_plot_bins .value (),linewidth =0 ,density =True )
        self .hist_22_right .hist (area ,edgecolor =None ,bins =self .small_plot_bins .value (),linewidth =0 ,orientation ='horizontal',density =True )
        sns .kdeplot (np .log (delta_t ),ax =self .hist_22_top )
        ax_temp =sns .kdeplot (area )


        lines =ax_temp .get_lines ()
        data_x =lines [0 ].get_xdata ()
        data_y =lines [0 ].get_ydata ()


        plt .close (ax_temp .figure )


        self .hist_22_right .plot (data_y ,data_x )

        if self .counts_button .isChecked ():
            if self .dt_plot_button .isChecked ():

                self .plot_21 .clear ()
                if self .gaussian_show_checkbox .isChecked ():
                    x =np .log (delta_t )

                    x_values =np .linspace (x .min (),x .max (),1000 )
                    kde_values =sns .kdeplot (x ,bw_adjust =0.5 ,gridsize =1000 ).get_lines ()[0 ].get_ydata ()
                    plt .close ()

                    if self .gaussian_fitting_combo_box .currentText ()=='Automatic':

                        kde_peaks ,_ =find_peaks (kde_values ,distance =70 ,height =0.01 )

                    else :
                        kde_peaks =np .zeros (self .gaussian_components_spin_box .value ())


                    gmm =GaussianMixture (n_components =len (kde_peaks ),random_state =0 ).fit (x .reshape (-1 ,1 ))
                    gmm_scores =gmm .score_samples (x_values .reshape (-1 ,1 ))


                    gmm_components =[weights *norm .pdf (x_values ,loc =mean ,scale =np .sqrt (covariance ))
                    for weights ,mean ,covariance in zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ])]
                    sns .histplot (x ,bins =self .big_plot_bins .value (),kde =False ,color ='#A9A9A9',stat ="density",label ='Histogram',ax =self .plot_21 ,linewidth =0 )
                    for i ,component in enumerate (gmm_components ):
                        self .plot_21 .plot (x_values ,component ,'--',label =f'Component {i+1}')
                    self .plot_21 .plot (x_values ,np .sum (gmm_components ,axis =0 ),'b-',label ='Combined GMM Fit',linewidth =2 )
                    y_max =self .plot_21 .get_ylim ()[1 ]
                    for mean in gmm .means_ :

                        self .plot_21 .text (mean [0 ],y_max *0.95 ,f'{mean[0]:.2f}')

                    self .plot_21 .set_xlabel ('log(Δt (ms))',fontsize =14 )
                    self .plot_21 .set_xlim (*adjust_limits (np .log (delta_t )))

                else :
                    sns .histplot (np .log (delta_t ),ax =self .plot_21 ,edgecolor =None ,bins =self .big_plot_bins .value (),linewidth =0 )
                    self .plot_21 .set_xlabel ('log(Δt (ms))',fontsize =14 )
                    self .plot_21 .set_xlim (*adjust_limits (np .log (delta_t )))
            else :
                self .plot_21 .clear ()
                if self .gaussian_show_checkbox .isChecked ():
                    x =delta_I 

                    x_values =np .linspace (x .min (),x .max (),1000 )
                    kde_values =sns .kdeplot (x ,bw_adjust =0.5 ,gridsize =1000 ).get_lines ()[0 ].get_ydata ()
                    plt .close ()

                    if self .gaussian_fitting_combo_box .currentText ()=='Automatic':

                        kde_peaks ,_ =find_peaks (kde_values ,distance =200 )

                    else :
                        kde_peaks =np .zeros (self .gaussian_components_spin_box .value ())


                    gmm =GaussianMixture (n_components =len (kde_peaks ),random_state =0 ).fit (x .reshape (-1 ,1 ))
                    gmm_scores =gmm .score_samples (x_values .reshape (-1 ,1 ))


                    gmm_components =[weights *norm .pdf (x_values ,loc =mean ,scale =np .sqrt (covariance ))
                    for weights ,mean ,covariance in zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ])]
                    sns .histplot (x ,bins =self .big_plot_bins .value (),kde =False ,color ='#A9A9A9',stat ="density",label ='Histogram',ax =self .plot_21 ,linewidth =0 )
                    for i ,component in enumerate (gmm_components ):
                        self .plot_21 .plot (x_values ,component ,'--',label =f'Component {i+1}')
                    self .plot_21 .plot (x_values ,np .sum (gmm_components ,axis =0 ),'b-',label ='Combined GMM Fit',linewidth =2 )
                    y_max =self .plot_21 .get_ylim ()[1 ]
                    for mean in gmm .means_ :

                        self .plot_21 .text (mean [0 ],y_max *0.95 ,f'{mean[0]:.2f}')

                    self .plot_21 .set_xlabel (standard_label ,fontsize =14 )
                    self .plot_21 .set_xlim (*adjust_limits (delta_I ))

                else :

                    sns .histplot (delta_I ,ax =self .plot_21 ,edgecolor =None ,bins =self .big_plot_bins .value (),linewidth =0 )
                    self .plot_21 .set_xlabel (standard_label ,fontsize =14 )
                    self .plot_21 .set_xlim (*adjust_limits (delta_I ))
        else :
            if self .dt_plot_button .isChecked ():

                self .plot_21 .clear ()
                if self .gaussian_show_checkbox .isChecked ():
                    x =np .log (delta_t )

                    x_values =np .linspace (x .min (),x .max (),1000 )
                    kde_values =sns .kdeplot (x ,bw_adjust =0.5 ,gridsize =1000 ).get_lines ()[0 ].get_ydata ()
                    plt .close ()

                    if self .gaussian_fitting_combo_box .currentText ()=='Automatic':

                        kde_peaks ,_ =find_peaks (kde_values ,distance =50 )

                    else :
                        kde_peaks =np .zeros (self .gaussian_components_spin_box .value ())


                    gmm =GaussianMixture (n_components =len (kde_peaks ),random_state =0 ).fit (x .reshape (-1 ,1 ))
                    gmm_scores =gmm .score_samples (x_values .reshape (-1 ,1 ))


                    gmm_components =[weights *norm .pdf (x_values ,loc =mean ,scale =np .sqrt (covariance ))
                    for weights ,mean ,covariance in zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ])]


                    components_tuples =list (zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ]))


                    sorted_components_tuples =sorted (components_tuples ,key =lambda x :x [1 ])


                    components_with_means =list (zip (gmm_components ,gmm .means_ ))


                    sorted_components_with_means =sorted (components_with_means ,key =lambda x :x [1 ])


                    sorted_gmm_components =[component for component ,mean in sorted_components_with_means ]


                    gmm_max =max (np .sum (gmm_components ,axis =0 ))



                    hist_counts ,bin_edges =np .histogram (np .log (delta_t ),bins =self .big_plot_bins .value ())

                    max_count =np .max (hist_counts )

                    normalized_counts =hist_counts /max_count 


                    self .plot_21 .bar (bin_edges [:-1 ],normalized_counts ,align ='edge',width =np .diff (bin_edges ),edgecolor =None ,linewidth =0 )


                    self .plot_21 .set_xlabel ('log(Δt (ms))',fontsize =14 )
                    self .plot_21 .set_ylabel ('Normalised Counts',fontsize =14 )
                    self .plot_21 .set_xlim (*adjust_limits (np .log (delta_t )))

                    for i ,component in enumerate (sorted_gmm_components ):
                        self .plot_21 .plot (x_values ,component /gmm_max ,'--',label =f'Component {i+1}')

                    normalized_gmm =np .sum (gmm_components ,axis =0 )/gmm_max 

                    self .plot_21 .plot (x_values ,normalized_gmm ,'b-',label ='Combined GMM Fit',linewidth =2 )
                    y_max =self .plot_21 .get_ylim ()[1 ]
                    for mean in gmm .means_ :

                        self .plot_21 .text (mean [0 ],y_max *0.95 ,f'{mean[0]:.2f}')

                    self .plot_21 .set_xlabel ('log(Δt (ms))',fontsize =14 )
                    self .plot_21 .set_xlim (*adjust_limits (np .log (delta_t )))

                else :

                    hist_counts ,bin_edges =np .histogram (np .log (delta_t ),bins =self .big_plot_bins .value ())

                    max_count =np .max (hist_counts )

                    normalized_counts =hist_counts /max_count 


                    self .plot_21 .bar (bin_edges [:-1 ],normalized_counts ,align ='edge',width =np .diff (bin_edges ),edgecolor =None ,linewidth =0 )






                    self .plot_21 .set_xlabel ('log(Δt (ms))',fontsize =14 )
                    self .plot_21 .set_ylabel ('Normalised Counts',fontsize =14 )
                    self .plot_21 .set_xlim (*adjust_limits (np .log (delta_t )))
            else :
                self .plot_21 .clear ()
                if self .gaussian_show_checkbox .isChecked ():
                    x =delta_I 

                    x_values =np .linspace (x .min (),x .max (),1000 )
                    kde_values =sns .kdeplot (x ,bw_adjust =0.5 ,gridsize =1000 ).get_lines ()[0 ].get_ydata ()
                    plt .close ()

                    if self .gaussian_fitting_combo_box .currentText ()=='Automatic':

                        kde_peaks ,_ =find_peaks (kde_values ,distance =200 )

                    else :
                        kde_peaks =np .zeros (self .gaussian_components_spin_box .value ())


                    gmm =GaussianMixture (n_components =len (kde_peaks ),random_state =0 ).fit (x .reshape (-1 ,1 ))
                    gmm_scores =gmm .score_samples (x_values .reshape (-1 ,1 ))


                    gmm_components =[weights *norm .pdf (x_values ,loc =mean ,scale =np .sqrt (covariance ))
                    for weights ,mean ,covariance in zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ])]


                    components_tuples =list (zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ]))


                    sorted_components_tuples =sorted (components_tuples ,key =lambda x :x [1 ])


                    components_with_means =list (zip (gmm_components ,gmm .means_ ))


                    sorted_components_with_means =sorted (components_with_means ,key =lambda x :x [1 ])


                    sorted_gmm_components =[component for component ,mean in sorted_components_with_means ]


                    gmm_max =max (np .sum (gmm_components ,axis =0 ))



                    hist_counts ,bin_edges =np .histogram (delta_I ,bins =self .big_plot_bins .value ())

                    max_count =np .max (hist_counts )

                    normalized_counts =hist_counts /max_count 

                    self .plot_21 .bar (bin_edges [:-1 ],normalized_counts ,align ='edge',width =np .diff (bin_edges ),edgecolor =None ,linewidth =0 )


                    self .plot_21 .set_xlabel (standard_label ,fontsize =14 )
                    self .plot_21 .set_xlim (*adjust_limits (delta_I ))
                    self .plot_21 .set_ylabel ('Normalised Counts',fontsize =14 )

                    for i ,component in enumerate (sorted_gmm_components ):
                        self .plot_21 .plot (x_values ,component /gmm_max ,'--',label =f'Component {i+1}')

                    normalized_gmm =np .sum (gmm_components ,axis =0 )/gmm_max 

                    self .plot_21 .plot (x_values ,normalized_gmm ,'b-',label ='Combined GMM Fit',linewidth =2 )
                    y_max =self .plot_21 .get_ylim ()[1 ]
                    for mean in gmm .means_ :

                        self .plot_21 .text (mean [0 ],y_max *0.95 ,f'{mean[0]:.2f}')

                    self .plot_21 .set_xlabel ('ΔI (pA)',fontsize =14 )
                    self .plot_21 .set_ylabel ('Normalised Counts',fontsize =14 )
                    self .plot_21 .set_xlim (*adjust_limits (delta_I ))

                else :

                    hist_counts ,bin_edges =np .histogram (delta_I ,bins =self .big_plot_bins .value ())

                    max_count =np .max (hist_counts )

                    normalized_counts =hist_counts /max_count 

                    self .plot_21 .bar (bin_edges [:-1 ],normalized_counts ,align ='edge',width =np .diff (bin_edges ),edgecolor =None ,linewidth =0 )


                    self .plot_21 .set_xlabel (standard_label ,fontsize =14 )
                    self .plot_21 .set_xlim (*adjust_limits (delta_I ))
                    self .plot_21 .set_ylabel ('Normalised Counts',fontsize =14 )


        self .plot_11 .figure .canvas .draw ()
        self .plot_22 .figure .canvas .draw ()
        self .plot_21 .figure .canvas .draw ()


    def create_density_plot (self ):
        try :
            self .plot_12 .clear ()


            self .colorbar_12_ax .clear ()

            X =self .data 


            if self .delta_t_button .isChecked ():
                x =X [:,4 ]*1e3 
            else :
                x =X [:,1 ]*1e3 

            x =np .log (x )

            if self .density_area_plot_button .isChecked ():
                y =X [:,3 ]
                density_y_label ="Area"
            else :
                if self .delta_I_button .isChecked ():
                    y =X [:,0 ]*1e3 
                else :
                    y =X [:,2 ]*1e3 
                density_y_label ="ΔI (pA)"

            if self .gmm_button .isChecked ():

                gmm =GaussianMixture (n_components =self .num_components_spin_box .value ()).fit (np .vstack ([x ,y ]).T )
                X ,Y =np .meshgrid (np .linspace (np .min (x ),np .max (x ),1000 ),np .linspace (np .min (y ),np .max (y ),1000 ))
                XX =np .array ([X .ravel (),Y .ravel ()]).T 
                Z =gmm .score_samples (XX )
                Z =Z .reshape (X .shape )
                Z =np .exp (Z )

                self .current_density_image =self .plot_12 .imshow (Z ,aspect ='auto',origin ='lower',
                extent =[x .min (),x .max (),y .min (),y .max ()],
                cmap =self .colormap_combo_box .currentText (),
                norm =self .get_norm (Z ))


                self .plot_12 .figure .colorbar (mappable =self .current_density_image ,ax =self .plot_12 ,cax =self .colorbar_12_ax )
                self .plot_12 .set_xlabel ('log(Δt (ms))',fontsize =14 )
                self .plot_12 .set_ylabel (density_y_label ,fontsize =14 )
                self .plot_12 .set_xlim ([np .min (x ),np .max (x )])
                self .plot_12 .set_ylim ([np .min (y ),np .max (y )])
                self .plot_12 .grid (False )


            else :

                H ,xedges ,yedges =np .histogram2d (x ,y ,bins =100 ,density =True )
                X ,Y =np .meshgrid (xedges [:-1 ],yedges [:-1 ])


                self .current_density_image =self .plot_12 .pcolormesh (X ,Y ,H .T ,
                cmap =self .colormap_combo_box .currentText (),
                norm =self .get_norm (H ))


                self .plot_12 .figure .colorbar (mappable =self .current_density_image ,ax =self .plot_12 ,cax =self .colorbar_12_ax )

                self .plot_12 .set_xlabel ('log(Δt (ms))',fontsize =14 )
                self .plot_12 .set_ylabel (density_y_label ,fontsize =14 )
                self .plot_12 .grid (False )

            self .hist_12_top .clear ()
            self .hist_12_right .clear ()
            self .hist_12_top .hist (x ,edgecolor =None ,bins =self .small_plot_bins .value (),linewidth =0 ,density =True )
            self .hist_12_right .hist (y ,edgecolor =None ,bins =self .small_plot_bins .value (),linewidth =0 ,orientation ='horizontal',density =True )
            sns .kdeplot (x ,ax =self .hist_12_top )
            ax_temp =sns .kdeplot (y )


            lines =ax_temp .get_lines ()
            data_x =lines [0 ].get_xdata ()
            data_y =lines [0 ].get_ydata ()


            plt .close (ax_temp .figure )


            self .hist_12_right .plot (data_y ,data_x )

            self .plot_12 .figure .canvas .draw ()
        except :
            QMessageBox .warning (self ,"Warning","There is nothing plotted!")
            pass 

    def update_contrast (self ):

        min_val =self .min_contrast_slider .value ()/1000.0 
        max_val =self .max_contrast_slider .value ()/1000.0 


        self .current_density_image .set_clim (min_val ,max_val )


        self .plot_12 .figure .canvas .draw ()


    def get_norm (self ,data_array =None ):
        try :
            if data_array is None :
                data_array =self .current_density_image .get_array ()


            if self .linear_button .isChecked ():
                return None 
            else :
                power =self .power_spin_box .value ()
                return PowerNorm (power /10 )
        except :
            QMessageBox .warning (self ,"Warning","There is nothing plotted!")
            pass 

    def update_density_plot (self ):

        try :
            norm =self .get_norm ()


            self .current_density_image .set_norm (norm )
            self .current_density_image .set_cmap (self .colormap_combo_box .currentText ())


            self .colorbar_12_ax .clear ()
            self .plot_12 .figure .colorbar (mappable =self .current_density_image ,ax =self .plot_12 ,cax =self .colorbar_12_ax )

            self .plot_12 .figure .canvas .draw ()
        except :
            QMessageBox .warning (self ,"Warning","There is nothing plotted!")
            pass 

    def create_pairwise_plots_tab (self ):
        """Set up the layout for pairwise plots"""

        pairwise_plots_layout =QVBoxLayout (self .pairwise_plots_tab )



        self .pairwise_plots_figure ,self .pairwise_plots_axes =plt .subplots (7 ,7 ,figsize =(14 ,14 ),dpi =80 )

        self .pairwise_plots_canvas =FigureCanvas (self .pairwise_plots_figure )


        pairwise_plots_toolbar =NavigationToolbar (self .pairwise_plots_canvas ,self )


        pairwise_plots_layout .addWidget (self .pairwise_plots_canvas )
        pairwise_plots_layout .addWidget (pairwise_plots_toolbar )


        self .pairwise_plots_canvas .mpl_connect ('button_press_event',self .on_pairwise_plot_clicked )


    def populate_pairwise_plots (self ):
        """Fill the pairwise plots with data"""
        if self .data is None :
            return 

        X =self .data 
        labels =['height','fwhm','heightatfwhm','area','basewidth','skew','kurt']


        axis_limits =[(min (X [:,i ])-0.1 *(max (X [:,i ])-min (X [:,i ])),
        max (X [:,i ])+0.1 *(max (X [:,i ])-min (X [:,i ])))for i in range (7 )]

        for i in range (7 ):
            for j in range (7 ):
                ax =self .pairwise_plots_axes [i ][j ]
                ax .clear ()

                x_data =X [:,j ]
                y_data =X [:,i ]


                x_ticks =np .linspace (axis_limits [j ][0 ],axis_limits [j ][1 ],6 )
                y_ticks =np .linspace (axis_limits [i ][0 ],axis_limits [i ][1 ],6 )

                ax .hlines (y_ticks ,xmin =axis_limits [j ][0 ],xmax =axis_limits [j ][1 ],
                colors ='grey',linestyles ='--',linewidth =0.5 )
                ax .vlines (x_ticks ,ymin =axis_limits [i ][0 ],ymax =axis_limits [i ][1 ],
                colors ='grey',linestyles ='--',linewidth =0.5 )

                if i ==j :
                    ax .hist (x_data ,bins =100 ,edgecolor ='k',color ='gray')
                    ax .set_xlim (axis_limits [j ])
                else :
                    ax .scatter (x_data ,y_data ,s =5 )
                    ax .set_xlim (axis_limits [j ])
                    ax .set_ylim (axis_limits [i ])

                if j ==0 :
                    ax .set_ylabel (labels [i ],fontsize =12 )
                else :
                    ax .set_yticks ([])

                if i ==6 :
                    ax .set_xlabel (labels [j ],fontsize =12 )
                else :
                    ax .set_xticks ([])

        self .pairwise_plots_figure .subplots_adjust (hspace =0.1 ,wspace =0.1 )
        self .pairwise_plots_figure .tight_layout ()
        self .pairwise_plots_canvas .draw ()




    def on_pairwise_plot_clicked (self ,event ):
        if event .inaxes :
            for i ,ax_row in enumerate (self .pairwise_plots_axes ):
                for j ,ax in enumerate (ax_row ):
                    if ax ==event .inaxes :
                        self .show_popup (i ,j )
                        return 

    def show_popup (self ,row ,col ):
        if self .data is None :
            return 

        labels =['height','fwhm','heightatfwhm','area','basewidth','skew','kurt']
        variable_a =labels [row ]
        variable_b =labels [col ]

        popup =QMainWindow (self )
        if row ==col :
            popup .setWindowTitle (f'Plot: {variable_a} Histogram')
        else :
            popup .setWindowTitle (f'Plot: {variable_a} vs {variable_b}')
        popup .setGeometry (200 ,200 ,600 ,400 )
        layout =QVBoxLayout ()


        fig ,ax =plt .subplots (figsize =(6 ,4 ))
        canvas =FigureCanvas (fig )
        layout .addWidget (canvas )


        toolbar =NavigationToolbar (canvas ,popup )
        layout .addWidget (toolbar )

        widget =QWidget ()
        widget .setLayout (layout )
        popup .setCentralWidget (widget )

        X =self .data 


        x_data =X [:,col ]
        y_data =X [:,row ]

        if row ==col :
            ax .hist (x_data ,bins =100 ,edgecolor ='k',color ='gray')
        else :
            ax .scatter (x_data ,y_data ,s =7 )

        ax .set_xlabel (variable_b )
        ax .set_ylabel (variable_a )

        canvas .draw ()
        popup .show ()


    def create_box_plots_tab (self ):

        box_plots_layout =QVBoxLayout (self .box_plots_tab )


        splitter =QSplitter (Qt .Orientation .Vertical )


        self .box_plots_figure =Figure (figsize =(10 ,7.5 ))
        self .box_plots_canvas =FigureCanvas (self .box_plots_figure )


        box_plot_container =QWidget ()
        box_plot_layout =QVBoxLayout (box_plot_container )


        box_plots_toolbar =NavigationToolbar (self .box_plots_canvas ,self )


        box_plot_layout .addWidget (self .box_plots_canvas )
        box_plot_layout .addWidget (box_plots_toolbar )


        splitter .addWidget (box_plot_container )


        self .statistics_table =QTableWidget ()


        splitter .addWidget (self .statistics_table )


        splitter .setSizes ([750 ,250 ])


        box_plots_layout .addWidget (splitter )

    def update_box_plots_and_statistics (self ):
        if self .data is None :
            return 


        X =self .data 


        variables =[X [:,i ]for i in range (7 )]
        labels =['ΔI','Δt(fwhm)','ΔI(fwhm)','Area','Δt','Skew','Kurt']


        self .box_plots_figure .clear ()
        axes =self .box_plots_figure .subplots (2 ,4 )

        for i ,(ax ,variable ,label )in enumerate (zip (axes .flatten (),variables ,labels )):
            ax .boxplot (variable )
            ax .set_title (label )


        axes [1 ,3 ].axis ('off')


        self .box_plots_canvas .draw ()


        statistics =[]
        for variable in variables :
            mean =np .mean (variable )
            median =np .median (variable )
            variance =np .var (variable )
            std_dev =np .std (variable )
            minimum =np .min (variable )
            maximum =np .max (variable )
            range_val =maximum -minimum 
            coef_var =(std_dev /mean )if mean !=0 else 0 
            q25 =np .percentile (variable ,25 )
            q75 =np .percentile (variable ,75 )

            statistics .append ([mean ,median ,variance ,std_dev ,minimum ,maximum ,range_val ,coef_var ,q25 ,q75 ])


        self .statistics_table .setRowCount (len (variables ))
        self .statistics_table .setColumnCount (10 )
        self .statistics_table .setHorizontalHeaderLabels (['Mean','Median','Variance','Std. Dev.','Min','Max','Range','Coef. Var.','Q25','Q75'])
        self .statistics_table .setVerticalHeaderLabels (labels )


        header =self .statistics_table .horizontalHeader ()
        header .setSectionResizeMode (QHeaderView .ResizeMode .Stretch )


        for i ,stats in enumerate (statistics ):
            for j ,stat in enumerate (stats ):
                self .statistics_table .setItem (i ,j ,QTableWidgetItem (str (round (stat ,8 ))))



    def create_pca_corr_tab (self ):

        pca_corr_layout =QVBoxLayout (self .pca_corr_tab )


        splitter =QSplitter (Qt .Orientation .Horizontal )


        pca_container =QWidget ()
        pca_layout =QVBoxLayout (pca_container )


        self .pca_figure =Figure ()
        self .pca_canvas =FigureCanvas (self .pca_figure )


        pca_toolbar =NavigationToolbar (self .pca_canvas ,self )


        pca_layout .addWidget (self .pca_canvas )
        pca_layout .addWidget (pca_toolbar )


        splitter .addWidget (pca_container )


        corr_matrix_container =QWidget ()
        corr_matrix_layout =QVBoxLayout (corr_matrix_container )


        self .corr_matrix_figure =Figure ()
        self .corr_matrix_canvas =FigureCanvas (self .corr_matrix_figure )


        corr_matrix_toolbar =NavigationToolbar (self .corr_matrix_canvas ,self )


        corr_matrix_layout .addWidget (self .corr_matrix_canvas )
        corr_matrix_layout .addWidget (corr_matrix_toolbar )


        splitter .addWidget (corr_matrix_container )


        pca_corr_layout .addWidget (splitter )




    def update_pca_and_corr_matrix (self ):
        if self .data is None :
            return 


        X =self .data 


        pca =PCA (n_components =2 )
        pca_result =pca .fit_transform (X )


        self .pca_figure .clear ()
        ax =self .pca_figure .add_subplot (111 )
        ax .scatter (pca_result [:,0 ],pca_result [:,1 ],s =7 ,alpha =0.6 )
        ax .set_xlabel ('PCA 1')
        ax .set_ylabel ('PCA 2')


        self .pca_canvas .draw ()


        corr_matrix =np .corrcoef (X .T )


        self .corr_matrix_figure .clear ()
        ax =self .corr_matrix_figure .add_subplot (111 )
        sns .heatmap (corr_matrix ,annot =True ,ax =ax ,cmap ='coolwarm',
        xticklabels =['ΔI','Δt(fwhm)','ΔI(fwhm)','Area','Δt','Skew','Kurt'],
        yticklabels =['ΔI','Δt(fwhm)','ΔI(fwhm)','Area','Δt','Skew','Kurt'])


        self .corr_matrix_canvas .draw ()

    def create_time_series_tab (self ):

        time_series_layout =QGridLayout (self .time_series_tab )


        self .stacked_kde_figure =Figure ()
        self .stacked_kde_canvas =FigureCanvas (self .stacked_kde_figure )


        stacked_kde_toolbar =NavigationToolbar (self .stacked_kde_canvas ,self )


        time_series_layout .addWidget (self .stacked_kde_canvas ,0 ,0 )
        time_series_layout .addWidget (stacked_kde_toolbar ,1 ,0 )


        self .line_plot_figure =Figure ()
        self .line_plot_canvas =FigureCanvas (self .line_plot_figure )


        line_plot_toolbar =NavigationToolbar (self .line_plot_canvas ,self )


        time_series_layout .addWidget (self .line_plot_canvas ,0 ,1 )
        time_series_layout .addWidget (line_plot_toolbar ,1 ,1 )

    def update_time_series (self ):
        try :

            if self .data is None or self .folder_path is None :
                return 

            if self .dt_plot_button .isChecked ():


                time_difference =self .time_diff_spin_box .value ()


                self .stacked_kde_figure .clear ()
                ax =self .stacked_kde_figure .add_subplot (111 )


                component_details =[]
                vertical_offset =0 
                gap_between_plots =0.1 
                text_height =0.1 
                gap_between_plot_and_text =0.05 

                file_names =sorted ([f for f in os .listdir (self .folder_path )if f .endswith ('.dataset.npz')])

                peak_values =[]
                times =[]

                '''# Get the colormap selected by the user
                colormap_name = self.colormap_combo_box.currentText()    
                cmap = plt.get_cmap(colormap_name)

                if len(file_names)>MAX_FILES:
                    MAX_FILES = len(file_names)
                colors_1 = [cmap(i/(MAX_FILES-1)) for i in range(MAX_FILES)]'''

                fixed_colors_20 =[
                '#000080',
                '#1E90FF',
                '#87CEFA',
                '#00FFFF',
                '#40E0D0',
                '#2E8B57',
                '#9ACD32',
                '#FFD700',
                '#FFA07A',
                '#FFA500',
                '#FF7F50',
                '#FA8072',
                '#FF69B4',
                '#FF00FF',
                '#FF1493'
                ]

                colors_1 =fixed_colors_20 


                overall_x_max =None 


                for file_name in file_names :
                    file_path =os .path .join (self .folder_path ,file_name )
                    data =np .load (file_path )
                    X =data ['X']
                    X ,nan_count =remove_nan_arrays (X )
                    if nan_count >0 :
                        print (f"Total Number of nan_counts: {nan_count}")
                    if self .delta_t_button .isChecked ():
                        delta_t =np .log (X [:,4 ]*1e3 )
                    else :
                        delta_t =np .log (X [:,1 ]*1e3 )

                    current_x_max =max (delta_t )

                    if overall_x_max is None or current_x_max >overall_x_max :
                        overall_x_max =current_x_max 


                for i ,file_name in enumerate (file_names ):
                    file_path =os .path .join (self .folder_path ,file_name )
                    data =np .load (file_path )

                    X =data ['X']
                    X ,nan_count =remove_nan_arrays (X )
                    if nan_count >0 :
                        print (f"Total Number of nan_counts: {nan_count}")


                    if self .delta_t_button .isChecked ():
                        delta_t =np .log (X [:,4 ]*1e3 )
                    else :
                        delta_t =np .log (X [:,1 ]*1e3 )


                    if len (delta_t )==0 :
                        QMessageBox .warning (self ,"Warning",f"{file_name} has empty Δt data.")
                        continue 


                    kde_func =gaussian_kde (delta_t )

                    x_range =max (delta_t )-min (delta_t )
                    x_kde =np .linspace (min (delta_t )-0.1 *x_range ,max (delta_t )+0.1 *x_range ,1000 )
                    y_kde =kde_func (x_kde )


                    y_kde_normalized =y_kde /max (y_kde )


                    peak_value =x_kde [np .argmax (y_kde )]
                    peak_values .append (peak_value )


                    current_time =(i +1 )*time_difference 
                    times .append (current_time )


                    label =f"{i * time_difference}-{current_time} min"


                    current_color =colors_1 [i ]

                    if self .gaussian_show_checkbox .isChecked ():

                        x_values =np .linspace (min (delta_t ),max (delta_t ),1000 )
                        kde_values =sns .kdeplot (delta_t ,bw_adjust =0.5 ,gridsize =1000 ).get_lines ()[0 ].get_ydata ()
                        plt .close ()


                        if self .gaussian_fitting_combo_box .currentText ()=='Automatic':
                            kde_peaks ,_ =find_peaks (kde_values ,distance =50 )
                        else :
                            kde_peaks =[0 ]*self .gaussian_components_spin_box .value ()


                        gmm =GaussianMixture (n_components =len (kde_peaks ),random_state =0 ).fit (delta_t .reshape (-1 ,1 ))
                        gmm_components =[weights *scipy .stats .norm .pdf (x_values ,loc =mean ,scale =np .sqrt (covariance ))
                        for weights ,mean ,covariance in zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ])]



                        components_tuples =list (zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ]))


                        sorted_components_tuples =sorted (components_tuples ,key =lambda x :x [1 ])


                        print ("Gaussian Components Details:")
                        for weight ,mean ,covariance in sorted_components_tuples :
                            component ={
                            "Weight":weight ,
                            "Mean":mean [0 ],
                            "Std Dev":np .sqrt (covariance )[0 ]
                            }
                            print (component )



                        components_with_means =list (zip (gmm_components ,gmm .means_ ))


                        sorted_components_with_means =sorted (components_with_means ,key =lambda x :x [1 ])


                        sorted_gmm_components =[component for component ,mean in sorted_components_with_means ]


                        gmm_max =max (np .sum (gmm_components ,axis =0 ))


                        for i ,component in enumerate (sorted_gmm_components ):
                            normalized_component =component /gmm_max 
                            ax .plot (x_values ,normalized_component +vertical_offset ,'--',color =colorlist [i ])

                        normalized_gmm =np .sum (gmm_components ,axis =0 )/gmm_max 


                        ax .plot (x_values ,normalized_gmm +vertical_offset ,'--',label ='Fit',color ='k')


                        ax .plot (x_kde ,y_kde_normalized +vertical_offset ,linewidth =2 ,color =current_color ,label ='Data')


                        y_max_offset =1 +vertical_offset 








                    else :
                        ax .fill_between (x_kde ,y_kde_normalized +vertical_offset ,vertical_offset ,alpha =0.8 ,color =colors_1 [i ],edgecolor ="black",linewidth =0.3 )

                    label_x_coord =overall_x_max +0.05 *(overall_x_max -min (delta_t ))


                    vertical_offset +=1 +gap_between_plots +text_height +gap_between_plot_and_text 



                ax .set_yticks ([])
                ax .set_ylabel ('')
                ax .set_xlabel ('log(Δt (ms))')


                from matplotlib .colors import ListedColormap 


                colors_for_files =colors_1 [:len (file_names )]
                colormap_for_files =ListedColormap (colors_for_files )


                norm =Normalize (vmin =0 ,vmax =len (file_names ))


                sm =plt .cm .ScalarMappable (cmap =colormap_for_files ,norm =norm )
                sm .set_array ([])
                cbar =self .stacked_kde_figure .colorbar (sm ,ax =ax ,orientation ="vertical",label ="Time (min)")
                cbar .set_ticks (list (range (len (file_names )+1 )))
                cbar .set_ticklabels ([i *time_difference for i in range (len (file_names )+1 )])













                ax .figure .tight_layout ()

                self .stacked_kde_canvas .draw ()


                self .line_plot_figure .clear ()
                ax_line =self .line_plot_figure .add_subplot (111 )
                ax_line .plot (times ,peak_values ,marker ='o',linestyle ='-',color ='royalblue')
                ax_line .set_xlabel ('Time')
                ax_line .set_ylabel ('Peak log(Δt) (ms)')
                ax_line .grid (True ,which ='both',linestyle ='--',linewidth =0.5 )

                ax_line .figure .tight_layout ()

                self .line_plot_canvas .draw ()

            else :
                MAX_FILES =11 

                if self .standardisation_used_combo_box .currentText ()=='ΔI':
                    standard_label ='ΔI (pA)'
                elif self .standardisation_used_combo_box .currentText ()=='(ΔI*I0)**0.1':
                    standard_label ='$(ΔI \u00D7 I_0)^{0.1}$'
                elif self .standardisation_used_combo_box .currentText ()=='(ΔI*I0)**0.5':
                    standard_label ='$(ΔI \u00D7 I_0)^{0.5}$'
                elif self .standardisation_used_combo_box .currentText ()=='ΔI/I0':
                    standard_label ='$ΔI/I_0$'
                else :
                    standard_label ='ΔI (pA)'


                time_difference =self .time_diff_spin_box .value ()


                self .stacked_kde_figure .clear ()
                ax =self .stacked_kde_figure .add_subplot (111 )


                component_details =[]
                vertical_offset =0 
                gap_between_plots =0.1 
                text_height =0.1 
                gap_between_plot_and_text =0.05 


                file_names =sorted ([f for f in os .listdir (self .folder_path )if f .endswith ('.dataset.npz')])

                peak_values =[]
                times =[]

                '''# Get the colormap selected by the user
                colormap_name = self.colormap_combo_box.currentText()    
                cmap = plt.get_cmap(colormap_name)

                if len(file_names)>MAX_FILES:
                    MAX_FILES = len(file_names)
                colors_1 = [cmap(i/(MAX_FILES-1)) for i in range(MAX_FILES)]'''

                fixed_colors_20 =[
                '#000080',
                '#1E90FF',
                '#87CEFA',
                '#00FFFF',
                '#40E0D0',
                '#2E8B57',
                '#9ACD32',
                '#FFD700',
                '#FFA07A',
                '#FFA500',
                '#FF7F50',
                '#FA8072',
                '#FF69B4',
                '#FF00FF',
                '#FF1493'
                ]

                colors_1 =fixed_colors_20 


                overall_x_max =None 


                for file_name in file_names :
                    file_path =os .path .join (self .folder_path ,file_name )
                    data =np .load (file_path )
                    X =data ['X']
                    X ,nan_count =remove_nan_arrays (X )
                    if nan_count >0 :
                        print (f"Total Number of nan_counts: {nan_count}")
                    if self .delta_I_button .isChecked ():
                        delta_I =X [:,0 ]*1e3 
                    else :
                        delta_I =X [:,2 ]*1e3 

                    current_x_max =max (delta_I )

                    if overall_x_max is None or current_x_max >overall_x_max :
                        overall_x_max =current_x_max 


                for i ,file_name in enumerate (file_names ):
                    print (file_name )
                    file_path =os .path .join (self .folder_path ,file_name )
                    data =np .load (file_path )

                    X =data ['X']
                    X ,nan_count =remove_nan_arrays (X )
                    if nan_count >0 :
                        print (f"Total Number of nan_counts: {nan_count}")

                    if self .delta_I_button .isChecked ():
                        delta_I =X [:,0 ]*1e3 
                    else :
                        delta_I =X [:,2 ]*1e3 


                    if len (delta_I )==0 :
                        QMessageBox .warning (self ,"Warning",f"{file_name} has empty ΔI data.")
                        continue 


                    kde_func =gaussian_kde (delta_I )

                    x_range =max (delta_I )-min (delta_I )
                    x_kde =np .linspace (min (delta_I )-0.1 *x_range ,max (delta_I )+0.1 *x_range ,1000 )
                    y_kde =kde_func (x_kde )


                    y_kde_normalized =y_kde /max (y_kde )


                    peak_value =x_kde [np .argmax (y_kde )]
                    peak_values .append (peak_value )


                    current_time =(i +1 )*time_difference 
                    times .append (current_time )


                    label =f"{i * time_difference}-{current_time} min"


                    current_color =colors_1 [i ]

                    if self .gaussian_show_checkbox .isChecked ():

                        x_values =np .linspace (min (delta_I ),max (delta_I ),1000 )
                        kde_values =sns .kdeplot (delta_I ,bw_adjust =0.5 ,gridsize =1000 ).get_lines ()[0 ].get_ydata ()
                        plt .close ()


                        if self .gaussian_fitting_combo_box .currentText ()=='Automatic':
                            kde_peaks ,_ =find_peaks (kde_values ,distance =200 )
                        else :
                            kde_peaks =[0 ]*self .gaussian_components_spin_box .value ()


                        gmm =GaussianMixture (n_components =len (kde_peaks ),random_state =0 ).fit (delta_I .reshape (-1 ,1 ))
                        gmm_components =[weights *scipy .stats .norm .pdf (x_values ,loc =mean ,scale =np .sqrt (covariance ))
                        for weights ,mean ,covariance in zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ])]


                        components_tuples =list (zip (gmm .weights_ ,gmm .means_ ,gmm .covariances_ [:,0 ]))


                        sorted_components_tuples =sorted (components_tuples ,key =lambda x :x [1 ])


                        print ("Gaussian Components Details:")
                        for weight ,mean ,covariance in sorted_components_tuples :
                            component ={
                            "Weight":weight ,
                            "Mean":mean [0 ],
                            "Std Dev":np .sqrt (covariance )[0 ]
                            }
                            print (component )




                        components_with_means =list (zip (gmm_components ,gmm .means_ ))


                        sorted_components_with_means =sorted (components_with_means ,key =lambda x :x [1 ])


                        sorted_gmm_components =[component for component ,mean in sorted_components_with_means ]


                        gmm_max =max (np .sum (gmm_components ,axis =0 ))


                        for i ,component in enumerate (sorted_gmm_components ):
                            normalized_component =component /gmm_max 
                            ax .plot (x_values ,normalized_component +vertical_offset ,'--',color =colorlist [i ])

                        normalized_gmm =np .sum (gmm_components ,axis =0 )/gmm_max 

                        ax .plot (x_values ,normalized_gmm +vertical_offset ,'--',color ='k',label ='Fit')


                        ax .plot (x_kde ,y_kde_normalized +vertical_offset ,linewidth =2 ,color =current_color ,label ='Data')


                        y_max_offset =max (np .sum (gmm_components ,axis =0 ))+vertical_offset 









                    else :
                        ax .fill_between (x_kde ,y_kde_normalized +vertical_offset ,vertical_offset ,alpha =0.8 ,color =colors_1 [i ],edgecolor ="black",linewidth =0.3 )

                    label_x_coord =overall_x_max +0.05 *(overall_x_max -min (delta_I ))


                    vertical_offset +=1 +gap_between_plots +text_height +gap_between_plot_and_text 

                if self .gaussian_show_checkbox .isChecked ():
                    print ("Gaussian Components Details:")
                    print (tabulate (component_details ,headers ="keys"))


                ax .set_yticks ([])
                ax .set_ylabel ('')
                ax .set_xlabel (standard_label ,fontsize =16 )
                ax .tick_params (axis ='x',labelsize =14 )
                ax .set_xlim ([250 ,2500 ])



                from matplotlib .colors import ListedColormap 


                colors_for_files =colors_1 [:len (file_names )]
                colormap_for_files =ListedColormap (colors_for_files )


                norm =Normalize (vmin =0 ,vmax =len (file_names ))


                sm =plt .cm .ScalarMappable (cmap =colormap_for_files ,norm =norm )
                sm .set_array ([])
                cbar =self .stacked_kde_figure .colorbar (sm ,ax =ax ,orientation ="vertical",label ="Time (min)")
                cbar .set_ticks (list (range (len (file_names )+1 )))
                cbar .set_ticklabels ([i *time_difference for i in range (len (file_names )+1 )])


















                ax .figure .tight_layout ()

                self .stacked_kde_canvas .draw ()



                self .line_plot_figure .clear ()
                ax_line =self .line_plot_figure .add_subplot (111 )
                ax_line .plot (times ,peak_values ,marker ='o',linestyle ='-',color ='royalblue')
                ax_line .set_xlabel ('Time')
                ax_line .set_ylabel ('Peak ΔI (pA)')
                ax_line .grid (True ,which ='both',linestyle ='--',linewidth =0.5 )

                ax_line .figure .tight_layout ()

                self .line_plot_canvas .draw ()


        except :
            pass 

if __name__ =="__main__":
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
    window =MainApp ()
    window .show ()
    sys .exit (app .exec ())
