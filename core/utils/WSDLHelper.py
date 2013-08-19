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
from suds.client import TransportError
from suds.sax.text import Raw
from suds import WebFault
from suds import null
from suds import TypeNotFound

from urllib2 import URLError
from urlparse import urlparse

from xml.sax._exceptions import SAXParseException

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
		
	# ---------------------------------
	# Config methods
	# ---------------------------------

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
			self.ws_client = Client(url, faults=True, prettyxml=True)
			self.setup()
		except URLError:
			msg = "Error: Can't connect to " + url
		except exceptions.ValueError:
			msg = "Error: Malformed URL\n" + url
		except os.error:
			msg = "Error: Can't write to offline WSDL file"
		except SAXParseException as e:
			msg = 'Error: Malformed WSDL. Are you sure you provided the correct WSDL path?'
		except TypeNotFound as e:
			msg = "Error: There is an import problem with this WSDL.\n We hope to add automatic fix for this in the future."
			msg += "\nReference is: https://fedorahosted.org/suds/wiki/TipsAndTricks#Schema-TypeNotFound"
		except Exception as e:
			msg = 'Error: unmanaged exception. Check stderr : ' + e.message
			print e.__dict__
			print type(e)
			raise antaresUnknownException("Got unknown exception while loading wsdl at WSDLHelper: %s" % str(e.__dict__))
	
		# Check if we are ok	
		if self.ws_client:
			msg = 'OK'
			self.is_loaded = True
			logger.info("Success loading WSDL from %s" % url)
			
		if not self.is_loaded:
			logger.error("Failed loading WSDL from %s" % url)
		return msg
	
	def setup(self):
		"""
		Setup some control variables 
		"""
		self.serviceName = self.ws_client.sd[0].service.name
		self.portName = self.ws_client.sd[0].ports[0][0].name
		
	# -------------------------
	# Manipulating requests
	# -------------------------
	"""
	Create and send a request with the specified payload in all the specified parameters of the specified opName
	Return data is a tuple of the response body and what was received in each parameter
	"""
	def customRequest(self, opName, params, payload):
		ret = (None, None)
		res = None
		try:
			if not opName or not params or not payload:
				return None
			
			tosend = self.getParamObjs(opName)
			for name, elem in self.getParams(opName):
				if name in params:
					tosend[name] = payload
					
			res = getattr(self.ws_client.service, opName)(**tosend)
		except WebFault as e:
			logger.error("Got WebFault exception at customRequest: %s" % e.message)
			ret = (str(e.message), res)
		except Exception as e:
			error = self.processException(e)
			if error == 401:
				# How do we stop this mess?
				pass
		else:
			ret = (str(self.ws_client.messages['rx']), res)
			
		return ret

	def findEnumerations(self, type):
		"""
		This function receives an element type (That is: type[0] -> name, type[1] -> namespace)
		It will find if it corresponds to enumeration values and return all possible values
		This function could work as a generic factory in the future, but that's to be seen
		"""
		
		ret = set()
		category = self.ws_client.factory.create('{' + type[1] + '}' + type[0])
		for key in category.__keylist__:
			ret.add(key)
		return ret

	def sendRaw(self, opName, xml):
		"""
		Send custom WSDL request from user interface
		"""
		res = None
		try:
			getattr(self.ws_client.service, opName)(__inject={'msg':xml})
			res = self.ws_client.messages['rx']
		except WebFault as wf:
			logger.error("Got WebFault sending raw request: %s", wf.message)
			res = str(wf.message)
		except Exception as e:
			self.processException(e)
		return res
	
	def getRqRx(self, opName):
		"""
		Craft and send a test request to the specified operation
		Return request template + response
		"""
		ret = (None, None)
		try:
			tosend = self.getParamObjs(opName)
			# tosend might be empty, this should be caught by the WebFault exception at retrieval
			getattr(self.ws_client.service, opName)(**tosend)
			ret = (self.ws_client.messages['tx'], self.ws_client.messages['rx'])
		except WebFault as e:
			logger.error("Got WebFault sending request: %s" % e.message)
			ret = (self.ws_client.messages['tx'], str(e.message))
		except TransportError as te:
			logger.error("Got TransportError sending request: %s" % te.message)
		# suds client class may just raise a regular Exception to tell us of HTTP code 401	
		except Exception as e:
			error = self.processException(e)
			if error == 401:
				txt = 'Got a 401 Unauthorized HTTP packet. \nThat means this EndPoint requires HTTP authentication.\n\n'
				txt += "Such method is known for being vulnerable to bruteforcing. \n"
				txt += "Fortunately, you can specify these credentials in the configuration tab."
				ret = (txt, None)
		return ret 
	
	def processException(self, except_obj):
		"""
		All methods interacting with the EndPoint should call this function if they found
		a general Exception. Suds will raise some of these with authentication messages.
		This function will return the HTTP code error int
		"""
		msg = except_obj.message
		# HTTP Authentication here
		if u'Unauthorized' in msg[1]:
			# Tell everyone 
			logger.error("Got HTTP code 401, please specify HTTP credentials in the config tab!")
			return 401
		else:
			logger.error("Unknown exception pat porcessException. Data is: %s" % msg)
		
	# ------------------
	# Getters and setters
	# ------------------"

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

	def getParamObjs(self, opName):
		"""
		Return parameters and sample data to be sent to the specified operation in the form of a dictionary
		"""

		tosend = {}
		try:
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
						tosend[name] = ''
						for enum in enums:
							tosend[name] += enum + '|'
				
		except Exception as e:
			tosend = {}
			raise antaresUnknownException("getParamObjs got unknown exception: " + e.message)
		return tosend
	
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
