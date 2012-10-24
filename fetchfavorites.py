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

config = vertx.config()

def response_handler(resp):
    @resp.body_handler
    def body_handler(body):
        if resp.status_code == 200:
            data = json.loads(body.to_string())
            for tweet in data:
                EventBus.send('log.event', "retweet.create")
                EventBus.send("retweet.create", tweet['id'])
            
def fetch_favorites(message):
    curators = json.loads(message.body)
    consumer = Consumer(api_endpoint="https://api.twitter.com/", consumer_key=config['consumer_key'], consumer_secret=config['consumer_secret'], oauth_token=config['oauth_token'], oauth_token_secret=config['oauth_token_secret'])
    for curator in curators:
        consumer.get("/1.1/favorites/list.json", {'user_id': curator['id'], 'count': 20}, response_handler)

# Update favorites every n minutes
def update_favorites(timer_id):
    EventBus.send('log.event', "curators.list")
    EventBus.send('curators.list', "")

EventBus.register_handler('curators.list.result', False, fetch_favorites)

vertx.set_periodic(1000 * 60 * 60, update_favorites)
vertx.set_timer(1000, update_favorites)