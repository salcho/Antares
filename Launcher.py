#!/usr/bin/env python

'''
@author = Santiago Diaz - salchoman@gmail.com
'''

from ui.main import mainUI
from core import dependencies
dependencies.checkDependencies()
from core.fwCore import Core
from core.Singleton import Singleton
from core.ProjectManager import ProjectManager
from core.WSDLHelper import WSDLHelper
from core.ResponseAnalyzer import responseAnalyzer
from core.PluginManager import PluginManager
from core.data import paths
from core.data import logger
from controller import exceptions

import os
import sys
import warnings
import optparse
import socket
from controller.exceptions import antaresDependenciesException

warnings.filterwarnings(action="ignore", category=DeprecationWarning)


class Launcher:

	__metaclass__ = Singleton
		
	def __init__(self):
			self.gui = mainUI()
			self.main()
	
	def getProjMan(self):
		return self.proj_manager
	
	def main(self):
		#TODO: Print banner, 
		try:
			self.wsdlhelper = WSDLHelper()
			self.proj_manager = ProjectManager()
			self.analyzer = responseAnalyzer()
			self.plugin_manager = PluginManager()
			self.core = Core()
			self.gui.start(self)
			
			"""
			#paths['main_path'] = self.mainPath()
			#logger.debug("Main path is: %s" % paths['main_path'])
			parser = optparse.OptionParser('usage %prog -t <seconds>')
			parser.add_option('-t', dest='tout', type='int', default='60', help='specify HTTP timeout in seconds')
			(opts, args) = parser.parse_args()
			if opts.tout:
				socket.setdefaulttimeout(opts.tout)
			else:
				socket.setdefaulttimeout(60)
			logger.info("Setting default timeout to %d seconds" % socket.getdefaulttimeout())
			"""
		except antaresDependenciesException:
			logger.debug("antaresDependenciesException @ Launcher")
	
	# Once the UI has the launcher we are on
	def getLauncher(self):
		return self
	
	def loadWSDL(self, url):
		rsp = self.wsdlhelper.loadWSDL(url)
		if 'Error' in rsp:
			self.gui.showError(rsp)
			return False
		elif 'Warning' in rsp:
			self.gui.showError(rsp)
		return True
	
	# This will call a function from the specified widget. No guarantees! xD
	def callUI(self, widget, function):
		return self.gui.callFromWidget(widget, function)

if __name__ == "__main__":
	launcher = Launcher()