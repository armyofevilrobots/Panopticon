"""Smooth scrolling marquee widget for pygtk 2.8ish
              ___  ___   _  ______  ___  ___________________  _  __
             / _ \/ _ | / |/ / __ \/ _ \/_  __/  _/ ___/ __ \/ |/ /
            / ___/ __ |/    / /_/ / ___/ / / _/ // /__/ /_/ /    /
           /_/  /_/ |_/_/|_/\____/_/    /_/ /___/\___/\____/_/|_/
          Turnkey  CCTV  and  online  broadcast  video  delivery"""

import gtk
import gobject
import pango

# pylint: disable-msg=R0904
class Marquee(gtk.HBox):
    """Smooth scrolling marquee widget for pygtk 2.8ish"""
    """P.S. This does not work. You should not use it."""
    def __init__(self, default_content="", fps=30):
        """Override to add the viewport and textholder"""
        gtk.HBox.__init__(self)
        self.viewport = gtk.Viewport()
        self.viewport.set_border_width(0)
        self.default_content = default_content
        self.content = gtk.Label(self.get_content())
        self.content.set_single_line_mode(True)
        gobject.timeout_add(1000/fps, self.tick, self.get_content)
        self.connect("size-allocate", self.on_resize)
        self.pack_end(self.viewport, True, True)
        self.viewport.add(self.content)
        self.fontsize = 12

    def on_resize(self, widget, event):
        """Catches the resize to force the font size."""
        print "RESIZE", widget, event
        x, y, width, height = self.get_allocation()
        print "ALLOC", self.get_allocation()

        #pfontsize = event.height * 0.8
        #print "Possible fsize is ", pfontsize
        #if pfontsize != self.fontsize:
            #print "Size changing to ", pfontsize
            #self.fontsize = pfontsize
            #self.content.modify_font(
                    #pango.FontDescription("sans %d" % self.fontsize))
        ##self.set_size_request(event.width, max(100, event.width/5))
        ##self.viewport.set_size_request(event.width, min(100, event.width/5))

    def get_content(self):
        """Returns the content, or calls the getter feature"""
        if callable(self.default_content):
            return self.default_content()
        else:
            return self.default_content

    def tick(self, getter = None):
        """Called fps times per second"""
        getter = getter or self.get_content()
        cwidth, cheight = self.content.size_request()
        vwidth, vheight = self.viewport.size_request()
        cadj = self.viewport.get_hadjustment()
        print "Cadj is ",cadj.get_value(), "vwidth is",vwidth,"cwidth is ",cwidth

        if cadj.get_value() > cwidth:
            self.viewport.set_hadjustment(0)
        else:
            self.viewport.set_hadjustment(gtk.Adjustment(cadj.get_value()+10))

        #print "tick.",width,height
        #print "tick.",self.get_size_request()

        return True



