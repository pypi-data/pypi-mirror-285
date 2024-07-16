import sys 
from PySide6 import QtWidgets ,QtCore ,QtGui 
from uncertainties import ufloat 
from PySide6 .QtGui import QPalette ,QColor ,QFont 
from PySide6 .QtCore import Qt 

class MainWindow (QtWidgets .QMainWindow ):
    def __init__ (self ,*args ,**kwargs ):
        super (MainWindow ,self ).__init__ (*args ,**kwargs )


        self .setWindowTitle ("SD Nanopore Size Calculator")
        self .setGeometry (400 ,150 ,700 ,400 )


        self .main_widget =QtWidgets .QWidget ()

        self .setCentralWidget (self .main_widget )

        self .layout =QtWidgets .QGridLayout ()
        self .main_widget .setLayout (self .layout )


        self .title =QtWidgets .QLabel ("SD Nanopore Size Calculator\nshankar.dutt@anu.edu.au",self )
        self .title .setAlignment (QtCore .Qt .AlignmentFlag .AlignCenter )
        self .title .setFont (QtGui .QFont ('Arial',20 ))



        self .fields =["Conductance (nS)","Conductivity (S/m)","Pore Length (nm)"]
        self .inputs ={}
        for i ,field in enumerate (self .fields ):
            self .inputs [field ]=[QtWidgets .QLineEdit (),QtWidgets .QLineEdit ()]
            self .inputs [field ][0 ].setMinimumHeight (30 )
            self .inputs [field ][0 ].setFont (QtGui .QFont ('Arial',14 ))
            self .inputs [field ][1 ].setMinimumHeight (30 )
            self .inputs [field ][1 ].setFont (QtGui .QFont ('Arial',14 ))

            label =QtWidgets .QLabel (field )

            plus_minus =QtWidgets .QLabel ("±")


            self .layout .addWidget (label ,i +1 ,0 )
            self .layout .addWidget (self .inputs [field ][0 ],i +1 ,1 )
            self .layout .addWidget (plus_minus ,i +1 ,2 )
            self .layout .addWidget (self .inputs [field ][1 ],i +1 ,3 )


        self .calculate_button =QtWidgets .QPushButton ("Calculate")

        self .calculate_button .setFixedSize (200 ,50 )
        self .calculate_button .clicked .connect (self .calculate )


        self .result_label =QtWidgets .QLabel ("Diameter (nm): ")
        self .result =QtWidgets .QLabel ()




        self .layout .addWidget (self .title ,0 ,0 ,1 ,4 )
        self .layout .addWidget (self .calculate_button ,5 ,0 ,1 ,4 ,alignment =QtCore .Qt .AlignmentFlag .AlignCenter )
        self .layout .addWidget (self .result_label ,6 ,0 ,1 ,2 )
        self .layout .addWidget (self .result ,6 ,2 ,1 ,2 )

    def calculate (self ):
        from math import pi 

        try :
            G =ufloat (float (self .inputs ["Conductance (nS)"][0 ].text ()),float (self .inputs ["Conductance (nS)"][1 ].text ()))
            S =ufloat (float (self .inputs ["Conductivity (S/m)"][0 ].text ()),float (self .inputs ["Conductivity (S/m)"][1 ].text ()))
            L =ufloat (float (self .inputs ["Pore Length (nm)"][0 ].text ()),float (self .inputs ["Pore Length (nm)"][1 ].text ()))

            D =G /(2 *S )*(1 +(1 +16 *S *L /pi /G )**0.5 )
            self .result .setText (str (D ))

        except ValueError :
            error_dialog =QtWidgets .QMessageBox ()
            error_dialog .setIcon (QtWidgets .QMessageBox .Icon .Critical )
            error_dialog .setWindowTitle ("Input Error")
            error_dialog .setText ("Invalid input, please check your values.")
            error_dialog .exec ()

def main ():
    app =QtWidgets .QApplication (sys .argv )
    app .setStyle (QtWidgets .QStyleFactory .create ('Fusion'))


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
    main_window =MainWindow ()
    main_window .show ()

    sys .exit (app .exec ())

if __name__ =="__main__":
    main ()
