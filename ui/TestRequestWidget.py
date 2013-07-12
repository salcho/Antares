'''
Created on Feb 12, 2013

@author: Santiago Diaz
'''

import gtk
from bs4 import BeautifulSoup
from core.fwCore import core
from core.utils.project_manager import pm
from ui.IWidget import IWidget

class TestRequestWidget(IWidget):
	'''
	TestRequestWidget used to send test requests to be later compared with injection requests
	IMPORTANT: This widget needs to be started!
	'''

	def __init__(self):
		self.oCombobox = None
		self.opName = None
		
		self.vbox = gtk.VBox(False, 0)
		self.TVRq = None
		self.TVRp = None

	def start(self):
		frame = gtk.Frame('Methods')
		frame2 = gtk.Frame('Request/Response')
		frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		frame2.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		self.oCombobox = gtk.combo_box_entry_new_text()
		self.oCombobox.append_text('')
		if core.iswsdlhelper():
			ops = core.iswsdlhelper().getMethods()
			for op in ops:
				self.oCombobox.append_text(op)
				self.oCombobox.child.connect('changed', self.changeOp)
			frame.add(self.oCombobox)
		self.vbox = gtk.VBox(False, 0)
		hpaned = gtk.HPaned()
		hpaned.show()
		#Create textview for responses
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.TVRq = gtk.TextView(buffer=None)
		self.TVRq.set_editable(True)
		self.TVRq.set_wrap_mode(gtk.WRAP_NONE)
		self.TVRq.set_justification(gtk.JUSTIFY_LEFT)
		self.TVRq.set_cursor_visible(True)
		sw.add_with_viewport(self.TVRq)
		sw.set_size_request(400, -1)
		sw.show_all()
		
		hpaned.pack1(sw, resize=True, shrink=False)
		
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.TVRp = gtk.TextView(buffer=None)
		self.TVRp.set_editable(False)
		self.TVRp.set_wrap_mode(gtk.WRAP_NONE)
		self.TVRp.set_justification(gtk.JUSTIFY_LEFT)
		self.TVRp.set_cursor_visible(True)
		sw.show_all()
		sw.add_with_viewport(self.TVRp)
		sw.set_size_request(400, -1)
		
		frame3 = gtk.Frame('Actions')
		box = gtk.HButtonBox()
		box.set_spacing(gtk.BUTTONBOX_SPREAD)
		btnSend = gtk.Button('Send', gtk.STOCK_EXECUTE)
		btnSend.connect('clicked', self.sendRx, None)
		btnCdata = gtk.Button('Add CDATA block')
		btnCdata.connect('clicked', self.addCDATA)
		btnCmnt = gtk.Button('Comment selection')
		btnCmnt.connect('clicked', self.comment)
		#box.add(gtk.Label('Lines: ' + self.TVRq.get_))
		box.add(btnSend)
		box.add(btnCdata)
		box.add(btnCmnt)
		frame3.add(box)
		
		hpaned.pack2(sw, resize=True, shrink=False)
		frame2.add(hpaned)
		self.vbox.pack_start(frame, False, False, 0)
		self.vbox.pack_start(frame2, True, True, 0)
		self.vbox.pack_start(frame3, False, False, 0)
		self.vbox.show_all()


	def sendRx(self, widget, data):
		buf = self.TVRq.get_buffer()
		start, end = buf.get_bounds()
		if core.iswsdlhelper():
			wsdl = core.iswsdlhelper()
			xml = wsdl.sendRaw(self.opName, buf.get_text(start, end))
			buf = self.TVRp.get_buffer()
			buf.set_text(str(xml))

	def changeOp(self, entry):
		if entry.get_text() != '':
			if self.opName != entry.get_text():
				self.opName = entry.get_text()
				if core.iswsdlhelper():
					wsdl = core.iswsdlhelper()
					req, res = wsdl.getRqRx(self.opName)
					if req and res:
						buf = self.TVRq.get_buffer()
						buf.set_text(str(req))
						buf = self.TVRp.get_buffer()
						buf.set_text(str(res))
					else:
						if not req:
							buf = self.TVRq.get_buffer()
							buf.set_text('ERROR CREATING REQUEST')
						if not res:
							buf = self.TVRp.get_buffer()
							buf.set_text('ERROR RECEIVING RESPONSE')

	def refresh(self, widget):
		print 'refresh ' + self.oCombobox
		print 'destroy ' + self.oCombobox
		ops = core.iswsdlhelper().getMethods()
		self.oCombobox = gtk.combo_box_new_text()
		self.oCombobox.append_text('')
		for op in ops:
			self.oCombobox.append_text(op)
			self.oCombobox.connect('changed', self.changeOp)
		self.oCombobox.connect('popdown', self.refresh)
		
	def comment(self, widget):
		buf = self.TVRq.get_buffer()
		if buf.get_selection_bounds() != ():
			start, end = buf.get_selection_bounds()
			markBnd = buf.create_mark('init', start, True)
			buf.insert(end, '-->')
			buf.insert(buf.get_iter_at_mark(markBnd), '<!--')
		self.TVRq.set_buffer(buf)
			

	def addCDATA(self, widget):
		#pos = self.TVRq.get_iter_location()
		#iter = self.TVRq.get_iter_at_location(pos)
		buf = self.TVRq.get_buffer()
		buf.insert_at_cursor('<![CDATA[  ]]>')
		self.TVRq.set_buffer(buf)
		#buf.insert(iter, '<![CDATA[  ]]> ')

	def getWidget(self):
		return self.vbox


