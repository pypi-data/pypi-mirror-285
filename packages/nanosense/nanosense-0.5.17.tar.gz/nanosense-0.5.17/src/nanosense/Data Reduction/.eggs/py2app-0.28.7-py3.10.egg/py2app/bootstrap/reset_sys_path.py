def _reset_sys_path ():

    import os 
    import sys 

    resources =os .environ ["RESOURCEPATH"]
    while sys .path [0 ]==resources :
        del sys .path [0 ]


_reset_sys_path ()
