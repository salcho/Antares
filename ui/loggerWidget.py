#!/usr/bin/env python

import gtk
from ui.IWidget import IWidget

#TODO: Implement file-like thread to show logging!
class loggerWidget(IWidget):
	
	def __init__(self):
		self.frame = gtk.Frame('Logger')
		self.text_view = gtk.TextView()

	def start(self):
		self.frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.text_view.set_editable(False)
		self.text_view.set_wrap_mode(gtk.WRAP_NONE)
		self.text_view.set_justification(gtk.JUSTIFY_LEFT)
		self.text_view.set_cursor_visible(True)
		sw.add_with_viewport(self.text_view)
		self.frame.add(sw)

	def getWidget(self):
		return self.frame
