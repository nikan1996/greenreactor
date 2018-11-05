from twisted.protocols.basic import LineOnlyReceiver
from twisted.test.proto_helpers import StringTransport

from _protocol import makeMain


class LineOnlyReceiver(LineOnlyReceiver):
    transport = StringTransport()

    def lineReceived(self, line):
        pass

main = makeMain(LineOnlyReceiver,
                ((b"a" * 50) + b"\r\n") * 1000)
main.__module__ = "only-lines"

if __name__ == '__main__':
    import sys
    import lineonlyreceiver
    from benchlib import driver
    driver(lineonlyreceiver.main, sys.argv)
