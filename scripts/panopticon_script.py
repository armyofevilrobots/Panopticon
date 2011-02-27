#! /usr/bin/python
"""
              ___  ___   _  ______  ___  ___________________  _  __
             / _ \/ _ | / |/ / __ \/ _ \/_  __/  _/ ___/ __ \/ |/ /
            / ___/ __ |/    / /_/ / ___/ / / _/ // /__/ /_/ /    /
           /_/  /_/ |_/_/|_/\____/_/    /_/ /___/\___/\____/_/|_/
          Turnkey  CCTV  and  online  broadcast  video  delivery"""

import sys

from panopticon.gtkvlc import VLCSlave
from panopticon.mainwindow import MainWindow
from panopticon import BANNER

from gettext import gettext as _
from twisted.internet import gtk2reactor # for gtk-2.0
gtk2reactor.install()

if __name__ == '__main__':
    if not sys.argv[1:]:
        print BANNER
        print _("You must provide at least 1 movie filename")
        sys.exit(1)
    else:
        #p=MultiVideoPlayer()
        p = MainWindow()
        p.main(sys.argv[1:])
        from twisted.internet import reactor
        reactor.run()
