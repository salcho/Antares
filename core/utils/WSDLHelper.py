'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.utils.project_manager import project_manager
from core.data import logger
from core.exceptions import antaresUnknownException
from suds.client import Client
from suds.sax.text import Raw
from suds import WebFault
from suds import null
from urllib2 import URLError
from urlparse import urlparse
import exceptions
import urllib2
import os
import logging

#TODO: Terminar tipos de datos!!! http://www.w3.org/TR/xmlschema-2/#built-in-datatypes
CONTENT_TYPE_EXCEPTION = "Cannot process the message because the content type"
DEFAULT_STRING_VALUE = 'antares'
DEFAULT_UNKNOWN_VALUE = 'UNKNOWN'
DEFAULT_DECIMAL_VALUE = 1.0
DEFAULT_BOOLEAN_VALUE = 1
DEFAULT_INTEGER_VALUE = 10
DEFAULT_LONG_VALUE = 99999
DEFAULT_DATE_VALUE = '12/12/1990'

class WSDLHelper(object):

    
	def __init__(self):
		#logging.basicConfig(level=logging.DEBUG)
	        #logging.getLogger('suds.client').setLevel(logging.DEBUG)
	        self._client = None
		# client lib, used when loading wsdl from file
	        self._cllib = None

	        # control variables
	        self.serviceName = ''
	        self.portName = ''
		self.is_loaded = False
		logger.debug("WSDLHelper object instansiated")

	def loadWSDL(self, url):
		"""
		Will load a WSDL and create a ServiceDefinition of it:

		ServiceDefinition @ client.sd
	        ports = (port, [methods])
        	ports = (port, [(name, [args])])
	        ports = (port, [name, [(type, name)]])
		"""
		try:
			msg = ''
			if url.startswith('file'):
				self._cllib = urllib2.urlopen(project_manager.getURL())
				logger.info("Loaded wsdl from local path %s" % project_manager.getWSDLPath())
			else:
				self._cllib = urllib2.urlopen(project_manager.getURL())
				logger.info("Loaded wsdl from remote path %s" % project_manager.getURL())
			self._client = Client(url, faults=False)
			self.setup()
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
			self.is_loaded = True
			logger.info("Success loading WSDL from %s" % url)
		finally:
			if not self.is_loaded:
				logger.error("Failed loading WSDL from %s" % url)
			return msg

	def setup(self):
		"""
		Setup some control variables 
		"""
        	self.serviceName = self._client.sd[0].service.name
		self.portName = self._client.sd[0].ports[0][0].name

	"""
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
	"""
        
	def getMethods(self):
        	rsp = []
	        for sd in self._client.sd:
	            if sd.service.name == self.serviceName:
	                for port, methods in sd.ports:
	                    if port.name == self.portName:
	                        for name, args in methods:
	                            rsp.append(name)
	        return rsp					

	def getRqRx(self, opName):
		"""
		Craft and send a test request to the specified operation
		"""
		try:
			tosend = self.getParamObjs(opName)
			res = getattr(self._client.service, opName)(**tosend)
        	except Exception as e:
			raise antaresUnknownException("Got unknown exception in getRqRX() at WSDLHelper. " + e)
		except WebFault as e:
			raise antaresUnknownException("Got WebFault exception in getRqRx() at WSDLHelper!" + e)			
		else:	
			logger.warning("Error sending/getting sample req/rsp")
			return (None, None)
		finally:
			logger.info("Success getting sample data from WS")
			return (self._client.messages['tx'], self._client.messages['rx'])

	def getParamObjs(self, opName):
		"""
		Return parameters and sample data to be sent to the specified operation in the form of a dictionary
		"""

		tosend = {}
		try:
			for name, elem in self.getParams(opName):
				#Simple types
				#TODO: Set default type values: Enum, DateTime, Single
				if str(elem.type[0]) == 'string':
					tosend[name] = DEFAULT_STRING_VALUE
				elif str(elem.type[0]) == 'decimal':
					tosend[name] = DEFAULT_DECIMAL_VALUE
				elif str(elem.type[0]) == 'int':
					tosend[name] = DEFAULT_INTEGER_VALUE
				elif str(elem.type[0]) == 'boolean':
					tosend[name] = DEFAULT_BOOLEAN_VALUE
				elif str(elem.type[0]) == 'long':
					tosend[name] = DEFAULT_LONG_VALUE
				#TODO: Please set a proper date. You should be ashamed
				elif str(elem.type[0]) == 'date':
					tosend[name] = DEFAULT_DATE_VALUE
				#Complex types
				else:
					param = self._client.factory.create('{' + elem.type[1] + '}' + elem.type[0])
					for key in param.__keylist__:
						#TODO: How to know type value?
						param[key] = DEFAULT_UNKNOWN_VALUE
						tosend[name] = param
		except Exception as e:
			print 'getParamObjs @ WSDLHelper: ' + str(e)
			tosend = {}
		return tosend
        
	def getParams(self, opName):
		"""
		Return parameter names of selected operation
		"""
        	for sd in self._client.sd:
			for port, methods in sd.ports:
				for name, args in methods:
					if name == opName:
						#Tuples: (name, Element)
						return args
		return None
    
	def getParamsSchema(self, opName):
		"""
		Return parameter's schema for selected op
		"""

		ret = []
		for name, elem in self.getParams(opName):
			if elem.type[1] and elem.type[0]:
				ret.append(self._client.factory.resolver.find('{' + elem.type[1] + '}' + elem.type[0]))
		return ret
    
	def getParamsNames(self, opName):
        	ret = []
		for name, elem in self.getParams(opName):
			ret.append(name)
		return ret
            
	def getBindings(self):
        	ret = []
		for sd in self._client.sd:
			for port, methods in sd.ports:
				ret.append(port)
		return ret

	def getServices(self):
        	ret = []
		for sd in self._client.sd:
			ret.append(sd.service.name)
		return ret

	def sendRaw(self, opName, xml):
		"""
		Send custom WSDL request from user interface
		"""
		res = getattr(self._client.service, opName)(__inject={'msg':xml})
		return self._client.messages['rx']
    
	def srvInfoDict(self):
		"""
		Create dictionary to show server's properties in UI
		#TODO: Rewrite this!
		"""
        	port = urlparse(self._cllib.url).port
		if not port:
			port = 80
		hostname = urlparse(self._cllib.url).hostname
		dict = {'hostname': hostname, 'port': port, 'header': self._cllib.headers.getheader('Server')}
		return dict

	def setPort(self, pName):
		if pName != '':
			self.portName = pName
			self._client.set_options(port=pName)

	def setService(self, sName):
        	if sName != '':
			self.serviceName = sName
			self._client.set_options(service=sName)

	def is_loaded(self):
		return is_loaded

wsdlhelper = WSDLHelper()
