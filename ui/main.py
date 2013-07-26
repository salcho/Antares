'''
Created on Jan 19, 2013

@author: Santiago Diaz M. - salchoman@gmail.com
'''

import pygtk
import gtk
from core.utils.project_manager import project_manager

class mainUI(object):
    def __init__(self):
        self.cw = None
        
    def start(self):
        self.cw = CustomWindow()
        self.cw.getWindow().show()
        gtk.main()
        
    def showError(self, txt):
        self.cw.showErrorDialog(txt)
        
    
class CustomWindow:
    
	def __init__(self):
        	self.uiManager = None
	        self.actionGroup = None
	        self.currProject = None
	        self.notebook = None
	        self.vbox = None
        
	        self._window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	        self._window.set_title('Antares')
	        self._window.resize(1000,450)
	        self._window.connect('delete_event',lambda w: gtk.main_quit)
	        self._window.connect('destroy', gtk.main_quit)
        
		#UIManager description
		uidesc = """
		    <ui>
		        <menubar name="MenuBar">
		            <menu action="FilesMenu">
		                <menuitem action="Exit" />
		            </menu>
		            <menu action="ProjectsMenu">
		                <menuitem action="CreateProject" />
		                <menuitem action="LoadProject" />
		                <menuitem action="DeleteProject" />
		                <menuitem action="SaveProject" />
		            </menu>
		        </menubar>
		        <toolbar name="ToolBar">
		            <toolitem action="Exit" />
		            <separator />
		            <toolitem action="LoadProject" />
		            <separator />
		            <toolitem action="SaveProject" />
		        </toolbar>
		    </ui>
		    """
        
		self.uiManager = gtk.UIManager()
		
		self.actionGroup = gtk.ActionGroup('UIM')
		self.actionGroup.add_actions([
		                              #xml, icon, label, accelerator, tooltip, callback 
		                              ('CreateProject', gtk.STOCK_ADD, ('Create project'), None, 'Create a new project', self.createProject),
		                              ('LoadProject', gtk.STOCK_CONVERT, ('_Load project'), None, 'Load an existing project', self.loadProject),
		                              ('DeleteProject', gtk.STOCK_DELETE, ('Delete project'), None, 'Delete this project', self.deleteProject),
		                              ('SaveProject', gtk.STOCK_SAVE, ('_Save project'), None, 'Save this project', self.saveProject),
		                              ('ProjectsMenu', None, ('_Projects')),
		                              ('Exit', gtk.STOCK_QUIT, ('_Exit'), None, 'Exit framework', gtk.main_quit),
		                              ('FilesMenu', None, ('_File'))                  
		                               ])
		self._window.add_accel_group(self.uiManager.get_accel_group())
		#TODO: Set toggle actions
		self.uiManager.insert_action_group(self.actionGroup, 0)
		self.uiManager.add_ui_from_string(uidesc)
		#Main VBox
		self.vbox = gtk.VBox(False, 0)
		menu_bar = self.uiManager.get_widget('/MenuBar')
		self.vbox.pack_start(menu_bar, False, False, 0)
		toolbar = self.uiManager.get_widget('/ToolBar')
		self.vbox.pack_start(toolbar, expand=False)
		self.vbox.show_all()
		self._window.set_position(gtk.WIN_POS_CENTER)
		self._window.add(self.vbox)
		self._window.show_all()
    
	def createProject(self, action):
		#TODO: Support auth
		dialog = gtk.Dialog("", None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		dialog.vbox.pack_start(gtk.Label("Name"), True, True, 0)
		name = gtk.Entry(20)           
		dialog.vbox.pack_start(name, True, True, 0)
		dialog.vbox.pack_start(gtk.Label("Initial WSDL URL"), True, True, 0)
		url = gtk.Entry(0)           
		dialog.vbox.pack_start(url, True, True, 0)
		dialog.show_all() 
		rsp = dialog.run()
		#dialog.hide()
		if rsp == gtk.RESPONSE_OK:
			if name.get_text() != '' and url.get_text() != "":
		        	ret = project_manager.createProject(name.get_text(), url.get_text())
		        if "Error" in ret:
				self.showErrorDialog(ret)
			else:
				self.showMessageDialog("Project created!")
		dialog.destroy()
    
	def showErrorDialog(self, txt):
		diag = gtk.Dialog("Error", None, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK))
		diag.vbox.pack_start(gtk.Label(txt), True, True, 0)
		diag.show_all()
		diag.run()
		diag.destroy()

	def showMessageDialog(self, txt):
		diag = gtk.Dialog("Information", None, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK))
		diag.vbox.pack_start(gtk.Label(txt), True, True, 0)
		diag.show_all()
		diag.run()
		diag.destroy()
        
	def loadProject(self, action):
		dialog = gtk.Dialog("", None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		frame = gtk.Frame("Select project to load")
		frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		projs = project_manager.projList()
		if projs:
			#self.vbox.pack_start(gtk.Label(project_manager.proj_name), True, True, 0)
			vbox = gtk.VBox(True, 0)
			if len(projs) > 1:
		        	group = gtk.RadioButton(group = None, label = None)
		        	for proj in projs:
					b = gtk.RadioButton(group, proj)
				    	b.connect("toggled", self.projSelected, proj)
					b.set_active(False)
					vbox.pack_start(b, True, True, 0)
			else:
		        	b = gtk.CheckButton(projs.pop())
		        	b.connect("toggled", self.projSelected, b.get_label())
		        	vbox.pack_start(b, True, True, 0)
			chkbtn = gtk.CheckButton('Read WSDL from file?')
			chkbtn.connect("toggled", self.readFrom)
			chkbtn.set_active(True)
			frame.add(vbox)
			dialog.vbox.pack_start(frame, True, True, 0)
			dialog.vbox.pack_start(chkbtn, True, True, 0)
			dialog.show_all()
			rsp = dialog.run()
			if rsp == gtk.RESPONSE_OK:
				ret = project_manager.loadProject(self.currProject)
				if 'Error' in ret:
					self.showErrorDialog(ret)

		        	if chkbtn.get_active():
		        		self.currProject = 'file://' + project_manager.getWSDLPath()
			        else:
					self.currProject = project_manager.getURL()

		        	#Create WSDLHelper object
			        from core.fwCore import core
			        if core.loadWSDL(self.currProject):
					self.addNotebook()
			        	self.vbox.show_all()
			
			dialog.destroy()
		else:
			dialog.vbox.pack_start(gtk.Label("No projects to load in current workspace"), True, True, 0)
			dialog.show_all()
			dialog.run()
			dialog.destroy()
            
	def addNotebook(self):
        	if not self.notebook:
			self.initNotebook()
		else:
			self.notebook.destroy()
			self.initNotebook()
			children = self.vbox.get_children()
			self.vbox.remove(children.pop())
		self.vbox.pack_start(self.notebook, True, True, 0)

	def initNotebook(self):
		from ui.fwNotebook import mainNotebook
		nt = mainNotebook()
		from core.fwCore import core
		if core.iswsdlhelper():
			#Get settings, populate notebook
			nt.populate(project_manager.getCurrentSettings(), core.getServerInfo())
			self.notebook = nt.getNotebook()

	def projSelected(self, widget, action):
        	self.currProject = action

	def readFrom(self, widget):
        	pass
    
	def deleteProject(self, widget):
		dialog = gtk.Dialog("", None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		frame = gtk.Frame("Select project to delete")
		frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		projs = project_manager.projList()
		vbox = gtk.VBox(True, 0)
		if projs:
			vbox.pack_start(gtk.Label(project_manager.proj_name), True, True, 0)
			vbox = gtk.VBox(True, 0)
			if len(projs) > 1:
		        	group = gtk.RadioButton(group = None, label = None)
		        	for proj in projs:
		        		b = gtk.RadioButton(group, proj)
					b.connect("toggled", self.toDelete, proj)
					b.set_active(False)
					vbox.pack_start(b, True, True, 0)
			else:
				b = gtk.CheckButton(projs.pop())
				b.connect("toggled", self.toDelete, b.get_label())
				vbox.pack_start(b, True, True, 0)
			frame.add(vbox)
			dialog.vbox.pack_start(frame, True, True, 0)
			dialog.show_all()
			rsp = dialog.run()
			if rsp == gtk.RESPONSE_OK:
		        	project_manager.deleteProject(self.todelete)
				self.showMessageDialog("Project deleted")
			dialog.destroy()
		else:
			dialog.destroy()
            
	def toDelete(self, w, name):
        	self.todelete = name
    
	def saveProject(self):
        	pass
    
	def getWindow(self):
        	return self._window
    
	'''
                    #Create/reload notebook
                    if len(self.vbox.get_children()) == 2:
                        self.vbox.pack_start(gtk.Label(project_manager.proj_name), True, True, 0)
                    else:
                        self.vbox.remove(self.vbox.get_children().pop())
                        self.vbox.pack_start(gtk.Label(project_manager.proj_name), True, True, 0)
                    self.vbox.show_all()
                    '''
