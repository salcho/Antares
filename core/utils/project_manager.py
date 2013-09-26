'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.data import wsdl_name
from core.data import settings_name
from core.data import logger
from core.data import paths
from core.data import EXTRACT_IP_REGEX
from core.exceptions import antaresWrongCredentialsException
from urllib2 import HTTPError
from urllib2 import URLError
import os
import exceptions
import urllib2
import shutil
import base64
import re
import cPickle as pickle
from core.exceptions import antaresDependenciesException,\
	antaresUnknownException

AUTH_NONE = 0
AUTH_BASIC = 1
AUTH_DIGEST = 2
AUTH_UNKNOWN = 3
AUTH_WINDOWS = 4
AUTH_WSSE = 5

class projMan:
	
	def __init__(self):
		self.proj_name = ''
		self.proj_url = ''
	
		#currSettings is a dictionary with keys [control,server] which values are as presented in the config widget
		self.currSettings = {}
		self.currSettings['control'] = {'name': None, 'url': None}
		self.currSettings['server'] = {}
		self.currSettings['auth'] = {'type': None, 'domain': None, 'user': None, 'password': None}
		#automatic wsdl save flag
		self.save_flag = False
		logger.debug("Project manager instansiated")
	
	def createProject(self, name, url, auth_dict=None):
		"""
		This function receives the auth_dict parameter which contains optional HTTP authentication
		credentials. Such dictionary should follow the same structure as self.currSettings['auth'].
		"""
		fail = False
		try:
			msg = ''
			if auth_dict:
				if auth_dict and auth_dict['type'] == AUTH_BASIC:
					request = self.createAuthorizationRequest(auth_dict['user'], auth_dict['password'], url, domain=auth_dict['domain'])
					wsdl = urllib2.urlopen(request)
					self.currSettings['auth'] = auth_dict
				elif auth_dict and auth_dict['type'] == AUTH_WINDOWS:
					wsdl = self.createNTLMRequest(auth_dict['user'], auth_dict['password'], url, auth_dict['domain'])
					self.currSettings['auth'] = auth_dict
			else:
				wsdl = urllib2.urlopen(url)
				self.currSettings['auth'] = {'type': None, 'domain': None, 'user': None, 'password': None}
			self.proj_name = name
			self.proj_url = url
			main = paths['main_path'] + os.path.sep + paths['projects_dir']
			if not os.path.exists(main):
				os.makedirs(main)
			os.chdir(main)
			if os.path.exists(os.path.curdir + os.path.sep + name):
				raise os.error
			os.mkdir(name)
			os.chdir(name)
			wsdl_file = open(wsdl_name, 'w')
			wsdl_file.write(wsdl.read())
			wsdl_file.close()
			
			sett_file = open(settings_name, 'w')
			self.currSettings['control']['name'] = name
			self.currSettings['control']['url'] = url
			sett_file.write(pickle.dumps(self.currSettings))
			sett_file.close()
		except HTTPError as e:
			
			msg = 'ERROR: Got %s trying to download WSDL\nDid you provided the correct credentials?' % str(e)
			fail = True
		except antaresWrongCredentialsException as e:
			msg = 'ERROR: Got error trying to download WSDL\nDid you provided the correct credentials?' 
			fail = True
		except os.error as e:   
			msg =  'Error: Project already exists'
		except exceptions.IOError as e:
			msg =  'Error writing to file: %s' % str(e)
			fail = True
		except Exception as e:
			msg = 'Error: createProject, unknown exception: %s ' % str(e)
			fail = True
		else:
			msg =  'Project %s created' % self.proj_name
			logger.info("Project %s created" % self.proj_name)
		finally:
			os.chdir(paths['main_path'])
		if fail:
			self.deleteProject(name)
		return msg
	
	def loadProject(self, name, save_wsdl, from_file):
		"""
		Load currSettings with the new pickle load, this function MUST be called before updating core, notebook, etc
		save_wsdl flag to save the last downloaded WSDL automatically into project
		from_file flag to actually read the WSDL from the offline copy
		"""

		try:
			msg = ''
			os.chdir(paths['main_path'] + os.path.sep + paths['projects_dir'] + os.path.sep + name)
			# Load pickle file
			self.currSettings = pickle.load(open(settings_name, 'rb'))
			
			# Load control structures
			self.currSettings['control']['name'] = name
			self.proj_name = name
			
			# Load WSDL in memory
			if from_file:
				fh = open(wsdl_name, 'r')
				fh.close()
			else:
				# This path happens when the WSDL is being read online while refreshing your offline copy
				if save_wsdl:
					fh = open(wsdl_name, 'w')
					if self.getAuthType() == AUTH_BASIC:
						request = self.createAuthorizationRequest(self.getUsername(), self.getPassword(), self.getURL(), domain=self.getDomain())
						wsdl = urllib2.urlopen(request)
					elif self.getAuthType() == AUTH_WINDOWS:
						wsdl = self.createNTLMRequest(self.getUsername(), self.getPassword(), self.getURL(), self.getDomain())
					else:
						wsdl = urllib2.urlopen(self.getURL())
					wsdl = wsdl.read()
					logger.info("Writing %d bytes to offline WSDL" % len(wsdl))
					fh.write(wsdl)
					fh.close()
					
		except Exception as e:
			msg = 'Error: ' + e
		else:
			msg = 'OK'
		finally:
			os.chdir(paths['main_path'])
			return msg
	
	def saveProject(self, d):
		"""
		Dump pickle according to currSettings dict
		"""
		try:
			for key in d.keys():
				self.currSettings['server'][key] = d[key]
			fh = open(self.getSettingsPath(), 'w')
			fh.write(pickle.dumps(self.currSettings))
			fh.close()
			if self.save_flag:
				fh = open(self.getWSDLPath(), 'w')
				wsdl = urllib2.urlopen(url)
				pass
		except:
			return False
		return True
		
	def projList(self):
		path = paths['main_path'] + os.path.sep + paths['projects_dir']
		if not os.path.exists(path):
			os.makedirs(path)
		return os.listdir(path)
	
	def deleteProject(self, name):
		try:
			shutil.rmtree(paths['main_path'] + os.path.sep + paths['projects_dir'] + os.path.sep + name)
		except Exception as e:
			#logger.error('deleteProject @ pm: ' + str(e))
			pass
			
	def detectProtocolAuth(self, url):
		"""
		This function will try to connect first to the server to check if any HTTP authentication
		method is enabled (e.g. Basic, Windows auth). 
		
		Return parameter tells the UI which authentication method was discovered in order for it
		to do the rest 
		"""
		ret = None
		wsdl = None
		try:
			# This should raise HTTPError if we find an authentication method
			self.currSettings['control']['url'] = url
			wsdl = urllib2.urlopen(url)
		except HTTPError as e:
			rsp = e.headers.getheader('WWW-Authenticate').lower()
			if 'basic' in rsp:
				ret = AUTH_BASIC
			elif 'negotiate' in rsp or 'ntlm' in rsp:
				ret = AUTH_WINDOWS
			else:
				logger.debug("Unsupported/Unknown authentication method detected: %s" % rsp )
				ret = AUTH_UNKNOWN
		except URLError as e:
			# Known reasons are: connection refused, no route to host
			try:
				ret = e.reason[1]
			except:
				# Timeout
				ret = e.reason
		"""
		finally:
			try:
				# urllib2 won't raise exception if you try to connect to the server for the second time!
				if wsdl.code == 401:
					rsp = wsdl.headers.getheader('WWW-Authenticate').lower()
					if 'basic' in rsp:
						ret = AUTH_BASIC
					elif 'negotiate' in rsp or 'ntlm' in rsp:
						ret = AUTH_WINDOWS
					else:
						logger.debug("Unsupported/Unknown authentication method detected: %s" % rsp )
						ret = AUTH_UNKNOWN
			except:
				pass
		"""
		return ret
		
	def createAuthorizationRequest(self, user, pwd, url, domain=None):
		"""
		Create the Authorization header to perform basic authentication. 
		"""
		req = urllib2.Request(url)
		if domain:
			b64 = base64.encodestring('%s\%s:%s' % (domain, user, pwd)).replace('\n', '')
		else:
			b64 = base64.encodestring('%s:%s' % (user, pwd)).replace('\n', '')
		#logger.debug('Authorization header is now %s for creds %s\%s:%s' % (b64, domain, user, pwd))
		req.add_header('Authorization', 'Basic %s' % b64)
		return req
	
	def createNTLMRequest(self, user, pwd, url, domain):
		"""
		Create the NTLM authentication handler for Windows authentication.
		"""
		from ntlm import HTTPNtlmAuthHandler
		passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
		passman.add_password(None, url, domain + '\\' + user, pwd)
		# NTLM handler
		auth_ntlm = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
		# Install opener
		opener = urllib2.build_opener(auth_ntlm)
		urllib2.install_opener(opener)
		rsp = urllib2.urlopen(url)
		if rsp.code == 200:
			return rsp
		else:
			raise antaresWrongCredentialsException(str(rsp.headers))
		
	
	def getCurrentSettings(self):
		"""
		Return basic information: project's name and URL
		"""
		return self.currSettings['control']
	
	def getURL(self):
		return self.currSettings['control']['url']
	
	def getWSDLPath(self):
		return paths['main_path'] + os.path.sep + paths['projects_dir'] + os.path.sep + self.proj_name + os.path.sep + wsdl_name
	
	def getSettingsPath(self):
		return paths['main_path'] + os.path.sep + paths['projects_dir'] + os.path.sep + self.currSettings['control']['name'] + os.path.sep + settings_name
	
	def getWSDLContents(self):
		fh = open(self.getWSDLPath(), 'r')
		return fh.read()
	
	def getName(self):
		return self.currSettings['control']['name']
	
	def getAuthType(self):
		return self.currSettings['auth']['type']
	
	def getUsername(self):
		return self.currSettings['auth']['user']
	
	def getPassword(self):
		return self.currSettings['auth']['password']
	
	def getDomain(self):
		return self.currSettings['auth']['domain']
	
	def getIP(self):
		return re.findall(EXTRACT_IP_REGEX, self.currSettings['control']['url'])[0]
		
project_manager = projMan()		
