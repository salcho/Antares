'''
Created on Aug 06, 2013

@author: Santiago Diaz M - salchoman@gmail.com
'''

from lib.pywebfuzz.fuzzdb import attack_payloads
from lib.pywebfuzz.fuzzdb import regex
from core.plugs.IPlugin import IPlugin

class IFuzzdbPlug(IPlugin):
    
    def __init__(self):
        IPlugin.__init__(self)
        self.name = 'fuzzdb plugin interface'
        self.description = 'all fuzzdb plugins must implement this'
        self.regex = regex.errors

class controlCharsPlug(IFuzzdbPlug):
    
    def __init__(self):
        IFuzzdbPlug.__init__(self)
        self.name = "Control characters"
        self.description = "NULL string control characters payload"
        self.payloads = attack_payloads.control_chars.null_fuzz
        
class ldapPlug(IFuzzdbPlug):
    
    def __init__(self):
        IFuzzdbPlug.__init__(self)
        self.name = "LDAP injector"
        self.description = "Generic LDAP payloads"
        self.payloads = attack_payloads.ldap.ldap_injection
    
class OsCmdPlug(IFuzzdbPlug):
    
    def __init__(self):
        IFuzzdbPlug.__init__(self)
        self.name = "OS command injector"
        self.description = "Unix/Windows command payloads"
        # TODO: Select payloads according to the info in the config widget! (util?)
        self.payloads = attack_payloads.os_cmd_execution.command_execution_unix
        self.payloads += attack_payloads.os_cmd_execution.commands_unix
        self.payloads += attack_payloads.os_cmd_execution.commands_windows
        self.payloads += attack_payloads.os_cmd_execution.source_disc_cmd_exec_traversal
    
class xssPlug(IFuzzdbPlug):
    
    def __init__(self):
        IFuzzdbPlug.__init__(self)
        self.name = "XSS injector"
        self.description = "For content shown at the front-end"
        self.payloads = attack_payloads.xss.xss_rsnake
        self.payloads += attack_payloads.xss.xss_uri
    
class pathTraversalPlug(IFuzzdbPlug):
    
    def __init__(self):
        IFuzzdbPlug.__init__(self)
        self.name = "Path traversal injector"
        self.description = "For file-based input"
        self.payloads = attack_payloads.path_traversal.path_traversal_windows
        self.payloads += attack_payloads.path_traversal.traversals_8_deep_exotic_encoding
    
class sqlPlug(IFuzzdbPlug):
    
    def __init__(self):
        IFuzzdbPlug.__init__(self)
        self.name = "SQL injector"
        self.description = "Various SQL vuln detection payloads"
        self.payloads = attack_payloads.sql_injection.detect.GenericBlind
        self.payloads += attack_payloads.sql_injection.detect.xplatform
        self.payloads += attack_payloads.sql_injection.detect.MSSQL
        self.payloads += attack_payloads.sql_injection.detect.MSSQL_blind
        self.payloads += attack_payloads.sql_injection.detect.MySQL
        self.payloads += attack_payloads.sql_injection.detect.MySQL_MSSQL
        self.payloads += attack_payloads.sql_injection.detect.oracle
    
class xmlPlug(IFuzzdbPlug):
    
    def __init__(self):
        IFuzzdbPlug.__init__(self)
        self.name = "XML injector"
        self.description = "Generic XML injection payload"
        self.payloads = attack_payloads.xml.xml_attacks
    
class xpathPlug(IFuzzdbPlug):
    
    def __init__(self):
        IFuzzdbPlug.__init__(self)
        self.name = "XPath injector"
        self.description = "Generic XPath injection payload"
        self.payloads = attack_payloads.xpath.xpath_injection