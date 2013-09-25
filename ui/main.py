'''
Created on Jan 19, 2013

@author: Santiago Diaz M. - salchoman@gmail.com
'''

import pygtk
import gtk
import cPickle 
from core.utils.project_manager import project_manager
from core.utils.project_manager import AUTH_BASIC
from core.utils.project_manager import AUTH_WINDOWS
from core.utils.project_manager import AUTH_UNKNOWN
from core.exceptions import antaresException

class mainUI(object):
	
	def __init__(self):
		self.cw = None

	def start(self):
		self.cw = CustomWindow()
		self.cw.getWindow().show()
		gtk.main()
		
	def showError(self, txt):
		self.cw.showErrorDialog(txt)
	
	# Call a function from one of the widgets!
	def callFromWidget(self, tab_name, function_name):
		widget = self.cw.getNotebook().getTabs()[tab_name]
		func = getattr(widget, function_name)
		return func()

class CustomWindow():
	
	def __init__(self):
		self.uiManager = None
		self.actionGroup = None
		self.currProject = None
		self.main_notebook = None
		self.notebook = None
		self.vbox = None
		
		self._window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self._window.set_title('Antares')
		self._window.resize(1400, 650)
		self._window.connect('delete_event', lambda w: gtk.main_quit)
		self._window.connect('destroy', gtk.main_quit)
		
		# UIManager description
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
									  # xml, icon, label, accelerator, tooltip, callback 
									  ('CreateProject', gtk.STOCK_ADD, ('Create project'), None, 'Create a new project', self.createProject),
									  ('LoadProject', gtk.STOCK_CONVERT, ('_Load project'), None, 'Load an existing project', self.loadProject),
									  ('DeleteProject', gtk.STOCK_DELETE, ('Delete project'), None, 'Delete this project', self.deleteProject),
									  ('SaveProject', gtk.STOCK_SAVE, ('_Save project'), None, 'Save this project', self.saveProject),
									  ('ProjectsMenu', None, ('_Projects')),
									  ('Exit', gtk.STOCK_QUIT, ('_Exit'), None, 'Exit framework', gtk.main_quit),
									  ('FilesMenu', None, ('_File'))				  
									   ])
		self._window.add_accel_group(self.uiManager.get_accel_group())
		# TODO: Set toggle actions
		self.uiManager.insert_action_group(self.actionGroup, 0)
		self.uiManager.add_ui_from_string(uidesc)
		# Main VBox
		self.vbox = gtk.VBox(False, 0)
		self.menu_bar = self.uiManager.get_widget('/MenuBar')
		self.vbox.pack_start(self.menu_bar, False, False, 0)
		self.toolbar = self.uiManager.get_widget('/ToolBar')
		self.vbox.pack_start(self.toolbar, expand=False)
		self.vbox.show_all()
		self._window.set_position(gtk.WIN_POS_CENTER)
		self._window.add(self.vbox)
		self._window.show_all()
	
	def createProject(self, action):
		dialog = gtk.Dialog("", None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		dialog.vbox.pack_start(gtk.Label("Name"), True, True, 0)
		name = gtk.Entry(0)		   
		dialog.vbox.pack_start(name, True, True, 0)
		dialog.vbox.pack_start(gtk.Label("Initial WSDL URL"), True, True, 0)
		url = gtk.Entry(0)		   
		dialog.vbox.pack_start(url, True, True, 0)
		dialog.show_all() 
		
		rsp = dialog.run()
		if rsp == gtk.RESPONSE_OK:
			if name.get_text() != '' and url.get_text() != "":
				if not url.get_text().lower().startswith('http') or url.get_text().lower().startswith('https'):
					self.showErrorDialog('Correct URLs must begin with HTTP or HTTPS protocols.')
					dialog.destroy()
					return 
				
				# Test for authentication methods on the application layer
				ret = project_manager.detectProtocolAuth(url.get_text())
				if ret:
					# Basic auth!
					if ret == AUTH_BASIC:
						auth_dict = self.showAuthDialog(AUTH_BASIC)
					# NTLM auth
					elif ret == AUTH_WINDOWS:
						# Is python_ntlm installed?
						try:
							import ntlm
						except ImportError:
							self.showErrorDialog("NTLM authentication detected!\nSorry, the python_ntlm library wasn't found. This operation isn't supported.")
							dialog.destroy()
							return
						auth_dict = self.showAuthDialog(AUTH_WINDOWS)
					# What could this be?
					elif ret == AUTH_UNKNOWN:
						self.showErrorDialog("This server uses a unsupported/unknown authentication method. Check debug messages for more details.")
						dialog.destroy()
						return
					# Something wrong happened
					else:
						if 'timed out' in ret:
							self.showErrorDialog('Connection to target timed out. Can you really connect to given port?')
						elif 'connection refused' in ret.lower():
							self.showErrorDialog('Connection refused while connecting with server. You sure server is up?')
						elif 'no route to host' in ret.lower():
							self.showErrorDialog('No route to host. Check IP address!')
						dialog.destroy()
						return
					
				if ret and auth_dict:
					ret = project_manager.createProject(name.get_text(), url.get_text(), auth_dict=auth_dict)
				elif ret and not auth_dict:
					self.showErrorDialog('Please specify a valid set of credentials...')
					dialog.destroy()
					return
				else:
					ret = project_manager.createProject(name.get_text(), url.get_text())
				if "error" in ret.lower():
					self.showErrorDialog(ret)
				else:
					self.showMessageDialog("Project created!")
	
		dialog.destroy()
		
	def loadProject(self, action):
		dialog = gtk.Dialog("", None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		frame = gtk.Frame("Select project to load")
		frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		projs = project_manager.projList()
		if projs:
			vbox = gtk.VBox(True, 0)
			if len(projs) > 1:
					group = gtk.RadioButton(group=None, label=None)
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
			chkbtn.set_active(False)
			savewsdl_btn = gtk.CheckButton("Save WSDL automatically?")
			savewsdl_btn.connect("toggled", self.saveWSDL)
			savewsdl_btn.set_active(False)
			
			frame.add(vbox)
			dialog.vbox.pack_start(frame, True, True, 0)
			dialog.vbox.pack_start(chkbtn, True, True, 0)
			dialog.vbox.pack_start(savewsdl_btn, True, True, 0)
			dialog.show_all()
			rsp = dialog.run()
			if rsp == gtk.RESPONSE_OK:
				ret = project_manager.loadProject(self.currProject, savewsdl_btn.get_active(), chkbtn.get_active())
				if 'Error' in ret:
					self.showErrorDialog(ret)

				if chkbtn.get_active():
					self.currProject = 'file://' + project_manager.getWSDLPath()
				else:
					self.currProject = project_manager.getURL()
					
				# Create WSDLHelper object
				from core.fwCore import core
				self.core = core
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
				self.initNotebook()
				
				# Delete and restore main vbox. Is there a better way to do this?
				for child in self.vbox.get_children():
					self.vbox.remove(child)
				self.vbox.pack_start(self.menu_bar, False, False, 0)
				self.vbox.pack_start(self.toolbar, expand=False)
				self.vbox.pack_start(self.main_notebook.getNotebook(), True, True, 0)

	def initNotebook(self):
		from ui.fwNotebook import mainNotebook
		self.main_notebook = mainNotebook()
		if self.core.iswsdlhelper():
			# Get settings, populate notebook
			self.main_notebook.populate(project_manager.getCurrentSettings(), self.core.getServerInfo())
			
	def projSelected(self, widget, action):
		self.currProject = action

	def readFrom(self, widget):
		pass
		
	def saveWSDL(self, widget):
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
					group = gtk.RadioButton(group=None, label=None)
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
			
	def showAuthDialog(self, type):
		realm = gtk.Entry(0)
		username = gtk.Entry(0)
		password = gtk.Entry(0)
		dialog = gtk.Dialog("", None, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK))
		if type == AUTH_BASIC:
			dialog.vbox.pack_start(gtk.Label("Basic authentication required to download WSDL object.\nPlease enter credentials below.\n"), True, True, 0)
		elif type == AUTH_WINDOWS:
			dialog.vbox.pack_start(gtk.Label("Windows authentication required to download WSDL object.\nPlease enter credentials below.\n"), True, True, 0)
		dialog.vbox.pack_start(gtk.Label("Realm/Domain <default:IP>"), True, True, 0)		   
		dialog.vbox.pack_start(realm, True, True, 0)
		dialog.vbox.pack_start(gtk.Label("Username"), True, True, 0)
		dialog.vbox.pack_start(username, True, True, 0)
		dialog.vbox.pack_start(gtk.Label("Password"), True, True, 0)		   
		dialog.vbox.pack_start(password, True, True, 0)
		dialog.show_all()
		rsp = dialog.run()
		if rsp == gtk.RESPONSE_OK:
			if not realm.get_text() and (type == AUTH_BASIC or type == AUTH_WINDOWS):
				realm.set_text(project_manager.getIP())
			if username.get_text() and password.get_text():
				# Tell given credentials using the self.currSettings['auth'] structure in project_manager
				auth_dict = {'type': type, 
							'domain': realm.get_text(), 
							'user': username.get_text(), 
							'password': password.get_text()}
				dialog.destroy()
				return auth_dict
		dialog.destroy()
		return None
	
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
			
	# For communication between widgets!
	def getNotebook(self):
		return self.main_notebook
	
	def toDelete(self, w, name):
		self.todelete = name
	
	def saveProject(self, w):
		try:
			if project_manager.saveProject(self.core.getServerInfo()):
				self.showMessageDialog("Project saved!")
			else:
				self.showErrorDialog("Error: Project couldn't be saved. You sure we have write permission on the file?")
		except:
			pass
			
	def getWindow(self):
			return self._window