# -*- coding: utf-8 -*-

#
#  Copyright 2014 Jérôme Colin, Jérôme Kerdreux, Telecom Bretagne.
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

from xaal.lib import Engine,MessageType
from xaal.lib import tools

from .ansi2 import term
import sys
import shutil

level = 0

HIDE_ACTION=['get_attributes','get_description','get_keys_values','is_alive']


def type_to_string(mtype):
    tmp = str(MessageType(mtype))
    return tmp.split('.')[-1]


def display(msg):
    term('yellow')

    if (msg.action in HIDE_ACTION and level==2):
        return
        
    if msg.is_reply():
        if level > 2: return
        term('red')

    if msg.is_request():
        if level > 3: return
        term('green')

    if msg.is_notify():
        if msg.is_alive():
            if level > 0: return
            term('grey')
        if msg.is_attributes_change():
            term('cyan')

    targets = [tools.reduce_addr(addr) for addr in msg.targets]
    tmp = shutil.get_terminal_size()[0] - (8 + 20 + 36 + 20 + 16 + 9)
    if tmp < 50:
        tmp = 50
    BODY_FORMAT = '%-50.'+str(tmp)+'s'
    FORMAT = '%-8.08s=> %-18.18s %-36.36s (%-20.20s) %-16.16s '+BODY_FORMAT
    res = FORMAT % (type_to_string(msg.msg_type),msg.action,msg.source,msg.dev_type,targets,msg.body)
    print(res)

def usage():
    print("%s : monitor xAAL network w/ tail format" % sys.argv[0])
    print("  usage : %s log-level" % sys.argv[0])
    print("    level=0 => display all messages")
    print("    level=1 => hide alive messages")
    print("    level=2 => hide xAAL actions messages")
    print("    level=3 => hide reply messages")
    print("    level=4 => only notifications (attributesChange)")


def main():
    global level
    if len(sys.argv) == 2:
        level = int(sys.argv[1])

        eng = Engine()
        eng.disable_msg_filter()
        eng.subscribe(display)

        eng.start()
        term('@@')
        FORMAT = '%-8.08s=> %-18.18s %-36.36s (%-20.20s) %-16.16s %-50.50s'        
        print(FORMAT % ('type','action','source','dev_type','targets','body'))
        try:
            eng.run()
        except KeyboardInterrupt:
            pass
    else:
        usage()

if __name__ == '__main__':
    main()
