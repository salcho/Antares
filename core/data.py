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

# Regular expressions to match error messages
ERROR_GENERIC_REGEXP = (
                          r'<.*faultstring>(.*%s.*)</faultstring.*',
                          r'^[<.*>]*?(.*%s.*)[<.*>]*$'
                          )