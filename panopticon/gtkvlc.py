"""Container classes for VLC under GTK"""
import gtk
import sys


# pylint: disable-msg=R0904
class VLCSlave(gtk.DrawingArea):
    """VLCSlave provides a playback window with an underlying player

    Its player can be controlled through the 'player' attribute, which
    is a vlc.MediaPlayer() instance.
    """
    def __init__(self, instance, name, width=320, height=200):
        """Generate a new VLC container using vlc instance "instance" and
        the given name variable for later referencing. Width/Height are self
        explanatory."""
        self.wname = name
        gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()
        def handle_embed(*args):
            """Args are ignored, but left here in case."""
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

    def deferred_action(self, delay = 0, action='play', *args):
        """Start playing in the background."""
        from twisted.internet.task import deferLater
        from twisted.internet import reactor
        return deferLater(reactor, delay, self.actions(action), *args)

