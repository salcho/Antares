'''
Created on Feb 12, 2013

@author: Santiago Diaz
'''

import gtk
import BeautifulSoup
from core.fwCore import core
from core.utils.project_manager import pm

class TestRequestWidget:
	'''
	TestRequestWidget used to send test requests to be later compared with injection requests
	IMPORTANT: This widget needs to be started!
	'''

	def __init__(self):
		self.oCombobox = None
		self.opSelected = None
		self.opName = None
		
		self.vbox = gtk.VBox()
		self.TVRq = None
		self.TVRp = None

	def start(self):
		frame = gtk.Frame('Methods')
		frame2 = gtk.Frame('Request/Response')
		frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		frame2.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.oCombobox = gtk.combo_box_new_text()
		self.oCombobox.append_text('')
		if core.iswsdlhelper():
			ops = core.iswsdlhelper().getMethods()
			for op in ops:
				self.oCombobox.append_text(op)
				self.oCombobox.connect('changed', self.changeOp)
		frame.add(self.oCombobox)
		self.vbox = gtk.VBox()
		hpaned = gtk.HPaned()
		hpaned.show()
		#Create textview for responses
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		self.TVRq = gtk.TextView(buffer=None)
		self.TVRq.set_editable(True)
		self.TVRq.set_wrap_mode(gtk.WRAP_WORD)
		self.TVRq.set_justification(gtk.JUSTIFY_LEFT)
		self.TVRq.set_cursor_visible(True)
		sw.add_with_viewport(self.TVRq)
		sw.set_size_request(400, -1)
		sw.show_all()
		
		hpaned.add1(sw)
		
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		self.TVRp = gtk.TextView(buffer=None)
                self.TVRp.set_editable(False)
                self.TVRp.set_wrap_mode(gtk.WRAP_WORD)
                self.TVRp.set_justification(gtk.JUSTIFY_LEFT)
                self.TVRp.set_cursor_visible(True)
		sw.show_all()
		sw.add_with_viewport(self.TVRp)
		sw.set_size_request(400, -1)
		
		btn = gtk.Button('Send', gtk.STOCK_EXECUTE)
		btn.connect('clicked', self.sendRx, None)
		hpaned.add2(sw)
		frame2.add(hpaned)
		self.vbox.pack_start(frame, True, False, 0)
		self.vbox.pack_start(frame2, True, True, 0)
		self.vbox.pack_start(btn, True, False, 0)
		self.vbox.show_all()


	def sendRx(self, widget, data):
		buf = self.TVRq.get_buffer()
		start, end = buf.get_bounds()
		if core.iswsdlhelper():
			wsdl = core.iswsdlhelper()
			xml = wsdl.sendRaw(self.opSelected, buf.get_text(start, end))
			buf = self.TVRp.get_buffer()
			buf.set_text(str(xml))

	def changeOp(self, w):
		model = w.get_model()
		index = w.get_active()
		tosend = {}
		if index:
			self.opSelected = model[index][0]
			if self.opName != model[index][0]:
				self.opName = model[index][0]
				if core.iswsdlhelper():
					wsdl = core.iswsdlhelper()
					req, res = wsdl.getRqRx(self.opName)
					if req and res:
						buf = self.TVRq.get_buffer()
						buf.set_text(str(req))
						buf = self.TVRp.get_buffer()
						buf.set_text(str(res))

	def getWidget(self):
		return self.vbox


