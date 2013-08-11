'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

import gtk
from ui.confWidget import cfgWidget
from ui.TestRequestWidget import TestRequestWidget
from ui.injWidget import injWidget
from ui.analyzeWidget import analyzeWidget
from ui.bfWidget import bfWidget
from ui.loggerWidget import loggerWidget

class mainNotebook(gtk.Notebook):
    
    def __init__(self):
        self.conf = None
        self.notebook = None
        #self.notebook = gtk.Notebook()
        #self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        #self.notebook.set_scrollable(scrollable=True)
        
    def populate(self, proj, server):
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        #Settings wdgt
        conf = cfgWidget()
        conf.start(proj, server)
        self.notebook.append_page(conf.getWidget(), gtk.Label('Settings'))
        #Test wdgt
        testwgt = TestRequestWidget()
        testwgt.start()
        self.notebook.append_page(testwgt.getWidget(), gtk.Label('Replay'))
        #Inject wdgt
        injwgt = injWidget()
        injwgt.start()
        self.notebook.append_page(injwgt.getWidget(), gtk.Label('Injector'))
        #Analyze wdgt
        anawgt = analyzeWidget()
        anawgt.start()
        self.notebook.append_page(anawgt.getWidget(), gtk.Label('XSD Analyzer'))
        #BF wdgr
        bfwgt = bfWidget()
        bfwgt.start()
        self.notebook.append_page(bfwgt.getWidget(), gtk.Label('BruteForce'))
        #Log wdgt
        #logwgt = loggerWidget()
        #logwgt.start()
        #self.notebook.append_page(logwgt.getWidget(), gtk.Label('Log'))
        
    def getNotebook(self):
        return self.notebook
    
    def addPage(self, txt):
        self.notebook.append_page(DummyWidget(), txt)
        
class DummyWidget():
    '''
    DummyWidget to be used with blank pages on the notebook
    '''
    def __init__(self):
        self._vbox = gtk.VBox(True, 0)
    def getWidget(self):
        return self._vbox
