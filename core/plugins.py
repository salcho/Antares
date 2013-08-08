'''
Created on Feb 28, 2013

@author: Santiago Diaz M - salchoman@gmail.com
'''

from core.plugs import fuzzdb_plugin
import sys
import inspect
import threading
import Queue

class PluginManager(object):

    def __init__(self):
        self.loaded_plugins = {}
        self.request_queue = Queue.Queue()
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
    while using plugs collection of plugins. 
    The progress parameter is a function callback to update the progressbar
    in the injector widget. This one's optional. Too messy?
    Return all results.
    """
    def startAttack(self, opName, args, plugs, num_threads, progress=None):
        # Get payloads
        from core.fwCore import core
        wsdlhelper = core.iswsdlhelper()
        if not wsdlhelper:
            return None

        # Spawn pool of threads
        for i in range(num_threads):
            t = attackThread(self.request_queue, wsdlhelper, i, opName)
            t.setDaemon(True)
            t.start()
        
        # Fill queue
        size = 0
        for plugin in plugs:
            if plugin in self.loaded_plugins.keys():
                payloads = self.loaded_plugins[plugin].getPayloads()
                size += len(payloads)
                # Create requests
                for payload in payloads:
                    # Fill queue
                    self.request_queue.put((args,payload))
                    
                    #request, response = wsdlhelper.customRequest(opName, args, payload)
                    #self.result_set.add((cnt, response))
                    #ret[cnt] = [sys.getsizeof(response), payload]
                    #print 'Got response [%d]: %10s' % (sys.getsizeof(response), response)
    
        # Wait till everyone finishes
        if progress:
            while not self.request_queue.empty():
                per = 1-(float(self.request_queue.qsize())/size)
                progress(percent=per, text=str(int(per*100)) + '%')
        
        self.request_queue.join()
        # Return results
        pass
    
    def getLoadedPlugins(self):
        return self.loaded_plugins
    
    
class attackThread(threading.Thread):
    
    def __init__(self, queue, wsdlhelper, id, op_name):
        threading.Thread.__init__(self)
        self.queue = queue
        self.wsdl = wsdlhelper
        self.id = id
        self.op_name = op_name
        
    def run(self):
        while True:
            args, payload = self.queue.get()
            response = self.wsdl.customRequest(self.op_name, args, payload)
            print 'Thread %d says: Got response [%d]: %5s' % (self.id, sys.getsizeof(response), response)
            self.queue.task_done()
    
