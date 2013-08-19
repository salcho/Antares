'''
Created on Jan 19, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.utils.WSDLHelper import wsdlhelper
from core.utils.analyzer import responseAnalyzer
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
		self.analyzer = responseAnalyzer()
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
	
	def initAnalyzer(self, data):
		self.analyzer.start(data)
		
	def reportRegex(self, result):
		self.analyzer.foundRegex(result)
	
	def getServerInfo(self):
		return wsdlhelper.getHeaders()
	
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
		
	def isAnalyzer(self):
		if self.analyzer.inUse():
			return self.analyzer
		else:
			return False
		
	# This will call a function from the specified widget. No guarantees! xD
	def callUI(self, widget, function):
		return self.gui.callFromWidget(widget, function)

core = Core()
