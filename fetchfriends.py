# coding=utf-8
"""
Lädt die Liste mit den Freunden des Accounts

@author Markus Tacker <m@coderbyheart.de>
"""
import vertx
import mutex
import time
from com.xhaus.jyson import JysonCodec as json
from oauth import Consumer
from core.event_bus import EventBus

config = vertx.config()
friends = None
fetching = mutex.mutex()

def response_handler(resp):
    # TODO: Error handling 
    # print "got response %s" % resp.status_code
    # print resp.headers
    @resp.body_handler
    def body_handler(body):
        global friends
        if resp.status_code == 200:
            data = json.loads(body.to_string())
            friends = []
            for id in data['ids']:
                friends.append(id)
            fetching.unlock()
            EventBus.send('log.event', "friends.list.result")
            EventBus.send('friends.list.result', json.dumps(friends))
            # TODO: Paging
            
def list_friends(message):
    global fetching
    if friends is None:
        if not fetching.testandset():
            return
        consumer = Consumer(api_endpoint="https://api.twitter.com/", consumer_key=config['consumer_key'], consumer_secret=config['consumer_secret'], oauth_token=config['oauth_token'], oauth_token_secret=config['oauth_token_secret'])
        consumer.get("/1.1/friends/ids.json", {'screen_name': config['account']}, response_handler)
    else:
        EventBus.send('log.event', "friends.list.result (Cached)")
        EventBus.send('friends.list.result', json.dumps(friends))

EventBus.register_handler('friends.list', False, list_friends)
