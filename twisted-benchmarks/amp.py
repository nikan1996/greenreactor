
"""
Benchmark for Twisted's (A)synchronous (M)essaging (P)rotocol.
"""

from twisted.internet.protocol import ServerFactory, ClientCreator
from twisted.protocols.amp import String, Integer, Float, ListOf
from twisted.protocols.amp import Command, CommandLocator, AMP

from benchlib import Client, driver


class Benchmark(Command):
    arguments = [
        (b'foo', String()),
        (b'bar', Integer()),
        (b'baz', ListOf(Float())),
        ]



class BenchmarkLocator(CommandLocator):
    @Benchmark.responder
    def benchmark(self, foo, bar, baz):
        return {}



class Client(Client):
    _string = b'hello, world' * 50
    _integer = 123454321
    _list = [1.2, 2.3, 3.4]

    def __init__(self, reactor, port):
        super(Client, self).__init__(reactor)
        self._port = port


    def run(self, *args, **kwargs):
        def connected(proto):
            self._proto = proto
            return super(Client, self).run(*args, **kwargs)
        client = ClientCreator(self._reactor, AMP)
        d = client.connectTCP('127.0.0.1', self._port)
        d.addCallback(connected)
        return d


    def cleanup(self):
        self._proto.transport.loseConnection()


    def _request(self):
        d = self._proto.callRemote(
            Benchmark, foo=self._string, bar=self._integer, baz=self._list)
        d.addCallback(self._continue)
        d.addErrback(self._stop)



def main(reactor, duration):
    concurrency = 150

    server = ServerFactory()
    server.protocol = lambda: AMP(locator=BenchmarkLocator())
    port = reactor.listenTCP(0, server)
    client = Client(reactor, port.getHost().port)
    d = client.run(concurrency, duration)
    def cleanup(passthrough):
        d = port.stopListening()
        d.addCallback(lambda ignored: passthrough)
        return d
    d.addCallback(cleanup)
    return d


if __name__ == '__main__':
    import sys
    import amp
    driver(amp.main, sys.argv)
