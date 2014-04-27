'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.data import logger
from controller import exceptions
from core.Singleton import Singleton	
from core.data import AUTH_BASIC
from core.data import AUTH_WINDOWS
from core.data import AUTH_UNKNOWN
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
from core.ProjectManager import ProjectManager	

# TODO: Terminar tipos de datos!!! http://www.w3.org/TR/xmlschema-2/#built-in-datatypes
CONTENT_TYPE_EXCEPTION = "Cannot process the message because the content type"
MUST_UNDERSTAND = Attribute('SOAP-ENV:mustUnderstand', 'true')

class WSDLHelper:
	__metaclass__ = Singleton

	def __init__(self):
		#logging.basicConfig(level=logging.DEBUG)
		#logging.getLogger('suds.client').setLevel(logging.DEBUG)
		self.project_manager = ProjectManager()
		self.ws_client = None
		# client lib, used when loading wsdl from file
		self.server_client = None
		# WSDL Descriptor
		self.wsdl_desc = None

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
        	ports = (port, [(name, [opers])])
	        ports = (port, [name, [(type, name)]])
		"""
		try:
			msg = ''
			
			# Check for protocol authentication methods
			if self.project_manager.getAuthType() == AUTH_BASIC:
				if self.project_manager.getUsername() and self.project_manager.getPassword():
					try:
						self.ws_client = Client(url, username=self.project_manager.getUsername(), password=self.project_manager.getPassword(), 
											faults=True, prettyxml=True, cache=None)
						request = self.project_manager.createAuthorizationRequest(self.project_manager.getUsername(), 
																	self.project_manager.getPassword(), 
																	self.project_manager.getURL(),
																	self.project_manager.getDomain())
						self.server_client = urllib2.urlopen(request)
					except URLError as e:
						try:
							if e.code == 401:
								msg = 'Error: Something went wrong while trying to authenticate with saved credentials -> %s' % str(e)
								logger.error('Credentials %s:%s [Basic] for project %s stopped working' % (self.project_manager.getUsername(), 
																									self.project_manager.getPassword(), 
																									self.project_manager.getName()))
								return msg
						except:
							msg = "\tWarning:\nWasn't able to connect to target.\nAntares is running in offline mode now."
			elif self.project_manager.getAuthType() == AUTH_WINDOWS:
				# Can we do this?
				try:
					import ntlm
					if self.project_manager.getUsername() and self.project_manager.getPassword():
						ntlm_transport = WindowsHttpAuthenticated(username='%s\\%s' % (self.project_manager.getDomain(), self.project_manager.getUsername()), 
														password=self.project_manager.getPassword())
						self.server_client = self.project_manager.createNTLMRequest(self.project_manager.getUsername(), self.project_manager.getPassword(), 
																		self.project_manager.getURL(), self.project_manager.getDomain())
						self.ws_client = Client(url, transport=ntlm_transport, faults=True, prettyxml=True, cache=None)
				except ImportError:
					msg = "Error: The project you're trying to load uses Windows authentication\n"
					msg += "but we couldn't load the proxy_ntlm third party package.\n"
					msg += "Please install it before proceeding. "
					return msg
				
				except (antaresWrongCredentialsException, TransportError) as e:
					msg = 'Error: Something went wrong while trying to authenticate with saved credentials -> %s' % str(e) 
					logger.error('Credentials %s:%s [NTLM] for project %s stopped working' % (self.project_manager.getUsername(), 
																						self.project_manager.getPassword(), 
																						self.project_manager.getName()))
					return msg

			else:
				if self.project_manager.getAuthType() == AUTH_UNKNOWN:
					msg = "Warning: Antares detected an unknown protocol mechanism for this EndPoint!\n"
					msg = "We probably won't be able to connect to the service."
				
				# Or fallback to regular connections
				self.ws_client = Client(url, faults=True, prettyxml=True, cache=None)
				self.server_client = urllib2.urlopen(self.project_manager.getURL())
			
			self.setup()
			
			if self.ws_client:
				self.wsdl_desc = WSDLDescription(self.ws_client.sd[0])
				msg = 'OK'
				logger.info("WSDL helper is:\n %s" % self.ws_client)
			if url.startswith('file'):
				logger.info("Loaded wsdl from local path %s" % self.project_manager.getWSDLPath())
			else:
				logger.info("Loaded wsdl from remote path %s" % self.project_manager.getURL())
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
			logger.error('Credentials %s:%s for project %s stopped working' % (self.project_manager.getUsername(), 
																						self.project_manager.getPassword(), 
																						self.project_manager.getName()))
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

	def findEnumerations(self, type, recur=False):
		"""
		This function receives an element type (That is: type[0] -> name, type[1] -> namespace)
		It will find if it corresponds to enumeration values and return all possible values
		If recur is True the object is nested inside other complex param 
		"""
		
		cmplx = '{%s}%s' % (type[1], type[0])
		elem = self.ws_client.factory.resolver.find(cmplx)
		xml = self.ws_client.factory.create(cmplx)
		args = [arg[0] for arg in elem.children()]
		
		# This could be just an enumeration
		if elem.enum():
			return dict(xml).keys()
		
		for arg in xml.__keylist__:
			items = getattr(xml, arg)
			if not items:
				for x in args:
					if x.name == arg:
						xml[arg] = x.type[0]
						break
			else:
				for k in items.__keylist__:
					xml[arg][k] = '1'
					
		ret = dict(xml)
		return dict(ret)	
		"""			
			 
		
			
		
		elem = self.ws_client.factory.resolver.find(cmplx)
		if recur:
			items = elem.attributes()
			at = self.ws_client.factory.create(cmplx)
		else:
			items = elem.children()
			
		for child in items:
			# This can be element or complex object
			obj = child[0]
			
			if obj.type[1] == schema:
				ret[obj.name] = obj.type[0]
			else:
				ret[obj.name] = {}
				ns = str(obj.namespace()[1])
				name = obj.type[0]
				print (ns, name)
				arg = self.ws_client.factory.create('{%s}%s' % (ns, name))
				#vals = self.findEnumerations((name, ns), recur=True)
				ret[obj.name][name] = dict(arg)
		print ret
		return ret
		"""
	
	def findSimpleTypes(self, elem):
		# XML Schema for comparison
		for t in ws_protocols:
			if t[0] == 'XML Schema':
				schema = t[1]	
				break
			
		if str(elem.type[0]) == 'string':
			return DEFAULT_STRING_VALUE
		elif str(elem.type[0]) == 'duration':
			return DEFAULT_DURATION_VALUE
		elif str(elem.type[0]) == 'dateTime':
			return DEFAULT_DATETIME_VALUE
		elif str(elem.type[0]) == 'time':
			return DEFAULT_TIME_VALUE
		elif str(elem.type[0]) == 'date':
			return DEFAULT_DATE_VALUE
		elif str(elem.type[0]) == 'gYearMonth':
			return DEFAULT_GYEARMONTH_VALUE
		elif str(elem.type[0]) == 'gYear':
			return DEFAULT_GYEAR_VALUE
		elif str(elem.type[0]) == 'gMonthDay':
			return DEFAULT_GMONTHDAY_VALUE
		elif str(elem.type[0]) == 'gDay':
			return DEFAULT_GDAY_VALUE
		elif str(elem.type[0]) == 'gMonth':
			return DEFAULT_GMONTH_VALUE
		elif str(elem.type[0]) == 'boolean':
			return DEFAULT_BOOLEAN_VALUE
		elif str(elem.type[0]) == 'base64Binary':
			return DEFAULT_BASE64BINARY_VALUE
		elif str(elem.type[0]) == 'hexBinary':
			return DEFAULT_HEXBINARY_VALUE
		elif str(elem.type[0]) == 'float':
			return DEFAULT_FLOAT_VALUE
		elif str(elem.type[0]) == 'decimal':
			return DEFAULT_DECIMAL_VALUE
		elif str(elem.type[0]) == 'int':
			return DEFAULT_INTEGER_VALUE
		elif str(elem.type[0]) == 'long':
			return DEFAULT_LONG_VALUE
		elif str(elem.type[0]) == 'double':
			return DEFAULT_DOUBLE_VALUE
		elif str(elem.type[0]) == 'anyURI':
			return DEFAULT_ANYURI_VALUE
		elif elem.type[1] == schema:
			return elem.type[0]
		else:
			return None

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
			ret = (self.ws_client.messages['tx'], 'This is an unsual error. Copy the HTTP packet for this request and investigate using a regular client')
			return ret
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
				#print except_obj.__dict__
				#print type(except_obj)
				logger.error("Unknown exception at processException. Data is: %s" % except_obj.message)
				
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
				simple = self.findSimpleTypes(elem)
				if simple:
					tosend[name] = simple
				# Complex types
				else:
					enums = self.findEnumerations(elem.type)
					if len(enums) > 0:
						tosend[name] = enums
		except Exception as e:
			tosend = {}
			print e.message
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
	
	def getParamsSchema(self, opName=None, obj=None):
		"""
		Return parameter's schema for selected op
		# TODO: This algorithm must be recursive
		"""
		ret = {}
		if opName:
			for name, elem in self.getParams(opName):
				if elem.type[1] and elem.type[0]:
					type = self.ws_client.factory.resolver.find('{' + elem.type[1] + '}' + elem.type[0])
					if not type.children():
						ret[name] = elem.type[0]
					else:
						ret[name] = self.getParamsSchema(obj=elem)
		else:
			type = self.ws_client.factory.resolver.find('{' + obj.type[1] + '}' + obj.type[0])
			# Check if this may be an enumeration
			if type.enum():
				type = self.ws_client.factory.create('{%s}%s' % (obj.type[1], obj.type[0]))
				ret[obj.type[0]] = '/'.join(type.__keylist__)
			else:
				for child in type.children():
					ret[child[0].name] = child[0].type[0]
					
		return ret
	
	def getElement(self, oper, param, cmplx=None):
		"""
		Get an element. If cmplx is not none get an input's element which is part of a complx object
		"""	
		for name, elem in self.getParams(oper):
			if name is param or name is cmplx:
				if cmplx:
					obj = self.ws_client.factory.resolver.find('{' + elem.type[1] + '}' + elem.type[0])
					for child in obj.children():
						if child[0].name is param:
							return child[0]
				else:
					return elem
		return None
	
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
				return self.project_manager.currSettings['server'] 
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

class WSDLDescription:
	
	def __init__(self, sd):
		# Service name
		self.name = sd.service.name
		# Target namespace
		self.ns = sd.wsdl.tns[1]
		# All operations per port
		self.port_ops = {}
		# All arguments
		self.opers = {}
		for i in range(len(sd.service.ports)):
			p = sd.service.ports[i]
			m = sd.ports[i]
			self.port_ops[p.name] = [x[0] for x in m[1]]
			for oper in m[1]:
				self.opers[oper[0]] = oper[1]

	def getServiceName(self):
		return self.name
	
	def getNamespace(self):
		return self.ns
	
	def getPorts(self):
		return self.port_ops.keys()
	
	def getOperations(self, port=None):
		if port:
			return self.port_ops[port]
		return self.port_ops
	
	def getOperationArguments(self, oper=None):
		if oper:
			return self.opers[oper]
		return self.opers
	
	def getArgumentType(self, oper=None, arg=None):
		if oper:
			for x in self.opers[oper]:
				if x[0] == arg:
					return x[1].type
		return None
	
	def txt(self):
		txt = 'Service name: %s' % self.name
		txt += 'TNS: %s' % self.ns
		for p in self.getPorts():
			txt += 'Port: %s' % p
			txt += 'Operations:\n'
			for op in self.getOperations(p):
				txt += '\tName: %s' % op
				txt += '\t\tArgs:'
				for arg in self.getOperationArguments(op):
					txt += '\t\t%s:%s' % (arg, self.getArgumentType(op, arg))
		return txt