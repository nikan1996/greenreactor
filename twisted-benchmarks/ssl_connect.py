
from time import time
from benchlib import driver

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import SSL4ServerEndpoint, SSL4ClientEndpoint

from ssl_throughput import cert
from tcp_connect import CloseConnection, Client


class WriteOneByte(Protocol):
    def connectionMade(self):
        self.transport.write(b"x")



class Client(Client):
    protocol = WriteOneByte



def main(reactor, duration):
    concurrency = 50

    interface = '127.0.0.%d' % (int(time()) % 254 + 1,)

    contextFactory = cert.options()
    factory = Factory()
    factory.protocol = CloseConnection
    serverEndpoint = SSL4ServerEndpoint(
        reactor, 0, contextFactory, interface=interface)

    listen = serverEndpoint.listen(factory)
    def cbListening(port):
        client = Client(
            reactor, SSL4ClientEndpoint(
                reactor, interface, port.getHost().port,
                contextFactory, bindAddress=(interface, 0)))
        d = client.run(concurrency, duration)
        def cleanup(passthrough):
            d = port.stopListening()
            d.addCallback(lambda ignored: passthrough)
            return d
        d.addCallback(cleanup)
        return d
    listen.addCallback(cbListening)
    return listen


if __name__ == '__main__':
    import sys
    import ssl_connect
    driver(ssl_connect.main, sys.argv)
