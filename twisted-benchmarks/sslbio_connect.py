
"""
This benchmark runs a trivial Twisted TLSv1 echo server using the memory BIO
based TLS implementation from L{twisted.protocols.tls}.
"""

from zope.interface import implementer

from twisted.internet.interfaces import IReactorTime, IReactorSSL
from twisted.protocols.tls import TLSMemoryBIOFactory
from twisted.python.components import proxyForInterface
from benchlib import driver

from ssl_connect import main as _main


@implementer(IReactorSSL)
class SSLBIOReactor(proxyForInterface(IReactorTime, '_reactor')):

    def listenSSL(self, port, factory, contextFactory, *args, **kw):
        return self._reactor.listenTCP(
            port, TLSMemoryBIOFactory(contextFactory, False, factory),
            *args, **kw)


    def connectSSL(self, host, port, factory, contextFactory, *args, **kw):
        return self._reactor.connectTCP(
            host, port, TLSMemoryBIOFactory(contextFactory, True, factory),
            *args, **kw)



def main(reactor, duration):
    return _main(SSLBIOReactor(reactor), duration)



if __name__ == '__main__':
    import sys
    import sslbio_connect
    driver(sslbio_connect.main, sys.argv)
