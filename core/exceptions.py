#!/usr/bin/python

class antaresException(Exception):
	pass

class antaresLogException(antaresException):
	pass		

class antaresDependenciesException(antaresException):
	pass

class antaresUnknownException(antaresException):
	pass
