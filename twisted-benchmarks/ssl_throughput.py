
"""
This benchmarks runs a trivial Twisted TLSv1 echo server using a certificate
with a 2048 bit RSA key as well as a client which pumps as much data to that
server as it can in a fixed period of time.
"""

from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import SSL4ClientEndpoint
from twisted.internet.ssl import (
    DN, KeyPair, PrivateCertificate, CertificateOptions)
from twisted.protocols.wire import Echo

from tcp_throughput import Client, driver

# Generate a new self-signed certificate
key = KeyPair.generate(size=2048)
req = key.certificateRequest(DN(commonName='localhost'), digestAlgorithm='sha1')
cert = PrivateCertificate.load(
    key.signCertificateRequest(
        DN(commonName='localhost'), req,
        lambda dn: True, 1, digestAlgorithm='sha1'),
    key)


def main(reactor, duration):
    chunkSize = 16384

    server = ServerFactory()
    server.protocol = Echo
    port = reactor.listenSSL(0, server, cert.options())
    client = Client(
        reactor,
        SSL4ClientEndpoint(
            reactor, '127.0.0.1', port.getHost().port,
            CertificateOptions(
                verify=True, requireCertificate=True, caCerts=[cert.original])))
    d = client.run(duration, chunkSize)
    def cleanup(passthrough):
        d = port.stopListening()
        d.addCallback(lambda ignored: passthrough)
        return d
    d.addCallback(cleanup)
    return d



if __name__ == '__main__':
    import sys
    import ssl_throughput
    driver(ssl_throughput.main, sys.argv)
