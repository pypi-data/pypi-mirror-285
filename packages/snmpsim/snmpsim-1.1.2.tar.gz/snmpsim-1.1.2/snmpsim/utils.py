#
# This file is part of snmpsim software.
#
# Copyright (c) 2010-2019, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/snmpsim/license.html
#
import importlib
import sys

import pysnmp
import pysmi
import pyasn1
import snmpsim

TITLE = """\
SNMP Simulator version {}, written by Ilya Etingof <etingof@gmail.com>
Using foundation libraries: pysmi {}, pysnmp {}, pyasn1 {}.
Python interpreter: {}
Documentation and support at https://www.pysnmp.com/snmpsim
""".format(
    snmpsim.__version__,
    pysmi.__version__,
    pysnmp.__version__,
    pyasn1.__version__,
    sys.version,
)


def try_load(module, package=None):
    """Try to load given module, return `None` on failure"""
    try:
        return importlib.import_module(module, package)

    except ImportError:
        return


def split(val, sep):
    for x in (3, 2, 1):
        if val.find(sep * x) != -1:
            return val.split(sep * x)

    return [val]
