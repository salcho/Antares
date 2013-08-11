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
        self.results_vbox = None
        self.tree_model = gtk.TreeStore(bool, str, str)
        self.tmsort = gtk.TreeModelSort(self.tree_model)
        self.tree_view = gtk.TreeView(self.tmsort)
        self.selected = []
    
    def start(self):
        self.results_vbox = gtk.VBox(True, 0)
        from core.fwCore import core
        wsdl = core.iswsdlhelper()
        if wsdl:
            for op in wsdl.getMethods():
                piter = self.tree_model.append(None, [ False, op, None])
                elem = None
                for x in wsdl.getParams(op):
                        self.tree_model.append(piter, [False, None, x])
                tvcolumns={}
                cells={}
                i=0
                for col in ('Selected','Methods', 'Arguments'):                
                    tvcolumns[col] = gtk.TreeViewColumn(col)
                    self.tree_view.append_column(tvcolumns[col])
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
                        cells[col].connect('toggled', self.opSelected, self.tree_model)
                    self.tree_view.set_search_column(i)
                    tvcolumns[col].set_sort_column_id(i)
                    i+=1
            self.tree_view.show()
            scrolled_window = gtk.ScrolledWindow()
            scrolled_window.add_with_viewport(self.tree_view)
            scrolled_window.set_size_request(300,200)
            scrolled_window.show()
        hbox = gtk.HBox(True, 0)
        btn = gtk.Button()
        self.results_vbox.pack_start(scrolled_window)
        self.results_vbox.show_all()
        
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
        return self.results_vbox
