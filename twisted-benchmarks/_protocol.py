"""
Base class for protocol benchmarks.
"""

from benchlib import Client


class Client(Client):
    # override in subclasses, Protocol class:
    _protocol = None

    # override in subclasses, string to be passed to protocol:
    _parseString = None

    _bytes = 0

    def _request(self):
        s = self._parseString
        for chunkSize in (16, 64, 256, 1024):
            # deliver string to protocol with given chunk size:
            p = self._protocol()
            i = 0
            while i < len(s):
                p.dataReceived(s[i:i+chunkSize])
                i += chunkSize
            self._bytes += chunkSize
        self._reactor.callLater(0.0, self._continue, None)

    def _stop(self, reason):
        if self._finished is not None:
            finished = self._finished
            self._finished = None
            finished.callback(self._bytes)


def makeMain(protocol, string):
    class ProtocolClient(Client):
        _protocol = protocol
        _parseString = string

    def main(reactor, duration):
        concurrency = 1

        client = ProtocolClient(reactor)
        d = client.run(concurrency, duration)
        return d

    return main
