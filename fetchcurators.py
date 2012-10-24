# coding=utf-8
"""
Lädt die Liste mit den Curatoren des Accounts

@author Markus Tacker <m@coderbyheart.de>
"""
import vertx
import mutex
import time
from com.xhaus.jyson import JysonCodec as json
from oauth import Consumer
from core.event_bus import EventBus

config = vertx.config()
curators = None
fetching = mutex.mutex()

def response_handler(resp):
    # TODO: Error handling 
    # print "got response %s" % resp.status_code
    # print resp.headers
    @resp.body_handler
    def body_handler(body):
        global curators
        if resp.status_code == 200:
            data = json.loads(body.to_string())
            curators = []
            for user in data['users']:
                curators.append({'screen_name': user['screen_name'], 'id': user['id']})
            fetching.unlock()
            EventBus.send('log.event', "curators.list.result")
            EventBus.send('curators.list.result', json.dumps(curators))
            
def list_curators(message):
    global fetching
    if curators is None:
        if not fetching.testandset():
            return
        consumer = Consumer(api_endpoint="https://api.twitter.com/", consumer_key=config['consumer_key'], consumer_secret=config['consumer_secret'], oauth_token=config['oauth_token'], oauth_token_secret=config['oauth_token_secret'])
        consumer.get("/1.1/lists/members.json", {'slug': config['curatorslist'], 'owner_screen_name': config['account']}, response_handler)
    else:
        EventBus.send('log.event', "curators.list.result (Cached)")
        EventBus.send('curators.list.result', json.dumps(curators))

EventBus.register_handler('curators.list', False, list_curators)
