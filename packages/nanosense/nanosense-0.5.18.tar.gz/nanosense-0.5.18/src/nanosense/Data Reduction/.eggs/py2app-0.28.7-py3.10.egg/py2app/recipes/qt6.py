import os 

from modulegraph .modulegraph import MissingModule 


def check (cmd ,mf ):
    m =mf .findNode ("PyQt6")
    if m and not isinstance (m ,MissingModule ):
        try :


            import sipconfig 

            return None 

        except ImportError :
            pass 

        try :
            import PyQt6 
            from PyQt6 .QtCore import QLibraryInfo 
        except ImportError :


            return None 

        qtdir =QLibraryInfo .path (QLibraryInfo .LibraryPath .LibrariesPath )
        if os .path .relpath (qtdir ,os .path .dirname (PyQt6 .__file__ )).startswith ("../"):




            print ("System install of Qt6")



            extra ={
            "resources":[
            ("..",[QLibraryInfo .path (QLibraryInfo .LibraryPath .PluginsPath )])
            ]
            }

        else :
            extra ={}






        try :
            mf .import_hook ("sip",m )
        except ImportError :
            mf .import_hook ("sip",m ,level =1 )

        result ={"packages":["PyQt6"]}
        result .update (extra )
        return result 

    return None 
