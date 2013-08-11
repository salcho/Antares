'''
Created on Aug 10, 2013

@author: user
'''

from core.exceptions import antaresException
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
    def checkRegex(self, result):
        if not self.regex:
            raise antaresException("No regex initialized in plugin")
        
        xml = str(result.getBody())
        for expression in ERROR_GENERIC_REGEXP:
            for error in self.regex:
                pattern = expression % re.escape(error)
                regexp = re.compile(pattern, re.IGNORECASE | re.DOTALL)
                r = regexp.search(xml)
                if r:
                    logger.info("Found matching error message in payload %s. Body is %s" % (result.getPayload(), result.getBody()))
                    # Report to analyzer!
                    pass
            
    """
    This function will be called each time one of our payloads has been sent
    Result parameter is a wsResponse object
    """
    def reportResult(self, result):
        body = result.getBody()
        self.checkRegex(result)
        return
            
    def getPayloads(self):
        return self.payloads
    
    def getName(self):
        return self.name
    
    def isPlugin(self):
        return True
    
    def getDescription(self):
        return self.description