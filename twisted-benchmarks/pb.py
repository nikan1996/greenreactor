
"""
Benchmark for Twisted Spread.
"""

from twisted.python.compat import _PY3

if _PY3:
    raise ImportError("Doesn't work on Py3 yet")

from twisted.spread.pb import PBServerFactory, PBClientFactory, Root

from benchlib import Client, driver


class BenchRoot(Root):
    def remote_discard(self, argument):
        pass



class Client(Client):
    _structure = [
        'hello' * 100,
        {'foo': 'bar',
         'baz': 100,
         u'these are bytes': (1, 2, 3)}]

    def __init__(self, reactor, port):
        super(Client, self).__init__(reactor)
        self._port = port


    def run(self, *args, **kwargs):
        def connected(reference):
            self._reference = reference
            return super(Client, self).run(*args, **kwargs)
        client = PBClientFactory()
        d = client.getRootObject()
        d.addCallback(connected)
        self._reactor.connectTCP('127.0.0.1', self._port, client)
        return d


    def cleanup(self):
        self._reference.broker.transport.loseConnection()


    def _request(self):
        d = self._reference.callRemote('discard', self._structure)
        d.addCallback(self._continue)
        d.addErrback(self._stop)



def main(reactor, duration):
    concurrency = 15

    server = PBServerFactory(BenchRoot())
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
    import pb
    driver(pb.main, sys.argv)
