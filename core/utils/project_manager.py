'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.data import projects_dir
from core.data import wsdl_name
from core.data import settings_name
from core.data import main_path
from core.data import logger
import os
import exceptions
import urllib2
import shutil
import cPickle as pickle

class projMan:
    
	def __init__(self):
		self.proj_name = ''
	        self.proj_url = ''
        
	        #Settings dict
	        self.currSettings = {'name': None, 'url': None, 'hostname': None, 'port': None, 'header': None, 'user': None, 'pwd': None}
	        self.currWSDL = None
	        self.headers = None
    
	def createProject(self, name, url):
	        try:
			msg = ''
			self.proj_name = name
			self.proj_url = url
			os.chdir(main_path + projects_dir)
			wsdl = urllib2.urlopen(url)
			os.mkdir(name)
			os.chdir(name)
			fh = open(wsdl_name, 'w')
			fh.write(wsdl.read())
			fh.close()
			fh = open(settings_name, 'w')
			self.currSettings['name'] = name
			self.currSettings['url'] = url
			fh.write(pickle.dumps(self.currSettings))
			fh.close()
		except os.error as e:   
			msg =  'Error creating project: ' + e
		except exceptions.IOError as e:
			msg =  'Error writing WSDL: ' + e
		except Exception as e:
			#print type(e)
			#return 'createProject: ' + str(e)
			msg = 'createProject, unknown exception: ' + e
		else:
			msg =  'Project created'
			logger.info("Project %s created" % self.proj_name)
		finally:
			os.chdir(main_path)
			return msg
    
	def loadProject(self, name):
		"""
		Load currSettings with the new pickle load, this function MUST be called before updating core, notebook, etc
		"""

		try:
			msg = ''
			os.chdir(projects_dir + os.path.sep + name)
			self.currSettings = pickle.load(open(settings_name, 'rb'))
			fh = open(wsdl_name, 'r')
			self.currWSDL = fh.read()
			fh.close()
		except Exception as e:
			msg = 'Error: ' + e
		else:
			msg = 'OK'
		finally:
			os.chdir(main_path)
			return msg
    
	def saveProject(self, d):
		"""
		Dump pickle according to currSettings dict
		"""
		for key in d.keys():
			self.currSettings[key] = d[key]
		fh = open(self.getSettingsPath(), 'w')
		fh.write(pickle.dumps(self.currSettings))
        
	def projList(self):
		os.chdir(main_path)
		return os.listdir(projects_dir)
    
	def deleteProject(self, name):
		try:
			shutil.rmtree(main_path + os.path.sep + projects_dir + os.path.sep + name)
		except Exception as e:
			print 'deleteProject @ pm: ' + str(e)
    
	def getCurrentSettings(self):
		return self.currSettings
    
	def getURL(self):
        	return self.currSettings['url']
    
	def getWSDLPath(self):
		return main_path + os.path.sep + projects_dir + os.path.sep + self.currSettings['name'] + os.path.sep + wsdl_name
    
	def getSettingsPath(self):
        	return main_path + os.path.sep + projects_dir + os.path.sep + self.currSettings['name'] + os.path.sep + settings_name
    
	def getWSDLContents(self):
		fh = open(self.getWSDLPath(), 'r')
		return fh.read()
        
project_manager = projMan()        
