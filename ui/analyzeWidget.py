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
from lib.pygtk_chart import pie_chart
import gtk
import pygtk

class analyzeWidget(IWidget):
    
    def __init__(self):
        IWidget.__init__(self)
        self.hbox = None
        self.info_frame = gtk.Frame("Statistics")
        self.plugin_frame = gtk.Frame("Plugins")
        self.graph_frame = gtk.Frame("Graphs")
    
    def start(self):
        self.hbox = gtk.HBox(True, 0)
        self.hbox.pack_start(self.info_frame, False, True, 0)
        self.hbox.pack_start(self.plugin_frame, False, True, 0)
        self.hbox.pack_start(self.graph_frame, True, True, 0)
        self.hbox.show_all()
        
    def refresh(self):
        self.analyzer = core.isAnalyzer()
        if self.analyzer:
            global_stats = self.analyzer.getStats()
        else:
            global_stats = None
        self._refreshStatistics(global_stats)    
        self._refreshPlugins(global_stats)   
        return True
    
    def _refreshStatistics(self, global_stats):
        for child in self.info_frame.get_children():
            self.info_frame.remove(child)
        self.info_frame.set_label("Statistics")
        regex_stats = self.analyzer.getRegexStats()
        plugins = global_stats[PLUGIN_DICT]
        box = gtk.VBox(False, 0)
        payloads = 'None'
        for plugin, amount in plugins.items():
            table = gtk.Table(6, 2, False)
            table.attach(gtk.Label("Plugin: "), 0, 1, 0, 1)
            table.attach(gtk.Label(plugin.getName()), 1, 2, 0, 1)
            table.attach(gtk.Label("Description: "), 0, 1, 1, 2)
            label = gtk.Label(plugin.getDescription())
            label.set_line_wrap(True)
            table.attach(label, 1, 2, 1, 2)
            table.attach(gtk.Label("Payloads: "), 0, 1, 2, 3)
            amount = str(amount) if amount else 0
            table.attach(gtk.Label(amount), 1, 0, 2, 3)
            table.attach(gtk.Label("Regex hits: "), 0, 1, 3, 4)
            regex_cnt = str(regex_stats[PLUGIN_DICT][plugin]) if regex_stats else 0
            table.attach(gtk.Label(regex_cnt), 1, 2, 3, 4)
            table.attach(gtk.Label("Payload hits: "), 0, 1, 4, 5)
            payloads = '\n'.join(self.analyzer.getPayloadHits(plugin.getName())[:15])
            entry = gtk.Entry(0)
            entry.set_text(payloads)
            table.attach(entry, 1, 2, 4, 5, yoptions=gtk.FILL)
            table.attach(gtk.Label("Parameters: "), 0, 1, 5, 6)
            params = '\n'.join(global_stats[PARAMS_DICT])
            table.attach(gtk.Label(params), 1, 2, 5, 6) 
            box.pack_start(table, False, False, 0)
            box.pack_start(gtk.HSeparator(), False, False, 0)
        
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add_with_viewport(box)
        self.info_frame.add(sw)
        self.info_frame.show_all()
        return True
    
    def _refreshPlugins(self, global_stats):
        for child in self.plugin_frame:
            self.plugin_frame.remove(child)
        self.plugin_frame.set_label("Plugins")
        
        box = gtk.VBox(True, 0)
        #Plugins vs payload
        chart = pie_chart.PieChart()
        chart.title.set_text("Payloads per plugin")
        #chart.background.set_color("#7A8386")
        chart.set_enable_scroll(True)
        for plugin, count in global_stats[PLUGIN_DICT].items():
            area = pie_chart.PieArea(plugin.getName(), count, plugin.getName())
            chart.add_area(area)
        chart = pie_chart.PieChart()
        chart.title.set_text("Payloads per plugin")
        #chart.background.set_color("#7A8386")
        box.pack_start(chart, True, True, 0)
        
        regex_stats = self.analyzer.getRegexStats(None)
        if regex_stats:
            chart = pie_chart.PieChart()
            chart.title.set_text("Errors found")
            for plugin, count in regex_stats[PLUGIN_DICT].items():
                area = pie_chart.PieArea(plugin.getName(), count, plugin.getName())
                chart.add_area(area)
            box.pack_start(chart, True, True, 0)
            
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add_with_viewport(box)
        self.plugin_frame.add(sw)
        self.plugin_frame.show_all()
        return True
        
    def chartRotate(self, range, scroll, value, chart):
        chart.set_rotate(min(value, 360))
        
    def getWidget(self):
        return self.hbox
