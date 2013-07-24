#!/usr/bin/env python

from core.log import LOGGER
import time

# misc variables
main_path = None
plugins_dir = '/core/plugins/'
projects_dir = '/projects/'
log_dir = '/log/'
log_file = time.strftime("%d-%b-%Y_%H:%M:%S") + ".log"

wsdl_name = 'target.wsdl'
settings_name = 'settings.p'

logger = LOGGER

# WSDL stuff
