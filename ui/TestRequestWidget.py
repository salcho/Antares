'''
Created on Feb 12, 2013

@author: Santiago Diaz
'''

import gtk
from bs4 import BeautifulSoup
from core.fwCore import core
from core.utils.project_manager import project_manager
from ui.IWidget import IWidget
from suds import WebFault

class TestRequestWidget(IWidget):
	'''
	TestRequestWidget used to send test requests to be later compared with injection requests
	IMPORTANT: This widget needs to be started!
	'''

	def __init__(self):
		IWidget.__init__(self)
		self.oCombobox = None
		self.opName = None
		
		self.results_vbox = gtk.VBox(False, 0)
		self.TVRq = None
		self.TVRp = None
		self.inProcess = None

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
		self.results_vbox = gtk.VBox(False, 0)
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
		self.TVRp.set_editable(True)
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
		self.inProcess = gtk.Image()
		self.inProcess.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
		box.add(btnSend)
		box.add(btnCdata)
		box.add(btnCmnt)
		box.add(self.inProcess)
		frame3.add(box)
		
		hpaned.pack2(sw, resize=True, shrink=False)
		frame2.add(hpaned)
		self.results_vbox.pack_start(frame, False, False, 0)
		self.results_vbox.pack_start(frame2, True, True, 0)
		self.results_vbox.pack_start(frame3, False, False, 0)
		self.results_vbox.show_all()


	def sendRx(self, widget, data):
		self.inProcess.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_BUTTON)
		self.inProcess.show()
		buf = self.TVRq.get_buffer()
		start, end = buf.get_bounds()
		wsdl = core.iswsdlhelper()
		if wsdl:
			try:
				xml = wsdl.sendRaw(self.opName, buf.get_text(start, end))
				while gtk.events_pending():
					gtk.main_iteration(False)
	
				buf = self.TVRp.get_buffer()
				buf.set_text(str(xml))
				
				self.inProcess.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
				self.inProcess.show()
			except Exception as e:
				buf = self.TVRp.get_buffer()
				buf.set_text(str(e))

	def changeOp(self, entry):
		if entry.get_text() != '':
			if self.opName != entry.get_text():
				self.opName = entry.get_text()
				self.inProcess.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
				while gtk.events_pending():
					gtk.main_iteration(False)
				self.inProcess.show()
				if core.iswsdlhelper():
					wsdl = core.iswsdlhelper()
					req, res = wsdl.getRqRx(self.opName)
					buf = self.TVRq.get_buffer()
					buf.set_text(str(req)) if req else buf.set_text('ERROR CREATING REQUEST')
					buf = self.TVRp.get_buffer()
					buf.set_text(str(res)) if res else buf.set_text('ERROR CREATING RESPONSE')
					
					if req and res:	
						self.inProcess.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
					else:
						self.inProcess.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_BUTTON)
						
					self.inProcess.show()

	def refresh(self, widget):
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
		return self.results_vbox


