from twisted.internet import defer, task

from time import time
from benchlib import driver


def _run():
    for x in range(1000):
        yield from defer.succeed(x)


def main(reactor, duration):
    start = time()
    count = 0
    while time() - start < duration:
        defer.ensureDeferred(_run())
        count += 1
    return defer.succeed(count)


if __name__ == '__main__':
    import sys
    import deferred_yieldfrom
    driver(deferred_yieldfrom.main, sys.argv)
