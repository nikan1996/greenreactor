import struct
from twisted.protocols.basic import Int16StringReceiver
from _protocol import makeMain


class Int16StringReceiver(Int16StringReceiver):
    def stringReceived(self, s):
        pass


main = makeMain(Int16StringReceiver,
                (struct.pack("!H", 50) + b"a" * 50) * 1000)
main.__module__ = "int16strings"

if __name__ == '__main__':
    import sys
    import int16receiver
    from benchlib import driver
    driver(int16receiver.main, sys.argv)
