def _site_packages ():
    import os 
    import site 
    import sys 

    paths =[]
    prefixes =[sys .prefix ]
    if sys .exec_prefix !=sys .prefix :
        prefixes .append (sys .exec_prefix )
    for prefix in prefixes :
        paths .append (
        os .path .join (
        prefix ,"lib","python%d.%d"%(sys .version_info [:2 ]),"site-packages"
        )
        )

    if os .path .join (".framework","")in os .path .join (sys .prefix ,""):
        home =os .environ .get ("HOME")
        if home :

            paths .append (
            os .path .join (
            home ,
            "Library",
            "Python",
            "%d.%d"%(sys .version_info [:2 ]),
            "lib",
            "python",
            "site-packages",
            )
            )


            paths .append (
            os .path .join (
            home ,
            "Library",
            "Python",
            "%d.%d"%(sys .version_info [:2 ]),
            "site-packages",
            )
            )





    sys .__egginsert =len (sys .path )

    for path in paths :
        site .addsitedir (path )


_site_packages ()
