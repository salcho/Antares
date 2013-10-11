'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

import gtk
from ui.confWidget import cfgWidget
from ui.TestRequestWidget import TestRequestWidget
from ui.injWidget import injWidget
from ui.xsdWidget import xsdWidget
from ui.analyzeWidget import analyzeWidget
from ui.loggerWidget import loggerWidget

CONFIG_TAB = 0
TESTREQ_TAB = 1
INJECT_TAB = 2
XSD_TAB = 3
ANALYZE_TAB = 4

class mainNotebook(gtk.Notebook):
    
    def __init__(self):
        self.conf = None
        self.notebook = None
        self.tabs = []
        #self.notebook = gtk.Notebook()
        #self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        #self.notebook.set_scrollable(scrollable=True)
        
    def populate(self, proj, server):
        del self.notebook
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        #Settings wdgt
        conf = cfgWidget()
        conf.start(proj, server)
        self.tabs.append(conf)
        self.notebook.append_page(conf.getWidget(), gtk.Label('Settings'))
        #Test wdgt
        testwgt = TestRequestWidget()
        testwgt.start()
        self.tabs.append(testwgt)
        self.notebook.append_page(testwgt.getWidget(), gtk.Label('Replay'))
        #XSD wdgt
        xsdwgt = xsdWidget()
        xsdwgt.start()
        self.tabs.append(xsdwgt)
        self.notebook.append_page(xsdwgt.getWidget(), gtk.Label('XSD reader'))
        #Inject wdgt
        injwgt = injWidget()
        injwgt.start()
        self.tabs.append(injwgt)
        self.notebook.append_page(injwgt.getWidget(), gtk.Label('Injector'))
        #Analyze wdgt
        anawgt = analyzeWidget()
        anawgt.start()
        self.tabs.append(anawgt)
        self.notebook.append_page(anawgt.getWidget(), gtk.Label('Analyzer'))
        #Log wdgt
        #logwgt = loggerWidget()
        #logwgt.start()
        #self.notebook.append_page(logwgt.getWidget(), gtk.Label('Log'))
        self.notebook.set_current_page(0)
    def getNotebook(self):
        return self.notebook
    
    def getTabs(self):
        return self.tabs
    
    def addPage(self, txt):
        self.notebook.append_page(DummyWidget(), txt)
        
    def getConfig(self):
        """
        This function will permit other objects to get the actual configuration that's
        being shown by the UI
        """
        pass
        
class DummyWidget():
    '''
    DummyWidget to be used with blank pages on the notebook
    '''
    def __init__(self):
        self._vbox = gtk.VBox(True, 0)
    def getWidget(self):
        return self._vbox
