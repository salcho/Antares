'''
Created on Jan 19, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.utils.WSDLHelper import wsdlhelper
from core.data import logger
from core import plugins
from ui.main import mainUI

import signal
import os
import sys

class Core(object):
	
	def __init__(self):
		"""
		Main core function.
		"""
		logger.debug("Core module instansiated")
		self.plugin_manager = plugins.PluginManager()
		self.gui = mainUI()
	
	def startUI(self):
		self.gui.start()
		
	def loadWSDL(self, url):
			#TODO: Change URL to any stream
		ret = wsdlhelper.loadWSDL(url)
		if 'Error' in ret:
			self.gui.showError(ret)
			return False
		return True
	
	def iswsdlhelper(self):
		if not wsdlhelper:
			return False
		else:
			return wsdlhelper
		
	def isPluginManager(self):
		if not self.plugin_manager:
			return False
		else:
			return self.plugin_manager
	
	def getServerInfo(self):
		#wsdlhelper already instansiated
		return wsdlhelper.srvInfoDict()
		
	'''
	def isProjMan(self):
			pass
	'''

core = Core()
