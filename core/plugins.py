'''
Created on Feb 28, 2013

@author: Santiago Diaz M - salchoman@gmail.com
'''

from core.plugs import fuzzdb_plugin
from core.utils.wsresponse_object import wsResponse
from core.data import logger
import sys
import inspect
import threading
import Queue
import gtk


class PluginManager(object):

    def __init__(self):
        logger.debug("Plugin Manager instansiated")
        
        self.loaded_plugins = {}
        # This queue is the job queue for the threads
        self.request_queue = Queue.Queue()
        # This list is filled by the attackThreads
        self.response_list = []
        # This dict will tell us which plugin sent a given payload
        self.plugin_payload = {}
        self.loadDefault()
    """
    This function will load all default plugins
    by getting all classes in fuzzdb_plugins
    """
    def loadDefault(self):
        for name, klass in inspect.getmembers(fuzzdb_plugin, inspect.isclass):
            # Get all classes registered except by the ones being imported. This will probably change in the future
            if name != 'IFuzzdbPlug' and name != 'attack_payloads' and name != 'regex' and name != 'IPlugin':
                plug = klass()
                self.loaded_plugins[plug.getName()] = plug
        
    def addPlugin(self, classPath):
        pass
    
    """
    Start an attack to operation opName, set attack parameters as args
    while using plugs collection of plugins. 
    The progress parameter is a function callback to update the progressbar
    in the injector widget. This one's optional. Too messy?
    Return wsResult list of objects.
    """
    def startAttack(self, opName, args, plugs, num_threads, progress=None):
        # Check required objects
        from core.fwCore import core
        wsdlhelper = core.iswsdlhelper()
        if not wsdlhelper or not opName:
            return None
        self.response_list = []

        # Spawn pool of threads
        for i in range(num_threads):
            t = attackThread(self.request_queue, self.response_list, wsdlhelper, i, opName, self.getPlugin)
            t.setDaemon(True)
            t.start()
        
        size = 0
        cnt = 1
        for plugin in plugs:
            if plugin in self.loaded_plugins.keys():
                payloads = self.loaded_plugins[plugin].getPayloads()
                size += len(payloads)
                for payload in payloads:
                    # Fill queue, fill plugin vs payload dict
                    if payload:
                        self.plugin_payload[payload] = plugin
                        self.request_queue.put([cnt, (args,payload)])
                        cnt += 1
                    #print 'Got response [%d]: %10s' % (sys.getsizeof(response), response)
    
        # Wait till everyone finishes, update progress bar meanwhile
        if progress:
            while not self.request_queue.empty():
                per = 1-(float(self.request_queue.qsize())/size)
                progress(percent=per, text=str(int(per*100)) + '%')
    
        # Report results to analyzer and each individual plugin
        core.initAnalyzer(self.response_list)
        for response in self.response_list:
            plugin = response.getPlugin()
            plugin.reportResult(response)
            
            
        return self.response_list
    
    # Return the plugin that sent this payload
    def getPlugin(self, payload):
        ret = None
        try:
            plugin = self.plugin_payload[payload]
            ret = self.loaded_plugins[plugin]
        except KeyError:
            pass
        return ret
    
    def getLoadedPlugins(self):
        return self.loaded_plugins
    
    
class attackThread(threading.Thread):
    """
    This threads will receive:
    Job queue
    Result list to fill
    Necessary wsdlhelper object for sending requests
    Request identifier
    Operation to be called
    getPlugin callback from plugin manager to fill in the wsResponse object
    """
         
    def __init__(self, queue, out_list, wsdlhelper, id, op_name, getPlugin):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_list = out_list
        self.wsdl = wsdlhelper
        self.id = id
        self.op_name = op_name
        self.get_plugin = getPlugin
        
    def run(self):
        while True:
            try:
                [req_id, (args, payload)] = self.queue.get()
                if not payload or not args or not req_id:
                    self.queue.task_done()
                else:
                    result = self.wsdl.customRequest(self.op_name, args, payload)
                    if result:
                        response = wsResponse(id=req_id, params=args, size=sys.getsizeof(result), response=result, payload=payload, plugin=self.get_plugin(payload))
                        # Report this to the appropiate plugin
                        self.out_list.append(response)
                    else:
                        raise
                    #print 'Thread %d says: Got result [%d]: %5s' % (self.id, sys.getsizeof(result), result)
            except Exception as e:
                self.queue.task_done()
                logger.error("Error sending request. Args are: %s ; Payload is: %s ; Message is: %s" % (args, payload, str(e)))
    
