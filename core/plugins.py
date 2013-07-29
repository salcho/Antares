'''
Created on Feb 28, 2013

@author: Santiago Diaz M - salchoman@gmail.com
'''

class PluginManager(object):
    
    PLUG_DIR = "core/plugins"

    def __init__(self):
        self.loadedPlugins = []

    def loadDefault(self):
	
        
    def addPlugin(self, classPath):
        
        pass
    
    def getLoadedPlugins(self):
        return self.loadedPlugins
    
    
