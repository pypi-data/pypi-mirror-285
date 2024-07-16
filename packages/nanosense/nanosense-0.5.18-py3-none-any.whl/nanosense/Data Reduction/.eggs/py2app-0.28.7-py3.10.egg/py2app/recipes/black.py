import os 
import ast 
import sys 

from pkg_resources import get_distribution 




def check (cmd ,mf ):
    m =mf .findNode ("black")
    if m is None or m .filename is None :
        return None 

    egg =get_distribution ("black").egg_info 
    top =os .path .join (egg ,"RECORD")


    packages =["black","blib2to3"]







    includes =set ()
    with open (top ,"r")as f :
        for line in f :
            fname =line .split (",",1 )[0 ]
            toplevel =fname .split ("/",1 )[0 ]
            if all (ch not in toplevel for ch in ('.','-')):
                includes .add (toplevel )


            if fname .endswith (".py"):
                toplevel_node =mf .findNode (toplevel )
                if toplevel_node is None :
                    continue 






                fqname =fname [:-3 ].replace ("/",".")
                source_path =os .path .join (os .path .dirname (egg ),fname )
                with open (source_path ,"rb")as fp :
                    update_dependencies_from_source (mf ,fqname ,fp ,source_path ,toplevel_node )


    includes =list (includes .difference (packages ))

    return {"includes":includes ,"packages":packages }


def update_dependencies_from_source (mf ,fqname ,fp ,pathname ,toplevel ):


    m =mf .findNode (fqname )
    if m is None :
        m =mf .import_hook (fqname ,toplevel )[0 ]

    contents =fp .read ()
    if isinstance (contents ,bytes ):
        contents +=b"\n"
    else :
        contents +="\n"

    try :
        co =compile (contents ,pathname ,"exec",ast .PyCF_ONLY_AST ,True )
        if sys .version_info [:2 ]==(3 ,5 ):


            compile (co ,"-","exec",0 ,True )
    except SyntaxError :
        return 

    mf ._scan_code (co ,m )
