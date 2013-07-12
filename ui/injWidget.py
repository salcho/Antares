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

		self.selectedOps = []

		self.frame_ops = gtk.Frame("Operations")
		self.frame_plugs = gtk.Frame("Plugins")
		self.frame_res = gtk.Frame("Results")

		self.hbox.pack_start(self.frame_ops, True, True, 0)
		self.hbox.pack_start(self.frame_plugs, True, True, 0)
		self.hbox.pack_start(self.frame_res, True, True, 0)

	def getWidget(self):
		self.hbox.show_all()
		return self.hbox
	
	def start(self):
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

	def opSelected(self, widget, action):
		if widget.get_active() and action not in self.selectedOps:
			self.selectedOps.append(action)
		if not widget.get_active() and action in self.selectedOps:
			self.selectedOps.remove(action)
		print self.selectedOps
