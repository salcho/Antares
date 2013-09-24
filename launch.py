#!/usr/bin/env python

'''
@author = Santiago Diaz - salchoman@gmail.com
'''

from core.data import paths
from core.data import logger
from core.utils.dependencies import checkDependencies
from core.exceptions import antaresDependenciesException
from core.fwCore import core
import os
import sys
import warnings
import optparse
import socket

warnings.filterwarnings(action="ignore", category=DeprecationWarning)

def mainPath():
	"""
	Get the program's directory
	"""
	return os.path.dirname(os.path.realpath(__file__))

def main():
	#TODO: Print banner, 
	try:
		paths['main_path'] = mainPath()
		logger.debug("Main path is: %s" % paths['main_path'])
		parser = optparse.OptionParser('usage %prog -t <seconds>')
		parser.add_option('-t', dest='tout', type='int', default='60', help='specify HTTP timeout in seconds')
		(opts, args) = parser.parse_args()
		if opts.tout:
			socket.setdefaulttimeout(opts.tout)
		else:
			socket.setdefaulttimeout(60)
		logger.info("Setting default timeout to %d seconds" % socket.getdefaulttimeout())
		checkDependencies()
		core.startUI()
	except antaresDependenciesException:
		exit()
	

if __name__ == "__main__":
	main()
