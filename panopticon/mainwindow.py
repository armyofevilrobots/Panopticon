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
from panopticon.gtkmarquee import Marquee

class MainWindow:
    """Holds all of the subwindows, and keeps track of them"""
    def __init__(self, *args):
        """args is passed through for compatibility"""
        # pylint: disable-msg=W0613
        self.window = None
        self.instance = None
        self.scrollbox = None
        self.fullscreen = False
        self.wrapper = None


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
        #elif event.keyval ==
        elif event.keyval == 113:
            gtk.main_quit()

    def on_window_state_event(self, window, event, *args):
        """Set a flag on our current fullscreen state so that we can do
        the right thing when asked to change state."""
        # pylint: disable-msg=W0613
        self.fullscreen = bool(event.new_window_state &
                gtk.gdk.WINDOW_STATE_FULLSCREEN)

    def main(self, slaves = False, fullscreen = False):
        """The main loop of this program. I always hated how the
        main window is also the logic loop singleton. Perhaps I
        should change that? Twisted gets halfway with a different
        reactor startup."""
        # Create a single vlc.Instance()
        # to be shared by (possible) multiple players.
        slaves = slaves or list()
        self.instance = vlc.Instance()
        self.window = gtk.Window()
        self.window.connect("key-press-event", self.on_window_key_press_event)
        self.window.connect("window-state-event", self.on_window_state_event)
        self.wrapper = gtk.Table(5, 1, True)
        mainbox = gtk.VBox(False)
        mainbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))
        self.window.add(self.wrapper)
        #self.wrapper.attach(mainbox, 0, 1, 0, 4)
        self.wrapper.attach(mainbox, 0, 1, 0, 5) #Without the scroller
        #self.scrollbox = Marquee("Foo message.")
        #mainbox.connect("configure-event", self.scrollbox.on_resize)

        vwindows = []
        hbox = None
        for fname in slaves:
            if hbox is None:
                hbox = gtk.HBox()
                hbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))
            smedia = self.instance.media_new(fname,
                    ":sout=#duplicate{"
                    "dst=display{sfilter=marq},dst=\"transcode{vcodec=h264,fps=30,vb=800,"
                    "ab=64,width=512,height=384, acodec=mp3,samplerate=44100,sfilter=marq}"
                    ":std{access=http{mime=video/x-flv},"
                    "mux=ffmpeg{mux=flv},dst=0.0.0.0:908%d/}\"}" %
                    len(vwindows))
            vslave = VLCSlave(self.instance, fname)
            vslave.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))
            vslave.player.set_media(smedia)
            #This is a bunch of MaGiC from http://liris.cnrs.fr/advene/download/python-ctypes/doc/index.html
            vslave.player.video_set_marquee_string(1,"FooBarBaz This is a long title... "*10)
            vslave.player.video_set_marquee_int(4,9)  #position rel bottom left
            vslave.player.video_set_marquee_int(8,10) #x position 10
            vslave.player.video_set_marquee_int(9,10) #y position 10
            hbox.add(vslave)
            vwindows.append(vslave)


        if hbox is not None:
            mainbox.pack_start(hbox)

        #self.wrapper.attach(self.scrollbox, 0, 1, 4, 5)

        self.window.show_all()
        self.window.connect("destroy", gtk.main_quit)
        self.fullscreen = fullscreen
        if fullscreen:
            self.window.fullscreen()

        from twisted.internet import defer
        # so that parallel runs don't assplode.
        @defer.deferredGenerator
        def _run():
            """Better than a lambda..."""
            for vslave in vwindows:
                wfd = defer.waitForDeferred(vslave.deferred_action(1, 'play'))
                yield wfd
                wfd.getResult()

        # pylint: disable-msg=E0611
        # pylint: disable-msg=E1101
        from twisted.internet import reactor
        reactor.callWhenRunning(_run)

