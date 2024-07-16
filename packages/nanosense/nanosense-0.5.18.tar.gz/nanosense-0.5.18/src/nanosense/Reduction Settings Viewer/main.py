import sys 
import os 
from PySide6 .QtWidgets import QApplication ,QWidget ,QLabel ,QPushButton ,QCheckBox ,QComboBox ,QListWidget ,QVBoxLayout ,QHBoxLayout ,QFileDialog ,QMessageBox ,QStyleFactory ,QInputDialog ,QDialog ,QTextEdit 
from PySide6 .QtCore import Qt 
from PySide6 .QtGui import QPalette ,QColor ,QFont 
import numpy as np 
import json 

class SDSettingsViewer (QWidget ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("SD Reduced File : Settings Viewer")
        self .resize (800 ,600 )


        self .app_name_label =QLabel ("SD Reduced File : Settings Viewer")
        self .app_name_label .setAlignment (Qt .AlignCenter )
        self .app_name_label .setFont (QFont ("Arial",16 ,QFont .Bold ))
        self .email_label =QLabel ("shankar.dutt@anu.edu.au")
        self .email_label .setAlignment (Qt .AlignCenter )
        self .select_folder_button =QPushButton ("Select Folder")
        self .include_subfolders_checkbox =QCheckBox ("Include Subfolders")
        self .extension_dropdown =QComboBox ()
        self .extension_dropdown .addItems ([".dataset.npz",".MLdataset.npz"])
        self .file_list =QListWidget ()
        self .folder_path_label =QLabel ()
        self .folder_path_label .setWordWrap (True )
        self .settings_text_edit =QTextEdit ()
        self .settings_text_edit .setReadOnly (True )


        main_layout =QHBoxLayout ()
        left_layout =QVBoxLayout ()
        left_layout .addWidget (self .app_name_label )
        left_layout .addWidget (self .email_label )
        left_layout .addWidget (self .select_folder_button )
        left_layout .addWidget (self .include_subfolders_checkbox )
        left_layout .addWidget (self .extension_dropdown )
        left_layout .addWidget (self .file_list )
        left_layout .addWidget (self .folder_path_label )
        main_layout .addLayout (left_layout )
        main_layout .addWidget (self .settings_text_edit )

        self .setLayout (main_layout )


        self .select_folder_button .clicked .connect (self .select_folder )
        self .file_list .currentItemChanged .connect (self .display_settings )

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
                            file_path =os .path .join (root ,file )
                            self .file_list .addItem (file_path )
            else :
                for file in os .listdir (folder_path ):
                    if file .endswith (extension ):
                        file_path =os .path .join (folder_path ,file )
                        self .file_list .addItem (file_path )

    def display_settings (self ,current ,previous ):
        if current :
            file_path =current .text ()
            try :
                data =np .load (file_path )
                settings =data ['settings']
                settings_str =settings .item ()
                settings_dict =json .loads (settings_str )
                settings_text =json .dumps (settings_dict ,indent =4 )
                self .settings_text_edit .setPlainText (settings_text )
            except Exception as e :
                QMessageBox .warning (self ,"Error",f"Failed to load settings:\n{str(e)}")
        else :
            self .settings_text_edit .clear ()

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

    window =SDSettingsViewer ()
    window .show ()
    sys .exit (app .exec ())