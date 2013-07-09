'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from suds.client import Client
from core.utils.project_manager import pm
from suds.sax.text import Raw
#from suds.plugin import *
from urllib2 import URLError
from urlparse import urlparse
import exceptions
import urllib2
import os
import logging

CONTENT_TYPE_EXCEPTION = "Cannot process the message because the content type"

class WSDLHelper(object):
    
    def __init__(self):
	#logging.basicConfig(level=logging.DEBUG)
	#logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
        self._client = None
        self._cllib = None
	
        
    def loadWSDL(self, url):
        #ServiceDefinition @ client.sd
        #ports = (port, [methods])
        #ports = (port, [(name, [args])])
        #ports = (port, [name, [(type, name)]])
        try:
            msg = ''
            self.cllib = urllib2.urlopen(url)
            self._client = Client(url, autoblend=True)
	    print self._client
	    self.fixHeaders(url)
        except URLError:
            msg =  "Error: Can't connect to " + url
        except exceptions.ValueError:
            msg =  "Error: Malformed URL\n" + url
        except os.error:
            msg =  "Error: Can't write to offline WSDL file"
        except Exception as e:
            msg = 'Error: loadWSDL @ WSDLHelper ' + str(e) + '; ' + type(e)
        else:
	    msg = 'OK'
	finally:
            return msg

    def fixHeaders(self, url):
	try:
		port, methods = self._client.sd[0].ports[0]
		name, args = methods[0]
		res = getattr(self._client.service, name)()
		print res
	except Exception as e:
		txt = str(e)
		if CONTENT_TYPE_EXCEPTION in txt:
			types = txt.split("'")
			#TODO: Delete
			#print 'type2: ' + types[3]
			self._client.set_options(headers={'Content-Type':types[3]})
		print type(e)
		print e
		return False
	else:
		return True

    def getMethods(self):
	rsp = []
	#TODO: if self._client:
	for sd in self._client.sd:
		for port, methods in sd.ports:
			for name, args in methods:
				rsp.append(name)
	return rsp					

    def getRqRx(self, opName):
	tosend = []
	try:
		for name, elem in self.getParams(opName):
			#Simple types
			#TODO: Set default type values
			if elem.type:
				if str(elem.type[0]) == 'string':
					tosend.append('hola')
				elif str(elem.type[0]) == 'decimal':
					tosend.append(12)
				elif str(elem.type[0]) == 'int':
					tosend.append(10)
			#TODO: Complex types
			#Use factory
			else:
				pass
		res = getattr(self._client.service, opName)(tosend)
	except Exception as e:
		print type(e)
		print 'getRqRx @ WSDLHelper ' + e
	else:	
		return (None, None)
	finally:
		return (self._client.messages['tx'], self._client.messages['rx'])

    def getParams(self, opName):
	for sd in self._client.sd:
		for port, methods in sd.ports:
			for name, args in methods:
				if name == opName:
					#Tuples: (name, Element)
					return args
	return None

    def sendRaw(self, opName, xml):
	#Inject raw XML from UI
	res = getattr(self._client.service, opName)(__inject={'msg':xml})
	return self._client.messages['rx']
    
    #Creates dict to show info in GUI
    def srvInfoDict(self):
        port = urlparse(self.cllib.url).port
        if not port:
            port = 80
        hostname = urlparse(self.cllib.url).hostname
        dict = {'hostname': hostname, 'port': port, 'header': self.cllib.headers.getheader('Server')}
        return dict

wsdlhelper = WSDLHelper()
