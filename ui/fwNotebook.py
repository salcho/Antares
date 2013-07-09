'''
Created on Jan 20, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

import gtk
from ui.confWidget import cfgWidget
from ui.TestRequestWidget import TestRequestWidget
from ui.injWidget import injWidget

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
        self.notebook.set_scrollable(scrollable=True)
        #Settings wdgt
        conf = cfgWidget()
        if len(proj) > 0 and len(server) > 0:
            conf.fillProject(proj)
            conf.fillServer(server)
        self.notebook.append_page(conf.getWidget(), gtk.Label('Settings'))
	#Test wdgt
	testwgt = TestRequestWidget()
	testwgt.start()
	self.notebook.append_page(testwgt.getWidget(), gtk.Label('Test Rx'))
	#Inj wdgt
	injwgt = injWidget()
	injwgt.start()
	self.notebook.append_page(injwgt.getWidget(), gtk.Label('Injection'))
        
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
