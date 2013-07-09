'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

import os
import exceptions
import urllib2
import cPickle as pickle

PROJ_DIR = 'projects'
WSDL_PATH = 'target.wsdl'
SETTINGS_PATH = 'settings.p'

class projMan:
    
    #No matter what, always return to SELF_PATH
    def __init__(self):
        self.name = ''
        self.url = ''
	self.PATH = None
        
        #Settings dict
        self.currSettings = {'name': None, 'url': None}
        self.currWSDL = None
        self.headers = None
    
    def createProject(self, name, url):
        try:
            msg = ''
	    from core.fwCore import core
	    if not self.PATH:
		self.PATH = core.SELF_PATH
            self.name = name
            self.url = url
            os.chdir(self.PATH + os.path.sep + PROJ_DIR)
            wsdl = urllib2.urlopen(url)
            os.mkdir(name)
            os.chdir(name)
            fh = open(WSDL_PATH, 'w')
            fh.write(wsdl.read())
            fh.close()
            fh = open(SETTINGS_PATH, 'w')
            dict = {'name': self.name, 'url': self.url}
            fh.write(pickle.dumps(dict))
            fh.close()
        except os.error as e:   
            msg =  'Error creating project: ' + str(e)
        except exceptions.IOError as e:
            msg =  'Error writing WSDL: ' + str(e)
        except Exception as e:
            print type(e)
            print 'createProject: ' + str(e)
            return 'createProject: ' + str(e)
        else:
            msg =  'Project created'
        finally:
            os.chdir(self.PATH)
            return msg
    
    def loadProject(self, name):
        try:
	    msg = ''
	    if not self.PATH:
	    	from core.fwCore import core
		self.PATH = core.SELF_PATH
            os.chdir(PROJ_DIR + os.path.sep + name)
            self.currSettings = pickle.load(open(SETTINGS_PATH, 'rb'))
            fh = open(WSDL_PATH, 'r')
            self.currWSDL = fh.read()
            fh.close()
        except Exception as e:
            msg = 'Error: ' + e
        else:
	    msg = 'OK'
	finally:
	    os.chdir(self.PATH)
	    return msg
        
    def projList(self):
        if not self.PATH:
	        from core.fwCore import core
                self.PATH = core.SELF_PATH
	os.chdir(self.PATH)
	print os.getcwd()
        return os.listdir(PROJ_DIR)
    
    def getCurrentSettings(self):
        return self.currSettings
    
    def getURL(self):
        return self.currSettings['url']
        
pm = projMan()        
