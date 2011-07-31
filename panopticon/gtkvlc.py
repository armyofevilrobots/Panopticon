"""Container classes for VLC under GTK"""
import gtk
import sys
import vlc


# pylint: disable-msg=R0904
class VLCSlave(gtk.DrawingArea):
    """VLCSlave provides a playback window with an underlying player

    Its player can be controlled through the 'player' attribute, which
    is a vlc.MediaPlayer() instance."""
    def __init__(self, instance, name, width=320, height=200):
        """Generate a new VLC container using vlc instance "instance" and
        the given name variable for later referencing. Width/Height are self
        explanatory."""
        self.wname = name
        gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()
        self.watchdog = None


        def handle_embed(*args):
            """This is a callback that handles the window being mapped to the
            display, and sets vlc to draw to it.
            Args are ignored, but left here in case."""
            # pylint: disable-msg=W0613
            if sys.platform == 'win32':
                self.player.set_hwnd(self.window.handle)
            else:
                self.player.set_xwindow(self.window.xid)
            return True
        self.connect("map", handle_embed)
        self.set_size_request(width, height)

    def actions(self, action):
        if hasattr(self.player, action):
            return getattr(self.player, action)
        else:
            return lambda x: None

    def watchdog_state(self, playing = True):
        if self.player.get_state() != vlc.State.Playing:
            if self.player.get_state() == vlc.State.Ended:
                #self.player.set_time(0)
                #self.player.set_media(self.name)
            if playing:
                self.player.stop()
                self.player.play()
            else:
                self.player.stop()



    def deferred_action(self, delay = 0, action='play', *args):
        """Start playing in the background."""
        from twisted.internet.task import deferLater
        from twisted.internet import reactor
        from twisted.internet.task import LoopingCall
        if action == 'play' and self.watchdog is None:
            self.watchdog = LoopingCall(self.watchdog_state, True)
            self.watchdog.start(1, False)
        elif action == 'stop':
            self.watchdog.stop()
            self.watchdog = None


        return deferLater(reactor, delay, lambda:None, *args)#Does the watchdog catch it?
        return deferLater(reactor, delay, self.actions(action), *args)

