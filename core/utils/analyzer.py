'''
Created on Aug 9, 2013

@author: salcho
'''

from core.exceptions import antaresException
from core.data import logger
from core.utils import wsresponse_object

PLUGIN_DICT = 0
HTTP_DICT = 1
RSP_DICT = 2
SIZE_DICT = 3
PARAMS_DICT = 4

class responseAnalyzer:
    '''
    This class will retrieve the last set of data produced and create series of data from them to be plotted
    '''


    def __init__(self):
        logger.debug("Analyzer object instansiated")
        self.data = None
        self.count = -1
        self.plugins = {}
        self.inuse = False
        self.stats = []
        self.regex_hits = []
        
    def start(self, res_list):
        '''
        The res_list parameter should correspond to the structure produced by startAttack from the plugin manager
        '''
        if not res_list:
            raise antaresException("Can't initialize responseAnalyzer without a set of data")
        
        self.inuse = True
        self.data = sorted(res_list, key=lambda id: id.getPlugin().getName())
        
        self.matched = []
        self.count = len(self.data)
        self.stats = self.countUnique()
    
    """    
    This function will produce sets of data with the following characteristics:
      - Unique HTTP Codes ratio
      - Unique Response contents
      - Unique Response size
      - Payloads per plugin
      
    In the presence of plugin_name it will do this for a specified plugin
    In the presence of opt_set it will do this for a specific set of data
    """
    def countUnique(self, plugin_name=None, opt_set=None):
        # Whats our set of data
        if opt_set:
            data = opt_set
        else:
            data = self.data
        # Wether this is done to one plugin or all of them
        if plugin_name: 
            sorted_list = list(x for x in data if x.getPlugin().getName() == plugin_name)
        else:
            sorted_list = sorted(data, key=lambda key: key.getID())
        
        # Control structs
        plugin_dict = {} 
        http_dict = {}
        resp_dict = {}
        size_dict = {}
        
        # Counting...
        for result in sorted_list:
            if result.getHTTPCode() in http_dict.keys():
                http_dict[result.getHTTPCode()] += 1
            else:
                http_dict[result.getHTTPCode()] = 1
            if result.getResponse() in resp_dict.keys():
                resp_dict[result.getResponse()] += 1
            else:
                resp_dict[result.getResponse()] = 1
            if result.getSize() in size_dict.keys():
                size_dict[result.getSize()] += 1
            else:
                size_dict[result.getSize()] = 1
            if result.getPlugin() not in plugin_dict.keys():
                plugin_dict[result.getPlugin()] = 1
            else:
                plugin_dict[result.getPlugin()] += 1
                
                
        return [plugin_dict, http_dict, resp_dict, size_dict, result.getParams()]
    """
    This function will be called from the plugins each time one of them finds a regex match
    """        
    def foundRegex(self, result):
        self.regex_hits.append(result)
        
    def getStats(self):
        return self.stats
    
    """
    Produce stats over this set
    """
    def getRegexStats(self, plugin=None):
        if len(self.regex_hits) > 0:
            if plugin:
                return self.countUnique(plugin_name=plugin, opt_set=self.regex_hits)
            else:
                return self.countUnique(opt_set=self.regex_hits)
        else:
            return None
    
    """
    Get a given plugin's payloads hits
    """
    def getPayloadHits(self, plugin):
        ret = list(x.getPayload() for x in self.regex_hits if x.getPlugin().getName() == plugin)
        return ret
    
    def inUse(self):
        return self.inuse