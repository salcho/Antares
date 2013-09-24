'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.data import wsdl_name
from core.data import settings_name
from core.data import logger
from core.data import paths
from urllib2 import HTTPError
from urllib2 import URLError
import os
import exceptions
import urllib2
import shutil
import base64
import cPickle as pickle

AUTH_BASIC = 0
AUTH_DIGEST = 1
AUTH_FORMS = 2
AUTH_WINDOWS = 3
AUTH_WSSE = 4

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
		try:
			msg = ''
			if auth_dict:
				if auth_dict and auth_dict['type'] == AUTH_BASIC:
					request = self.createAuthorizationRequest(auth_dict['user'], auth_dict['password'], url, domain=auth_dict['domain'])
					wsdl = urllib2.urlopen(request)
					self.currSettings['auth'] = auth_dict
			else:
				wsdl = urllib2.urlopen(url)
			self.proj_name = name
			self.proj_url = url
			os.chdir(paths['main_path'] + os.path.sep + paths['projects_dir'])
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
			msg = 'ERROR: Got %s trying to download WSDL\nDid you provided the correct creds?' % str(e)
		except os.error as e:   
			msg =  'Error creating project: %s' % e.strerror
		except exceptions.IOError as e:
			msg =  'Error writing to file: %s' % e.strerror
		except Exception as e:
			msg = 'createProject, unknown exception: %s ' % e.strerror
		else:
			msg =  'Project %s created' % self.proj_name
			logger.info("Project %s created" % self.proj_name)
		finally:
			os.chdir(paths['main_path'])
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
				# Save to disk?
				if save_wsdl:
					fh = open(wsdl_name, 'w')
					wsdl = urllib2.urlopen(self.getURL())
					fh.write(wsdl.read())
					fh.close()
			print self.currSettings['server']
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
			logger.error('deleteProject @ pm: ' + str(e))
			
	def detectProtocolAuth(self, url):
		"""
		This function will try to connect first to the server to check if any HTTP authentication
		method is enabled (e.g. Basic auth). 
		
		Return parameter tells the UI which authentication method was discovered in order for it
		to show the correct dialog 
		"""
		try:
			wsdl = urllib2.urlopen(url)
		except HTTPError as e:
			return e.code
		except URLError as e:
			# Known reasons are: connection refused, no route to host
			try:
				return e.reason[1]
			except:
				# Timeout
				return e.reason
		else:
			return None
		
	def createAuthorizationRequest(self, user, pwd, url, domain=None):
		"""
		Create the header needed to perform basic authentication. All by ourselves 8]
		"""
		req = urllib2.Request(url)
		if domain:
			b64 = base64.encodestring('%s\%s:%s' % (domain, user, pwd)).replace('\n', '')
		else:
			b64 = base64.encodestring('%s:%s' % (user, pwd)).replace('\n', '')
		logger.debug('Authorization header is now %s for creds %s\%s:%s' % (b64, domain, user, pwd))
		req.add_header('Authorization', 'Basic %s' % b64)
		return req
	
	def getCurrentSettings(self):
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
		
project_manager = projMan()		
