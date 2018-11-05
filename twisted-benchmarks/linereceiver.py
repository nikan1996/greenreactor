from twisted.protocols.basic import LineReceiver
from _protocol import makeMain


class LineReceiver(LineReceiver):
    def lineReceived(self, line):
        pass

main = makeMain(LineReceiver,
                ((b"a" * 50) + b"\r\n") * 1000)
main.__module__ = "lines"


if __name__ == '__main__':
    import sys
    import linereceiver
    from benchlib import driver
    driver(linereceiver.main, sys.argv)
