'''
Created on Feb 20, 2013

@author: Santiago Diaz M.
'''

import gtk
from core.fwCore import core

class injWidget:
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
			#TODO: Adding widgets to frame
			sc = gtk.GtkScrolledWindow()
                        for op in ops:
				chkbtn = gtk.CheckButton(op)
				chkbtn.connect("toggled", self.opSelected, chkbtn.get_label())
				vbox.pack_start(chkbtn, False, False, 0)
				self.frame_ops.add(chkbtn)

	def opSelected(self, widget, action):
		if widget.get_active():
			self.selectedOps.append(action)
			print self.selectedOps
