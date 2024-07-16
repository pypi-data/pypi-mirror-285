import textwrap 

try :
    from cStringIO import StringIO 
except ImportError :
    from io import StringIO 


def check (cmd ,mf ):
    m =mf .findNode ("multiprocessing")
    if m is None :
        return None 






    prescript =textwrap .dedent (
    """\
        def _boot_multiprocessing():
            import sys
            import multiprocessing.spawn

            orig_get_command_line = multiprocessing.spawn.get_command_line
            def wrapped_get_command_line(**kwargs):
                orig_frozen = sys.frozen
                del sys.frozen
                try:
                    return orig_get_command_line(**kwargs)
                finally:
                    sys.frozen = orig_frozen
            multiprocessing.spawn.get_command_line = wrapped_get_command_line

        _boot_multiprocessing()
        """
    )

    return {"prescripts":[StringIO (prescript )]}
