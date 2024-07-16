import sys 


def check (cmd ,mf ):
    if sys .version_info [:2 ]>=(3 ,6 ):



        m =mf .findNode ("sysconfig")
        if m is not None :
            import sysconfig 

            mf .import_hook (sysconfig ._get_sysconfigdata_name (),m )

    else :
        return None 
