'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.data import wsdl_name
from core.data import settings_name
from core.data import logger
from core.data import paths
from collections import defaultdict
import os
import exceptions
import urllib2
import shutil
import cPickle as pickle

class projMan:
	
	def __init__(self):
		self.proj_name = ''
		self.proj_url = ''
	
		#currSettings is a dictionary with keys [control,server] which values are as presented in the config widget
		self.currSettings = {}
		self.currSettings['control'] = {'name': None, 'url': None, 'user': None, 'password': None}
		self.currSettings['server'] = {}
		#automatic wsdl save flag
		self.save_flag = False
		logger.debug("Project manager instansiated")
	
	def createProject(self, name, url):
		try:
			msg = ''
			self.proj_name = name
			self.proj_url = url
			os.chdir(paths['main_path'] + os.path.sep + paths['projects_dir'])
			wsdl = urllib2.urlopen(url)
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
		except os.error as e:   
			msg =  'Error creating project: %s' % e.strerror
		except exceptions.IOError as e:
			msg =  'Error writing to file: %s' % e.strerror
		except Exception as e:
			msg = 'createProject, unknown exception: %s ' % e.strerror
		else:
			msg =  'Project created'
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
			print 'deleteProject @ pm: ' + str(e)
	
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
		
project_manager = projMan()		
