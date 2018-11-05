
from __future__ import division, print_function

import sys

from twisted.python import log
from twisted.internet.defer import Deferred
from twisted.internet.task import cooperate
from twisted.application.app import ReactorSelectionMixin
from twisted.python.usage import Options


class BenchmarkOptions(Options, ReactorSelectionMixin):
    optParameters = [
        ('iterations', 'n', 1, 'number of iterations', int),
        ('duration', 'd', 5, 'duration of each iteration', float),
        ('warmup', 'w', 0, 'number of warmup iterations', int),
    ]



class Client(object):
    def __init__(self, reactor):
        self._reactor = reactor
        self._requestCount = 0


    def run(self, concurrency, duration):
        self._reactor.callLater(duration, self._stop, None)
        self._finished = Deferred()
        self._finished.addBoth(self._cleanup)
        for i in range(concurrency):
            self._request()
        return self._finished


    def cleanup(self):
        pass


    def _continue(self, ignored):
        self._requestCount += 1
        if self._finished is not None:
            self._request()


    def _stop(self, reason):
        if self._finished is not None:
            finished = self._finished
            self._finished = None
            if reason is not None:
                finished.errback(reason)
            else:
                finished.callback(self._requestCount)


    def _cleanup(self, passthrough):
        self.cleanup()
        return passthrough



PRINT_TEMPL = ('%(stats)s %(name)s/sec (%(count)s %(name)s '
              'in %(duration)s seconds)')

def benchmark_report(acceptCount, duration, name):
    print(PRINT_TEMPL % {
        'stats'    : acceptCount / duration,
        'name'     : name,
        'count'    : acceptCount,
        'duration' : duration
        })


def perform_benchmark(reactor, duration, iterations, warmup, f, reporter):
    jobs = [f] * iterations
    d = Deferred()
    def work(res, counter):
        try:
            f = jobs.pop()
        except IndexError:
            d.callback(None)
        else:
            try:
                nxt = f(reactor, duration)
            except:
                d.errback()
            else:
                if counter <= 0:
                    nxt.addCallback(reporter, duration, f.__module__)
                nxt.addCallbacks(work, d.errback, (counter - 1,))
    work(None, warmup)
    return d


class Driver(object):
    benchmark_report = staticmethod(benchmark_report)

    def driver(self, f, argv):
        options = BenchmarkOptions()
        options.parseOptions(argv[1:])

        from twisted.internet import reactor

        d = perform_benchmark(
            reactor,
            options['duration'], options['iterations'], options['warmup'],
            f, benchmark_report)
        d.addErrback(log.err)
        reactor.callWhenRunning(d.addBoth, lambda ign: reactor.stop())
        reactor.run()


    def multidriver(self, f):
        options = BenchmarkOptions()
        options.parseOptions(sys.argv[1:])
        self.run_jobs(
            f, options['duration'], options['iterations'], options['warmup'])


    def run_jobs(self, f, duration, iterations, warmup):
        from twisted.internet import reactor

        def work(job):
            d = perform_benchmark(
                reactor, duration, iterations, warmup,
                job, self.benchmark_report)
            d.addErrback(
                log.err, "Problem running benchmark %s" % (job.__module__,))
            return d

        def go():
            task = cooperate(work(job) for job in f)
            d = task.whenDone()
            d.addErrback(log.err, "Problem coordinating benchmarks")
            d.addCallback(lambda ignored: reactor.stop())

        reactor.callWhenRunning(go)
        reactor.run()



_driver = Driver()
driver = _driver.driver
multidriver = _driver.multidriver
del _driver
