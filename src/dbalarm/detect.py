#--------------------
# System wide imports
# -------------------
import re
import logging

# -----------------------
# Module global variables
# -----------------------

log = logging.getLogger(__name__)
RE = re.compile( r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4} \[dbase#info\] DB Stats Readings \[Total, OK, NOK\] = \(0, 0, 0\)$" )

# ------------------
# Auxiliar functions
# ------------------


# ===================
# Module entry points
# ===================

def run(options):
	log.debug("Executing command %s, subcomand %s with options %s", __name__, run.__name__, options)
	with open(options.file) as fd:
		lines = fd.readlines()
	log.info("Read %d lines", len(lines))
	lines = [line for line in lines if re.match(RE, line)]
	log.warn("Matching %d lines", len(lines))

