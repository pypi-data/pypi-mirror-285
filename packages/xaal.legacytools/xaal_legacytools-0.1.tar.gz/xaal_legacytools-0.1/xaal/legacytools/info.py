# -*- coding: utf-8 -*-

#
#  Copyright 2016  Jérôme Kerdreux, IMT Atlantique.
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


from xaal.lib import Engine, Device
from xaal.lib import tools

import sys
import time
import pprint

from .ansi2 import term

def usage():
    print("xaal-info xxxx-xxxx-xxxx : display information about a given device")


class InfoDumper:

    def __init__(self,engine):
        self.eng = engine
        # new fake device
        addr = tools.get_random_uuid()
        dev = Device("cli.experimental",addr)
        dev.vendor_id = "IHSEV"
        dev.product_id = "xAAL InfoDumper"
        self.eng.add_device(dev)
        self.eng.subscribe(self.parse_answer)
        print(f"xAAL Info dumper [{addr}]")
        self.dev = dev

    def query(self,addr):
        """ send getDescription & getAttributes and wait for reply"""

        self.target = addr
        self.msgCnt = 0
        self.timer = 0

        self.eng.send_get_description(self.dev,[addr,])
        self.eng.send_get_attributes(self.dev,[addr,])

        term('cyan')
        print("** Device : [%s]" % self.target)
        term()

        while 1:
            self.eng.loop()
            if self.timer > 30:
                print("TimeOut...")
                break
            if self.msgCnt > 1:break
            self.timer += 1
        print('\n')

    def parse_answer(self,msg):
        """ message parser """
        if msg.is_reply():
            if self.dev.address in msg.targets:
                if self.target == msg.source:
                    if msg.is_get_attribute_reply():
                        print("== Attributes =====")

                    if msg.is_get_description_reply():
                        print("== Description ====")

                    pprint.pprint(msg.body)
                    self.msgCnt += 1


def main():
    if len(sys.argv) == 2:
        addr = tools.get_uuid(sys.argv[1])
        if addr:
            t0 = time.time()
            eng = Engine()
            eng.start()
            dev = InfoDumper(eng)
            dev.query(addr)
            print("Time : %0.3f sec" % (time.time() -t0))
        else:
            print("Invalid addr")

    else:
        usage()


if __name__ == '__main__':
    main()
