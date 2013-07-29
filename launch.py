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
import argparse

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
		checkDependencies()
		core.startUI()
	except antaresDependenciesException:
		exit()
	

if __name__ == "__main__":
	main()
