
"""
This benchmarks runs a trivial Twisted TCP echo server and a client pumps as
much data to it as it can in a fixed period of time.

The size of the string passed to each write call may play a significant
factor in the performance of this benchmark.
"""

from twisted.internet.defer import Deferred
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import ServerFactory, Factory, Protocol
from twisted.protocols.wire import Echo

from benchlib import driver


class Counter(Protocol):
    count = 0

    def dataReceived(self, b):
        self.count += len(b)



class Client(object):
    _finished = None

    def __init__(self, reactor, server):
        self._reactor = reactor
        self._server = server


    def run(self, duration, chunkSize):
        self._duration = duration
        self._bytes = b'x' * chunkSize
        # Set up a connection
        factory = Factory()
        factory.protocol = Counter
        d = self._server.connect(factory)
        d.addCallback(self._connected)
        return d


    def cleanup(self):
        self._client.transport.loseConnection()


    def _connected(self, client):
        self._client = client
        self._stopCall = self._reactor.callLater(self._duration, self._stop)
        client.transport.registerProducer(self, False)
        self._finished = Deferred()
        return self._finished


    def _stop(self):
        self.stopProducing()
        self._client.transport.unregisterProducer()
        self._finish(self._client.count)


    def _finish(self, value):
        if self._finished is not None:
            finished = self._finished
            self._finished = None
            finished.callback(value)


    def resumeProducing(self):
        self._client.transport.write(self._bytes)


    def stopProducing(self):
        self.cleanup()


    def connectionLost(self, reason):
        self._finish(reason)



def main(reactor, duration):
    chunkSize = 16384

    server = ServerFactory()
    server.protocol = Echo
    port = reactor.listenTCP(0, server)
    client = Client(
        reactor,
        TCP4ClientEndpoint(
            reactor, '127.0.0.1', port.getHost().port))
    d = client.run(duration, chunkSize)
    def cleanup(passthrough):
        d = port.stopListening()
        d.addCallback(lambda ignored: passthrough)
        return d
    d.addCallback(cleanup)
    return d


if __name__ == '__main__':
    import sys
    import tcp_throughput
    driver(tcp_throughput.main, sys.argv)
