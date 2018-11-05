
from twisted.internet.defer import succeed

from benchlib import Client, driver


class Client(Client):
    def _request(self):
        d = succeed('result')
        def cbRaiseErr(result):
            raise Exception('boom!')
        d.addCallback(cbRaiseErr)
        def ebHandleErr(failure):
            failure.trap(Exception)
            raise Exception('lesser boom!')
        d.addErrback(ebHandleErr)
        def swallowErr(failure):
            return None
        d.addBoth(swallowErr)
        self._reactor.callLater(0.0, self._continue, None)


def main(reactor, duration):
    concurrency = 10

    client = Client(reactor)
    d = client.run(concurrency, duration)
    return d


if __name__ == '__main__':
    import sys
    import deferred_callback_chains
    driver(deferred_callback_chains.main, sys.argv)
