
from zope.interface import implementer

from twisted.internet.defer import succeed
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.cred.portal import IRealm, Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.conch.avatar import ConchUser
from twisted.conch.ssh.userauth import SSHUserAuthClient
from twisted.conch.ssh.session import ISession, SSHSession

from ssh_connect import BenchmarkSSHFactory
from tcp_throughput import Client

from sshendpoint import SSHCommandClientEndpoint

from benchlib import driver


class Client(Client):
    def cleanup(self):
        # The base implementation should work, but does not.
        self._client.transport.conn.transport.transport.loseConnection()



class SSHPasswordUserAuth(SSHUserAuthClient):
    def __init__(self, user, password, instance):
        SSHUserAuthClient.__init__(self, user, instance)
        self.password = password


    def getPassword(self, prompt=None):
        return succeed(self.password)



class EchoTransport(object):
    def __init__(self, protocol):
        self.protocol = protocol


    def write(self, bytes):
        self.protocol.childDataReceived(1, bytes)


    def loseConnection(self):
        pass


@implementer(ISession)
class BenchmarkAvatar(ConchUser):

    def __init__(self):
        ConchUser.__init__(self)
        self.channelLookup[b'session'] = SSHSession


    def execCommand(self, proto, cmd):
        if cmd == b'chargen':
            self.proto = proto
            transport = EchoTransport(proto)
            proto.makeConnection(transport)
        else:
            raise RuntimeError("Unexpected execCommand")


    def closed(self):
        pass


@implementer(IRealm)
class BenchmarkRealm(object):

    def requestAvatar(self, avatarId, mind, *interfaces):
        return (
            interfaces[0],
            BenchmarkAvatar(),
            lambda: None)


def main(reactor, duration):
    chunkSize = 16384

    server = BenchmarkSSHFactory()
    server.portal = Portal(BenchmarkRealm())

    checker = InMemoryUsernamePasswordDatabaseDontUse()
    checker.users = {b"username": b"password"}

    server.portal.registerChecker(checker)

    port = reactor.listenTCP(0, server)
    tcpServer = TCP4ClientEndpoint(reactor, '127.0.0.1', port.getHost().port)
    sshServer = SSHCommandClientEndpoint(
        b'chargen', tcpServer,
        lambda command:
            SSHPasswordUserAuth(b'username', b'password', command))

    client = Client(reactor, sshServer)
    d = client.run(duration, chunkSize)
    def cleanup(passthrough):
        d = port.stopListening()
        d.addCallback(lambda ignored: passthrough)
        return d
    d.addCallback(cleanup)
    return d



if __name__ == '__main__':
    import sys
    import ssh_throughput
    # from twisted.python.log import startLogging
    # startLogging(sys.stderr, False)
    driver(ssh_throughput.main, sys.argv)
