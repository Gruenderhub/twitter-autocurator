"""
Startet die App

@author Markus Tacker <m@coderbyheart.de>
"""

import vertx
from core.event_bus import EventBus

def log_event(message):
    print ">> %s" % message.body

EventBus.register_handler('log.event', False, log_event)

config = vertx.config()

vertx.deploy_verticle("fetchcurators.py", config)
vertx.deploy_verticle("fetchfavorites.py", config)
vertx.deploy_verticle("fetchfriends.py", config)
vertx.deploy_verticle("fetchfavorites.py", config)
vertx.deploy_verticle("createfavorite.py", config)
vertx.deploy_verticle("createretweet.py", config)
vertx.deploy_verticle("publishretweets.py", config)
