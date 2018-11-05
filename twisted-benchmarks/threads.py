
from twisted.internet.threads import deferToThread

from benchlib import Client, driver


class Client(Client):
    def _request(self):
        d = deferToThread(lambda: None)
        d.addCallback(self._continue)
        d.addErrback(self._stop)



def main(reactor, duration):
    concurrency = 10

    client = Client(reactor)
    d = client.run(concurrency, duration)
    return d



if __name__ == '__main__':
    import sys
    import threads
    driver(threads.main, sys.argv)
