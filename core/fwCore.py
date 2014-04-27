'''
Created on Jan 19, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.data import logger
from core.Singleton import Singleton

import signal
import os
import sys

class Core:
	__metaclass__ = Singleton
	
	def __init__(self):
		"""
		Main core function.
		"""
		logger.debug("Core module instansiated")
	
	def initAnalyzer(self, data):
		self.analyzer.start(data)
		
	def reportRegex(self, result):
		self.analyzer.foundRegex(result)
	
	def getServerInfo(self):
		return self.wsdlhelper.getHeaders()
	
	def iswsdlhelper(self):
		if not self.wsdlhelper:
			return False
		else:
			return self.wsdlhelper
		
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

#core = Core()


