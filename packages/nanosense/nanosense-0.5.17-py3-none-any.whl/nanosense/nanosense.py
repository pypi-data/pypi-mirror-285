import sys ,os 
import math 
import subprocess 
from PySide6 .QtWidgets import QApplication ,QMainWindow ,QPushButton ,QLabel ,QWidget ,QMessageBox ,QDialog ,QVBoxLayout ,QMenuBar ,QMenu ,QInputDialog 
from PySide6 .QtGui import QPixmap ,QIcon ,QAction ,QPalette 
from PySide6 .QtCore import Qt ,QSize ,QDateTime ,QSettings 
from cryptography .fernet import Fernet 
import requests 
import dateutil .parser 

DEVELOPMENT_MODE = False

def verify_activation_code (activation_code ):
    url ="https://1fmjoam3kk.execute-api.ap-southeast-2.amazonaws.com/default/check-authentication"
    data ={"activation_code":activation_code }
    headers ={"Content-Type":"application/json"}

    try :
        response =requests .post (url ,json =data ,headers =headers )
        if response .status_code ==200 :
            response_data =response .json ()
            is_valid =response_data .get ("is_valid",False )
            is_indefinite =response_data .get ("is_indefinite",False )
            expiration_date_str =response_data .get ("expiration_date")

            if expiration_date_str :
                try :
                    expiration_datetime =dateutil .parser .parse (expiration_date_str )
                    expiration_date =QDateTime (
                    expiration_datetime .year ,
                    expiration_datetime .month ,
                    expiration_datetime .day ,
                    expiration_datetime .hour ,
                    expiration_datetime .minute ,
                    expiration_datetime .second ,
                    expiration_datetime .microsecond //1000 ,
                    Qt .LocalTime 
                    )
                except ValueError :
                    print (f"Error: Invalid expiration date format '{expiration_date_str}'")

                    expiration_date =None 
            else :
                expiration_date =QDateTime .currentDateTime ().addYears (100 )
                is_indefinite =False 


            return is_valid ,is_indefinite ,expiration_date 
        else :
            print (f"Error: {response.status_code} - {response.text}")
            return False ,False ,None 
    except requests .exceptions .RequestException as e :
        print (f"Error: {str(e)}")
        return False ,False ,None 

def get_application_path ():
    """Get the directory where the application is running."""
    if getattr (sys ,'frozen',False ):

        application_path =os .path .dirname (sys .executable )
    else :

        application_path =os .path .dirname (os .path .abspath (__file__ ))
    return application_path 

class NanoSenseApp (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ('NanoSense - A Suite of Nanopore Data Analysis Tools')
        self .setGeometry (100 ,100 ,700 ,850 )
        self .central_widget =QWidget (self )
        self .setCentralWidget (self .central_widget )


        self .setStyleSheet ("background-color: #a7c1cf;")


        nanoSense_html =('<p style="font-size: 35px; color: #154360; margin-top: 0; margin-bottom: 0;">NanoSense</p>'
        '<p style="font-size: 15px; margin: 2px; color: #154360;">A Suite of Nanopore Data Analysis Tools</p>')
        self .title_label =QLabel (nanoSense_html ,self .central_widget )
        self .title_label .setAlignment (Qt .AlignmentFlag .AlignCenter )


        self .image_label =QLabel (self .central_widget )

        application_path =get_application_path ()


        image_path =os .path .join (application_path ,'image_1.jpg')


        pixmap =QPixmap (image_path )
        self .image_label .setPixmap (pixmap .scaled (400 ,400 ,Qt .AspectRatioMode .KeepAspectRatio ))
        self .image_label .setAlignment (Qt .AlignmentFlag .AlignCenter )


        self .button_radius =240 
        self .button_size =QSize (210 ,60 )
        self .button_names =['Data Visualisation','Frequency and multi-plots','Event Analysis','Combine Datasets and Files','Clustering and Data Reduction','ML Analysis','Spectrogram and PSD','Nanopore Size Calc','Resource Monitor', 'Reduction Settings Viewer' , 'Plotting and selecting','Data Reduction']

        self .buttons =[]


        self .create_circular_buttons ()


        info_html =(
        '<p style="font-size: 18px; margin: 2px; color: #1F618D;">Shankar Dutt</p>'
        '<p style="font-size: 15px; margin: 2px; color: #1F618D;">shankar.dutt@anu.edu.au</p>'
        )
        self .info_label =QLabel (info_html ,self .central_widget )
        self .info_label .setAlignment (Qt .AlignmentFlag .AlignCenter )


        self .resize_widgets ()


        menubar =QMenuBar ()


        options_menu =QMenu ("Options",self )
        for button_name in self .button_names :
            if button_name !="Help":
                action =QAction (button_name ,self )
                action .triggered .connect (lambda _ ,app_name =button_name :self .start_application (app_name ))
                options_menu .addAction (action )
        menubar .addMenu (options_menu )




        help_menu =QMenu ("Help",self )
        help_action =QAction ("Help",self )
        help_action .triggered .connect (self .show_help_dialog )
        help_menu .addAction (help_action )
        menubar .addMenu (help_menu )


        activation_menu =QMenu ("Activation Status",self )
        activation_action =QAction ("Check Activation Status",self )
        activation_action .triggered .connect (self .show_activation_status )
        activation_menu .addAction (activation_action )

        if DEVELOPMENT_MODE :

            reset_activation_action =QAction ("Reset Activation",self )
            reset_activation_action .triggered .connect (self .reset_activation_status )
            activation_menu .addAction (reset_activation_action )

        menubar .addMenu (activation_menu )

        self .setMenuBar (menubar )


        # Set the appropriate icon based on the OS
        try:
            if sys.platform == "darwin":
                icon_path = os.path.join(application_path, "icons.icns")
            elif sys.platform == "win32":
                icon_path = os.path.join(application_path, "icons.ico")
            else:  # Assume Linux or other
                icon_path = os.path.join(application_path, "icons.png")
            self.setWindowIcon(QIcon(icon_path))
        except:
            pass

        self .check_activation_status ()


    def create_circular_buttons (self ):
        button_style ="""
            QPushButton {
                color: white;
                background-color: #3b3b6d;
                border-radius: 30px;
                font: bold 12px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #505090;
            }
        """
        for i ,name in enumerate (self .button_names ):
            button =QPushButton (name ,self .central_widget )
            button .setStyleSheet (button_style )
            button .setFixedSize (self .button_size )
            self .buttons .append (button )

            if name !="Help":
                button .clicked .connect (lambda _ ,app_name =name :self .start_application (app_name ))
            else :
                button .clicked .connect (self .show_help_dialog )

    def resize_widgets (self ):

        self .title_label .setGeometry (
        10 ,
        5 ,
        self .width ()-20 ,
        80 
        )


        image_size =self .image_label .pixmap ().size ()
        self .image_label .setGeometry (
        (self .width ()-image_size .width ())//2 ,
        (self .height ()-image_size .height ())//2 ,
        image_size .width (),
        image_size .height ()
        )

        self .button_angles =[0 ,-27 ,-60 ,-90 ,-120 ,-153 ,-36 *5 ,-207 ,-240 ,-270 ,-300 ,-333 ]


        assert len (self .button_angles )==len (self .buttons ),"The number of angles must match the number of buttons."

        self .button_radii =[self .button_radius ]*len (self .buttons )
        self .button_radii [3 ]=self .button_radius +50 
        self .button_radii [9 ]=self .button_radius +40 

        center_x =self .width ()/2 
        center_y =self .height ()/2 -25 

        for i ,button in enumerate (self .buttons ):
            angle_degrees =self .button_angles [i ]
            angle_radians =math .radians (angle_degrees )

            button_radius =self .button_radii [i ]

            x =center_x +math .cos (angle_radians )*button_radius -self .button_size .width ()/2 
            y =center_y -math .sin (angle_radians )*button_radius -self .button_size .height ()/2 

            button .setGeometry (int (x ),int (y ),self .button_size .width (),self .button_size .height ())


        self .info_label .setGeometry (
        5 ,
        self .height ()-100 ,
        self .width ()-10 ,
        70 
        )

    def start_application (self ,app_name ):
        if self .is_activated ():
            app_path =os .path .join (get_application_path (),app_name ,"main.py")
            subprocess .Popen (["python",app_path ])
        else :
            QMessageBox .warning (self ,"Activation Required","Please enter a valid activation code to use this feature.")

    def show_help_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Help")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
        """)
        layout = QVBoxLayout(dialog)

        image_label = QLabel(dialog)
        pixmap = QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_1.jpg"))
        image_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(image_label)

        help_text = QLabel(
            "For Help, please contact Shankar Dutt (shankar.dutt@anu.edu.au)\n"
            "Version: 0.5.17\n"
            "Release Date: 16/07/2024\n"
            "Author: Shankar Dutt\n"
            "Author Email: shankar.dutt@anu.edu.au",
            dialog
        )
        help_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(help_text)

        dialog.exec()


    def resizeEvent (self ,event ):
        self .resize_widgets ()

        super ().resizeEvent (event )

    def check_activation_status (self ):
        settings =QSettings ("NanoSense","ActivationStatus")
        activation_code =settings .value ("activation_code")
        expiration_date =settings .value ("expiration_date")
        is_indefinite =settings .value ("is_indefinite",False )

        if activation_code and expiration_date :
            if is_indefinite or QDateTime .currentDateTime ()<QDateTime .fromString (expiration_date ,Qt .ISODate ):
                return 


        self .prompt_activation_code ()

    def prompt_activation_code (self ):
        while True :
            activation_code ,ok =QInputDialog .getText (self ,"Activation","Please enter your activation code.\n\nIf you do not have an activation code, please contact Shankar Dutt (shankar.dutt@anu.edu.au)")
            if not ok :
                sys .exit ()

            is_valid ,is_indefinite ,expiration_date =verify_activation_code (activation_code )


            if is_valid :

                settings =QSettings ("NanoSense","ActivationStatus")
                settings .setValue ("activation_code",activation_code )
                if is_indefinite :
                    settings .setValue ("expiration_date",None )
                    settings .setValue ("is_indefinite",True )
                else :
                    settings .setValue ("expiration_date",expiration_date .toString (Qt .ISODate ))
                    settings .setValue ("is_indefinite",False )
                break 
            else :
                QMessageBox .warning (self ,"Invalid Code","The entered activation code is invalid. Please try again.")
    def is_activated (self ):
        settings =QSettings ("NanoSense","ActivationStatus")
        activation_code =settings .value ("activation_code")
        expiration_date =settings .value ("expiration_date")

        if activation_code and expiration_date :
            expiration_date =QDateTime .fromString (expiration_date ,Qt .ISODate )
            current_time =QDateTime .currentDateTime ()

            if current_time <expiration_date :
                return True 

        return False 

    def reset_activation_status (self ):
        settings =QSettings ("NanoSense","ActivationStatus")
        settings .remove ("activation_code")
        settings .remove ("activation_time")
        QMessageBox .information (self ,"Reset Activation","Activation status has been reset.")

    def show_activation_status (self ):
        settings =QSettings ("NanoSense","ActivationStatus")
        activation_code =settings .value ("activation_code")
        expiration_date =settings .value ("expiration_date")

        if activation_code and expiration_date :
            expiration_date =QDateTime .fromString (expiration_date ,Qt .ISODate )
            current_time =QDateTime .currentDateTime ()

            if current_time <expiration_date :
                days_remaining =current_time .daysTo (expiration_date )
                if expiration_date .date ()==QDateTime .currentDateTime ().addYears (100 ).date ():
                    QMessageBox .information (self ,"Activation Status","The software is activated for lifetime.")
                else :
                    QMessageBox .information (self ,"Activation Status",f"The software is activated. Days remaining: {days_remaining}")
                return 

        QMessageBox .information (self ,"Activation Status","The software is not currently activated.")

def main ():
    app =QApplication (sys .argv )


    app .setStyle ("Fusion")


    palette =app .palette ()
    palette .setColor (QPalette .Window ,Qt .white )
    palette .setColor (QPalette .WindowText ,Qt .black )
    palette .setColor (QPalette .Base ,Qt .white )
    palette .setColor (QPalette .AlternateBase ,Qt .lightGray )
    palette .setColor (QPalette .ToolTipBase ,Qt .white )
    palette .setColor (QPalette .ToolTipText ,Qt .black )
    palette .setColor (QPalette .Text ,Qt .black )
    palette .setColor (QPalette .Button ,Qt .lightGray )
    palette .setColor (QPalette .ButtonText ,Qt .black )
    palette .setColor (QPalette .BrightText ,Qt .red )
    palette .setColor (QPalette .Link ,Qt .blue )
    palette .setColor (QPalette .Highlight ,Qt .darkBlue )
    palette .setColor (QPalette .HighlightedText ,Qt .white )
    app .setPalette (palette )

    window =NanoSenseApp ()
    window .show ()
    sys .exit (app .exec ())

if __name__ =="__main__":
    main ()