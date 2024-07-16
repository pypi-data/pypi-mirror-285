"""
Little helper script to walk in device list
It first send an isAlive message and then
gather information on each device
"""

import sys
import time

import xaal.lib


from . import info
from . import isalive


def main():
    """ search for alive devices and gather informations about this device"""

    eng = xaal.lib.Engine()
    eng.disable_msg_filter()
    eng.start()
    devtype = 'any.any'
    if len(sys.argv) == 2:
        devtype = sys.argv[1]
    devs = isalive.search(eng,devtype)
    print()
    dumper = info.InfoDumper(eng)
    t0 = time.time()
    for k in devs:
        dumper.query(k)
    print("Time : %0.3f sec (%d devices)" % (time.time() -t0,len(devs)))

if __name__=='__main__':
    main()
