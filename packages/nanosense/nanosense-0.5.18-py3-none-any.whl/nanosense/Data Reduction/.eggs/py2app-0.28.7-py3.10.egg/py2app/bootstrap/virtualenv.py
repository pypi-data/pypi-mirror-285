def _fixup_virtualenv (real_prefix ):
    import os 
    import sys 

    sys .real_prefix =real_prefix 





    paths =[
    os .path .join (sys .real_prefix ,"lib","python%d.%d"%(sys .version_info [:2 ]))
    ]
    hardcoded_relative_dirs =paths [:]
    plat_path =os .path .join (
    sys .real_prefix ,
    "lib",
    "python%d.%d"%(sys .version_info [:2 ]),
    "plat-%s"%sys .platform ,
    )
    if os .path .exists (plat_path ):
        paths .append (plat_path )



    for path in list (paths ):
        tk_dir =os .path .join (path ,"lib-tk")
        if os .path .exists (tk_dir ):
            paths .append (tk_dir )



    hardcoded_paths =[
    os .path .join (relative_dir ,module )
    for relative_dir in hardcoded_relative_dirs 
    for module in ("plat-darwin","plat-mac","plat-mac/lib-scriptpackages")
    ]

    for path in hardcoded_paths :
        if os .path .exists (path ):
            paths .append (path )

    sys .path .extend (paths )
