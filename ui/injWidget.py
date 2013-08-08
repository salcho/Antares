'''
Created on Feb 20, 2013

@author: Santiago Diaz M.
'''

import gtk
from core.fwCore import core
from ui.IWidget import IWidget

class injWidget(IWidget):
	
	def __init__(self):
		self.hbox = gtk.HBox(True, 0)

		self.selectedOp = None
		self.selectedArgs = []
		self.selectedPayloads = []
		self.wsdl = core.iswsdlhelper()

		self.frame_ops = gtk.Frame("Operations")
		self.frame_params = gtk.Frame("Parameters")
		self.frame_payloads = gtk.Frame("Payloads")
		self.frame_res = gtk.Frame("Results")
		
		frame_vbox = gtk.VBox(True, 0)
		frame_vbox.pack_start(self.frame_ops, True, True, 0)
		frame_vbox.pack_start(self.frame_params, True, True, 0)
		
		self.hbox.pack_start(frame_vbox, True, True, 0)
		self.hbox.pack_start(self.frame_payloads, True, True, 0)
		self.hbox.pack_start(self.frame_res, True, True, 0)

	def getWidget(self):
		self.hbox.show_all()
		return self.hbox
	
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
		check_all_btn.connect("clicked", self.checkAllPlugins, vbtnbox)
		uncheck_all_btn = gtk.Button('Uncheck all')
		uncheck_all_btn.connect("clicked", self.uncheckAllPlugins, vbtnbox)
		hbtnbox.add(check_all_btn)
		hbtnbox.add(uncheck_all_btn)
		return hbtnbox
	
	#---------------
	# fill frames
	# --------------
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
				chkbtn.connect("toggled", self.opSelected, chkbtn.get_label())
				vbtnbox.add(chkbtn)
				
			sw.add_with_viewport(vbtnbox)
			self.frame_ops.add(sw)
				
		self.frame_ops.show_all()
		
	def fillFrameParams(self, opName):
		if self.wsdl:
			for child in self.frame_params.get_children():
				self.frame_params.remove(child)
			self.frame_params.set_label("Parameters")
			ops = self.wsdl.getParamsNames(opName)
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
	
				vbtnbox.add(self.getCheckButtons(vbtnbox))
				sw.add_with_viewport(vbtnbox)
				self.frame_params.add(sw)
			else:
				sw.add_with_viewport(gtk.Label("This method has no parameters"))

		self.frame_params.show_all()
		
	def fillFramePayloads(self):
		plug_manager = core.isPluginManager()
		if plug_manager:
			self.frame_payloads.set_label("Payloads")
			sw = gtk.ScrolledWindow()
			sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
			vbtnbox = gtk.VButtonBox()
			vbtnbox.set_layout(gtk.BUTTONBOX_START)
			vbtnbox.set_spacing(1)
			for plug in plug_manager.getLoadedPlugins().values():
				chkbtn = gtk.CheckButton(plug.getName())
				chkbtn.connect("toggled", self.payloadSelected, chkbtn.get_label())
				vbtnbox.add(chkbtn)
			
			vbtnbox.add(self.getCheckButtons(vbtnbox))
			launch_btn = gtk.Button('Launch', gtk.STOCK_EXECUTE)
			launch_btn.connect("clicked", self.launchAttack, plug_manager)
			vbtnbox.add(launch_btn)
			
			sw.add_with_viewport(vbtnbox)
			self.frame_payloads.add(sw)
			
		self.frame_payloads.show_all()
		
	#---------------
	# select different stuff
	#---------------
	def payloadSelected(self, widget, action):
		if widget.get_active() and action not in self.selectedPayloads:
			self.selectedPayloads.append(action)
		if not widget.get_active() and action in self.selectedPayloads:
			self.selectedPayloads.remove(action)
		
	def paramSelected(self, widget, action):
		if widget.get_active() and action not in self.selectedArgs:
			self.selectedArgs.append(action)
		if not widget.get_active() and action in self.selectedArgs:
			self.selectedArgs.remove(action)
		
	def opSelected(self, widget, action):
		if widget.get_active() and action != self.selectedOp:
			self.selectedOp = action
		if not widget.get_active() and action != self.selectedOp:
			self.selectedOp = action
		self.fillFrameParams(self.selectedOp)
		
	def checkAllPlugins(self, widget, vbtnbox):
		for child in vbtnbox.get_children():
			try:
				child.set_active(True)
			except AttributeError:
				continue
			
	def uncheckAllPlugins(self, widget, vbtnbox):
		for child in vbtnbox.get_children():
			try:
				child.set_active(False)
			except AttributeError:
				continue
			
	def launchAttack(self, widget, plug_manager):
		if self.selectedOp and self.selectedArgs and self.selectedPayloads:
			res_table = plug_manager.startAttack(self.selectedOp, self.selectedArgs, self.selectedPayloads)
			return res_table
		return None