#! /usr/bin/python
BANNER = \
"""
Panopticon 2.0
              ___  ___   _  ______  ___  ___________________  _  __
             / _ \/ _ | / |/ / __ \/ _ \/_  __/  _/ ___/ __ \/ |/ /
            / ___/ __ |/    / /_/ / ___/ / / _/ // /__/ /_/ /    /
           /_/  /_/ |_/_/|_/\____/_/    /_/ /___/\___/\____/_/|_/
          Turnkey  CCTV  and  online  broadcast  video  delivery
                              . .   .    ..   .
                               .  .=ZZODMZ=. ...
                       .....?MMMMNNNDDDDDDDD8DNMMD?,. .
                       .?NMMNDDZ=....... .....Z8DDDDMD,
                 .  .ZMDDDD+..                .N.....,8MMM= .
                 .?MDD$.ON..                  ..O..      ,MMMM=.    .
                =NDZ....+I..                  ..D..      . .,N8MMN~ .
            ...+MN..   .D...                    D..             .OMNN .
             .OMZ...   .O...                  . D..             . M ...
            .ZMD.      .I?..                   .8..             ~ .
            =MZ,.      ..O..                   .. .        ... ~..
           .NON .      . I:.                   N. .         =,=. .
           $N$,          .O8..             . .$=     . ..:~$....
          ,M.I.:         ..OD.             .,D..     ,,~Z. .....
          $?7.. +.  .    . ..OD7..    . ..ZI.. . ,,7DD:
       . =I ..,=~.+.,$$,::   ...,$D88DD, .  . ~DN8. .
       .,~. ,  ... ~?O7++=.. .. ....... ,?$DDNI, . ..
         ...         ....:=..  .=?$OZ7$OI::: .
                              ..:,,,..
                                   ...
"""

import gtk
import sys
import vlc
from panopticon.gtkvlc import VLCSlave

from gettext import gettext as _
from twisted.internet import gtk2reactor # for gtk-2.0
gtk2reactor.install()

class VideoContainer:
    """Holds all of the subwindows, and keeps track of them"""

    def on_window_key_press_event(self, window, event):
            print event.state, event.keyval
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
        self.fullscreen = bool(event.new_window_state & gtk.gdk.WINDOW_STATE_FULLSCREEN)
        print "Full: ", self.fullscreen

    def main(self, slaves=[], fullscreen=False):
        # Create a single vlc.Instance() to be shared by (possible) multiple players.
        self.instance = vlc.Instance()
        self.window=gtk.Window()
        self.window.connect("key-press-event",self.on_window_key_press_event)
        self.window.connect("window-state-event",self.on_window_state_event)
        #window.set_background(gtk.gdk.Color())
        mainbox=gtk.VBox()
        mainbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0,0))
        self.window.add(mainbox)


        vwindows = []
        hbox = None
        for fname in slaves:
            if hbox is None:
                hbox = gtk.HBox()
                hbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0,0))
            v = VLCSlave(self.instance, fname)
            v.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0,0))

            v.player.set_media(self.instance.media_new(fname))
            hbox.add(v)
            vwindows.append(v)
            if len(hbox.get_children())>1:
                mainbox.add(hbox)
                hbox = None
        if hbox is not None:
            mainbox.add(hbox)

        self.window.show_all()
        self.window.connect("destroy", gtk.main_quit)
        self.fullscreen = fullscreen
        if fullscreen:
            self.window.fullscreen()
        for v in vwindows:
            v.player.play()
        #gtk.main()



if __name__ == '__main__':
    if not sys.argv[1:]:
        print BANNER
        print "You must provide at least 1 movie filename"
        sys.exit(1)
    else:
        #p=MultiVideoPlayer()
        p=VideoContainer()
        p.main(sys.argv[1:])
        from twisted.internet import reactor
        reactor.run()
