'''
Created on Aug 9, 2013

@author: salcho
'''

from core.exceptions import antaresException
from core.data import logger
from core.utils import wsresponse_object

class responseAnalyzer:
    '''
    This class will retrieve the last set of data produced and create series of data from them to be plotted
    '''


    def __init__(self):
        self.data = None
        self.count = -1
        self.inuse = False
        
    def start(self, res_list):
        '''
        The res_list parameter should correspond to the structure produced by startAttack from the plugin manager
        '''
        if not res_list:
            
            raise antaresException("Can't initialize responseAnalyzer without a set of data")
        
        self.data = sorted(res_list, key=lambda id: id.getID())
        self.count = len(self.data)
        self.inuse = True
        
        self.countUnique()
    
    """    
    This function will produce sets of data with the following characteristics:
      - Unique HTTP Codes ratio
      - Unique Response contents
      - Unique Response size
    """
    def countUnique(self): 
        sorted_list = sorted(self.data, key=lambda key: key.getHTTPCode())
        http_dict = {}
        resp_dict = {}
        size_dict = {}
        for result in sorted_list:
            if result.getHTTPCode() in http_dict.keys():
                http_dict[result.getHTTPCode()] += 1
            else:
                http_dict[result.getHTTPCode()] = 1
            if result.getResponse() in resp_dict.keys():
                resp_dict[result.getResponse()] += 1
            else:
                resp_dict[result.getResponse()] = 1
            if result.getSize() in resp_dict.keys():
                size_dict[result.getSize()] += 1
            else:
                size_dict[result.getSize()] = 1
    
    """
    This function will be called from the plugins each time one of them finds a regex match
    """        
    def foundRegex(self):
        pass
    
    def inUse(self):
        return self.inuse