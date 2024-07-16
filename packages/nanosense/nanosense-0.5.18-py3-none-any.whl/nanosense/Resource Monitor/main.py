import os 


os .environ ['QT_LOGGING_RULES']='qt.pointer.dispatch=false'

import sys 
import platform 
import psutil 
from PySide6 .QtWidgets import QApplication ,QMainWindow ,QWidget ,QGridLayout ,QLabel ,QComboBox ,QHBoxLayout ,QSplitter ,QStyleFactory 
from PySide6 .QtCore import QTimer ,Qt 
from PySide6 .QtGui import QPalette ,QColor ,QFont 
import pyqtgraph as pg 

class ResourceMonitor (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("SD Resource Monitor")
        self .setGeometry (100 ,100 ,800 ,600 )

        central_widget =QWidget (self )
        self .setCentralWidget (central_widget )

        layout =QGridLayout (central_widget )

        splitter_main =QSplitter (Qt .Vertical )
        splitter_top =QSplitter (Qt .Horizontal )
        splitter_bottom =QSplitter (Qt .Horizontal )

        self .cpu_plot =pg .PlotWidget ()
        self .cpu_plot .setTitle ("CPU Usage")
        self .cpu_plot .setLabel ("left","Usage (%)")
        self .cpu_plot .setLabel ("bottom","Time")
        self .cpu_plot .addLegend ()
        splitter_top .addWidget (self .cpu_plot )

        self .cpu_cores_widget =QWidget ()
        self .cpu_cores_layout =QGridLayout (self .cpu_cores_widget )
        self .cpu_cores_layout .setSpacing (1 )
        self .cpu_cores_layout .setContentsMargins (1 ,1 ,1 ,1 )
        self .cpu_cores_plots =[]
        self .cpu_cores_legends =[]
        for i in range (psutil .cpu_count ()):
            plot =pg .PlotWidget ()
            plot .setLabel ("left","Usage (%)")
            plot .setLabel ("bottom","Time")
            self .cpu_cores_layout .addWidget (plot ,i //2 ,i %2 )
            self .cpu_cores_plots .append (plot )

            legend =pg .LegendItem ((0 ,0 ),offset =(0 ,0 ))
            legend .setParentItem (plot .graphicsItem ())
            self .cpu_cores_legends .append (legend )
        splitter_top .addWidget (self .cpu_cores_widget )

        self .ram_plot =pg .PlotWidget ()
        self .ram_plot .setTitle ("RAM Usage")
        self .ram_plot .setLabel ("left","Usage (%)")
        self .ram_plot .setLabel ("bottom","Time")
        self .ram_plot .addLegend ()
        splitter_bottom .addWidget (self .ram_plot )

        self .gpu_plot =pg .PlotWidget ()
        self .gpu_plot .setTitle ("GPU Usage")
        self .gpu_plot .setLabel ("left","Usage (%)")
        self .gpu_plot .setLabel ("bottom","Time")
        self .gpu_plot .addLegend ()
        splitter_bottom .addWidget (self .gpu_plot )

        splitter_main .addWidget (splitter_top )
        splitter_main .addWidget (splitter_bottom )

        splitter_main .setSizes ([400 ,220 ])
        splitter_top .setSizes ([180 ,400 ])
        splitter_bottom .setSizes ([400 ,400 ])

        layout .addWidget (splitter_main ,0 ,0 )

        info_layout =QHBoxLayout ()
        self .os_label =QLabel (f"Operating System: {platform.system()}")
        info_layout .addWidget (self .os_label )

        self .update_interval_combo =QComboBox ()
        self .update_interval_combo .addItems (["0.1 second","0.5 second","1 second","2 seconds","5 seconds"])
        self .update_interval_combo .setCurrentIndex (1 )
        self .update_interval_combo .currentIndexChanged .connect (self .change_update_interval )
        info_layout .addWidget (QLabel ("Update Interval:"))
        info_layout .addWidget (self .update_interval_combo )

        self .data_duration_combo =QComboBox ()
        self .data_duration_combo .addItems (["10 seconds","30 seconds","1 minute","2 minutes","5 minutes"])
        self .data_duration_combo .setCurrentIndex (2 )
        self .data_duration_combo .currentIndexChanged .connect (self .change_data_duration )
        info_layout .addWidget (QLabel ("Data Duration:"))
        info_layout .addWidget (self .data_duration_combo )

        self .status_label =QLabel ()
        info_layout .addWidget (self .status_label )

        layout .addLayout (info_layout ,1 ,0 )

        self .update_timer =QTimer ()
        self .update_timer .timeout .connect (self .update_data )
        self .update_timer .start (1000 )

        self .cpu_data =[]
        self .cpu_cores_data =[[]for _ in range (psutil .cpu_count ())]
        self .ram_data =[]
        self .gpu_data =[]

        self .data_duration =60 
        self .time_data =[]

        self .gpu_monitoring_available =False 
        self .initialize_gpu_monitoring ()

    def initialize_gpu_monitoring (self ):
        if platform .system ()=="Windows":
            try :
                import pynvml 
                pynvml .nvmlInit ()
                self .gpu_monitoring_available =True 
            except (ModuleNotFoundError ,pynvml .NVMLError ):
                self .status_label .setText ("GPU monitoring not available")
        elif platform .system ()=="Darwin":
            try :
                from Metal import MTLCreateSystemDefaultDevice 
                self .gpu_device =MTLCreateSystemDefaultDevice ()
                self .gpu_monitoring_available =True 
            except ImportError :
                self .status_label .setText ("GPU monitoring not available")
        elif platform .system ()=="Linux":
            self .gpu_monitoring_available =True 

    def change_update_interval (self ,index ):
        intervals =[100 ,500 ,1000 ,2000 ,5000 ]
        self .update_timer .setInterval (intervals [index ])
        self .clear_data ()
        self .clear_plots ()

    def clear_data (self ):
        self .cpu_data .clear ()
        for data in self .cpu_cores_data :
            data .clear ()
        self .ram_data .clear ()
        self .gpu_data .clear ()
        self .time_data .clear ()

    def clear_plots (self ):
        self .cpu_plot .clear ()
        for plot in self .cpu_cores_plots :
            plot .clear ()
        self .ram_plot .clear ()
        self .gpu_plot .clear ()

    def change_data_duration (self ,index ):
        durations =[10 ,30 ,60 ,120 ,300 ]
        self .data_duration =durations [index ]
        self .clear_data ()
        self .clear_plots ()

    def update_data (self ):
        cpu_percent =psutil .cpu_percent ()
        cpu_cores_percent =psutil .cpu_percent (percpu =True )
        ram_percent =psutil .virtual_memory ().percent 
        ram_used =psutil .virtual_memory ().used /(1024 **3 )


        try :
            cpu_freq =psutil .cpu_freq ().current 
        except FileNotFoundError :
            cpu_freq =None 

        self .cpu_data .append (cpu_percent )
        for i ,percent in enumerate (cpu_cores_percent ):
            self .cpu_cores_data [i ].append (percent )
        self .ram_data .append ((ram_percent ,ram_used ))

        if self .gpu_monitoring_available :
            if platform .system ()=="Windows":
                import pynvml 
                handle =pynvml .nvmlDeviceGetHandleByIndex (0 )
                gpu_util =pynvml .nvmlDeviceGetUtilizationRates (handle ).gpu 
                self .gpu_data .append (gpu_util )
            elif platform .system ()=="Darwin":
                utilization =self .gpu_device .utilization ()
                self .gpu_data .append (utilization )
            elif platform .system ()=="Linux":
                gpu_util =self .get_gpu_usage_linux ()
                if gpu_util is not None :
                    self .gpu_data .append (gpu_util )

        elapsed_time =len (self .time_data )*self .update_timer .interval ()/1000 
        self .time_data .append (elapsed_time )

        num_data_points =self .data_duration *1000 //self .update_timer .interval ()

        if len (self .time_data )>num_data_points :
            self .cpu_data =self .cpu_data [-num_data_points :]
            for i in range (len (self .cpu_cores_data )):
                self .cpu_cores_data [i ]=self .cpu_cores_data [i ][-num_data_points :]
            self .ram_data =self .ram_data [-num_data_points :]
            self .gpu_data =self .gpu_data [-num_data_points :]
            self .time_data =self .time_data [-num_data_points :]
            self .time_data =[t -self .time_data [0 ]for t in self .time_data ]

        self .update_plots (cpu_freq )

    def get_gpu_usage_linux (self ):
        try :
            import subprocess 
            output =subprocess .check_output (["nvidia-smi","--query-gpu=utilization.gpu","--format=csv,noheader,nounits"])
            gpu_utils =output .decode ().strip ().split ('\n')
            gpu_util =float (gpu_utils [0 ])
            return gpu_util 
        except (subprocess .CalledProcessError ,FileNotFoundError ,IndexError ,ValueError ):
            return None 

    def update_plots (self ,cpu_freq ):
        x_min =self .time_data [0 ]
        x_max =self .time_data [-1 ]

        self .cpu_plot .clear ()
        self .cpu_plot .plot (self .time_data ,self .cpu_data ,pen =pg .mkPen (color =(255 ,0 ,0 )),name ="CPU Usage")
        if cpu_freq is not None :
            self .cpu_plot .setLabel ("bottom",f"Current Clock Speed: {cpu_freq:.2f} MHz")
        else :
            self .cpu_plot .setLabel ("bottom","CPU Clock Speed: Not Available")
        self .cpu_plot .setXRange (x_min ,x_max ,padding =0 )

        colors =[(255 ,0 ,0 ),(0 ,255 ,0 ),(0 ,0 ,255 ),(255 ,255 ,0 ),(0 ,255 ,255 ),(255 ,0 ,255 ),(128 ,128 ,128 ),(128 ,0 ,0 )]
        for i ,plot in enumerate (self .cpu_cores_plots ):
            color =colors [i %len (colors )]
            plot .clear ()
            curve =plot .plot (self .time_data ,self .cpu_cores_data [i ],pen =pg .mkPen (color =color ),name =f"Core {i+1}")
            self .cpu_cores_legends [i ].clear ()
            self .cpu_cores_legends [i ].addItem (curve ,f"Core {i+1}")
            plot .setXRange (x_min ,x_max ,padding =0 )
            plot .enableAutoRange (axis ='y',enable =True )

        self .ram_plot .clear ()
        ram_percent_data ,ram_used_data =zip (*self .ram_data )
        self .ram_plot .plot (self .time_data ,ram_percent_data ,pen =pg .mkPen (color =(255 ,0 ,0 )),name ="Usage (%)")
        self .ram_plot .setLabel ("bottom",f"RAM Usage: {ram_used_data[-1]:.2f} GB")
        self .ram_plot .setXRange (x_min ,x_max ,padding =0 )

        self .gpu_plot .clear ()
        self .gpu_plot .plot (self .time_data ,self .gpu_data ,pen =pg .mkPen (color =(0 ,255 ,0 )),name ="GPU Usage")
        self .gpu_plot .setXRange (x_min ,x_max ,padding =0 )

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
    resource_monitor =ResourceMonitor ()
    resource_monitor .showMaximized ()
    sys .exit (app .exec ())