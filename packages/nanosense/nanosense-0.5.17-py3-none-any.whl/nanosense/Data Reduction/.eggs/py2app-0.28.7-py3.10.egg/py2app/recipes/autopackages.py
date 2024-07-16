AUTO_PACKAGES =[


"botocore",
"docutils",
"pylint",

"h5py",





"Crypto",

"sentencepiece",



"imageio_ffmpeg",

"numpy",
"scipy",
"tensorflow",
]


def check (cmd ,mf ):
    to_include =[]
    for python_package in AUTO_PACKAGES :
        m =mf .findNode (python_package )
        if m is None or m .filename is None :
            continue 

        to_include .append (python_package )

    if to_include :
        return {"packages":to_include }
    return None 
