'''
Created on Feb 20, 2013

@author: Santiago Diaz M.
'''

from core.fwCore import core
from ui.IWidget import IWidget
from core.utils.wsresponse_object import wsResponse
import gtk

class injWidget(IWidget):
	
	def __init__(self):
		IWidget.__init__(self)
		self.hbox = gtk.HBox(False, 0)

		self.selected_op = None
		self.selected_params = []
		self.selected_payloads = []
		self.wsdl = core.iswsdlhelper()
		self.progressbar = None
		self.num_threads = gtk.Entry(0)
		self.tree_model = None
		self.tmsort = None
		self.tree_view = None
		self.launch_button = None
		self.stop_button = None

		self.frame_ops = gtk.Frame("Operations")
		self.frame_params = gtk.Frame("Parameters")
		self.frame_payloads = gtk.Frame("Payloads")
		self.frame_res = gtk.Frame("Results")
		
		frame_vbox = gtk.VBox(True, 0)
		frame_vbox.pack_start(self.frame_ops, True, True, 0)
		frame_vbox.pack_start(self.frame_params, True, True, 0)
		
		self.hbox.pack_start(frame_vbox, False, True, 0)
		self.hbox.pack_start(self.frame_payloads, False, True, 0)
		self.hbox.pack_start(self.frame_res, True, True, 0)

	def getWidget(self):
		self.hbox.show_all()
		return self.hbox
	
	# Load operations for this binding and loaded payloads
	def start(self):
		self.fillFrameOperations()
		self.fillFramePayloads()

	"""
	Pack and return buttons for checking and unchecking all checkbuttons
	"""
	def getCheckButtons(self, vbtnbox):
		hbtnbox = gtk.HButtonBox()
		hbtnbox.set_layout(gtk.BUTTONBOX_SPREAD)
		check_all_btn = gtk.Button('Check all')
		check_all_btn.connect("clicked", self.checkAll, vbtnbox)
		uncheck_all_btn = gtk.Button('Uncheck all')
		uncheck_all_btn.connect("clicked", self.uncheckAll, vbtnbox)
		hbtnbox.add(check_all_btn)
		hbtnbox.add(uncheck_all_btn)
		return hbtnbox
	
	def fillFrameOperations(self):
		if self.wsdl:
			ops = self.wsdl.getMethods()
			sw = gtk.ScrolledWindow()
			sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
			vbtnbox = gtk.VButtonBox()
			vbtnbox.set_layout(gtk.BUTTONBOX_START)
			vbtnbox.set_spacing(1)
			chkbtn = None
			for op in ops:
				chkbtn = gtk.RadioButton(group=chkbtn, label=op)
				chkbtn.connect("clicked", self.opSelected, chkbtn.get_label())
				chkbtn.set_active(False)
				vbtnbox.add(chkbtn)
			
			sw.add_with_viewport(vbtnbox)
			self.frame_ops.add(sw)
				
		self.frame_ops.show_all()
		
	# Fill this frame with the params corresponding to the selected operation
	def fillFrameParams(self):
		if self.wsdl:
			for child in self.frame_params.get_children():
				self.frame_params.remove(child)
			self.frame_params.set_label("Parameters")
			ops = self.wsdl.getParamsNames(self.selected_op)
			sw = gtk.ScrolledWindow()
			sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
			if ops:
				vbtnbox = gtk.VButtonBox()
				vbtnbox.set_layout(gtk.BUTTONBOX_START)
				vbtnbox.set_spacing(1)
				for op in ops:
					chkbtn = gtk.CheckButton(op)
					chkbtn.connect("toggled", self.paramSelected, chkbtn.get_label())
					vbtnbox.add(chkbtn)
	
				vbtnbox.add(gtk.HSeparator())
				vbtnbox.add(self.getCheckButtons(vbtnbox))
				sw.add_with_viewport(vbtnbox)
				self.frame_params.add(sw)
			else:
				self.frame_params.add(gtk.Label("This method has no parameters"))

		self.frame_params.show_all()
		
	# Fill this frame with loaded payloads
	def fillFramePayloads(self):
		plug_manager = core.isPluginManager()
		if plug_manager:
			self.frame_payloads.set_label("Payloads")
			sw = gtk.ScrolledWindow()
			sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
			vbtnbox = gtk.VButtonBox()
			vbtnbox.set_layout(gtk.BUTTONBOX_START)
			vbtnbox.set_spacing(1)
			for plug in plug_manager.getLoadedPlugins().values():
				chkbtn = gtk.CheckButton(plug.getName())
				chkbtn.connect("toggled", self.payloadSelected, chkbtn.get_label())
				vbtnbox.add(chkbtn)
			
			hbox = gtk.HBox(False, 1)
			hbox.pack_start(gtk.Label("Threads"))
			hbox.pack_start(self.num_threads)
			self.launch_button = gtk.Button('Launch', gtk.STOCK_EXECUTE)
			self.launch_button.connect("clicked", self.launchAttack, plug_manager)
			
			self.stop_button = gtk.Button('Stop', gtk.STOCK_STOP)
			self.stop_button.set_sensitive(False)
			self.stop_button.connect("clicked", self.stopAttack, plug_manager)
			
			self.progressbar = gtk.ProgressBar(adjustment=None)
			self.num_threads.set_buffer(gtk.EntryBuffer('5', 1))
			self.num_threads.set_alignment(0.5)
			
			vbtnbox.add(gtk.HSeparator())
			vbtnbox.add(self.getCheckButtons(vbtnbox))
			vbtnbox.add(hbox)
			vbtnbox.add(self.launch_button)
			vbtnbox.add(self.stop_button)
			vbtnbox.add(self.progressbar)
			
			sw.add_with_viewport(vbtnbox)
			self.frame_payloads.add(sw)
			
		self.frame_payloads.show_all()
		
	def fillResultsFrame(self, res_list):
		# Reset frame
		for child in self.frame_res.get_children():
			self.frame_res.remove(child)
		self.frame_res.set_label("Results")
		
		if res_list:
			self.tree_model = gtk.TreeStore(str, str, str, str, str, str, str) 
			# Sort results by ID
			res_list = sorted(res_list, key=lambda plugin: plugin.getPlugin().getName())
			# Fill the TreeModel
			parent_iters = {}
			for response in res_list:
				plugin_name = response.getPlugin().getName()
				if plugin_name not in parent_iters:
					parent_iters[plugin_name] = self.tree_model.append(None, [plugin_name, None, None, None, None, None, None])
				
				if response.getBody():
					self.tree_model.append(parent_iters[plugin_name], 
										[None, 
										response.getID(), 
										response.getParams(), 
										response.getSize(), 
										response.getHTTPCode(), 
										response.getPayload(), 
										response.getBody()])
			
			# Setup TreeView
			self.tmsort = gtk.TreeModelSort(self.tree_model)
			self.tree_view = gtk.TreeView(self.tmsort)
			tvcolumns = {}
			cells = {}
			i = 0
			for col in ('Plugin','ID', 'Parameter', 'Size', 'HTTP Code', 'Payload', 'Response (truncated)'):	
				tvcolumns[col] = gtk.TreeViewColumn(col)	
				self.tree_view.append_column(tvcolumns[col])
				cells[col] = gtk.CellRendererText()
				tvcolumns[col].pack_start(cells[col], True)
				tvcolumns[col].add_attribute(cells[col], 'text', i)
				i += 1
			
			# Make searchable
			self.tree_view.set_search_column(1)
			scrolled_window = gtk.ScrolledWindow()
			scrolled_window.add_with_viewport(self.tree_view)
			self.frame_res.add(scrolled_window)
		else:
			self.frame_res.add(gtk.Label("Kaput! The analyzer had no time to calculate statistics. Try lowering the number of attacking threads."))
		
		
		self.frame_res.show_all()
		
	#---------------
	# manage selected operations, parameters and payloads
	#---------------
	def payloadSelected(self, widget, action):
		if widget.get_active() and action not in self.selected_payloads:
			self.selected_payloads.append(action)
		if not widget.get_active() and action in self.selected_payloads:
			self.selected_payloads.remove(action)
		
	def paramSelected(self, widget, action):
		if widget.get_active() and action not in self.selected_params:
			self.selected_params.append(action)
		if not widget.get_active() and action in self.selected_params:
			self.selected_params.remove(action)
		
	def opSelected(self, widget, action):
		if widget.get_active() and action != self.selected_op:
			self.selected_op = action
			self.selected_params = []
			self.fillFrameParams()
		
	def checkAll(self, widget, vbtnbox):
		for child in vbtnbox.get_children():
			try:
				child.set_active(True)
			except AttributeError:
				continue
			
	def uncheckAll(self, widget, vbtnbox):
		for child in vbtnbox.get_children():
			try:
				child.set_active(False)
			except AttributeError:
				continue
			
	# Call plugin_manager and execute attack
	def launchAttack(self, widget, plug_manager):
		if self.selected_op and self.selected_params and self.selected_payloads and int(self.num_threads.get_text()):
			self.launch_button.set_sensitive(False)
			self.stop_button.set_sensitive(True)
			self.updateProgress(text='Waiting')
			res_list = plug_manager.startAttack(self.selected_op, 
												self.selected_params, 
												self.selected_payloads, 
												int(self.num_threads.get_text()), 
												progress=self.updateProgress)
			
			# Tell the analyzer to refresh this
			from ui.fwNotebook import ANALYZE_TAB
			ret = core.callUI(ANALYZE_TAB, 'refresh')
			self.updateProgress(text='Done')
			if ret:
				self.fillResultsFrame(res_list)
			else:
				self.fillResultsFrame(None)
			#return res_list
		else:
			if not self.selected_op:
				self.updateProgress(percent=0, text='No operation selected')
			if not self.selected_params:
				self.updateProgress(percent=0, text='No params to inject')
			if not self.selected_payloads:
				self.updateProgress(percent=0, text='No plugins selected')
			if not int(self.num_threads.get_text()):
				self.updateProgress(percent=0, text='No threads')
		self.stop_button.set_sensitive(False)
		self.launch_button.set_sensitive(True)
		return
	
	def stopAttack(self, widget, plug_manager):
		self.updateProgress(text="Stopping threads")
		plug_manager.stopAttack()
		self.stop_button.set_sensitive(False)
		self.launch_button.set_sensitive(True)
		
	"""
	Receives percentage done, optional text and updates the progress bar
	"""
	def updateProgress(self, percent=None, text=None):
		if not percent and not text:
			return
		if percent > 1 or percent < 0:
			return
		if text:
			self.progressbar.set_text(text)
		if percent != None:
			self.progressbar.set_fraction(percent)
			while gtk.events_pending():
				gtk.main_iteration()