'''
Created on Aug 9, 2013

@author: salchoman@gmail.com - salcho
'''

class wsResponse:
    
    def __init__(self, id=-1, params=None, size=-1, response=None, payload=None, plugin=None):
        self.id = id
        self.params = params
        self.size = size
        self.http_code = -1
        self.response = None

        self.response = response[0] if response[0] else None
        self.body = response[1] if response[1] else None
        #self.http_code = response[1][0] if response[1][0] else -1
        self.http_code = 200
        self.payload = payload
        self.plugin = plugin
        
    def getID(self):
        return self.id
    
    def getParams(self):
        return self.params
    
    def getSize(self):
        return self.size
    
    def getBody(self):
        return self.body
    
    def getHTTPCode(self):
        return self.http_code
    
    def getResponse(self):
        return self.response
    
    def getPayload(self):
        return self.payload
    
    def getPlugin(self):
        return self.plugin