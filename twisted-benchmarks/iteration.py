
from benchlib import Client, driver


class Client(Client):
    def _request(self):
        self._reactor.callLater(0.0, self._continue, None)



def main(reactor, duration):
    concurrency = 10

    client = Client(reactor)
    d = client.run(concurrency, duration)
    return d



if __name__ == '__main__':
    import sys
    import iteration
    driver(iteration.main, sys.argv)
