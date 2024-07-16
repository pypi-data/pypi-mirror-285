from xaal.lib import NetworkConnector,config,cbor,core

class ParseError(Exception):pass

def incr(value,max_value,increment=1):
    tmp = value + increment
    if tmp > max_value:
        raise ParseError("Unable to go forward, issue w/ packet lenght ?")
    return tmp

def hexdump(data):
    print("HEX:",end="")
    for k in data:
        print("0x%x" % k,end=", ")

def parse(data):
    i = 0
    size = len(data)

    print("========= Headers ========")
    header_size = data[i]
    if header_size != 0x85:
        raise ParseError("Wrong array in header: 0x%x" % header_size)
    print("Array w/ size=5 (0x85) : 0x%x" %header_size)

    i = incr(i,size)
    ver = data[i]
    if ver != 7:
        raise ParseError("Wrong packet version: 0x%x" % ver)
    print("Version: 0%x" % ver)

    i = incr(i,size)
    ts0_size = data[i]
    if ts0_size not in [0x1a,0x1b]:
        raise ParseError("Wrong timestamp part0 size: 0x%x" % ts0_size)
    print("TS0 size (0x1a or 0x1b): 0x%x" % ts0_size )
    if ts0_size == 0x1a:
        i=incr(i,size,5)
        ts0 = list(data[i-4:i])
        print("TS0: ",end="")
        hexdump(ts0)
        print("=> %s" % cbor.loads(bytes(data[i-5:i])))

    if ts0_size == 0x1b:
        i=incr(i,size,9)
        ts0 = list(data[i-8:i])
        print("TS0: ",end="")
        hexdump(ts0)
        print("=> %s" % cbor.loads(bytes(data[i-9:i])))

    ts1_size = data[i]
    if ts1_size != 0x1a:
        raise ParseError("Wrong timestamp part1 size: 0x%x" % ts1_size)
    print("TS1 size (0x1a): 0x%x" % ts0_size )
    i = incr(i,size,5)
    ts1 = list(data[i-4:i])
    print("TS1: ",end="")
    hexdump(ts1)
    print("=> %s" % cbor.loads(bytes(data[i-5:i])))

    target_size = data[i]
    hexdump(data[i:i+10])
    #print("0x%x" % target_size)

    print()

def main():
    nc = NetworkConnector(config.address,config.port,config.hops)
    while 1:
        data = nc.get_data()
        if data:
            try:
                parse(data)
            except ParseError as e:
                print("ERROR ==> %s" % e)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Bye...")
    