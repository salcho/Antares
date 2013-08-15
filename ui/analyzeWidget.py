'''
Created on Feb 25, 2013

@author: Santiago Diaz - salchoman@gmail.com
'''

from core.fwCore import core
from core.utils.analyzer import HTTP_DICT
from core.utils.analyzer import PARAMS_DICT
from core.utils.analyzer import PLUGIN_DICT
from core.utils.analyzer import RSP_DICT
from core.utils.analyzer import SIZE_DICT
from ui.IWidget import IWidget
import gtk
import pygtk

class analyzeWidget(IWidget):
    
    def __init__(self):
        IWidget.__init__(self)
        self.hbox = None
        self.info_frame = gtk.Frame("Statistics")
        self.plugin_frame = gtk.Frame("Plugins")
        self.graph_frame = gtk.Frame("Graphs")
        self.plugin_tables = []
    
    def start(self):
        self.hbox = gtk.HBox(True, 0)
        self.hbox.pack_start(self.info_frame, False, True, 0)
        self.hbox.pack_start(self.plugin_frame, False, True, 0)
        self.hbox.pack_start(self.graph_frame, True, True, 0)
        self.hbox.show_all()
        
    def refresh(self):
        self.analyzer = core.isAnalyzer()
        
        for child in self.info_frame.get_children():
            self.info_frame.remove(child)
        self.info_frame.set_label("Statistics")
        # Get global statistics
        global_stats = self.analyzer.getStats()
        regex_stats = self.analyzer.getRegexStats()
        plugins = global_stats[PLUGIN_DICT]
        box = gtk.VBox(False, 0)
        for plugin, amount in plugins.items():
            table = gtk.Table(6, 2, True)
            table.attach(gtk.Label("Plugin: "), 0, 1, 0, 1)
            table.attach(gtk.Label(plugin.getName()), 1, 2, 0, 1)
            table.attach(gtk.Label("Payloads: "), 0, 1, 1, 2)
            table.attach(gtk.Label(amount), 1, 2, 1, 2)
            table.attach(gtk.Label("Description: "), 0, 1, 2, 3)
            table.attach(gtk.Label(plugin.getDescription()), 1, 2, 2, 3, xoptions=gtk.SHRINK)
            table.attach(gtk.Label("Regex hits: "), 0, 1, 3, 4)
            regex_cnt = regex_stats[PLUGIN_DICT][plugin] if regex_stats else 0  
            table.attach(gtk.Label(str(regex_cnt)), 1, 2, 3, 4)
            table.attach(gtk.Label("Payload hits: "), 0, 1, 4, 5)
            payloads = '\n'.join(self.analyzer.getPayloadHits(plugin.getName()))
            table.attach(gtk.Label(payloads), 1, 2, 4, 5, xoptions=gtk.SHRINK)
            table.attach(gtk.Label("Parameters: "), 0, 1, 5, 6)
            params = '\n'.join(global_stats[PARAMS_DICT])
            table.attach(gtk.Label(params), 1, 2, 5, 6)
            self.plugin_tables.append(table)
        
        for table in self.plugin_tables:    
            box.pack_start(table, False, True, 0)
            box.pack_start(gtk.HSeparator(), False, True, 0)
        
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add_with_viewport(box)
        self.info_frame.add(sw)
        self.info_frame.show_all()
        return True

    def getWidget(self):
        return self.hbox
