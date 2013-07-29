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
	
				sw.add_with_viewport(vbtnbox)
				self.frame_params.add(sw)
			else:
				sw.add_with_viewport(gtk.Label("This method has no parameters"))

		self.frame_params.show_all()
		self.fillFramePayloads()
		
	def fillFramePayloads(self):
		if len(self.selectedArgs) == 0 or not self.wsdl:
			pass
			return
		
		res = self.wsdl.getParamObjs(self.selectedOp, params=self.selectedArgs)
		print res
		
		
		
	#---------------
	# select different stuff
	#---------------
	def paramSelected(self, widget, action):
		if widget.get_active() and action != self.selectedOp:
			self.selectedArgs.append(action)
		if not widget.get_active() and action != self.selectedOp:
			self.selectedArgs.remove(action)
		self.fillFramePayloads()
		
	def opSelected(self, widget, action):
		if widget.get_active() and action != self.selectedOp:
			#self.selectedOp.append(action)
			self.selectedOp = action
		if not widget.get_active() and action != self.selectedOp:
			#self.selectedOp.remove(action)
			self.selectedOp = action
		self.fillFrameParams(self.selectedOp)
