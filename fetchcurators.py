import vertx
import random
from hashlib import sha1
import hmac
import binascii
import time
import urllib
from com.xhaus.jyson import JysonCodec as json

config = vertx.config()
account = config['account']
list = config['curatorslist']
consumer_key = config['consumer_key']
consumer_secret = config['consumer_secret']
oauth_token = config['oauth_token']
oauth_token_secret = config['oauth_token_secret']
api_host = 'api.twitter.com'
api_ssl = True if not 'api_ssl' in config else config['api_ssl']
api_scheme = 'http' if not api_ssl else 'https'

def response_handler(resp):
    # TODO: Error handling 
    # print "got response %s" % resp.status_code
    # print resp.headers
    @resp.body_handler
    def body_handler(body):
        data = json.loads(body.to_string())
        for user in data['users']:
            print "@%s" % user['screen_name']

def sign_get(path, query=None):
    """
    Create an oauth signed GET request
    """
    method = "GET"    
    path = "/1.1/" + path + ".json"
    auth_params = {
      'oauth_consumer_key': consumer_key,
      'oauth_nonce': ''.join([str(random.randint(0, 9)) for i in range(32)]),
      #'oauth_nonce': "d5abdf4ee75698e48a09c784c47dab35",
      'oauth_signature_method': "HMAC-SHA1",
      'oauth_timestamp': int(time.time()),
      #'oauth_timestamp': 1350428144,
      'oauth_token': oauth_token,
      'oauth_version': "1.0"
    }
            
    sig_data = method + "&" + quote(api_scheme + "://" + api_host + path)
    params_encoded = []
    for key in sorted(auth_params.iterkeys()):
        params_encoded.append(quote(key) + "=" + quote("%s" % auth_params[key]))
    if query is not None:
        for key in sorted(query.iterkeys()):
            params_encoded.append(quote(key) + "=" + quote("%s" % query[key]))
    sig_data = sig_data + "&" + quote("&".join(params_encoded))
    signing_key = quote(consumer_secret) + "&" + quote(oauth_token_secret)
    
    hashed = hmac.new(signing_key, sig_data, sha1)
    signature = binascii.b2a_base64(hashed.digest())[:-1] 
    auth_params['oauth_signature'] = signature
            
    auth_params_encoded = []
    for key in sorted(auth_params.iterkeys()):
        auth_params_encoded.append('%s="%s"' % (quote(key), quote("%s" % auth_params[key])))
    auth = "OAuth " + ', '.join(auth_params_encoded)
    
    query_params = []
    query_str = ''
    for key in query:
        query_params.append('%s=%s' % (quote(key), quote("%s" % query[key])))
    if len(query_params) > 0:
       query_str = '&'.join(query_params)
         
    client = vertx.create_http_client()
    client.host = api_host
    client.ssl = api_ssl
    client.port = 80 if not api_ssl else 443
    
    request = client.get(path + ('?' + query_str if len(query_str) > 0 else ''), response_handler)
    request.put_header('Authorization', auth)
    request.end()

def quote(str):
    return urllib.quote(str, '')
    
sign_get('lists/members', {'slug': list, 'owner_screen_name': account})

