#!/usr/bin/python
 

class antaresException(Exception):
	def __init__(self, txt):
		Exception.__init__(self, txt)

class antaresLogException(antaresException):
	def __init__(self, txt):
		antaresException(txt)
		
class antaresDependenciesException(antaresException):
	def __init__(self, txt):
		antaresException(txt)

class antaresWrongCredentialsException(antaresException):
	def __init__(self, txt):
		antaresException(txt)
		
class antaresUnknownException(Exception):
	def __init__(self, txt):
		Exception.__init__(self, txt)
