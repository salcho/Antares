'''
Created on Jan 19, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from ui.main import mainUI

import os
import sys

class Core(object):
    
    SELF_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    def __init__(self):
        self.wsdlhelper = None
        self.gui = mainUI()
    
    def startUI(self):
        self.gui.start()
        
    def loadWSDL(self, url):
        #TODO: Change URL to any stream
        if not self.iswsdlhelper():
            from core.utils.WSDLHelper import wsdlhelper
            self.wsdlhelper = wsdlhelper
        ret = self.wsdlhelper.loadWSDL(url)
        if 'Error' in ret:
            raise Exception(ret)
    
    def iswsdlhelper(self):
        if not self.wsdlhelper:
            return False
        else:
            return self.wsdlhelper
    
    def getServerInfo(self):
        #wsdlhelper already instansiated
        return self.wsdlhelper.srvInfoDict()
        
    '''
    def isProjMan(self):
        pass
    '''

core = Core()
