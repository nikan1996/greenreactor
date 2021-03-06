#!/usr/bin/env python
# encoding: utf-8
"""
@author:nikan(859905874@qq.com)🎂

@file: geventreactor.py

@time: 2018/10/28 下午10:28
"""
import gevent

from greenlet import GreenletExit
from gevent import get_hub
from gevent._interfaces import ILoop
from gevent._socketcommon import getaddrinfo, wait_read, wait_write
from zope.interface import implementer

from twisted.internet._resolver import GAIResolver
from twisted.internet.base import DelayedCall
from twisted.internet.interfaces import IReactorFDSet
from twisted.internet.posixbase import PosixReactorBase, _NO_FILEDESC
from twisted.logger import Logger


class _DCHandle(object):
    """
    Wraps Greenlet Instance
    """

    def __init__(self, handle: gevent.Greenlet):
        self.handle = handle

    def cancel(self):
        """
        kill the greenlet
        """
        self.handle.kill(block=False)


@implementer(IReactorFDSet)
class GreenReactor(PosixReactorBase):
    """ Reactor running on top of Gevent Event Loop,

        Attributes:
            spawn: alias to gevent spawn
            spawn_later: alias to gevent spawnlater
            _log: twisted logger
    """
    spawn = gevent.spawn
    spawn_later = gevent.spawn_later
    _log = Logger()

    def __init__(self):
        self.hub = get_hub()
        self.greenlet = None
        self.event_loop = self.hub.loop  # type: ILoop
        self._writers = {}
        self._readers = {}
        self._delayedCalls = set()

        super().__init__()

    def mainLoop(self):
        self.greenlet = gevent.getcurrent()
        try:
            while True:
                gevent.sleep(10)
                if self._justStopped:
                    self._justStopped = False
        except (GreenletExit, KeyboardInterrupt):
            pass

        gevent.get_hub().join()  # wait the event loop to finish
        self.fireSystemEvent('shutdown')

    def _initThreads(self):
        self.installNameResolver(GAIResolver(self, getaddrinfo=getaddrinfo))
        self.usingThreads = True

    def _readOrWrite(self, selectable, read):
        if read:
            method = selectable.doRead
            wait = wait_read
        else:
            method = selectable.doWrite
            wait = wait_write

        fileno = selectable.fileno()
        if selectable.fileno() == -1:
            self._disconnectSelectable(selectable, _NO_FILEDESC, read)
            return

        try:
            while True:
                wait(fileno)
                why = method()
                if why:
                    break
        except Exception as e:
            why = e
            self._log.failure(None)
        if why:
            self._disconnectSelectable(selectable, why, read)

    def addReader(self, reader):
        """
        Add a FileDescriptor for notification of data available to read.
        """
        if reader in self._readers:
            return

        g = self.spawn(self._readOrWrite, reader, True)
        self._readers[reader] = g

    def addWriter(self, writer):
        """
        Add a FileDescriptor for notification of data available to write.
        """
        if writer in self._writers:
            return
        g = self.spawn(self._readOrWrite, writer, False)
        self._writers[writer] = g

    def removeReader(self, reader):
        """
        Remove a Selectable for notification of data available to read.
        """
        if reader not in self._readers:
            return
        g = self._readers.pop(reader)

        g.kill(block=False)

    def removeWriter(self, writer):
        """
        Remove a Selectable for notification of data available to write.
        """
        if writer not in self._writers:
            return
        g = self._writers.pop(writer)
        g.kill(block=False)

    def removeAll(self):
        """
        Remove all readers and writers.

        """
        return self._removeAll(self._readers.keys(), self._writers.keys())

    def getReaders(self):
        """
        Return the list of file descriptors currently monitored for input
        events by the reactor.
        """
        return self._readers.keys()

    def getWriters(self):
        """
        Return the list file descriptors currently monitored for output events
        by the reactor.
        """
        return self._writers.keys()

    def seconds(self):
        return self.event_loop.now()

    def stop(self):
        super().stop()
        gevent.kill(self.greenlet)



    def callLater(self, seconds, f, *args, **kwargs):
        def run(*a, **k):
            dc.called = True
            self._delayedCalls.remove(dc)
            result = f(*a, **k)
            return result

        handle = self.spawn_later(seconds, run, *args, **kwargs)
        dchandle = _DCHandle(handle)

        def cancel(dc):
            self._delayedCalls.remove(dc)
            dchandle.cancel()

        def reset(dc):
            dchandle.handle = self.spawn_later(dc.time - self.seconds(), run)

        dc = DelayedCall(self.seconds() + seconds, run, (), {},
                         cancel, reset, seconds=self.seconds)
        self._delayedCalls.add(dc)
        return dc

    def callFromThread(self, f, *args, **kwargs):
        self.spawn(f, *args, **kwargs)


def install():
    """
    Install a gevent-based reactor.
    """
    reactor = GreenReactor()
    from twisted.internet.main import installReactor
    installReactor(reactor)
