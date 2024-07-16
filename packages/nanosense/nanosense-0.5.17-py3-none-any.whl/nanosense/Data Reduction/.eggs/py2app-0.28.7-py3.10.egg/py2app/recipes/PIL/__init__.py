import os 
import sys 

from modulegraph .util import imp_find_module 

try :
    from cStringIO import StringIO 
except ImportError :
    from io import StringIO 

try :
    set 
except NameError :
    from sets import Set as set 

try :
    basestring 
except NameError :
    basestring =str 


def check (cmd ,mf ):
    m =mf .findNode ("Image")or mf .findNode ("PIL.Image")
    if m is None or m .filename is None :
        return None 

    have_PIL =bool (mf .findNode ("PIL.Image"))

    plugins =set ()
    visited =set ()



    for folder in sys .path :
        if not isinstance (folder ,basestring ):
            continue 

        for extra in ("","PIL"):
            folder =os .path .realpath (os .path .join (folder ,extra ))
            if (not os .path .isdir (folder ))or (folder in visited ):
                continue 
            for fn in os .listdir (folder ):
                if not fn .endswith ("ImagePlugin.py"):
                    continue 

                mod ,ext =os .path .splitext (fn )
                try :
                    sys .path .insert (0 ,folder )
                    imp_find_module (mod )
                    del sys .path [0 ]
                except ImportError :
                    pass 
                else :
                    plugins .add (mod )
        visited .add (folder )
    s =StringIO ("_recipes_pil_prescript(%r)\n"%list (plugins ))
    print (plugins )
    plugins =set ()

    for plugin in plugins :
        if have_PIL :
            mf .implyNodeReference (m ,"PIL."+plugin )
        else :
            mf .implyNodeReference (m ,plugin )

    mf .removeReference (m ,"FixTk")


    sip =mf .findNode ("SpiderImagePlugin")
    if sip is not None :
        mf .removeReference (sip ,"ImageTk")





    sip =mf .findNode ("PIL.ImageQt")
    if sip is not None :
        mf .removeReference (sip ,"PyQt5")
        mf .removeReference (sip ,"PyQt5.QtGui")
        mf .removeReference (sip ,"PyQt5.QtCore")

        mf .removeReference (sip ,"PyQt4")
        mf .removeReference (sip ,"PyQt4.QtGui")
        mf .removeReference (sip ,"PyQt4.QtCore")
        pass 

    imagefilter =mf .findNode ("PIL.ImageFilter")
    if imagefilter is not None :




        mf .removeReference (imagefilter ,"numpy")

    image =mf .findNode ("PIL.Image")
    if image is not None :


        mf .removeReference (image ,"numpy")

    return {
    "prescripts":["py2app.recipes.PIL.prescript",s ],
    "include":"PIL.JpegPresets",
    "flatpackages":[os .path .dirname (m .filename )],
    }
