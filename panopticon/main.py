#! /usr/bin/python
"""
              ___  ___   _  ______  ___  ___________________  _  __
             / _ \/ _ | / |/ / __ \/ _ \/_  __/  _/ ___/ __ \/ |/ /
            / ___/ __ |/    / /_/ / ___/ / / _/ // /__/ /_/ /    /
           /_/  /_/ |_/_/|_/\____/_/    /_/ /___/\___/\____/_/|_/
          Turnkey  CCTV  and  online  broadcast  video  delivery"""


import vlc
from panopticon.config import gen_config
from panopticon.mainwindow import MainWindow
from twisted.python import log
from icalendar import Calendar, Event, UTC
from httplib2 import Http
import datetime
import feedparser
from twisted.internet.task import LoopingCall

#class CalendarSrv:
    #"""Caches, parses, and returns the details of a remote
    #ical file."""

    #def __init__(self, uri, filter=None):
        #self.filter = filter
        #self.uri = uri
        #self.http = Http()
        #resp, body = self.http.request(uri)
        #self.calendar = Calendar.from_string(body)

        ##for item in self.calendar.walk('VEVENT'):
            ##print item.keys()
            ##print item['SUMMARY']
        #print self.get_next()

    #def get_next(self):
        #for item in self.calendar.walk('VEVENT'):
            #print item, item.__dict__
            #print item['DTSTART'].__class__
            #print item['DTSTART']
            #print item['DTSTAMP'].__dict__
            #print item['DTSTART'].dt
            #if item['DTSTAMP'].dt > datetime.datetime.utcnow():

                #return item['SUMMARY']
        #return "No more events."







class Main:
    """Holds all of the subwindows, and keeps track of them"""
    def __init__(self, args, options, config):
        """args is passed through for compatibility"""
        # pylint: disable-msg=W0613
        self.instance = None
        self.config = config
        if self.config.get('service', 'ui', 'no') == 'yes':
            self.window = MainWindow(args, options)
        else:
            self.window = None
        self.calendars = dict()
        #TODO: We need to sanity check the config here.
        self.rsscache = {}

    def main(self):
        """The main loop of this program. I always hated how the
        main window is also the logic loop singleton. Perhaps I
        should change that? Twisted gets halfway with a different
        reactor startup."""
        from twisted.internet import reactor
        # Create a single vlc.Instance()
        # to be shared by (possible) multiple players.
        slaves = [uri.strip() for uri in
                str(self.config.get('service', 'streams', "")).split(",")
                if uri != ""]
        self.instance = vlc.Instance()
        self.instance.set_log_verbosity(3)
        streams = 0
        vslaves = []

        for stream in slaves:
            ssec = 'stream:%s' % stream
            fname = self.config.get('stream:%s' % stream, 'uri', None)
            murl = ":sout="
            if self.window is not None:
                murl += "#duplicate{dst=display{sfilter=marq},dest="
            murl += (str(self.config.get(ssec, 'transcode', None))
                    .replace("!WINDOW!", str(len(vslaves))))
            smedia = self.instance.media_new(fname, murl)
            smedia.add_options("h264-fps=25")

            vslave = self.instance.media_player_new()
            vslave.set_media(smedia)
            #This is a bunch of MaGiC from http://liris.cnrs.fr/advene/download/python-ctypes/doc/index.html
            vslave.video_set_marquee_string(1, "%s $u $d %%sX" % stream)
            vslave.video_set_marquee_int(4,9)  #position rel bottom left
            vslave.video_set_marquee_int(6,int(self.config.get(ssec, 'marquee_height', 20))) #size
            vslave.video_set_marquee_int(8,10) #x position 10
            vslave.video_set_marquee_int(9,10) #y position 10
            #vslave.video_set_marquee_int(5,1)  #timeout is 6 seconds
            vslaves.append(vslave)

            #Get the calendar too...
            curi = self.config.get(ssec, 'rss')
            if curi is not None:
                if not self.rsscache.has_key(curi):
                    self.calendars[stream] = feedparser.parse(curi)
                    self.rsscache[curi] = self.calendars[stream]
                else:
                    self.calendars[stream] = self.rsscache[curi]

                #log.msg(str(self.calendars[stream]))

        log.msg("Now we start the players.")

        from twisted.internet import defer
        # so that parallel runs don't assplode.
        from twisted.internet.task import deferLater

        @defer.deferredGenerator
        def _run():
            """Better than a lambda..."""
            wfd = defer.waitForDeferred(
                    deferLater(
                        reactor, 1,
                        lambda: log.msg("Done waiting for init")))
            yield wfd
            wfd.getResult()
            for vslave in vslaves:
                log.msg("Starting slave %s" % vslave)
                wfd = defer.waitForDeferred(deferLater(reactor, 1, vslave.play))
                yield wfd
                wfd.getResult()
                log.msg("Detected FPS: %s" % vslave.get_fps())

            def _updaterss():
                for vslave in vslaves:
                    try:
                        log.msg("Updating rss for %s." % stream)
                        if vslave.get_state() == vlc.State.Playing:
                            newstring = "%s %s %%s" % (stream, datetime.datetime.now())
                            log.msg("New msg %s %%s" % newstring)
                            vslave.get_media().set_meta(6, newstring)
                            vslave.get_media().save_meta()
                    except Exception, e:
                        log.msg("Err %s" % e)

                        #vslave.video_set_marquee_string(1, newstring)
            looper = LoopingCall(_updaterss)
            looper.start(7)

        # pylint: disable-msg=E0611
        # pylint: disable-msg=E1101
        from twisted.internet import reactor
        reactor.callWhenRunning(_run)

