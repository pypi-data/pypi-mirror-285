import os 
import sys 

from modulegraph .modulegraph import MissingModule 


def check (cmd ,mf ):
    m =mf .findNode ("PyQt5")
    if m and not isinstance (m ,MissingModule ):
        try :


            import sipconfig 

            return None 

        except ImportError :
            pass 

        try :
            import PyQt5 
            from PyQt5 .QtCore import QLibraryInfo 
        except ImportError :

            return None 






        try :
            mf .import_hook ("PyQt5.sip",m )
        except ImportError :
            mf .import_hook ("sip",m ,level =1 )

        qtdir =QLibraryInfo .location (QLibraryInfo .LibrariesPath )
        if os .path .relpath (qtdir ,os .path .dirname (PyQt5 .__file__ )).startswith ("../"):




            print ("System install of Qt5")



            extra ={
            "resources":[("..",[QLibraryInfo .location (QLibraryInfo .PluginsPath )])]
            }

        else :
            extra ={}

        if sys .version [0 ]!=2 :
            result ={
            "packages":["PyQt5"],
            "expected_missing_imports":{"copy_reg","cStringIO","StringIO"},
            }
            result .update (extra )
            return result 
        else :
            result ={"packages":["PyQt5"]}
            result .update (extra )
            return result 

    return None 
