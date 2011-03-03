"""The fancypants interface over SSH."""

import getpass

from twisted.cred import portal
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh import userauth, connection, keys
from twisted.conch.manhole import ColoredManhole
from twisted.conch.insults import insults
from twisted.conch.manhole_ssh import ConchFactory, TerminalRealm

# These are both publicly known keys, are not at all secure, and will be
# discarded before I do a releawse. For testing only.
_PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4t" \
            "fBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx" \
            "+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+B" \
            "R3utDS555mV"
_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
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

class SSHRestrictedPKDB(SSHPublicKeyDatabase):
    """Wouldn't it be nice to restrict to the owner user?"""
    def __init__(self, allowed_users):
        """Sets a list of allowed users."""
        self.allowed_users = allowed_users

    # pylint: disable-msg=C0103
    def checkKey(self, credentials):
        """Override the default behavior so that we
        only allow the owner user."""
        if not credentials.username in self.allowed_users:
            return False
        else:
            return SSHPublicKeyDatabase.checkKey(self, credentials)


class SSHFactory(ConchFactory):
    """My dupe of the SSHFactory that sets up the basics of a ColoredManhole
    and gets things configured with login/pass stuff."""
    def __init__(self, namespace = None):
        """Generates the manhole, contstrained to the namespace..."""
        realm = TerminalRealm()
        realm.chainedProtocolFactory = \
                lambda: insults.ServerProtocol(ColoredManhole, namespace)
        xportal = portal.Portal(realm)
        xportal.registerChecker(SSHRestrictedPKDB([getpass.getuser(),]))
        ConchFactory.__init__(self, xportal)

    # I _hate_ this warning.
    # pylint: disable-msg=C0103
    def getPrivateKeys(self):
        pass

    def getPublicKeys(self):
        pass


    publicKeys = {
        'ssh-rsa': keys.Key.fromString(data=_PUBLIC_KEY)
    }
    privateKeys = {
        'ssh-rsa': keys.Key.fromString(data=_PRIVATE_KEY)
    }
    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection
    }
