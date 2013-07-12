'''
Created on Feb 25, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

import gtk
import types
from ui.IWidget import IWidget
from suds.xsd.sxbasic import *

class bfWidget(IWidget):
    def __init__(self):
        self.vbox = None
        self.treestore = None
        self.treeview = None
        self.selected = []
    
    def start(self):
        self.vbox = gtk.VBox(True, 0)
        from core.fwCore import core
        wsdl = core.iswsdlhelper()
        if wsdl:
            self.treestore = gtk.TreeStore(bool, str, str)
            for op in wsdl.getMethods():
                piter = self.treestore.append(None, [ False, op, None])
                #for i in wsdl.getParams(op):
                elem = None
                #params = wsdl.get
                for x in wsdl.getParams(op):
                        self.treestore.append(piter, [False, None, x])
                tmsort = gtk.TreeModelSort(self.treestore)
                self.treeview = gtk.TreeView(tmsort)
                tvcolumns={}
                cells={}
                i=0
                for col in ('Selected','Methods', 'Arguments'):                
                    tvcolumns[col] = gtk.TreeViewColumn(col)
                    self.treeview.append_column(tvcolumns[col])
                    if i == 1 or i == 2:
                        cells[col]=gtk.CellRendererText()
                    else:
                        cells[col] = gtk.CellRendererToggle()
                    tvcolumns[col].pack_start(cells[col], True)
                    if i == 1 or i == 2:
                        tvcolumns[col].add_attribute(cells[col], 'text', i)
                    else:
                        tvcolumns[col].add_attribute(cells[col], 'active', i)
                    if i == 0:
                        cells[col].connect('toggled', self.opSelected, self.treestore)
                    self.treeview.set_search_column(i)
                    tvcolumns[col].set_sort_column_id(i)
                    i+=1
            self.treeview.show()
            scrolled_window = gtk.ScrolledWindow()
            scrolled_window.add_with_viewport(self.treeview)
            scrolled_window.set_size_request(300,200)
            scrolled_window.show()
        hbox = gtk.HBox(True, 0)
        btn = gtk.Button()
        self.vbox.pack_start(scrolled_window)
        self.vbox.show_all()
        
    def opSelected(self, widget, path, model):
        meth = model[path][1]
        args = model[path][2]
        if meth:
            if [meth, 0] in self.selected:
                self.selected.remove([meth, 0])
            else:
                self.selected.append([meth, 0])
        if args:
            if [args, 1] in self.selected:
                self.selected.remove([args, 1])
            else:
                self.selected.append([args, 1])
        model[path][0] = not model[path][0]
        
    def getWidget(self):
        return self.vbox