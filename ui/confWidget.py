'''
Created on Aug 10, 2012

@author: "Santiago Diaz M."
'''
from core.fwCore import core
from core.utils.project_manager import project_manager
from core.utils.project_manager import AUTH_BASIC
from core.exceptions import antaresException
from ui.IWidget import IWidget
from bs4 import BeautifulSoup
import gobject
import logging
import pygtk
import gtk
from gtk import gdk

class cfgWidget(IWidget):
    
    '''
    This Widget handles the configuration tab
    '''
    
    def __init__(self):
        IWidget.__init__(self)
        self.conf_dict = {}
        self.server_dict = {}
        self.service_combobox = None
        self.port_combobox = None
        
        self.project_frame = gtk.Frame("Project")
        self.project_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.server_frame = gtk.Frame("Server")
        self.server_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.auth_frame = gtk.Frame("Authentication")
        self.auth_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.service_frame = gtk.Frame("Default service")
        self.service_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.port_frame = gtk.Frame("Default port")
        self.port_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        
        self.save_btn = None
        self.vbox = None
        
    def start(self, conf_list, server_list):
        # Generate labels
        if not conf_list or not server_list:
            raise antaresException("Either configuration or settings list parameters are missing for config widget")
        
        # Create widgets (lables, entries, combobox, ...
        for key, value in conf_list.items():
            label = gtk.Label(key.title())
            entry = gtk.Entry(0)
            entry.set_editable(False)
            if not value:
                entry.set_text('')
            else:
                entry.set_text(value)
            self.conf_dict[key] = (label, entry)
            
        for key, value in server_list.items():
            label = gtk.Label(key.title())
            entry = gtk.Entry(0)
            entry.set_editable(False)
            if not value:
                entry.set_text('')
            else:
                entry.set_text(value)
            self.server_dict[key] = (label, entry) 
        
        # Project frame
        label = gtk.Label("View WSDL")
        viewButton = gtk.Button("View WSDL", gtk.STOCK_EXECUTE)
        viewButton.connect("clicked", self.viewWSDL, None)
        self.conf_dict["viewwsdl"] = (label, viewButton)
        
        table = gtk.Table(len(self.conf_dict)-2, 2, True)
        column = 0
        row = 0
        for text in sorted(self.conf_dict.iterkeys()):
            table.attach(self.conf_dict[text][0], column, column+1, row, row+1)
            column += 1
            table.attach(self.conf_dict[text][1], column, column+1, row, row+1)
            column = 0
            row += 1
            
        self.project_frame.add(table)
        
        # Server frame
        table = gtk.Table(len(self.server_dict), 2, True)
        column = 0
        row = 0
        for text in sorted(self.server_dict.iterkeys()):
            table.attach(self.server_dict[text][0], column, column+1, row, row+1)
            column += 1
            table.attach(self.server_dict[text][1], column, column+1, row, row+1)
            column = 0
            row += 1
            
        self.server_frame.add(table)
        
        # Authentication frame
        table = gtk.Table(4, 2, True)
        table.attach(gtk.Label('Type'), 0, 1, 0, 1)
        if project_manager.getAuthType() == AUTH_BASIC:
            entry = gtk.Entry(0)
            entry.set_text('Basic')
            table.attach(entry, 1, 2, 0, 1)
        table.attach(gtk.Label('Domain'), 0, 1, 1, 2)
        entry = gtk.Entry(0)
        entry.set_text(project_manager.getDomain())
        table.attach(entry, 1, 2, 1, 2)
        table.attach(gtk.Label('Username'), 0, 1, 2, 3)
        entry = gtk.Entry(0)
        entry.set_text(project_manager.getUsername())
        table.attach(entry, 1, 2, 2, 3)
        table.attach(gtk.Label('Password'), 0, 1, 3, 4)
        entry = gtk.Entry(0)
        entry.set_text(project_manager.getPassword())
        table.attach(entry, 1, 2, 3, 4)
        
        self.auth_frame.add(table)
        
        # Default webService service and port combobox
        wsdl = core.iswsdlhelper()
        if wsdl:
            self.service_combobox = gtk.combo_box_entry_new_text()
            self.service_combobox.append_text('')
            for service in wsdl.getServices():
                self.service_combobox.append_text(service)
                self.service_combobox.child.connect('changed', self.changeService)
        self.service_combobox.set_active(0)
        self.service_frame.add(self.service_combobox)
        
        if wsdl:
            self.port_combobox = gtk.combo_box_entry_new_text()
            self.port_combobox.append_text('')
            for bind in wsdl.getBindings():
                self.port_combobox.append_text(bind.name)
                self.port_combobox.child.connect('changed', self.changeBind)
        self.port_combobox.set_active(0)
        self.port_frame.add(self.port_combobox)
        
        self.vbox = gtk.VBox(False, 0)
        self.vbox.pack_start(self.project_frame, True, True, 0)
        self.vbox.pack_start(self.server_frame, True, True, 0)
        self.vbox.pack_start(self.auth_frame, True, True, 0)
        self.vbox.pack_start(self.service_frame, True, True, 0)
        self.vbox.pack_start(self.port_frame, True, True, 0)
        self.vbox.show_all()
        
    def getWidget(self):
        return self.vbox
    
    def viewWSDL(self, widget, action):
        popup = gtk.Window()
        popup.set_title( "WSDL" )
        popup.set_modal( True )
        popup.resize(600,800)
        popup.set_type_hint( gtk.gdk.WINDOW_TYPE_HINT_DIALOG )
        popup.connect( "destroy", lambda *w:popup.destroy() )
        vb = gtk.VBox(False, 2)
        frame = gtk.Frame('WSDL Contents')
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        buff = gtk.TextBuffer()
        soup = BeautifulSoup(project_manager.getWSDLContents())
        buff.set_text(soup.prettify())
        textview = gtk.TextView(buffer=buff)
        textview.set_editable(False)
        textview.set_wrap_mode(gtk.WRAP_NONE)
        textview.set_justification(gtk.JUSTIFY_LEFT)
        textview.set_cursor_visible(True)
        sw.show_all()
        sw.add_with_viewport(textview)
        sw.set_size_request(400, -1)
        vb.pack_start(sw, True, True, 0)
        btn = gtk.Button('Close', gtk.STOCK_CLOSE)
        btn.connect('clicked', lambda *w: popup.destroy() )
        vb.pack_start(btn, False, False, 0)
        frame.add(vb)
        popup.add(frame)
        popup.show_all()
        
    def changeBind(self, entry):
        core.iswsdlhelper().setPort(entry.get_text())
    def changeService(self, entry):
        core.iswsdlhelper().setService(entry.get_text())
    
        """
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
        saveButton.connect("clicked", self.saveSettings)
        hbox = gtk.HBox(False, 0)
        hbox.pack_end(saveButton, False, False, 0)
        
        
        #Add everything to VBox
        
        self.vbox.pack_start(self.fProj, False, False, 0)
        self.vbox.pack_start(self.server_frame, False, False, 0)
        self.vbox.pack_start(fService, False, False, 0)
        self.vbox.pack_start(self.fBinding, False, False, 0)
        self.vbox.pack_start(self.fAuth, False, False, 0)
        self.vbox.pack_start(hbox, False, False, 0)
        self.vbox.show_all()

        
    def saveSettings(self, w):
        d = {}
        d['name']  = self.prjName.get_text()
        d['url'] = self.uri.get_text()
        d['hostname'] = self.IP.get_text()
        d['port'] = self.port.get_text()
        d['header'] = self.servHeader.get_text()
        d['user'] = self.user.get_text()
        d['pwd'] = self.pwd.get_text()
        project_manager.saveProject(d)

"""