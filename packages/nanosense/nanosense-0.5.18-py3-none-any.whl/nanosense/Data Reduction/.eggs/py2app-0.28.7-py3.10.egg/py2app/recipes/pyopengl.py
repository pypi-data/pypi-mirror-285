from __future__ import absolute_import 

import os 


def check (cmd ,mf ):
    m =mf .findNode ("OpenGL")
    if m is None or m .filename is None :
        return None 
    p =os .path .splitext (m .filename )[0 ]+".py"

    if os .path .exists (p ):
        for line in open (p ,"r"):
            if line .startswith ("__version__ = "):
                return {}

    return {"packages":["OpenGL"]}
