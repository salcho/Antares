'''
Created on Aug 10, 2013

@author: user
'''

from controller import exceptions
from core.utils.wsresponse_object import wsResponse
from core.data import ERROR_GENERIC_REGEXP
from core.data import logger
import re

class IPlugin:
    '''
    Standard plugin interface
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.name = 'generic plugin interface'
        self.description = 'all plugins must implement this'
        self.payloads = []
        self.regex = None
        
    """
    This function will check an wsResponse object parameter against any regexp
    """
    def checkRegex(self, result, core):
        if not self.regex:
            raise antaresException("No regex initialized in plugin")
        
        xml = str(result.getBody())
        for expression in ERROR_GENERIC_REGEXP:
            for error in self.regex:
                pattern = expression % re.escape(error)
                regexp = re.compile(pattern, re.IGNORECASE | re.DOTALL)
                r = regexp.search(xml)
                if r:
                    logger.info("Found matching error message in payload %s." % result.getPayload())
                    # Report to analyzer!
                    core.reportRegex(result)
            
    """
    This function will be called each time one of our payloads has been sent
    Result parameter is a wsResponse object
    """
    def reportResult(self, result):
        body = result.getBody()
        # Have to remove this import from here!
        from core.fwCore import core
        self.checkRegex(result, core)
        return
            
    def getPayloads(self):
        return self.payloads
    
    def getName(self):
        return self.name
    
    def isPlugin(self):
        return True
    
    def getDescription(self):
        return self.description