# coding=utf-8
"""
Lädt die Favoriten der Curatoren

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

def response_handler(resp):
    @resp.body_handler
    def body_handler(body):
        if resp.status_code == 200:
            data = json.loads(body.to_string())
            for tweet in data:
                created_at = parse_date(tweet['created_at'])
                if created_at > aday: # Retweet is recent
                    if tweet['user']['id'] in friends: # Tweet is by an account we follow
                        EventBus.send('log.event', "retweet.create")
                        EventBus.send("retweet.create", tweet['id'])
            
def fetch_favorites():
    consumer = Consumer(api_endpoint="https://api.twitter.com/", consumer_key=config['consumer_key'], consumer_secret=config['consumer_secret'], oauth_token=config['oauth_token'], oauth_token_secret=config['oauth_token_secret'])
    for curator in curators:
        consumer.get("/1.1/favorites/list.json", {'user_id': curator['id'], 'count': 20}, response_handler)

def update_favorites(timer_id):
    EventBus.send('log.event', "curators.list")
    EventBus.send('curators.list', "")
    
def curators_received(message):
    global curators
    curators = json.loads(message.body)
    EventBus.send('log.event', "friends.list")
    EventBus.send('friends.list', "")
    
def friends_received(message):
    global friends
    friends = json.loads(message.body)
    fetch_favorites()

EventBus.register_handler('curators.list.result', False, curators_received)
EventBus.register_handler('friends.list.result', False, friends_received)

# Update favorites every n minutes
vertx.set_periodic(1000 * 60 * 60, update_favorites)

# Wait for first fetch
vertx.set_timer(1000, update_favorites)