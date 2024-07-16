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


from xaal.lib import Engine, Device, MessageType
from xaal.lib import tools
from . import isalive


import sys
import json
import time

from .ansi2 import term

def usage():
    print("xaal-querydb xxxx-xxxx-xxxx : display metadata for a given device")


class QueryDB:

    def __init__(self,engine,db_servers):
        self.eng = engine
        self.db_servers = db_servers
        # new fake device
        self.addr = tools.get_random_uuid()
        self.dev = Device("cli.experimental",self.addr)
        self.eng.add_device(self.dev)
        self.eng.add_rx_handler(self.parse_answer)
        
        print("xAAL DB query [%s]" % self.addr)


    def query(self,addr):
        self.timer = 0

        mf = self.eng.msg_factory
        body = {'device': addr,}
        msg = mf.build_msg(self.dev,self.db_servers, MessageType.REQUEST,'get_keys_values',body)
        self.eng.queue_msg(msg)

        while 1:
            self.eng.loop()
            if self.timer > 40:
                print("TimeOut...")
                break
            self.timer += 1
        print('\n')

    def parse_answer(self,msg):
        """ message parser """
        if msg.is_reply():
            if (self.addr in msg.targets) and (msg.action == 'get_keys_values'):
                term('yellow')
                print("%s => " % msg.source,end='')
                print(msg.body)
                term()


def main():
    if len(sys.argv) == 2:
        addr = tools.get_uuid(sys.argv[1])
        if tools.is_valid_address(addr):
            t0 = time.time()
            eng = Engine()
            eng.start()
            db_servers = isalive.search(eng,'metadatadb.basic')
            if len(db_servers) == 0:
                print("No metadb server found")
                return
            dev = QueryDB(eng,db_servers)
            dev.query(addr)
            print("Time : %0.3f sec" % (time.time() -t0))
        else:
            print("Invalid addr")

    else:
        usage()


if __name__ == '__main__':
    main()
