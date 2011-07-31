#! /usr/bin/python
"""
              ___  ___   _  ______  ___  ___________________  _  __
             / _ \/ _ | / |/ / __ \/ _ \/_  __/  _/ ___/ __ \/ |/ /
            / ___/ __ |/    / /_/ / ___/ / / _/ // /__/ /_/ /    /
           /_/  /_/ |_/_/|_/\____/_/    /_/ /___/\___/\____/_/|_/
          Turnkey  CCTV  and  online  broadcast  video  delivery"""

import sys


from gettext import gettext as _
from twisted.internet import gtk2reactor # for gtk-2.0
gtk2reactor.install()

from panopticon.sshconsole import SSHFactory
from panopticon.mainwindow import MainWindow
from panopticon import BANNER
from ConfigParser import SafeConfigParser
from optparse import OptionParser



def main(args):
    """Just to make pylint happier..."""
    parser = OptionParser()
    parser.add_option("-c", "--config", dest = "config",
            help = "Configuration file location.")
    options, argv = parser.parse_args(args)

    if not argv[1:]:
        print BANNER
        print _("You must provide at least 1 movie filename")
        sys.exit(1)
    else:
        #p=MultiVideoPlayer()
        main_window = MainWindow()
        main_window.main(argv[1:], options)
        from twisted.internet import reactor
        # pylint: disable-msg=E0611
        # pylint: disable-msg=E1101
        reactor.listenTCP(5022, SSHFactory(dict(main=main_window)),)
        reactor.run()


if __name__ == '__main__':
    main(sys.argv)
