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
retweets = []
aday = datetime.now() - timedelta(1)

def update_favorites(timer_id=None):
    if len(curators) == 0:
        EventBus.send('log.event', "curators.list")
        EventBus.send('curators.list', "")
        return
    if len(friends) == 0:
        EventBus.send('log.event', "friends.list")
        EventBus.send('friends.list', "")
        return
    for curator in curators:
        EventBus.send('log.event', "user.favorites.list")
        EventBus.send('user.favorites.list', curator)
    
def curators_received(message):
    global curators
    curators = json.loads(message.body)
    update_favorites()
    
def friends_received(message):
    global friends
    friends = json.loads(message.body)
    update_favorites()
        
def favorites_received(message):
    global retweets
    data = json.loads(message.body)
    for tweet in data['favorites']:
        if tweet['id'] in retweets:
            continue 
        created_at = parse_date(tweet['created_at'])
        if created_at <= aday: # Retweet is recent
            continue
        if tweet['user']['id'] not in friends: 
            # Tweet is not by an account we follow
            continue
        if tweet['text'][0] == '@': 
            # Tweet is a reply
            # Of course there is: tweet['in_reply_to_screen_name'] but a reply may be a valid candidate for a retweet, as 
            # an old school RT creates this type of tweet
            continue
        # TODO: make this list persistent
        retweets.append(tweet['id'])
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
publishretweets_interval = 20 if 'publishretweets_interval' not in config else int(config['publishretweets_interval'])
vertx.set_periodic(1000 * 60 * publishretweets_interval, update_favorites)
vertx.set_periodic(1000 * 60 * 10, lambda timer_id: EventBus.send('log.event', datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")))
