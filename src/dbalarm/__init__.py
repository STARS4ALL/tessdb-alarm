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

import os
import os.path

# Access SQL scripts withing the package
from pkg_resources import resource_filename

#--------------
# local imports
# -------------

from ._version import get_versions

# ----------------
# Module constants
# ----------------

# Database resources
SQL_SCHEMA           = resource_filename(__name__, os.path.join('sql', 'schema.sql'))
SQL_INITIAL_DATA_DIR = resource_filename(__name__, os.path.join('sql', 'initial' ))
SQL_UPDATES_DATA_DIR = resource_filename(__name__, os.path.join('sql', 'updates' ))

__version__ = get_versions()['version']

del get_versions
