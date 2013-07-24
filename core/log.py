#!/usr/bin/env python

from exceptions import antaresLogException
import logging
import sys
import data


LOGGER = logging.getLogger("antaresLog")
FORMATTER = logging.Formatter("\r [%(asctime)s - %(levelname)s - %(message)s]", "%H:%M:%S")
HANDLERS = []

HANDLERS.append(logging.StreamHandler(sys.stdout))
#open(data.main_path + data.log_dir + data.log_file, 'w').close()
#HANDLERS.append(logging.FileHandler(data.main_path + data.log_dir + data.log_file, mode="w"))

for handler in HANDLERS:
	handler.setFormatter(FORMATTER)
	LOGGER.addHandler(handler)

LOGGER.setLevel(logging.CRITICAL)
