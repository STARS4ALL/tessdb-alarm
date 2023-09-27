# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) 2021
#
# See the LICENSE file for details
# see the AUTHORS file for authors
# ----------------------------------------------------------------------

#--------------------
# System wide imports
# -------------------

import sys
import argparse
import os.path
import logging
#import logging.handlers
import traceback
import importlib

# ---------------------
# Thrid-party libraries
# ---------------------

import decouple

# -------------
# Local imports
# -------------

from . import  __version__
from .dbutils import create_or_open_database

# -----------------------
# Module global variables
# -----------------------

log = logging.getLogger()

# -----------------------
# Module global functions
# -----------------------

def configureLogging(options):
	global log
	
	if options.verbose:
		level = logging.DEBUG
	elif options.quiet:
		level = logging.WARN
	else:
		level = logging.INFO
	
	log.setLevel(level)
	# Log formatter
	#fmt = logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] %(message)s')
	fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
	# create console handler and set level
	if options.console:
		ch = logging.StreamHandler()
		ch.setFormatter(fmt)
		ch.setLevel(level)
		log.addHandler(ch)
	# Create a file handler
	if options.log_file:
		#fh = logging.handlers.WatchedFileHandler(options.log_file)
		fh = logging.FileHandler(options.log_file)
		fh.setFormatter(fmt)
		fh.setLevel(level)
		log.addHandler(fh)

def validfile(path):
    if not os.path.isfile(path):
        raise IOError(f"Not valid or existing file: {path}")
    return path

def validdir(path):
    if not os.path.isdir(path):
        raise IOError(f"Not valid or existing directory: {path}")
    return path

def validbool(boolstr):
    result = None
    if boolstr == 'True':
        result = True
    elif boolstr == 'False':
        result = False
    return result

def validdate(datestr):
    date = None
    for fmt in ['%Y-%m','%Y-%m-%d','%Y-%m-%dT%H:%M:%S','%Y-%m-%dT%H:%M:%SZ']:
        try:
            date = datetime.datetime.strptime(datestr, fmt)
        except ValueError:
            pass
    return date

# =================== #
# THE ARGUMENT PARSER #
# =================== #

def createParser():
	# create the top-level parser
	name = os.path.split(os.path.dirname(sys.argv[0]))[-1]
	parser = argparse.ArgumentParser(prog=name, description="TESSDB alarm tool")

	# Global options
	parser.add_argument('--version', action='version', version='{0} {1}'.format(name, __version__))
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
	group.add_argument('-q', '--quiet',   action='store_true', help='Quiet output.')
	parser.add_argument('-c','--console', action='store_true', help='Log to console.')
	parser.add_argument('-l', '--log-file', type=str, default=None, help='Optional log file')
	
	# --------------------------
	# Create first level parsers
	# --------------------------

	subparser = parser.add_subparsers(dest='command')

	parser_detect  = subparser.add_parser('detect', help='summary command')
	parser_detect.add_argument('-f', '--file', type=validfile, required=True, help='Input log file to analyze')
	
	return parser

# ================ #
# MAIN ENTRY POINT #
# ================ #

def main():
	'''
	Utility entry point
	'''
	try:
		options = createParser().parse_args(sys.argv[1:])
		configureLogging(options)
		name = os.path.split(os.path.dirname(sys.argv[0]))[-1]
		log.info(f"============== {name} {__version__} ==============")
		database_url = decouple.config('DATABASE_URL')
		connection = create_or_open_database(database_url)
		package = f"{name}"
		command  = f"{options.command}"
		subcommand = "run"
		try: 
			command = importlib.import_module(command, package=package)
		except ModuleNotFoundError:	# when debugging module in git source tree ...
			command  = f".{options.command}"
			command = importlib.import_module(command, package=package)
		getattr(command, subcommand)(connection, options)
	except KeyboardInterrupt as e:
		log.critical("[%s] Interrupted by user ", __name__)
	except Exception as e:
		log.critical("[%s] Fatal error => %s", __name__, str(e) )
		traceback.print_exc()
	finally:
		pass

main()
