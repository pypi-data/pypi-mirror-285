def _site_packages (prefix ,real_prefix ,global_site_packages ):
    import os 
    import site 
    import sys 

    paths =[]

    paths .append (
    os .path .join (
    prefix ,"lib","python%d.%d"%(sys .version_info [:2 ]),"site-packages"
    )
    )
    if os .path .join (".framework","")in os .path .join (prefix ,""):
        home =os .environ .get ("HOME")
        if home :
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




    sys .__egginsert =len (sys .path )

    if global_site_packages :
        site .addsitedir (
        os .path .join (
        real_prefix ,
        "lib",
        "python%d.%d"%(sys .version_info [:2 ]),
        "site-packages",
        )
        )
