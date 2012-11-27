# coding=utf-8
"""
Veröffentlich die Favoriten der Curatoren als Retweets

@author Markus Tacker <m@coderbyheart.de>
"""
import vertx
import mutex
import time
from com.xhaus.jyson import JysonCodec as json
from oauth import Consumer
from core.event_bus import EventBus
from util import parse_date
from datetime import datetime, timedelta

config = vertx.config()

curators = []
friends = []
aday = datetime.now() - timedelta(1)

def update_favorites(timer_id):
    EventBus.send('log.event', "update_favorites")
    for curator in curators:
        EventBus.send('log.event', "user.favorites.list")
        EventBus.send('user.favorites.list', curator)
    
def curators_received(message):
    global curators
    curators = json.loads(message.body)
    
def friends_received(message):
    global friends
    friends = json.loads(message.body)
        
def favorites_received(message):
    data = json.loads(message.body)
    for tweet in data['favorites']:
        created_at = parse_date(tweet['created_at'])
        if created_at > aday: # Retweet is recent
            if tweet['user']['id'] in friends: # Tweet is by an account we follow
                EventBus.send('log.event', "retweet.create")
                EventBus.send("retweet.create", tweet['id'])

EventBus.register_handler('curators.list.result', False, curators_received)
EventBus.register_handler('friends.list.result', False, friends_received)
EventBus.register_handler('user.favorites.list.result', False, favorites_received)

# Initialize lists
EventBus.send('log.event', "curators.list")
EventBus.send('curators.list', "")
EventBus.send('log.event', "friends.list")
EventBus.send('friends.list', "")

# Update favorites every n minutes
vertx.set_periodic(1000 * 60 * 15, update_favorites)

# Wait for first fetch
vertx.set_timer(10000, update_favorites)
