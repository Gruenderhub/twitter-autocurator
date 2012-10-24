# coding=utf-8
"""
Favorisiert tweets

@author Markus Tacker <m@coderbyheart.de>
"""
import vertx
from oauth import Consumer
from core.event_bus import EventBus

config = vertx.config()

def response_handler(resp):
    @resp.body_handler
    def body_handler(body):
        pass

def create_favorite(message):
    consumer = Consumer(api_endpoint="https://api.twitter.com/", consumer_key=config['consumer_key'], consumer_secret=config['consumer_secret'], oauth_token=config['oauth_token'], oauth_token_secret=config['oauth_token_secret'])
    consumer.post("/1.1/favorites/create.json", {'id': message.body}, response_handler)

EventBus.register_handler('favorite.create', False, create_favorite)
