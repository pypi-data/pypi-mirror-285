# -*- coding: utf-8 -*-
version = None 

try:  
    from importlib.metadata import version as v
    version = v("gtocclient")
except Exception :
    pass

if not version:
    try:
        import pkg_resources
        version = pkg_resources.get_distribution('gtocclient').version
    except Exception :
        version = "Unknown"

