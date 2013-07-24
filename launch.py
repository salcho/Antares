#!/usr/bin/env python

'''
@author = Santiago Diaz - salchoman@gmail.com
'''

# Launch!
from core.fwCore import core
from core import data
import os
import sys

def mainPath():
	"""
	Get the program's directory
	"""
	print os.path.dirname(os.path.realpath(__file__))
	return os.path.dirname(os.path.realpath(__file__))

def main():
	#TODO: Print banner, 
	data.main_path = mainPath() 
	core.startUI()



if __name__ == "__main__":
	main()
