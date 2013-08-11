'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.utils.project_manager import project_manager
from core.data import logger
from core.exceptions import antaresUnknownException

from core.data import DEFAULT_ANYURI_VALUE
from core.data import DEFAULT_BASE64BINARY_VALUE
from core.data import DEFAULT_BOOLEAN_VALUE
from core.data import DEFAULT_DATE_VALUE
from core.data import DEFAULT_DATETIME_VALUE
from core.data import DEFAULT_DECIMAL_VALUE
from core.data import DEFAULT_DOUBLE_VALUE
from core.data import DEFAULT_DURATION_VALUE
from core.data import DEFAULT_FLOAT_VALUE
from core.data import DEFAULT_GDAY_VALUE
from core.data import DEFAULT_GMONTH_VALUE
from core.data import DEFAULT_GMONTHDAY_VALUE
from core.data import DEFAULT_GYEAR_VALUE
from core.data import DEFAULT_GYEARMONTH_VALUE
from core.data import DEFAULT_HEXBINARY_VALUE
#from core.data import DEFAULT_NOTATION_VALUE
from core.data import DEFAULT_STRING_VALUE
from core.data import DEFAULT_TIME_VALUE
from core.data import DEFAULT_INTEGER_VALUE
from core.data import DEFAULT_LONG_VALUE

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

# TODO: Terminar tipos de datos!!! http://www.w3.org/TR/xmlschema-2/#built-in-datatypes
CONTENT_TYPE_EXCEPTION = "Cannot process the message because the content type"


class WSDLHelper(object):


	def __init__(self):
		#logging.basicConfig(level=logging.DEBUG)
		#logging.getLogger('suds.client').setLevel(logging.DEBUG)
		self.ws_client = None
		# client lib, used when loading wsdl from file
		self.server_client = None

		#control variables
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
				self.server_client = urllib2.urlopen(project_manager.getURL())
				logger.info("Loaded wsdl from local path %s" % project_manager.getWSDLPath())
			else:
				self.server_client = urllib2.urlopen(project_manager.getURL())
				logger.info("Loaded wsdl from remote path %s" % project_manager.getURL())
			self.ws_client = Client(url, faults=False)
			self.setup()
		except URLError:
			msg = "Error: Can't connect to " + url
		except exceptions.ValueError:
			msg = "Error: Malformed URL\n" + url
		except os.error:
			msg = "Error: Can't write to offline WSDL file"
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
		self.serviceName = self.ws_client.sd[0].service.name
		self.portName = self.ws_client.sd[0].ports[0][0].name

	def getMethods(self):
		"""
		Return all methods
		"""
		rsp = []
		for sd in self.ws_client.sd:
			if sd.service.name == self.serviceName:
				for port, methods in sd.ports:
					if port.name == self.portName:
						for name, args in methods:
							rsp.append(name)
		return rsp					

	def getRqRx(self, opName):
		"""
		Craft and send a test request to the specified operation
		Return request template + response
		"""
		try:
			tosend = self.getParamObjs(opName)
			res = getattr(self.ws_client.service, opName)(**tosend)
		except Exception as e:
			raise antaresUnknownException("Got unknown exception in getRqRX() at WSDLHelper. " + str(e))
		except WebFault as e:
			raise antaresUnknownException("Got WebFault exception in getRqRx() at WSDLHelper!" + e)			
		else:	
			logger.warning("Error sending/getting sample req/rsp")
			return (None, None)
		finally:
			logger.info("Success getting sample data from WS")
			return (self.ws_client.messages['tx'], self.ws_client.messages['rx'])

	def getParamObjs(self, opName):
		"""
		Return parameters and sample data to be sent to the specified operation in the form of a dictionary
		"""

		tosend = {}
		#target_params = set()
		try:
			"""
			if params and len(params) > 0:
				for name, elem in self.getParams(opName):
					if name in params:
						target_params.add((name, elem))
			else:
				target_params = self.getParams(opName) 
			"""
			for name, elem in self.getParams(opName):
				# Simple types
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
				# TODO: Please set a proper date. You should be ashamed
				elif str(elem.type[0]) == 'date':
					tosend[name] = DEFAULT_DATE_VALUE
				# Complex types
				else:
					enums = self.findEnumerations(elem.type)
					if len(enums) > 0:
						for enum in enums:
							tosend[name] += enum + '|'
				
		except Exception as e:
			print 'getParamObjs @ WSDLHelper: ' + str(e)
			tosend = {}
		return tosend
	
	"""
	Create and send a request with the specified payload in all the specified parameters of the specified opName
	Return data is a tuple of the response body and what was received in each parameter
	"""
	def customRequest(self, opName, params, payload):
		try:
			if not opName or not params or not payload:
				return None
			
			tosend = {}
			for name, elem in self.getParams(opName):
				if name in params:
					tosend[name] = payload
					
			res = getattr(self.ws_client.service, opName)(**tosend)
			return (self.ws_client.messages['rx'], res)
		except Exception as e:
			print ("Got unknown exception in customRequest() at WSDLHelper. " + e)

	def findEnumerations(self, type):
		"""
		This function receives an element type (That is: type[0] -> name, type[1] -> namespace)
		It will find if it corresponds to enumeration values and return all possible values
		This function could work as a generic factory in the future, but that's to be seen
		"""
		
		ret = set()
		category = self.ws_client.factory.create('{' + type[1] + '}' + type[0])
		for key in category.__keylist__:
			ret.add(getattr(category, key))
		return ret
	
	def getParams(self, opName):
		"""
        Return parameter tuples (name, element) of selected operation
        """
		for sd in self.ws_client.sd:
			for port, methods in sd.ports:
				for name, args in methods:
					if name == opName:
						# Tuples: (name, Element)
						return args
		return None
	
	def getParamsSchema(self, opName):
		"""
		Return parameter's schema for selected op
		"""

		ret = []
		for name, elem in self.getParams(opName):
			if elem.type[1] and elem.type[0]:
				ret.append(self.ws_client.factory.resolver.find('{' + elem.type[1] + '}' + elem.type[0]))
		return ret
	
	def getParamsNames(self, opName):
		"""
		Return parameter names. Should this be deleted?
		"""
		ret = []
		if self.getParams(opName):
			for name, elem in self.getParams(opName):
				ret.append(name)
		return ret
	
	def getBindings(self):
		ret = []
		for sd in self.ws_client.sd:
			for port, methods in sd.ports:
				ret.append(port)
		return ret

	def getServices(self):
		ret = []
		for sd in self.ws_client.sd:
			ret.append(sd.service.name)
		return ret

	def sendRaw(self, opName, xml):
		"""
		Send custom WSDL request from user interface
		"""
		res = getattr(self.ws_client.service, opName)(__inject={'msg':xml})
		return self.ws_client.messages['rx']
	
	def getHeaders(self):
		"""
		Create dictionary to show server's properties in UI
		"""
		return self.server_client.headers.dict

	def setPort(self, pName):
		if pName != '':
			self.portName = pName
			self.ws_client.set_options(port=pName)

	def setService(self, sName):
		if sName != '':
			self.serviceName = sName
			self.ws_client.set_options(service=sName)

	def getServerClient(self):
		return self.server_client

	def is_loaded(self):
		return self.is_loaded

wsdlhelper = WSDLHelper()
