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

		self.selectedOps = None

		self.frame_ops = gtk.Frame("Operations")
		self.frame_params = gtk.Frame("Parameters")
		self.frame_res = gtk.Frame("Results")

		self.hbox.pack_start(self.frame_ops, True, True, 0)
		self.hbox.pack_start(self.frame_params, True, True, 0)
		self.hbox.pack_start(self.frame_res, True, True, 0)

	def getWidget(self):
		self.hbox.show_all()
		return self.hbox
	
	def start(self):
		"""
		if core.iswsdlhelper():
			ops = core.iswsdlhelper().getMethods()
			sw = gtk.ScrolledWindow()
			sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
			vbtnbox = gtk.VButtonBox()
			vbtnbox.set_layout(gtk.BUTTONBOX_START)
			vbtnbox.set_spacing(1)
			for op in ops:
				chkbtn = gtk.CheckButton(op)
				chkbtn.connect("toggled", self.opSelected, chkbtn.get_label())
				vbtnbox.add(chkbtn)
			sw.add_with_viewport(vbtnbox)
			self.frame_ops.add(sw)
		"""
		self.fillFrameOperations()
		

	def opSelected(self, widget, action):
		if widget.get_active() and action != self.selectedOps:
			#self.selectedOps.append(action)
			self.selectedOps = action
		if not widget.get_active() and action != self.selectedOps:
			#self.selectedOps.remove(action)
			self.selectedOps = action
		self.fillFrameParams(self.selectedOps)

	def fillFrameOperations(self):
		"""
		This will one of the frames with whatever you ask for
		Frames are: operations, parameters, results
		"""
		wsdl = core.iswsdlhelper()
		if wsdl:
			ops = wsdl.getMethods()
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
		"""
		This will one of the frames with whatever you ask for
		Frames are: operations, parameters, results
		"""
		wsdl = core.iswsdlhelper()
		if wsdl:
			for child in self.frame_params.get_children():
				self.frame_params.remove(child)
			self.frame_params.set_label("Parameters")
			ops = wsdl.getParamsNames(opName)
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
	
				sw.add_with_viewport(vbtnbox)
				self.frame_params.add(sw)
			else:
				sw.add_with_viewport(gtk.Label("This method has no parameters"))
				
		self.frame_ops.show_all()
		self.frame_params.show_all()

	def paramSelected(self, w):
		pass
