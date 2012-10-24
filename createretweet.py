# coding=utf-8
"""
Re-tweetet tweets

@author Markus Tacker <m@coderbyheart.de>
"""
import vertx
from oauth import Consumer
from core.event_bus import EventBus
from com.xhaus.jyson import JysonCodec as json

config = vertx.config()

def response_handler(resp):
    @resp.body_handler
    def body_handler(body):
        if resp.status_code == 200:
            data = json.loads(body.to_string())
            print "Retweeted https://twitter.com/%s/status/%d" % (data['retweeted_status']['user']['screen_name'], data['retweeted_status']['id'])
        else:
            print "ERROR! " + body.to_string()

def create_retweet(message):
    consumer = Consumer(api_endpoint="https://api.twitter.com/", consumer_key=config['consumer_key'], consumer_secret=config['consumer_secret'], oauth_token=config['oauth_token'], oauth_token_secret=config['oauth_token_secret'])
    consumer.post("/1.1/statuses/retweet/%d.json" % message.body, None, response_handler)

EventBus.register_handler('retweet.create', False, create_retweet)

