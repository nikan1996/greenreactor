
"""
Benchmark for SSH connection setup between a Conch client and server using RSA
keys.
"""

from twisted.internet.defer import Deferred, succeed
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Factory
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.conch.ssh.transport import SSHClientTransport

from benchlib import Client, driver


PUBLIC_KEY = (
    b'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az6'
    b'4fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkb'
    b'h/C+BR3utDS555mV')

PRIVATE_KEY = b"""-----BEGIN RSA PRIVATE KEY-----
MIIByAIBAAJhAK8ycfDmDpyZs3+LXwRLy4vA1T6yd/3PZNiPwM+uH8Yx3/YpskSW
4sbUIZR/ZXzY1CMfuC5qyR+UDUbBaaK3Bwyjk8E02C4eSpkabJZGB0Yr3CUpG4fw
vgUd7rQ0ueeZlQIBIwJgbh+1VZfr7WftK5lu7MHtqE1S1vPWZQYE3+VUn8yJADyb
Z4fsZaCrzW9lkIqXkE3GIY+ojdhZhkO1gbG0118sIgphwSWKRxK0mvh6ERxKqIt1
xJEJO74EykXZV4oNJ8sjAjEA3J9r2ZghVhGN6V8DnQrTk24Td0E8hU8AcP0FVP+8
PQm/g/aXf2QQkQT+omdHVEJrAjEAy0pL0EBH6EVS98evDCBtQw22OZT52qXlAwZ2
gyTriKFVoqjeEjt3SZKKqXHSApP/AjBLpF99zcJJZRq2abgYlf9lv1chkrWqDHUu
DZttmYJeEfiFBBavVYIF1dOlZT0G8jMCMBc7sOSZodFnAiryP+Qg9otSBjJ3bQML
pSTqy7c3a2AScC/YyOwkDaICHnnD3XyjMwIxALRzl0tQEKMXs6hH8ToUdlLROCrP
EhQ0wahUTCk1gKA4uPD6TMTChavbh4K63OvbKg==
-----END RSA PRIVATE KEY-----"""


class SimpleTransport(SSHClientTransport):
    def verifyHostKey(self, hostKey, fingerprint):
        return succeed(True)


    def connectionSecure(self):
        self.transport.loseConnection()
        self.factory.finished.callback(None)



class Client(Client):
    def __init__(self, reactor, server):
        super(Client, self).__init__(reactor)
        self._server = server


    def _request(self):
        client = Factory()
        client.protocol = SimpleTransport
        client.finished = Deferred()
        client.finished.addCallback(self._continue)
        client.finished.addErrback(self._stop)
        self._server.connect(client)


class BenchmarkSSHFactory(SSHFactory):
    publicKeys = {
        b'ssh-rsa': Key.fromString(data=PUBLIC_KEY),
    }
    privateKeys = {
        b'ssh-rsa': Key.fromString(data=PRIVATE_KEY),
    }


def main(reactor, duration):
    server = BenchmarkSSHFactory()
    port = reactor.listenTCP(0, server)
    client = Client(
        reactor,
        TCP4ClientEndpoint(reactor, '127.0.0.1', port.getHost().port))
    d = client.run(1, duration)
    def cleanup(passthrough):
        d = port.stopListening()
        d.addCallback(lambda ignored: passthrough)
        return d
    d.addCallback(cleanup)
    return d



if __name__ == '__main__':
    import sys
    import ssh_connect
    driver(ssh_connect.main, sys.argv)
