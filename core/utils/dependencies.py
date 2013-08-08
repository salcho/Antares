#!/usr/bin/env python

from core.data import logger
from core.exceptions import antaresDependenciesException

def checkDependencies():
	failed_deps = 0

	try:
		import suds
		logger.info("Success loading: [('suds', %s)]" % suds.__version__)
	except ImportError:
		msg = "Antares couldn't find suds third-party library "
		msg += "which will be used to support a wide range of WSDL operations. "
		msg += "Please install it from pip, easy_install or apt."
		logger.critical(msg)
		failed_deps += 1

	try:
		import bs4
		logger.info("Success loading: [('bs4', %s)]" % bs4.__version__)
	except ImportError:
		msg = "Antares couldn't find bs4 third-party library "
		msg += "which will help with XML representation. "
		logger.critical(msg)
		failed_deps += 1
	
	try:
		import pywebfuzz
		logger.info("Success loading: [('pyxb', %s)]" % pywebfuzz.__version__)
	except ImportError:
		msg = "Antares couldn't find pywebfuzz third-party library "
		msg += "which contains fuzzdb payload lists. "
		logger.critical(msg)
		failed_deps += 1
		
	if failed_deps:
		raise antaresDependenciesException("%d dependencies aren't met" % failed_deps)
		
