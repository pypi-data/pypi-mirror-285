# -*- coding: utf-8 -*-

#
#  Copyright 2014 Jérôme Kerdreux, Telecom Bretagne.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from xaal.lib import Engine, Device, tools, config,helpers

import sys
import time
import logging

helpers.setup_console_logger()
logger = logging.getLogger("xaal-isalive")

class Scanner:

    def __init__(self,engine):
        self.eng = engine
        # new fake device
        self.dev = Device("cli.experimental",tools.get_random_uuid())
        self.eng.add_device(self.dev)
        self.eng.subscribe(self.parse_answer)

    def query(self,dev_type):
        if not tools.is_valid_dev_type(dev_type):
            logger.warning("dev_type not valid [%s]" % dev_type)
            return
        self.dev_type = dev_type
        self.seen = []

        logger.info("[%s] searching [%s]" % (self.dev.address,self.dev_type))
        self.eng.send_is_alive(self.dev,dev_types=[self.dev_type,])

        print("="*70)
        self.loop()
        print("="*70)
        print("Found %d devices" % len(self.seen))

    def loop(self):
        t0 = time.time()
        while 1:
            self.eng.loop()
            if time.time() > (t0 + 2):
                break

    def parse_answer(self,msg):
        if msg.is_alive():
            # hidding myself
            if msg.source == self.dev.address:
                return
            #it is really for us ?
            if self.dev_type != 'any.any':
                (target_dev_type,target_devsubtype) = self.dev_type.split('.')
                (msg_dev_type,msg_devsubtype) = msg.dev_type.split('.')
                if msg_dev_type != target_dev_type:
                    return
                if target_devsubtype != 'any' and target_devsubtype != msg_devsubtype:
                    return
            if msg.source in self.seen:
                return
            # everything is Ok :)
            print("%s : %s" % (msg.source,msg.dev_type))
            self.seen.append(msg.source)



def run():
    """ run the isalive scanner from cmdline"""
    eng = Engine()
    eng.disable_msg_filter()

    scan = Scanner(eng)
    eng.start()
    dev_type = 'any.any'
    if len(sys.argv) == 2:
        dev_type = sys.argv[1]
    scan.query(dev_type)


def search(engine,dev_type='any.any'):
    """ send request and return list of xaal-addr"""
    scan = Scanner(engine)
    scan.query(dev_type)
    return scan.seen

def main():
    try:
        run()
    except KeyboardInterrupt:
        print("Bye bye")

if __name__ == '__main__':
    main()
