
from twisted.names.dns import DNSDatagramProtocol
from twisted.names.server import DNSServerFactory
from twisted.names import hosts, client

from benchlib import Client, driver


class Client(Client):
    def __init__(self, reactor, portNumber, timeout):
        self._resolver = client.Resolver(servers=[('127.0.0.1', portNumber)])
        self._timeout = timeout
        super(Client, self).__init__(reactor)


    def _request(self):
        d = self._resolver.lookupAddress(
            'localhost', timeout=(self._timeout,))
        d.addCallback(self._continue)
        d.addErrback(self._stop)




def main(reactor, duration):
    concurrency = 10

    controller = DNSServerFactory([hosts.Resolver()])
    port = reactor.listenUDP(0, DNSDatagramProtocol(controller))
    # Have queries time out no sooner than the duration of this benchmark so
    # we don't have to deal with retries or timeout errors.
    client = Client(reactor, port.getHost().port, duration)
    d = client.run(concurrency, duration)
    def cleanup(passthrough):
        d = port.stopListening()
        d.addCallback(lambda ign: passthrough)
        return d
    d.addBoth(cleanup)
    return d


if __name__ == '__main__':
    import sys
    import names
    driver(names.main, sys.argv)
