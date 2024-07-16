""" dumb script that display attributes change the xAAL bus"""

from xaal.lib import Engine,helpers,Message
import time

helpers.set_console_title("xaal-log")

def print_evt(msg):
    if msg.is_alive():
        return
    if msg.is_notify():
        print("%s %s %s %s %s" % (time.ctime(),msg.source,msg.dev_type,msg.action,msg.body))


def main():
    try:
        eng = Engine()
        eng.disable_msg_filter()
        eng.subscribe(print_evt)
        eng.run()
    except KeyboardInterrupt:
        print("ByeBye..")

if __name__ == '__main__':
    main()
