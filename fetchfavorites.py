# coding=utf-8
"""
Lädt die Favoriten eines Users

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

def response_handler(resp, user_id):
    favs = {'user_id': user_id, 'favorites': []}
    @resp.body_handler
    def body_handler(body):
        if resp.status_code == 200:
            favs['favorites'] = json.loads(body.to_string())
        EventBus.send('log.event', "user.favorites.list.result")
        EventBus.send('user.favorites.list.result', json.dumps(favs))
            
def fetch_favorites(message):
    user_id = message.body
    consumer = Consumer(api_endpoint="https://api.twitter.com/", consumer_key=config['consumer_key'], consumer_secret=config['consumer_secret'], oauth_token=config['oauth_token'], oauth_token_secret=config['oauth_token_secret'])
    consumer.get("/1.1/favorites/list.json", {'user_id': user_id, 'count': 20}, lambda resp: response_handler(resp, user_id))

EventBus.register_handler('user.favorites.list', False, fetch_favorites)

