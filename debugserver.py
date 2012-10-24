import vertx

server = vertx.create_http_server()

@server.request_handler    
def request_handler(resp): 
    print resp.headers
    @resp.body_handler
    def body_handler(body):
        print "The total body received was %s bytes" % body.length
        print body
    
server.listen(8080)