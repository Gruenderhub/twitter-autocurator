"""
Jython 2.5 & vert.x kompatible Implementierung von OAuth

@author Markus Tacker <m@coderbyheart.de>
"""
import vertx
import random
from hashlib import sha1
import hmac
import binascii
import time
import urllib
from urlparse import urlparse

class Consumer(object):
    """
    Jython 2.5 & vert.x kompatible Implementierung von OAuth
    
    @author Markus Tacker <m@coderbyheart.de>
    """
    
    debug = False
    nonce = None
    timestamp = None
    
    def __init__(self, api_endpoint, consumer_key, consumer_secret, oauth_token, oauth_token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.api_endpoint = urlparse(api_endpoint)
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
    
    def get(self, path, query, response_handler):
        """
        Make an oauth signed GET request
        """
        return self.request(path=path, query=query, response_handler=response_handler)
    
    def post(self, path, query, response_handler):
        """
        Make an oauth signed POST request
        """
        return self.request(method="POST", path=path, query=query, response_handler=response_handler)
    
    def quote(self, str):
        return urllib.quote(str, '')
    
    def request(self, response_handler, method="GET", path="/", query=None):
        """
        Make an oauth signed request
        """
        
        if path[0] != "/":
           path = "/" + path
           
        # Data required for a sgned request 
        auth_params = {
          'oauth_consumer_key': self.consumer_key,
          'oauth_nonce': ''.join([str(random.randint(0, 9)) for i in range(32)]) if self.nonce is None else self.nonce,
          'oauth_signature_method': "HMAC-SHA1",
          'oauth_timestamp': int(time.time()) if self.timestamp is None else self.timestamp,
          'oauth_token': self.oauth_token,
          'oauth_version': "1.0"
        }
                
        # Build signature
        sig_data = method + "&" + self.quote(self.api_endpoint.scheme + "://" + self.api_endpoint.hostname + path)
        params_encoded = []
        for key in sorted(auth_params.iterkeys()):
            params_encoded.append(self.quote(key) + "=" + self.quote("%s" % auth_params[key]))
        if query is not None:
            for key in sorted(query.iterkeys()):
                params_encoded.append(self.quote(key) + "=" + self.quote("%s" % query[key]))
        sig_data = sig_data + "&" + self.quote("&".join(sorted(params_encoded)))
        signing_key = self.quote(self.consumer_secret) + "&" + self.quote(self.oauth_token_secret)
        hashed = hmac.new(signing_key, sig_data, sha1)
        signature = binascii.b2a_base64(hashed.digest())[:-1] 
        auth_params['oauth_signature'] = signature

        # Build oauth header                
        auth_params_encoded = []
        for key in sorted(auth_params.iterkeys()):
            auth_params_encoded.append('%s="%s"' % (self.quote(key), self.quote("%s" % auth_params[key])))
        auth = "OAuth " + ', '.join(auth_params_encoded)
        
        # Build request
        query_params = []
        query_str = ''
        if query is not None:
            for key in query:
                query_params.append('%s=%s' % (self.quote(key), self.quote("%s" % query[key])))
        if len(query_params) > 0:
           query_str = '&'.join(query_params)
             
        client = vertx.create_http_client()
        client.host = self.api_endpoint.hostname
        ssl = True if self.api_endpoint.scheme == "https" else False
        client.ssl = ssl
        if self.api_endpoint.port is None:
            client.port = 80 if not ssl else 443
        else:
            client.port = self.api_endpoint.port
            
        if self.debug:
            print "Compare this output to twitters OAuth tool"
            print "Signature base string:\n" + sig_data
            print "Authorization header:\nAuthorization: " + auth
            print "cURL command:\ncurl %s '%s://%s%s' --data '%s' --header 'Authorization: %s' --verbose" % ("--get" if method == 'GET' else "--request '%s'" % method, self.api_endpoint.scheme, self.api_endpoint.netloc, path, query_str, auth)
            
        if method == 'GET':
            request = client.get(path + ('?' + query_str if len(query_str) > 0 else ''), response_handler)
        else:
            request = client.post(path, response_handler)
            if len(query_str) > 0:
                request.put_header('Content-Length', len(query_str))
                request.put_header('Content-Type', "application/x-www-form-urlencoded")
                request.write_str(query_str)
        request.put_header('Authorization', auth)
        request.end()
