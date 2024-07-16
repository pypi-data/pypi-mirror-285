import sys 

from modulegraph .modulegraph import MissingModule 


def check (cmd ,mf ):
    if sys .version_info [0 ]!=2 :
        return {}



    m =mf .findNode ("_xmlplus")
    if m is not None and isinstance (m ,MissingModule ):
        mf .removeReference (mf .findNode ("xml"),m )

    return {}
