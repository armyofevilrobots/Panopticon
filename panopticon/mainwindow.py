#! /usr/bin/python
"""
              ___  ___   _  ______  ___  ___________________  _  __
             / _ \/ _ | / |/ / __ \/ _ \/_  __/  _/ ___/ __ \/ |/ /
            / ___/ __ |/    / /_/ / ___/ / / _/ // /__/ /_/ /    /
           /_/  /_/ |_/_/|_/\____/_/    /_/ /___/\___/\____/_/|_/
          Turnkey  CCTV  and  online  broadcast  video  delivery"""


import gtk
import vlc
from panopticon.gtkvlc import VLCSlave

class MainWindow:
    """Holds all of the subwindows, and keeps track of them"""
    def __init__(self, *args):
        """args is passed through for compatibility"""
        # pylint: disable-msg=W0613
        self.window = None
        self.instance = None
        self.fullscreen = False

    def on_window_key_press_event(self, window, event):
        """Handle local keypresses for window, and event, so we can do cool
        things like fullscreening or quitting. Real control should be over
        ssh though..."""
        # pylint: disable-msg=W0613
        if event.state == gtk.gdk.MOD2_MASK:
            print "Control"
        if event.keyval == 102:
            if self.fullscreen:
                self.window.unfullscreen()
            else:
                self.window.fullscreen()
        elif event.keyval == 113:
            gtk.main_quit()

    def on_window_state_event(self, window, event, *args):
        """Set a flag on our current fullscreen state so that we can do
        the right thing when asked to change state."""
        # pylint: disable-msg=W0613
        self.fullscreen = bool(event.new_window_state &
                gtk.gdk.WINDOW_STATE_FULLSCREEN)

    def main(self, slaves = list(), fullscreen = False):
        """The main loop of this program. I always hated how the
        main window is also the logic loop singleton. Perhaps I
        should change that? Twisted gets halfway with a different
        reactor startup."""
        # Create a single vlc.Instance()
        # to be shared by (possible) multiple players.
        self.instance = vlc.Instance()
        self.window = gtk.Window()
        self.window.connect("key-press-event", self.on_window_key_press_event)
        self.window.connect("window-state-event", self.on_window_state_event)
        mainbox = gtk.VBox()
        mainbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))
        self.window.add(mainbox)

        vwindows = []
        hbox = None
        for fname in slaves:
            if hbox is None:
                hbox = gtk.HBox()
                hbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))
            vslave = VLCSlave(self.instance, fname)
            vslave.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))

            vslave.player.set_media(self.instance.media_new(fname))
            hbox.add(vslave)
            vwindows.append(vslave)
            if len(hbox.get_children()) > 1:
                mainbox.add(hbox)
                hbox = None
        if hbox is not None:
            mainbox.add(hbox)

        self.window.show_all()
        self.window.connect("destroy", gtk.main_quit)
        self.fullscreen = fullscreen
        if fullscreen:
            self.window.fullscreen()

        from twisted.internet import defer
        from twisted.internet import reactor
        @defer.deferredGenerator
        def _run():
            """Better than a lambda..."""
            for vslave in vwindows:
                wfd = defer.waitForDeferred(vslave.deferred_action(1, 'play'))
                yield wfd
                wfd.getResult()
        self.vwindows = vwindows

        # pylint: disable-msg=E0611
        # pylint: disable-msg=E1101
        reactor.callWhenRunning(_run)
