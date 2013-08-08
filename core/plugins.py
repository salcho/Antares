'''
Created on Feb 28, 2013

@author: Santiago Diaz M - salchoman@gmail.com
'''

from core.plugs import fuzzdb_plugin
import sys
import inspect

class PluginManager(object):

    def __init__(self):
        self.loaded_plugins = {}
        self.loadDefault()
    """
    This function will load all default plugins
    by getting all classes in fuzzdb_plugins
    """
    def loadDefault(self):
        for name, klass in inspect.getmembers(fuzzdb_plugin, inspect.isclass):
            if name != 'IFuzzdbPlug' and name != 'attack_payloads' and name != 'regex':
                plug = klass()
                self.loaded_plugins[plug.getName()] = plug
        
    def addPlugin(self, classPath):
        pass
    
    """
    Start an attack to operation opName, set attack parameters as args
    while using plugs collection of plugins. Return all results
    """
    def startAttack(self, opName, args, plugs):
        # Get payloads
        from core.fwCore import core
        wsdlhelper = core.iswsdlhelper()
        if not wsdlhelper:
            return None
        
        ret = {}
        cnt = 1
        for plugin in plugs:
            if plugin in self.loaded_plugins.keys():
                payloads = self.loaded_plugins[plugin].getPayloads()
                # Create requests
                for payload in payloads:
                    response = wsdlhelper.customRequest(opName, args, payload)
                    ret[cnt] = [sys.getsizeof(response), payload]
                    cnt += 1
                    #print 'Got response [%d]: %10s' % (sys.getsizeof(response), response)
        
        print ret
        # Pass results to regexp
        
        # Return results
        
        pass
    
    def getLoadedPlugins(self):
        return self.loaded_plugins
    
    
