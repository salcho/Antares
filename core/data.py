#!/usr/bin/env python

from core.log import LOGGER
import time

# Misc variables
paths = {}
paths['main_path'] = None
paths['plugins_dir'] = '/core/plugins/'
paths['projects_dir'] = 'projects'
paths['log_dir'] = '/log/'
# TODO: This is only a temp workaround. 
plugins_dir = '/core/plugins/'
projects_dir = 'projects/'
log_dir = '/log/'
log_file = time.strftime("%d-%b-%Y_%H:%M:%S") + ".log"
wsdl_name = 'target.wsdl'
settings_name = 'settings.p'
logger = LOGGER

# WSDL datatypes: http://www.w3.org/TR/xmlschema-2/#built-in-datatypes
DEFAULT_STRING_VALUE = 'antares'
DEFAULT_BOOLEAN_VALUE = 1
DEFAULT_DECIMAL_VALUE = 1.0
DEFAULT_FLOAT_VALUE = '-1.10e'
DEFAULT_DOUBLE_VALUE = '-0'
DEFAULT_DURATION_VALUE = '-P1Y1M1T1H1M'
DEFAULT_DATETIME_VALUE = '1001-10-10+10:01'
DEFAULT_TIME_VALUE = '10:11:10.11'
DEFAULT_DATE_VALUE = '00:00:00'
DEFAULT_GYEARMONTH_VALUE = '1000-10'
DEFAULT_GYEAR_VALUE = '1000'
DEFAULT_GMONTHDAY_VALUE = '10-10'
DEFAULT_GDAY_VALUE = '10'
DEFAULT_GMONTH_VALUE = '1'
DEFAULT_HEXBINARY_VALUE = 'THIS_FIELD_TYPE_IS_HEXBINARY'
DEFAULT_BASE64BINARY_VALUE = 'THIS_FIELD_TYPE_IS_BASE64BINARY'
DEFAULT_ANYURI_VALUE = 'http://anyhost/anyURI'
#DEFAULT_QNAME_VALUE = 1.0 WTF?
#DEFAULT_NOTATION_VALUE = 1.0
DEFAULT_UNKNOWN_VALUE = 'UNKNOWN'
DEFAULT_INTEGER_VALUE = 1
DEFAULT_LONG_VALUE = 1

# Regular expressions to match various stuff
ERROR_GENERIC_REGEXP = (
                          r'<.*faultstring>(.*%s.*)</faultstring.*',
                          r'^[<.*>]*?(.*%s.*)[<.*>]*$'
                          )
EXTRACT_IP_REGEX = r'[0-9]+(?:\.[0-9]+){3}'

# WS specifications dictionary
ws_protocols = [('WS-Addressing','http://schemas.xmlsoap.org/ws/2004/08/addressing'), ('WS-Policy','http://schemas.xmlsoap.org/ws/2004/09/policy'), 
		('WS-MetadataExchange','http://schemas.xmlsoap.org/ws/2004/09/mex'), ('XML Schema','http://www.w3.org/2001/XMLSchema'),
		('WS-Policy','http://schemas.xmlsoap.org/ws/2002/12/policy'), ('WS-Addressing 1.0','http://www.w3.org/2005/08/addressing'),
		('SOAP-1.1','http://schemas.xmlsoap.org/wsdl/soap/'), ('SOAP-1.1','http://schemas.xmlsoap.org/soap/envelope'),
		('SOAP-1.2','http://www.w3.org/2003/05/soap-envelope'), ('SOAP-1.2','http://www.w3.org/2003/05/soap-encoding'), ('SOAP-1.2','http://www.w3.org/2003/05/soap-rpc'),
		('SOAP-1.2','http://schemas.xmlsoap.org/wsdl/soap12'), ('WS-Addresing Metadata','http://www.w3.org/2007/05/addressing/metadata')]
