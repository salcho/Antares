'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.data import logger
from core.exceptions import antaresUnknownException
from core.exceptions import antaresWrongCredentialsException
from core.utils.project_manager import project_manager
from core.utils.project_manager import AUTH_BASIC
from core.utils.project_manager import AUTH_WINDOWS
from core.utils.project_manager import AUTH_UNKNOWN
from core.data import ws_protocols
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
from suds.transport.https import HttpAuthenticated
from suds.transport.https import WindowsHttpAuthenticated
from suds.sax.text import Raw
from suds.sax.element import Element
from suds.xsd.sxbasic import Import
from suds.sax.attribute import Attribute
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
import socket
import fcntl
import struct

# TODO: Terminar tipos de datos!!! http://www.w3.org/TR/xmlschema-2/#built-in-datatypes
CONTENT_TYPE_EXCEPTION = "Cannot process the message because the content type"
MUST_UNDERSTAND = Attribute('SOAP-ENV:mustUnderstand', 'true')

class WSDLHelper(object):


	def __init__(self):
		#logging.basicConfig(level=logging.DEBUG)
		#logging.getLogger('suds.transport').setLevel(logging.DEBUG)
		self.ws_client = None
		# client lib, used when loading wsdl from file
		self.server_client = None

		#control variables
		self.serviceName = ''
		self.portName = ''
		#online/offline switch
		self.is_offline = True
		logger.debug("WSDLHelper object instansiated")
		
	# ---------------------------------
	# Config methods
	# ---------------------------------

	def loadWSDL(self, url):
		"""
		This function should be called right after the project_manager has loaded any projects,
		it will query the PM in order to perform authentication tasks before loading the WSDL and
		URL objects used to represent the EndPoint.

		Error handling is a quite a mess here.
		Default HTTP timeout is set from command line or default (100 seconds) if not specified. 
		The url parameter may point to the offline WSDL copy in the filesystem while pm.getURL() will give EndPoint's addr.
		A WSDL file can be loaded from it's offline copy while the document contains _a_ valid EndPoint's IP addr. 

		ServiceDefinition @ client.sd
	        ports = (port, [methods])
        	ports = (port, [(name, [args])])
	        ports = (port, [name, [(type, name)]])
		"""
		try:
			msg = ''
			
			# Check for protocol authentication methods
			if project_manager.getAuthType() == AUTH_BASIC:
				if project_manager.getUsername() and project_manager.getPassword():
					try:
						self.ws_client = Client(url, username=project_manager.getUsername(), password=project_manager.getPassword(), 
											faults=True, prettyxml=True, cache=None)
						request = project_manager.createAuthorizationRequest(project_manager.getUsername(), 
																	project_manager.getPassword(), 
																	project_manager.getURL(),
																	project_manager.getDomain())
						self.server_client = urllib2.urlopen(request)
					except URLError as e:
						try:
							if e.code == 401:
								msg = 'Error: Something went wrong while trying to authenticate with saved credentials -> %s' % str(e)
								logger.error('Credentials %s:%s [Basic] for project %s stopped working' % (project_manager.getUsername(), 
																									project_manager.getPassword(), 
																									project_manager.getName()))
								return msg
						except:
							msg = "\tWarning:\nWasn't able to connect to target.\nAntares is running in offline mode now."
			elif project_manager.getAuthType() == AUTH_WINDOWS:
				# Can we do this?
				try:
					import ntlm
					if project_manager.getUsername() and project_manager.getPassword():
						ntlm_transport = WindowsHttpAuthenticated(username='%s\\%s' % (project_manager.getDomain(), project_manager.getUsername()), 
														password=project_manager.getPassword())
						self.server_client = project_manager.createNTLMRequest(project_manager.getUsername(), project_manager.getPassword(), 
																		project_manager.getURL(), project_manager.getDomain())
						self.ws_client = Client(url, transport=ntlm_transport, faults=True, prettyxml=True, cache=None)
				except ImportError:
					msg = "Error: The project you're trying to load uses Windows authentication\n"
					msg += "but we couldn't load the proxy_ntlm third party package.\n"
					msg += "Please install it before proceeding. "
					return msg
				
				except (antaresWrongCredentialsException, TransportError) as e:
					msg = 'Error: Something went wrong while trying to authenticate with saved credentials -> %s' % str(e) 
					logger.error('Credentials %s:%s [NTLM] for project %s stopped working' % (project_manager.getUsername(), 
																						project_manager.getPassword(), 
																						project_manager.getName()))
					return msg

			else:
				if project_manager.getAuthType() == AUTH_UNKNOWN:
					msg = "Warning: Antares detected an unknown protocol mechanism for this EndPoint!\n"
					msg = "We probably won't be able to connect to the service."
				
				# Or fallback to regular connections
				self.ws_client = Client(url, faults=True, prettyxml=True, cache=None)
				self.server_client = urllib2.urlopen(project_manager.getURL())
			
			self.setup()
			
			if self.ws_client:
				msg = 'OK'
				logger.info("WSDL helper is:\n %s" % self.ws_client)
			if url.startswith('file'):
				logger.info("Loaded wsdl from local path %s" % project_manager.getWSDLPath())
			else:
				logger.info("Loaded wsdl from remote path %s" % project_manager.getURL())
		except exceptions.ValueError:
			msg = "Error: Malformed URL\n" + url
		except URLError:
			msg = "Error: No route to host\n " + url
		except os.error:
			msg = "Error: Can't read offline WSDL file"
		except SAXParseException as e:
			msg = 'Error: Malformed WSDL. Are you sure you provided the correct WSDL path?'
		except TypeNotFound as e:
			msg = "Error: There is an import problem with this WSDL.\n We hope to add automatic fix for this in the future."
			msg += "\nReference is: https://fedorahosted.org/suds/wiki/TipsAndTricks#Schema-TypeNotFound"
		except TransportError as e:
			msg = 'Error: Something went wrong while trying to authenticate with saved credentials'
			logger.error('Credentials %s:%s for project %s stopped working' % (project_manager.getUsername(), 
																						project_manager.getPassword(), 
																						project_manager.getName()))
		except Exception as e:
			msg = 'FATAL: unmanaged exception. Check stderr : ' + e.message
			print e.__dict__
			print type(e)
			raise antaresUnknownException("Got unknown exception while loading wsdl at WSDLHelper: %s" % str(e) )
	
		# Check how we'll run
		if self.server_client:
			self.is_offline = False	
		else:
			logger.error("Running in offline mode on %s" % url)
		return msg
	
	def setup(self):
		"""
		Setup some control variables 
		"""
		self.serviceName = self.ws_client.sd[0].service.name
		self.portName = self.ws_client.sd[0].ports[0][0].name

	def findProtocol(self, ns):
		"""
		See if we recognize this protocol from it's
		namespace
		"""
		for k,v in ws_protocols:
			if v in ns:
				return k
		return None
		
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
			#logger.error("Got WebFault sending raw request: %s", wf.message)
			res = str(wf.fault)
			raise Exception(wf.message)
		except Exception as e:
			self.processException(e)
		return res
	
	def getRqRx(self, opName):
		"""
		Craft and send a test request to the specified operation
		Return: request template + response
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
			txt = self.processException(e)
			ret = (txt, self.ws_client.messages['rx'])
		return ret 

	def addAddressing(self, opName):
		wsa = ('wsa', 'http://schemas.xmlsoap.org/2004/08/addressing')
		wsa10 = ('wsa10', 'http://www.w3.org/2005/08/addressing')
		local_ip = self.getLocalIP()
		if not local_ip:
			local_ip = '127.0.0.1'
		ep_ref = Element('EndpointReference', ns=wsa).insert(Element('Address', wsa)).setText('http://%s/antares_endpoint' % local_ip)
		wsa_from = Element('From', ns=wsa).insert(ep_ref)
		fault_to = Element('FaultTo', ns=wsa).insert(ep_ref)
		reply_to = Element('ReplyTo', ns=wsa).insert(ep_ref)
		reply_to.append(MUST_UNDERSTAND)
		goes_to = Element('To', ns=wsa).setText('XXXXXXXXXXXXXXXX').append(MUST_UNDERSTAND)
		action = Element('Action', ns=wsa).setText(self.getAction(opName))
		
		headers = []
		headers.append(wsa_from)
		headers.append(fault_to)
		headers.append(reply_to)
		headers.append(goest_to)
		headers.append(action)
		#pass!
		
		
	
	def processException(self, except_obj):
		"""
		All methods interacting with the EndPoint should call this function if they found
		a general Exception. Suds will raise some of these with authentication messages.
		This function will return the HTTP code error int
		"""
		try:
			msg = except_obj.message
			txt = ''
			# HTTP Authentication here
			if u'Unauthorized' in msg[1]:
				# We should probably tell to proj_man here 
				logger.error("Got HTTP code 401, please specify HTTP credentials in the config tab!")
				txt = 'Got a 401 Unauthorized HTTP packet. \nThat means this EndPoint requires protocol authentication.\n\n'
				txt += "Fortunately, you can specify these credentials in the configuration tab."
			elif msg[0] == 404:
				logger.error("Got HTTP code 404, Not Found! Removed??")
				txt = "Got a 404 Not Found HTTP packet. \nThe EndPoint might have changed it's location.\n\nCheck URL!"
			else:
				print except_obj.__dict__
				print type(except_obj)
				logger.error("Unknown exception at processException. Data is: %s" % except_obj.__dict__)
			return txt
		except:
			pass
		
	# ------------------
	# Getters and setters
	# ------------------"

	def getAction(cl, method):
	        try:
        	        m = getattr(cl.service, method)
                	action = cl.wsdl.services[0].ports[0].methods[method].soap.action
        	        action = action.replace('"', '')
	        except MethodNotFound:
        	        # "[-] MethodNotFound"
                	return None
	        return action

	def getInterfaces(self):
		"""
		Get all interfaces on the system
		Found on http://code.activestate.com/recipes/439093/#c1
		"""
	        max_possible = 128 # arbitrary. raise if needed.
        	bytes = max_possible * 32
	        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	        names = array.array('B', '\0' * bytes)
	        outbytes = struct.unpack('iL', fcntl.ioctl(
	        s.fileno(),
	        0x8912, # SIOCGIFCONF
	        struct.pack('iL', bytes, names.buffer_info()[0])
	        ))[0]
	        namestr = names.tostring()
	        lst = []
	        for i in range(0, outbytes, 40):
	                name = namestr[i:i+16].split('\0', 1)[0]
	                ip = namestr[i+20:i+24]
	                lst.append(name)
	        return lst

	def getLocalIP(self):
		"""
		Get IP address associated to an interface
		Found on http://code.activestate.com/recipes/439094-get-the-ip-address-associated-with-a-network-inter/
		"""
		ifaces = getInterfaces()
		for ifname in sorted(ifaces):
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				ret = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
				return ret
			except IOError:
				continue
		return None

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
		try:
			if self.is_offline:
				return project_manager.currSettings['server'] 
			else:
				return self.server_client.headers.dict
		except:
			return self.server_client.headers.dict
		
	def getNamespaces(self):
		"""
		Get all namespaces from the <definitions> tag.
		This should gives us a fair idea of what protocols are in use.
		""" 
		return self.ws_client.wsdl.root.nsprefixes
	
	def getSOAPActionHeader(self, opName):
		for op in self.ws_client.wsdl.root.childrenAtPath('binding/operation'):
			if opName == op.getAttribute('name').value:
				soap_op = op.getChild('operation')
				return soap_op.getAttribute('soapAction').value
		return None

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

	def is_offline(self):
		return self.is_offline

wsdlhelper = WSDLHelper()
