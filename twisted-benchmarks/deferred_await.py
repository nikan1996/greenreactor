from twisted.internet import defer, task

from time import time
from benchlib import driver


async def _run():
    for x in range(1000):
        await defer.succeed(x)


def main(reactor, duration):
    start = time()
    count = 0
    while time() - start < duration:
        defer.ensureDeferred(_run())
        count += 1
    return defer.succeed(count)


if __name__ == '__main__':
    import sys
    import deferred_await
    driver(deferred_await.main, sys.argv)
