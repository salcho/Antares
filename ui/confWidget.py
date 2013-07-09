'''
Created on Aug 10, 2012

@author: "Santiago Diaz M."
'''
import gobject
import logging
import pygtk
import gtk

class cfgWidget:
    
    '''
    This Widget handles the configuration tab, it's responsible for loading and saving 
    XML-based hostInfoTable by interacting with Mr. workspace director
    
    '''
    
    
    def __init__(self):
        self.prjName= None
        self.localPath = None
        self.uri= None
        self.IP = None
        self.port = None
        self.servHeader = None
        self.vbox = None
        self.authType = None
        self.user = None
        self.pwd = None
        self.fProj = None
        self.fSettings = None
        self.fBinding = None
        self.fAuth = None
        self.bCombobox = None
        
        self.prjName = gtk.Entry(0)
        self.prjName.set_editable(False)
        self.localPath = gtk.Label('')
        self.uri = gtk.Entry(0)
        self.uri.set_editable(False)
        self.authType = gtk.Label('Options combobox')
        self.user = gtk.Entry(0)
        self.user.set_editable(False)
        self.pwd = gtk.Entry(0)
        self.pwd.set_editable(False)
    
        #Project frame
        self.fProj = gtk.Frame("Project")
        self.fProj.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        table = gtk.Table(3,2, True)
        table.attach(gtk.Label("Project name"), 0,1,0,1)
        table.attach(self.prjName, 1,2,0,1)
        table.attach(gtk.Label("URL"), 0,1,1,2)
        table.attach(self.uri, 1,2,1,2)
        table.attach(gtk.Label("View WSDL"), 0,1,2,3)
        viewButton = gtk.Button("View WSDL", gtk.STOCK_EXECUTE)
        viewButton.connect("clicked", self.viewWSDL, None)
        table.attach(viewButton, 1,2,2,3)
        self.fProj.add(table)
        
        #Server frame
        self.fSettings = gtk.Frame("Settings")
        self.fSettings.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        hostInfoTable = gtk.Table(3,2,True)
        hostInfoTable.attach(gtk.Label("Hostname"),0,1,0,1)
        self.IP = gtk.Entry(30)        
        self.IP.set_editable(False)
        hostInfoTable.attach(self.IP, 1,2,0,1)
        hostInfoTable.attach(gtk.Label("Port"), 0,1,1,2)
        self.port = gtk.Entry(5)
        self.port.set_editable(False)
        hostInfoTable.attach(self.port, 1,2,1,2)
        hostInfoTable.attach(gtk.Label('Server header'), 0, 1, 2, 3)
        self.servHeader = gtk.Entry(30)
        self.servHeader.set_editable(False)
        hostInfoTable.attach(self.servHeader, 1,2,2,3)
        self.fSettings.add(hostInfoTable)
        
        #Default binding frame
	#TODO: Add default binding feature
        self.fBinding = gtk.Frame("Default binding")
        self.bCombobox = gtk.combo_box_new_text()
        self.bCombobox.append_text('')
        self.bCombobox.set_active(0)
        self.fBinding.add(self.bCombobox)
        
        #Authentication frame
        self.fAuth = gtk.Frame("Authentication")
        table = gtk.Table(3,2, True)
        table.attach(gtk.Label("Type"), 0,1,0,1)
        table.attach(self.authType, 1,2,0,1)
        table.attach(gtk.Label("User"), 0,1,1,2)
        table.attach(self.user, 1,2,1,2)
        table.attach(gtk.Label("Password"), 0,1,2,3)
        table.attach(self.pwd, 1,2,2,3)
        self.fAuth.add(table)
        
        #HBox
        saveButton = gtk.Button("Save", gtk.STOCK_SAVE)
        saveButton.connect("clicked", self.saveSettings, None)
        hbox = gtk.HBox(False, 0)
        hbox.pack_end(saveButton, False, False, 0)
        
        
        #Add everything to VBox
        self.vbox = gtk.VBox(False, 0)
        self.vbox.pack_start(self.fProj, False, False, 0)
        self.vbox.pack_start(self.fSettings, False, False, 0)
        self.vbox.pack_start(self.fBinding, False, False, 0)
        self.vbox.pack_start(self.fAuth, False, False, 0)
        self.vbox.pack_start(hbox, False, False, 0)
        self.vbox.show_all()
        
    def getWidget(self):
        return self.vbox
    
    #TODO
    def saveSettings(self, widget):
        pass
    
    #TODO
    def viewWSDL(self):
        pass
    
    def fillProject(self, dict):
        self.prjName.set_text(dict['name'])
        self.uri.set_text(dict['url'])
    
    def fillServer(self, dict):
        self.IP.set_text(dict['hostname'])
        self.port.set_text(str(dict['port']))
        self.servHeader.set_text(dict['header'])


'''
    def bNameChange(self, w):
        model = w.get_model()
        index = w.get_active()
        if index:
            if wd.changeBinding(model[index][0]):
                injWdgt.getOpts()
                testrq.getOperations()
                return True
        else:
            self.logger.error('Fail to get mode,index')
        return False
    
    def getProjectDescription(self):
        pass
    
    def getWidget(self):
        return self.vbox
    
    def refresh(self):
        #Refresh structures
        self._wsdldict = wd.getDicts()['wsdl']
        self._authdict = wd.getDicts()['auth']
        #Set all variables
        self.prjName.set_text(wd.getCurrentProject())
        self.localPath.set_text(self._wsdldict['path'])
        self.uri.set_text(self._wsdldict['url'])
        self.IP.set_text(self._wsdldict['ip'])
        self.port.set_text(self._wsdldict['port'])
        self.authType = gtk.Label(self._authdict['type'])
        self.user = gtk.Label(self._authdict['user'])
        self.pwd = gtk.Label(self._authdict['pwd'])
        if self._wsdldict['ssl']:
            self.checkSSL.set_active(True)
        else:
            self.checkSSL.set_active(False)    
        
    def setBindings(self):
        if wsdlhelper.isWSDLSet:
            if len(wsdlhelper.getBindings()) > 0 :
                for binding in wsdlhelper.getBindings():
                    self.bCombobox.append_text(binding)
                    self.bCombobox.connect('changed', self.bNameChange)
                self.bCombobox.set_active(0)
            else:
                self.bCombobox.append_text('Reload WSDL')
        
    def setSettings(self, settings):
        #@param hostInfoTable: It's a dict container for WSDL, SETTINGS and AUTH dicts 
        if not len(settings) == 0:
            self._wsdldict = settings['wsdl']
            self._authdict = settings['auth']
        self.refresh()
        
    def saveSettings(self, *args):
        #Refresh dictionaries
        self._wsdldict['url']  = self.uri.get_text()
        self._wsdldict['ip'] = self.IP.get_text()
        self._wsdldict['port'] = self.port.get_text()
        self._wsdldict['path'] = self.localPath.get_text()
        self.SSLcallback(None, None)
        self._authdict['type'] = self.authType.get_text()
        self._authdict['user'] = self.user.get_text()
        self._authdict['pwd'] = self.pwd.get_text()
        
        #Tell workspace director
        wd.setDicts(self._wsdldict, self._authdict)
        #Persist
        wd.saveProject()
        #injWdgt.getOpts()

    
    def SSLcallback(self, w, data):
        if self.checkSSL.get_active():
            self._wsdldict['ssl'] = 1
        else:
            self._wsdldict['ssl'] = 0
            
            
    def setTechnology(self, dict, key, value):
        wd.setParam(dict, key, value)
        self.refresh()
        
cfg = cfgWidget()
wdgt = cfg.getWidget()'''
