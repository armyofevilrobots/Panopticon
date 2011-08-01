"""
              ___  ___   _  ______  ___  ___________________  _  __
             / _ \/ _ | / |/ / __ \/ _ \/_  __/  _/ ___/ __ \/ |/ /
            / ___/ __ |/    / /_/ / ___/ / / _/ // /__/ /_/ /    /
           /_/  /_/ |_/_/|_/\____/_/    /_/ /___/\___/\____/_/|_/
          Turnkey  CCTV  and  online  broadcast  video  delivery"""

from ConfigParser import SafeConfigParser
from os.path import abspath


config = SafeConfigParser({'ready':False, 'rss':None, 'ui':'no', 'streams':''})

def gen_config(config_file):
    if config_file is not None:
        config.read(abspath(config_file))
    return config

