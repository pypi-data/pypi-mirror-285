import sys 
import os 
import numpy as np 
from PySide6 .QtWidgets import (QApplication ,QMainWindow ,QWidget ,QVBoxLayout ,QHBoxLayout ,QPushButton ,QListWidget ,QSpinBox ,QDoubleSpinBox ,QLabel ,QCheckBox ,QFileDialog ,QTabWidget ,QSizePolicy ,QGridLayout ,QSpinBox ,QMessageBox ,QLineEdit ,QFormLayout ,QHBoxLayout ,QStyleFactory ,QComboBox ,QScrollArea )
from PySide6 .QtCore import Qt 
from matplotlib .backends .backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib .figure import Figure 
from matplotlib .backends .backend_qt5agg import NavigationToolbar2QT as NavigationToolbar 
from functools import partial 
import seaborn as sns 
import matplotlib .pyplot as plt 
from matplotlib .ticker import ScalarFormatter 
from PySide6 .QtGui import QPalette ,QColor ,QFont 
import math 

class MplCanvas (FigureCanvas ):
    def __init__ (self ,width =5 ,height =4 ,dpi =300 ):
        fig =Figure (figsize =(width ,height ),dpi =dpi )
        self .axes =fig .add_subplot (111 )
        super ().__init__ (fig )

class PlottingApplication (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("SD Frequency and multi-plots")
        self .histogram_bins =100 
        self .scatter_marker_size =3 
        self .global_limits ={}
        self .filtered_data ={}
        self .initUI ()

    def initUI (self ):

        mainWidget =QWidget ()
        self .setCentralWidget (mainWidget )
        mainLayout =QHBoxLayout (mainWidget )


        self .leftPanel =QTabWidget ()
        fileSelectionTab =QWidget ()
        self .plotOptionsTab =QWidget ()
        databaseTab =QWidget ()

        self .leftPanel .addTab (fileSelectionTab ,"Files")
        self .leftPanel .addTab (self .plotOptionsTab ,"Options")
        self .leftPanel .addTab (databaseTab ,"Database")


        self .rightPanel =QTabWidget ()

        mainLayout .addWidget (self .leftPanel ,25 )
        mainLayout .addWidget (self .rightPanel ,75 )

        self .setupFileSelectionTab (fileSelectionTab )
        self .setupPlotOptionsTab (self .plotOptionsTab )
        self .setupDatabaseTab (databaseTab )



    def calculateGridSize (self ,numberOfPlots ):


        gridSize =math .ceil (math .sqrt (numberOfPlots ))




        nrows =gridSize 
        ncols =gridSize 


        if gridSize *(gridSize -1 )>=numberOfPlots :
            ncols -=1 

        return nrows ,ncols 



    def setupFileSelectionTab (self ,tab ):
        layout =QVBoxLayout (tab )

        headerLabel =QLabel ("SD Frequency and multi-plots\nshankar.dutt@anu.edu.au")
        headerLabel .setWordWrap (True )
        headerLabel .setAlignment (Qt .AlignmentFlag .AlignCenter )
        headerLabel .setFont (QFont ('Arial',18 ,QFont .Weight .Bold ))
        headerLabel .setStyleSheet ("QLabel { color : white; margin-top: 20px; margin-bottom: 20px; }")


        app .setStyleSheet ("""
        QPushButton {
            background-color: #2b5b84;
            color: white;
            border-radius: 5px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #1d4560;
        }
        """)

        layout .addWidget (headerLabel )

        selectFolderBtn =QPushButton ("Select Folder")
        selectFolderBtn .clicked .connect (self .selectFolder )
        layout .addWidget (selectFolderBtn )

        self .fileListWidget =QListWidget ()
        self .fileListWidget .setSelectionMode (QListWidget .SelectionMode .MultiSelection )
        layout .addWidget (self .fileListWidget )

        self .includeSubfoldersCheckbox =QCheckBox ("Include Subfolders")
        layout .addWidget (self .includeSubfoldersCheckbox )

        plotButton =QPushButton ("Plot")
        plotButton .clicked .connect (self .plotSelectedFiles )
        layout .addWidget (plotButton )


        self .plotOptions ={
        'Histogram of dI':QCheckBox ('Histogram of dI'),
        'Histogram of dt':QCheckBox ('Histogram of dt'),
        'Histogram of Area':QCheckBox ('Histogram of Area'),
        'Scatter plot dI vs dt':QCheckBox ('Scatter plot dI vs dt'),
        'Scatter plot area vs dt':QCheckBox ('Scatter plot area vs dt'),
        'Histogram of dt (ln)':QCheckBox ('Histogram of dt (ln)'),
        'Scatter plot dI vs dt (ln)':QCheckBox ('Scatter plot dI vs dt (ln)'),
        'Frequency plot':QCheckBox ('Frequency plot')
        }
        for option in self .plotOptions .values ():
            layout .addWidget (option )

        syncZoomButton =QPushButton ("Sync Zoom")
        syncZoomButton .clicked .connect (self .syncZoomAcrossPlots )
        layout .addWidget (syncZoomButton )
        self .selectedFilesOrder =[]


        self .fileListWidget .itemSelectionChanged .connect (self .updateSelectionOrder )


    def setupPlotOptionsTab (self ,tab ):
        layout =QVBoxLayout (tab )


        formLayout =QFormLayout ()


        self .histogramBinsSpinBox =QSpinBox ()
        self .histogramBinsSpinBox .setMinimum (1 )
        self .histogramBinsSpinBox .setMaximum (1000 )
        self .histogramBinsSpinBox .setValue (100 )
        formLayout .addRow ("Histogram Bins:",self .histogramBinsSpinBox )


        self .markerSizeSpinBox =QSpinBox ()
        self .markerSizeSpinBox .setMinimum (1 )
        self .markerSizeSpinBox .setMaximum (100 )
        self .markerSizeSpinBox .setValue (3 )
        formLayout .addRow ("Marker Size:",self .markerSizeSpinBox )


        self .linearFitCheckBox =QCheckBox ("Enable Linear Fit in the Frequency Plots")
        formLayout .addRow (self .linearFitCheckBox )


        self .fitBetweenPointsCheckBox =QCheckBox ("Fit Between Two Points")
        formLayout .addRow (self .fitBetweenPointsCheckBox )


        self .fitStartPointSpinBox =QDoubleSpinBox ()
        self .fitStartPointSpinBox .setMinimum (-np .inf )
        self .fitStartPointSpinBox .setMaximum (np .inf )
        self .fitStartPointSpinBox .setValue (0 )


        self .fitEndPointSpinBox =QDoubleSpinBox ()
        self .fitEndPointSpinBox .setMinimum (-np .inf )
        self .fitEndPointSpinBox .setMaximum (np .inf )
        self .fitEndPointSpinBox .setValue (1 )

        self .fitRangeLabel =QLabel ("Fit Range:")
        self .fitRangeLayout =QHBoxLayout ()
        self .fitRangeLayout .addWidget (self .fitRangeLabel )
        self .fitRangeLayout .addWidget (self .fitStartPointSpinBox )
        self .fitRangeLayout .addWidget (self .fitEndPointSpinBox )
        formLayout .addRow (self .fitRangeLayout )

        self .fitBetweenPointsCheckBox .stateChanged .connect (self .toggleFitRangeVisibility )
        self .toggleFitRangeVisibility (False )

        self .overlayPlotsCheckBox =QCheckBox ("Overlay Plots")
        formLayout .addRow (self .overlayPlotsCheckBox )

        self .alphaSpin =QDoubleSpinBox ()
        self .alphaSpin .setMinimum (0.0 )
        self .alphaSpin .setMaximum (1.0 )
        self .alphaSpin .setSingleStep (0.1 )
        self .alphaSpin .setValue (0.5 )
        formLayout .addRow ("Alpha:",self .alphaSpin )


        self .saveDirectoryLineEdit =QLineEdit ()
        self .saveDirectoryButton =QPushButton ("Select Save Folder")
        self .saveDirectoryButton .clicked .connect (self .selectSaveFolder )
        saveFolderLayout =QHBoxLayout ()
        saveFolderLayout .addWidget (self .saveDirectoryLineEdit )
        saveFolderLayout .addWidget (self .saveDirectoryButton )
        formLayout .addRow ("Save Figures To:",saveFolderLayout )


        updatePlotsButton =QPushButton ("Update Plots")
        updatePlotsButton .clicked .connect (self .updatePlots )
        formLayout .addRow ("",updatePlotsButton )


        saveFiguresButton =QPushButton ("Save Figures")
        saveFiguresButton .clicked .connect (self .saveAllFigures )
        formLayout .addRow ("",saveFiguresButton )

        layout .addLayout (formLayout )


        layout .setSpacing (10 )
        tab .setLayout (layout )

    def setupDatabaseTab (self ,tab ):
        layout =QVBoxLayout (tab )

        self .filterLayout =QVBoxLayout ()

        filterScrollArea =QScrollArea ()
        filterScrollArea .setWidgetResizable (True )
        filterScrollAreaContent =QWidget ()
        filterScrollAreaContent .setLayout (self .filterLayout )
        filterScrollArea .setWidget (filterScrollAreaContent )
        layout .addWidget (filterScrollArea )

        addFilterButton =QPushButton ("Add Filter")
        addFilterButton .clicked .connect (self .addFilter )
        layout .addWidget (addFilterButton )

        buttonLayout =QHBoxLayout ()
        applyFiltersButton =QPushButton ("Apply Filters")
        applyFiltersButton .clicked .connect (self .applyFilters )
        buttonLayout .addWidget (applyFiltersButton )

        saveFilteredDataButton =QPushButton ("Save Filtered Data")
        saveFilteredDataButton .clicked .connect (self .saveFilteredData )
        buttonLayout .addWidget (saveFilteredDataButton )

        layout .addLayout (buttonLayout )

    def addFilter (self ):
        filterWidget =QWidget ()
        filterLayout =QFormLayout (filterWidget )

        variableComboBox =QComboBox ()
        variables =["ΔI","Δt_fwhm","ΔI_fwhm","Area","Δt","Skew","Kurtosis","Event_Baseline","Event_Time"]
        variableComboBox .addItems (variables )
        filterLayout .addRow ("Variable:",variableComboBox )

        minValueSpinBox =QDoubleSpinBox ()
        minValueSpinBox .setMinimum (-np .inf )
        minValueSpinBox .setMaximum (np .inf )
        filterLayout .addRow ("Min Value:",minValueSpinBox )

        maxValueSpinBox =QDoubleSpinBox ()
        maxValueSpinBox .setMinimum (-np .inf )
        maxValueSpinBox .setMaximum (np .inf )
        filterLayout .addRow ("Max Value:",maxValueSpinBox )

        removeFilterButton =QPushButton ("Remove")
        removeFilterButton .clicked .connect (lambda :self .removeFilter (filterWidget ))
        filterLayout .addRow ("Remove:",removeFilterButton )

        self .filterLayout .addWidget (filterWidget )
        self .updateLogicComboBoxes ()


    def updateLogicComboBoxes (self ):
        filterCount =self .filterLayout .count ()

        for i in range (filterCount -1 ):
            filterWidget =self .filterLayout .itemAt (i ).widget ()
            filterLayout =filterWidget .layout ()

            if filterLayout .rowCount ()==4 :
                logicComboBox =QComboBox ()
                logicComboBox .addItems (["AND","OR"])
                filterLayout .addRow ("Logic:",logicComboBox )
            elif i <filterCount -2 :
                logicLabel =None 
                for j in range (filterLayout .rowCount ()):
                    label =filterLayout .itemAt (j ,QFormLayout .ItemRole .LabelRole ).widget ()
                    if isinstance (label ,QLabel )and label .text ()=="Logic:":
                        logicLabel =label 
                        break 
                if logicLabel is None :
                    logicComboBox =QComboBox ()
                    logicComboBox .addItems (["AND","OR"])
                    filterLayout .addRow ("Logic:",logicComboBox )
            else :
                for j in range (filterLayout .rowCount ()):
                    label =filterLayout .itemAt (j ,QFormLayout .ItemRole .LabelRole ).widget ()
                    if isinstance (label ,QLabel )and label .text ()=="Logic:":
                        filterLayout .removeRow (j )
                        break 

    def toggleFitRangeVisibility (self ,visible ):
        self .fitRangeLabel .setVisible (visible )
        self .fitStartPointSpinBox .setVisible (visible )
        self .fitEndPointSpinBox .setVisible (visible )


    def selectSaveFolder (self ):
        folder =QFileDialog .getExistingDirectory (self ,"Select Folder")
        if folder :
            self .saveDirectoryLineEdit .setText (folder )

    def saveAllFigures (self ):
        saveFolder =self .saveDirectoryLineEdit .text ().strip ()
        if not saveFolder :
            QMessageBox .information (self ,"Info","Please select a folder to save the figures.")
            return 

        for i in range (self .rightPanel .count ()):
            tab =self .rightPanel .widget (i )
            if hasattr (tab ,"property"):
                tabCanvases =tab .property ("canvases")
                if tabCanvases :
                    tabFolder =os .path .join (saveFolder ,self .rightPanel .tabText (i ))
                    if not os .path .exists (tabFolder ):
                        os .makedirs (tabFolder )
                    for j ,canvas in enumerate (tabCanvases ):
                        figure =canvas .figure 
                        figure .savefig (os .path .join (tabFolder ,f"figure_{j+1}.png"),dpi =300 ,bbox_inches ='tight')
        QMessageBox .information (self ,"Info","Figures saved successfully.")

    def removeFilter (self ,filterWidget ):
        self .filterLayout .removeWidget (filterWidget )
        filterWidget .deleteLater ()
        self .updateLogicComboBoxes ()

    def applyFilters (self ):
        self .filtered_data ={}
        selectedFiles =[self .fileListWidget .item (i ).text ()for i in range (self .fileListWidget .count ())if self .fileListWidget .item (i ).isSelected ()]

        for filePath in selectedFiles :
            fileData =np .load (filePath )
            X =fileData ['X']

            mask =np .ones (len (X ),dtype =bool )

            for i in range (self .filterLayout .count ()):
                filterWidget =self .filterLayout .itemAt (i ).widget ()
                filterLayout =filterWidget .layout ()

                for j in range (filterLayout .rowCount ()):
                    label =filterLayout .itemAt (j ,QFormLayout .ItemRole .LabelRole ).widget ()
                    if isinstance (label ,QLabel ):
                        if label .text ()=="Variable:":
                            variableComboBox =filterLayout .itemAt (j ,QFormLayout .ItemRole .FieldRole ).widget ()
                        elif label .text ()=="Min Value:":
                            minValueSpinBox =filterLayout .itemAt (j ,QFormLayout .ItemRole .FieldRole ).widget ()
                        elif label .text ()=="Max Value:":
                            maxValueSpinBox =filterLayout .itemAt (j ,QFormLayout .ItemRole .FieldRole ).widget ()
                        elif label .text ()=="Logic:":
                            logicComboBox =filterLayout .itemAt (j ,QFormLayout .ItemRole .FieldRole ).widget ()

                variable =variableComboBox .currentText ()
                minValue =minValueSpinBox .value ()
                maxValue =maxValueSpinBox .value ()

                variableIndex =["ΔI","Δt_fwhm","ΔI_fwhm","Area","Δt","Skew","Kurtosis","Event_Baseline","Event_Time"].index (variable )
                variableValues =X [:,variableIndex ]

                condition =(variableValues >=minValue )&(variableValues <=maxValue )

                if i ==0 :
                    mask =condition 
                else :
                    if isinstance (logicComboBox ,QComboBox ):
                        logic =logicComboBox .currentText ()
                        if logic =="AND":
                            mask &=condition 
                        else :
                            mask |=condition 
                    else :
                        mask &=condition 

            self .filtered_data [filePath ]=X [mask ]

        self .plotSelectedFiles ()

    def selectFolder (self ):
        folderPath =QFileDialog .getExistingDirectory (self ,"Select Folder")
        if folderPath :
            self .populateFileList (folderPath ,self .includeSubfoldersCheckbox .isChecked ())

    def saveFilteredData (self ):
        saveFolder =QFileDialog .getExistingDirectory (self ,"Select Folder to Save Filtered Data")
        if saveFolder :
            for filePath ,filteredData in self .filtered_data .items ():
                fileName =os .path .basename (filePath )
                savePath =os .path .join (saveFolder ,f"filtered_{fileName}")


                fileData =np .load (filePath )
                settings =fileData ['settings'].item ()


                np .savez (savePath ,X =filteredData ,settings =settings )

            QMessageBox .information (self ,"Info","Filtered data and settings saved successfully.")

    def populateFileList (self ,folderPath ,includeSubfolders ):
        self .fileListWidget .clear ()
        if includeSubfolders :
            for root ,dirs ,files in os .walk (folderPath ):
                for file in files :
                    if file .endswith ('.dataset.npz'):
                        fullPath =os .path .join (root ,file )
                        self .fileListWidget .addItem (fullPath )
        else :
            for file in os .listdir (folderPath ):
                if file .endswith ('.dataset.npz'):
                    fullPath =os .path .join (folderPath ,file )
                    self .fileListWidget .addItem (fullPath )

    def updateSelectionOrder (self ):

        currentSelection ={self .fileListWidget .item (i ).text ()for i in range (self .fileListWidget .count ())if self .fileListWidget .item (i ).isSelected ()}


        self .selectedFilesOrder =[f for f in self .selectedFilesOrder if f in currentSelection ]


        for i in range (self .fileListWidget .count ()):
            itemText =self .fileListWidget .item (i ).text ()
            if self .fileListWidget .item (i ).isSelected ()and itemText not in self .selectedFilesOrder :
                self .selectedFilesOrder .append (itemText )


    def updatePlots (self ):

        self .histogram_bins =self .histogramBinsSpinBox .value ()
        self .scatter_marker_size =self .markerSizeSpinBox .value ()


        self .plotSelectedFiles ()


    @staticmethod 
    def create_joint_plot (self ,fig ,data_x ,data_y ,min_x ,max_x ,min_y ,max_y ,plotType ,alpha ):

        gs =fig .add_gridspec (4 ,4 )


        ax_scatter =fig .add_subplot (gs [1 :4 ,0 :3 ])
        if data_x is not None and data_y is not None :
            ax_scatter .scatter (data_x ,data_y ,s =int (self .markerSizeSpinBox .value ()),alpha =alpha )
        ax_scatter .set_xlim (min_x ,max_x )
        ax_scatter .set_ylim (min_y ,max_y )


        ax_histx =fig .add_subplot (gs [0 ,0 :3 ],sharex =ax_scatter )
        if data_x is not None :
            ax_histx .hist (data_x ,bins =self .histogramBinsSpinBox .value ())
        ax_histx .set_ylabel (' ')


        ax_histy =fig .add_subplot (gs [1 :4 ,3 ],sharey =ax_scatter )
        if data_y is not None :
            ax_histy .hist (data_y ,bins =self .histogramBinsSpinBox .value (),orientation ='horizontal')
        ax_histy .set_xlabel (' ')


        plt .setp (ax_histx .get_xticklabels (),visible =False )
        plt .setp (ax_histy .get_yticklabels (),visible =False )

        ax_scatter .xaxis .set_major_formatter (ScalarFormatter (useMathText =True ))
        ax_scatter .yaxis .set_major_formatter (ScalarFormatter (useMathText =True ))
        if 'dI vs dt'in plotType and 'ln'not in plotType :
            ax_scatter .set_xlabel ('Δt (ms)')
            ax_scatter .set_ylabel ('ΔI (nA)')
        elif 'area vs dt'in plotType :
            ax_scatter .set_xlabel ('Δt (ms)')
            ax_scatter .set_ylabel ('Area (C)')
        elif 'dI vs dt (ln)'in plotType :
            ax_scatter .set_xlabel ('ln(Δt (ms))')
            ax_scatter .set_ylabel ('ΔI (nA)')

        ax_scatter .ticklabel_format (style ='sci',axis ='both',scilimits =(0 ,0 ))
        ax_histx .ticklabel_format (style ='sci',axis ='both',scilimits =(0 ,0 ))
        ax_histy .ticklabel_format (style ='sci',axis ='both',scilimits =(0 ,0 ))
        fig .tight_layout ()


        return {'ax_scatter':ax_scatter ,'ax_histx':ax_histx ,'ax_histy':ax_histy }

    def plotSelectedFiles (self ):
        '''selectedFiles = [self.fileListWidget.item(i).text() for i in range(self.fileListWidget.count()) if self.fileListWidget.item(i).isSelected()]
        plotOptions = {key: option.isChecked() for key, option in self.plotOptions.items() if option.isChecked()}'''

        plotOptions ={key :option .isChecked ()for key ,option in self .plotOptions .items ()if option .isChecked ()}
        self .rightPanel .clear ()

        self .rightPanel .clear ()

        if not self .selectedFilesOrder or not plotOptions :
            return 

        data =self .prepareData (self .selectedFilesOrder ,plotOptions )

        for plotType ,plotData in data .items ():
            tab =QWidget ()
            layout =QVBoxLayout (tab )
            plotLayout =QGridLayout ()
            alpha =self .alphaSpin .value ()
            tabCanvases =[]

            if self .overlayPlotsCheckBox .isChecked ():

                fig =Figure (figsize =(10 ,5 ))
                canvas =FigureCanvas (fig )
                tabCanvases .append (canvas )

                min_x ,max_x ,min_y ,max_y =self .calculateGlobalAxisLimits (plotData ,plotType )

                if 'Scatter plot dI vs dt'in plotType and 'ln'not in plotType :
                    axes_dict =self .create_joint_plot (self ,fig ,None ,None ,min_x ,max_x ,min_y ,max_y ,'dI vs dt',alpha )
                    ax_scatter =axes_dict ['ax_scatter']
                    ax_histx =axes_dict ['ax_histx']
                    ax_histy =axes_dict ['ax_histy']

                    for filePath ,values in plotData .items ():
                        alpha =self .alphaSpin .value ()
                        label =os .path .basename (filePath )

                        ax_scatter .scatter (values [0 ],values [1 ],s =int (self .markerSizeSpinBox .value ()),alpha =alpha ,label =label )
                        ax_histx .hist (values [0 ],bins =self .histogramBinsSpinBox .value (),alpha =alpha )
                        ax_histy .hist (values [1 ],bins =self .histogramBinsSpinBox .value (),orientation ='horizontal',alpha =alpha )

                    ax .set_xlabel ('Δt (ms)')
                    ax .set_ylabel ('ΔI (nA)')
                    fig .tight_layout ()
                    ax_scatter .legend ()

                elif 'Scatter plot area vs dt'in plotType :
                    axes_dict =self .create_joint_plot (self ,fig ,None ,None ,min_x ,max_x ,min_y ,max_y ,'area vs dt',alpha )
                    ax_scatter =axes_dict ['ax_scatter']
                    ax_histx =axes_dict ['ax_histx']
                    ax_histy =axes_dict ['ax_histy']

                    for filePath ,values in plotData .items ():
                        alpha =self .alphaSpin .value ()
                        label =os .path .basename (filePath )

                        ax_scatter .scatter (values [0 ],values [1 ],s =int (self .markerSizeSpinBox .value ()),alpha =alpha ,label =label )
                        ax_histx .hist (values [0 ],bins =self .histogramBinsSpinBox .value (),alpha =alpha )
                        ax_histy .hist (values [1 ],bins =self .histogramBinsSpinBox .value (),orientation ='horizontal',alpha =alpha )
                    ax .set_xlabel ('Δt (ms)')
                    ax .set_ylabel ('Area')
                    fig .tight_layout ()
                    ax_scatter .legend ()

                elif 'Scatter plot dI vs dt (ln)'in plotType :
                    axes_dict =self .create_joint_plot (self ,fig ,None ,None ,np .log (min_x ),np .log (max_x ),min_y ,max_y ,'dI vs dt (ln)',alpha )
                    ax_scatter =axes_dict ['ax_scatter']
                    ax_histx =axes_dict ['ax_histx']
                    ax_histy =axes_dict ['ax_histy']

                    for filePath ,values in plotData .items ():
                        alpha =self .alphaSpin .value ()
                        label =os .path .basename (filePath )

                        ax_scatter .scatter (np .log (values [0 ]),values [1 ],s =int (self .markerSizeSpinBox .value ()),alpha =alpha ,label =label )
                        ax_histx .hist (np .log (values [0 ]),bins =self .histogramBinsSpinBox .value (),alpha =alpha )
                        ax_histy .hist (values [1 ],bins =self .histogramBinsSpinBox .value (),orientation ='horizontal',alpha =alpha )
                    ax .set_xlabel ('ln(Δt (ms))')
                    ax .set_ylabel ('ΔI (nA)')
                    fig .tight_layout ()
                    ax_scatter .legend ()


                elif 'Histogram of dt (ln)'in plotType :
                    ax =fig .add_subplot (111 )

                    for filePath ,values in plotData .items ():
                        alpha =self .alphaSpin .value ()
                        label =os .path .basename (filePath )
                        log_values =np .log (values [values >0 ]*1e3 )

                        ax .hist (log_values ,bins =self .histogramBinsSpinBox .value (),range =(np .log (min_x *1e3 ),np .log (max_x *1e3 )),alpha =alpha ,label =label ,density =True )
                    ax .set_xlabel ('ln(Δt (ms))')
                    ax .set_ylabel ('Density')
                    fig .tight_layout ()
                    ax .legend ()

                elif 'Frequency plot'in plotType :
                    ax =fig .add_subplot (111 )

                    for filePath ,values in plotData .items ():
                        alpha =self .alphaSpin .value ()
                        label =os .path .basename (filePath )

                        ax .plot (values [0 ],values [1 ],'o',markersize =self .scatter_marker_size ,alpha =alpha ,label =label )

                        if self .linearFitCheckBox .isChecked ():
                            if self .fitBetweenPointsCheckBox .isChecked ():
                                start_point =self .fitStartPointSpinBox .value ()
                                end_point =self .fitEndPointSpinBox .value ()
                                mask =(values [0 ]>=start_point )&(values [0 ]<=end_point )
                                x_fit =values [0 ][mask ]
                                y_fit =values [1 ][mask ]
                                slope ,intercept =np .polyfit (x_fit ,y_fit ,1 )
                            else :
                                slope ,intercept =np .polyfit (values [0 ],values [1 ],1 )
                                x_fit =np .array ([min_x ,max_x ])
                                y_fit =slope *x_fit +intercept 

                            ax .plot (x_fit ,slope *x_fit +intercept ,'--',alpha =alpha )

                    ax .legend ()
                    ax .set_xlabel ('Time (s)')
                    ax .set_ylabel ('Event Number')

                else :
                    ax =fig .add_subplot (111 )

                    for filePath ,values in plotData .items ():
                        alpha =self .alphaSpin .value ()
                        label =os .path .basename (filePath )

                        ax .hist (values ,bins =self .histogramBinsSpinBox .value (),range =(min_x ,max_x ),alpha =alpha ,label =label ,density =True )

                    ax .legend ()

                ax .set_xlabel ('ΔI (nA)')
                ax .set_ylabel ('Density')
                fig .suptitle ("Overlaid Plots",fontsize =12 )

                fig .tight_layout ()
                fig .tight_layout ()
                fig .tight_layout ()
                fig .tight_layout ()
                fig .tight_layout ()
                plotLayout .addWidget (canvas ,0 ,0 )



            else :
                row =col =0 
                max_col =1 

                min_x ,max_x ,min_y ,max_y =self .calculateGlobalAxisLimits (plotData ,plotType )

                for filePath ,values in plotData .items ():
                    fig =Figure (figsize =(5 ,5 ))
                    canvas =FigureCanvas (fig )

                    if 'Scatter plot dI vs dt'in plotType and 'ln'not in plotType :
                        axes_dict =self .create_joint_plot (self ,fig ,values [0 ],values [1 ],min_x ,max_x ,min_y ,max_y ,'dI vs dt',alpha =1.0 )
                        canvas .axes_dict =axes_dict 
                        canvas .plotType ='Scatter plot dI vs dt'
                        title =f"{os.path.basename(filePath)}\nEvents: {len(values[0])}"

                    elif 'Scatter plot area vs dt'in plotType :
                        axes_dict =self .create_joint_plot (self ,fig ,values [0 ],values [1 ],min_x ,max_x ,min_y ,max_y ,'area vs dt',alpha =1.0 )
                        canvas .axes_dict =axes_dict 
                        canvas .plotType ='Scatter plot area vs dt'
                        title =f"{os.path.basename(filePath)}\nEvents: {len(values[0])}"

                    elif 'Scatter plot dI vs dt (ln)'in plotType :
                        axes_dict =self .create_joint_plot (self ,fig ,np .log (values [0 ]),values [1 ],np .log (min_x ),np .log (max_x ),min_y ,max_y ,'dI vs dt (ln)',alpha =1.0 )
                        canvas .axes_dict =axes_dict 
                        canvas .plotType ='Scatter plot dI vs dt (ln)'
                        title =f"{os.path.basename(filePath)}\nEvents: {len(values[0])}"

                    elif 'Histogram of dt (ln)'in plotType :
                        log_values =np .log (values [values >0 ]*1e3 )
                        axes_dict =self .create_histogram (fig ,log_values ,np .log (min_x *1e3 ),np .log (max_x *1e3 ),'dt (ln)',alpha )
                        canvas .axes_dict =axes_dict 
                        canvas .plotType ='Histogram of dt (ln)'
                        title =f"{os.path.basename(filePath)}\nEvents: {len(log_values)}"

                    elif 'Frequency plot'in plotType :
                        self .create_frequency_plot (fig ,values [0 ],values [1 ],min_x ,max_x ,min_y ,max_y ,alpha =1.0 )
                        canvas .plotType ='Frequency plot'
                        title =f"{os.path.basename(filePath)}\nEvents: {len(values[0])}"
                        if self .linearFitCheckBox .isChecked ():
                            if self .fitBetweenPointsCheckBox .isChecked ():
                                start_point =self .fitStartPointSpinBox .value ()
                                end_point =self .fitEndPointSpinBox .value ()
                                mask =(values [0 ]>=start_point )&(values [0 ]<=end_point )
                                x_fit =values [0 ][mask ]
                                y_fit =values [1 ][mask ]
                                slope ,intercept =np .polyfit (x_fit ,y_fit ,1 )
                            else :
                                slope ,intercept =np .polyfit (values [0 ],values [1 ],1 )
                                x_fit =np .array ([min_x ,max_x ])
                                y_fit =slope *x_fit +intercept 

                            ax =fig .axes [0 ]
                            ax .plot (x_fit ,slope *x_fit +intercept ,'r--',label =f'Fit: {slope:.2f} Events/s, Intercept: {intercept:.2f}')
                            ax .legend ()
                            title +=f"\nFit: {slope:.2f} Events/s, Intercept: {intercept:.2f}"

                    else :

                        axes_dict =self .create_histogram (fig ,values ,min_x ,max_x ,plotType ,alpha =1.0 )
                        canvas .axes_dict =axes_dict 
                        canvas .plotType =plotType 
                        title =f"{os.path.basename(filePath)}\nEvents: {len(values)}"

                    fig .suptitle (title ,fontsize =8 )

                    plotLayout .addWidget (canvas ,row ,col )
                    tabCanvases .append (canvas )

                    col +=1 
                    if col >max_col :
                        col =0 
                        row +=1 


                    fig .tight_layout ()

            layout .addLayout (plotLayout )

            if tabCanvases :
                toolbar =NavigationToolbar (tabCanvases [0 ],self )
                layout .addWidget (toolbar )

            fig .tight_layout ()

            resetButton =QPushButton ("Reset Zoom")
            resetButton .clicked .connect (self .resetZoom )
            layout .addWidget (resetButton )

            self .rightPanel .addTab (tab ,plotType )
            tab .setProperty ("canvases",tabCanvases )


    def create_frequency_plot (self ,fig ,times ,event_numbers ,min_x ,max_x ,min_y ,max_y ,alpha ):
        ax =fig .add_subplot (111 )
        ax .plot (times ,event_numbers ,'o',markersize =self .scatter_marker_size ,alpha =alpha )
        ax .set_xlim (min_x ,max_x )

        ax .set_xlabel ('Time (s)')
        ax .set_ylabel ('Event Number')
        ax .ticklabel_format (style ='sci',axis ='both',scilimits =(0 ,0 ))
        fig .tight_layout ()


    def syncZoomAcrossPlots (self ):
        currentTab =self .rightPanel .currentWidget ()
        if hasattr (currentTab ,"property"):
            tabCanvases =currentTab .property ("canvases")
            if tabCanvases and len (tabCanvases )>0 :

                referenceAxes =tabCanvases [0 ].figure .axes [0 ]
                xlim =referenceAxes .get_xlim ()
                ylim =referenceAxes .get_ylim ()

                for canvas in tabCanvases :
                    plotType =getattr (canvas ,'plotType','')
                    if 'Scatter plot'in plotType :
                        if hasattr (canvas ,'axes_dict'):
                            canvas .axes_dict ['ax_scatter'].set_xlim (xlim )
                            canvas .axes_dict ['ax_scatter'].set_ylim (ylim )
                            canvas .axes_dict ['ax_histx'].set_xlim (xlim )
                            canvas .axes_dict ['ax_histy'].set_ylim (ylim )
                    elif 'Histogram'in plotType or 'Frequency plot'in plotType :

                        ax =canvas .figure .axes [0 ]
                        ax .set_xlim (xlim )
                    else :

                        for ax in canvas .figure .axes :
                            ax .set_xlim (xlim )
                            ax .set_ylim (ylim )

                    canvas .draw_idle ()



    def create_histogram (self ,fig ,values ,min_x ,max_x ,plotType ,alpha ):
        ax =fig .add_subplot (111 )
        ax .hist (values ,bins =self .histogramBinsSpinBox .value (),range =(min_x ,max_x ),alpha =alpha )
        ax .xaxis .set_major_formatter (ScalarFormatter (useMathText =True ))
        if 'dI'in plotType :
            ax .set_xlabel ('ΔI (nA)')
        elif 'dt'in plotType and 'ln'not in plotType :
            ax .set_xlabel ('Δt (s)')
        elif 'dt (ln)'in plotType :
            ax .set_xlabel ('ln(Δt (ms))')
        ax .set_ylabel ('Count')
        ax .ticklabel_format (style ='sci',axis ='both',scilimits =(0 ,0 ))
        fig .tight_layout ()


        return {'ax_hist':ax }


    def resetZoom (self ):
        currentTab =self .rightPanel .currentWidget ()
        if currentTab is None :
            return 

        plotType =self .rightPanel .tabText (self .rightPanel .indexOf (currentTab ))

        if plotType in self .global_limits :
            min_x ,max_x ,min_y ,max_y =self .global_limits [plotType ]

            tabCanvases =currentTab .property ("canvases")
            if tabCanvases :
                for canvas in tabCanvases :
                    if plotType =='Scatter plot dI vs dt'or plotType =='Scatter plot area vs dt'or plotType =='Scatter plot dI vs dt (ln)':
                        if hasattr (canvas ,'axes_dict'):
                            canvas .axes_dict ['ax_scatter'].set_xlim (min_x ,max_x )
                            canvas .axes_dict ['ax_scatter'].set_ylim (min_y ,max_y )
                            canvas .axes_dict ['ax_histx'].set_xlim (min_x ,max_x )
                            canvas .axes_dict ['ax_histy'].set_ylim (min_y ,max_y )
                    elif plotType =='Frequency plot':
                        ax =canvas .figure .axes [0 ]
                        ax .set_xlim (min_x ,max_x )

                    elif plotType in ['Histogram of dI','Histogram of dt','Histogram of Area','Histogram of dt (ln)']:
                        ax =canvas .figure .axes [0 ]
                        ax .set_xlim (min_x ,max_x )
                    else :
                        print (f"Unsupported plot type: {plotType}")

                    canvas .draw_idle ()


    def prepareData (self ,selectedFiles ,plotOptions ):
        data ={}
        for filePath in selectedFiles :
            if filePath in self .filtered_data :
                X =self .filtered_data [filePath ]
                fileData ={'X':X }
            else :
                fileData =np .load (filePath )
                X =fileData ['X']

            for option in plotOptions :
                if option not in data :
                    data [option ]={}

                if 'Histogram'in option :
                    index =0 if 'dI'in option else 3 if 'Area'in option else 4 
                    values =X [:,index ].astype (float )

                    values =values [~np .isnan (values )]
                    data [option ][filePath ]=values 
                elif 'Histogram of dt (ln)'in option :

                    dt_values =X [:,4 ]

                    positive_dt_values =dt_values [dt_values >0 ]

                    log_dt_values =np .log (positive_dt_values *1e3 )

                    log_dt_values =log_dt_values [~np .isnan (log_dt_values )]
                    data ['Histogram of dt (ln)'][filePath ]=log_dt_values .astype (float )
                elif 'Frequency plot'in option :
                    event_numbers =np .arange (1 ,len (X )+1 ).astype (float )
                    times =X [:,-1 ].astype (float )

                    valid_indices =~np .isnan (times )
                    event_numbers =event_numbers [valid_indices ]
                    times =times [valid_indices ]
                    data [option ][filePath ]=(times ,event_numbers )
                else :
                    x_index ,y_index =(4 ,0 )if 'dI vs dt'in option else (4 ,3 )
                    x_values =X [:,x_index ]*1e3 
                    y_values =X [:,y_index ]

                    valid_indices =~np .isnan (x_values )&~np .isnan (y_values )
                    x_values =x_values [valid_indices ]
                    y_values =y_values [valid_indices ]
                    data [option ][filePath ]=(x_values ,y_values )

        return data 

    def calculateGlobalAxisLimits (self ,plotData ,plotType ):
        min_x =min_y =np .inf 
        max_x =max_y =-np .inf 
        for values in plotData .values ():
            if isinstance (values ,dict ):

                for subvalues in values .values ():
                    if 'Histogram'in plotType :
                        curr_min_x =np .min (subvalues )
                        curr_max_x =np .max (subvalues )

                        if not np .isfinite (curr_min_x )or not np .isfinite (curr_max_x ):
                            continue 
                        if curr_min_x <curr_max_x :
                            min_x =min (min_x ,curr_min_x )
                            max_x =max (max_x ,curr_max_x )
                        else :
                            min_x =min (min_x ,curr_min_x )
                            max_x =max (max_x ,curr_min_x +1e-6 )
                    elif 'Frequency plot'in plotType :
                        x ,y =subvalues 
                        min_x =min (min_x ,np .min (x ))
                        max_x =max (max_x ,np .max (x ))
                        curr_min_y =np .min (y )
                        curr_max_y =np .max (y )
                        if not np .isfinite (curr_min_y )or not np .isfinite (curr_max_y ):
                            continue 
                        min_y =min (min_y ,curr_min_y )
                        max_y =max (max_y ,curr_max_y )
                    else :
                        x ,y =subvalues 
                        min_x =min (min_x ,np .min (x ))
                        max_x =max (max_x ,np .max (x ))
                        curr_min_y =np .min (y )
                        curr_max_y =np .max (y )
                        if not np .isfinite (curr_min_y )or not np .isfinite (curr_max_y ):
                            continue 
                        min_y =min (min_y ,curr_min_y )
                        max_y =max (max_y ,curr_max_y )
            else :
                if 'Histogram'in plotType :
                    curr_min_x =np .min (values )
                    curr_max_x =np .max (values )

                    if not np .isfinite (curr_min_x )or not np .isfinite (curr_max_x ):
                        continue 
                    if curr_min_x <curr_max_x :
                        min_x =min (min_x ,curr_min_x )
                        max_x =max (max_x ,curr_max_x )
                    else :
                        min_x =min (min_x ,curr_min_x )
                        max_x =max (max_x ,curr_min_x +1e-6 )
                elif 'Frequency plot'in plotType :
                    x ,y =values 
                    min_x =min (min_x ,np .min (x ))
                    max_x =max (max_x ,np .max (x ))
                    curr_min_y =np .min (y )
                    curr_max_y =np .max (y )
                    if not np .isfinite (curr_min_y )or not np .isfinite (curr_max_y ):
                        continue 
                    min_y =min (min_y ,curr_min_y )
                    max_y =max (max_y ,curr_max_y )
                else :
                    x ,y =values 
                    min_x =min (min_x ,np .min (x ))
                    max_x =max (max_x ,np .max (x ))
                    curr_min_y =np .min (y )
                    curr_max_y =np .max (y )
                    if not np .isfinite (curr_min_y )or not np .isfinite (curr_max_y ):
                        continue 
                    min_y =min (min_y ,curr_min_y )
                    max_y =max (max_y ,curr_max_y )

        if not np .isfinite (min_x )or not np .isfinite (max_x ):
            min_x ,max_x =0 ,1 
        if not np .isfinite (min_y )or not np .isfinite (max_y ):
            min_y ,max_y =0 ,1 


        self .global_limits [plotType ]=(min_x ,max_x ,min_y ,max_y )

        return min_x ,max_x ,min_y ,max_y 


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

    mainWindow =PlottingApplication ()
    mainWindow .showMaximized ()
    sys .exit (app .exec ())
