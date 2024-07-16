#!/usr/bin/env python
try:
    from gevent import monkey;monkey.patch_all(thread=False)
except ModuleNotFoundError:
    pass

import sys
import importlib


from xaal.lib import helpers
from xaal.lib import AsyncEngine as Engine
import logging


MY_NAME = "xaal-pkgrun"
logger = logging.getLogger(MY_NAME)


def load_pkgs(eng):
    for k in sys.argv[1:]:
        xaal_mod = 'xaal.' + k
        try:
            mod = importlib.import_module(xaal_mod)
        except ModuleNotFoundError:
            logger.critical("Unable to load module: %s" %xaal_mod )
            continue
    
        if hasattr(mod,'setup') == False:
            logger.critical("Unable to setup %s" % xaal_mod)
            continue
        mod.setup(eng)

def run():
    # some init stuffs
    helpers.setup_console_logger()
    #helpers.setup_file_logger(MY_NAME) 
    # Start the engine
    eng = Engine()
    eng.start()
    load_pkgs(eng)
    eng.run()    

def main():
    try:
        run()
    except KeyboardInterrupt:
        print("Byebye")


if __name__ == '__main__':
    main()
