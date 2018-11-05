
from time import time

from twisted.internet.protocol import ServerFactory, Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint

from benchlib import Client, driver


class CloseConnection(Protocol):
    def makeConnection(self, transport):
        transport.loseConnection()



class Client(Client):
    protocol = CloseConnection

    def __init__(self, reactor, server):
        super(Client, self).__init__(reactor)
        self._server = server


    def _request(self):
        factory = Factory()
        factory.protocol = self.protocol

        d = self._server.connect(factory)
        d.addCallback(self._continue)
        d.addErrback(self._stop)



def main(reactor, duration):
    concurrency = 50

    factory = ServerFactory()
    factory.protocol = CloseConnection

    interface = '127.0.0.%d' % (int(time()) % 254 + 1,)
    interface = '127.0.0.1'
    port = reactor.listenTCP(0, factory, interface=interface)

    client = Client(
        reactor, TCP4ClientEndpoint(
            reactor, port.getHost().host, port.getHost().port,
            bindAddress=(interface, 0)))
    d = client.run(concurrency, duration)
    def cleanup(passthrough):
        d = port.stopListening()
        d.addCallback(lambda ignored: passthrough)
        return d
    d.addCallback(cleanup)
    return d



if __name__ == '__main__':
    import sys
    import tcp_connect
    driver(tcp_connect.main, sys.argv)
