def _argv_inject (argv ):
    import sys 


    if len (sys .argv )>1 and sys .argv [1 ].startswith ("-psn"):
        sys .argv [1 :2 ]=argv 
    else :
        sys .argv [1 :1 ]=argv 
