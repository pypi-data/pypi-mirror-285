# -*- coding: utf-8 -*-
"""
Package info, database targets, paging/debug flags, PROJECT_ROOT,
    and other configurations.

Created on Fri Jan 31 16:01:31 2020

@author: shane
"""
import os
import platform
import shutil
import sys

from ntclient.ntsqlite.sql import NT_DB_NAME

# Package info
__title__ = "nutra"
__version__ = "0.2.8.dev2"
__author__ = "Shane Jaroch"
__email__ = "chown_tee@proton.me"
__license__ = "GPL v3"
__copyright__ = "Copyright 2018-2022 Shane Jaroch"
__url__ = "https://github.com/nutratech/cli"

# Sqlite target versions
# TODO: should this be via versions.csv file?  Don't update in two places?
__db_target_nt__ = "0.0.7"
__db_target_usda__ = "0.0.10"
USDA_XZ_SHA256 = "25dba8428ced42d646bec704981d3a95dc7943240254e884aad37d59eee9616a"

# Global variables
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
NUTRA_HOME = os.getenv("NUTRA_HOME", os.path.join(os.path.expanduser("~"), ".nutra"))
USDA_DB_NAME = "usda.sqlite3"
# NOTE: NT_DB_NAME = "nt.sqlite3" is defined in ntclient.ntsqlite.sql

NTSQLITE_BUILDPATH = os.path.join(PROJECT_ROOT, "ntsqlite", "sql", NT_DB_NAME)
NTSQLITE_DESTINATION = os.path.join(NUTRA_HOME, NT_DB_NAME)


def version_check() -> None:
    """Check Python version"""
    # pylint: disable=global-statement
    global PY_SYS_VER, PY_SYS_STR
    PY_SYS_VER = sys.version_info[0:3]
    PY_SYS_STR = ".".join(str(x) for x in PY_SYS_VER)

    if PY_SYS_VER < PY_MIN_VER:
        # TODO: make this testable with: `class CliConfig`?
        raise RuntimeError(
            "ERROR: %s requires Python %s or later to run" % (__title__, PY_MIN_STR),
            "HINT:  You're running Python %s" % PY_SYS_STR,
        )


PY_MIN_VER = (3, 4, 3)
PY_SYS_VER = sys.version_info[0:3]
PY_MIN_STR = ".".join(str(x) for x in PY_MIN_VER)
PY_SYS_STR = ".".join(str(x) for x in PY_SYS_VER)
# Run the check
version_check()

# Console size, don't print more than it
BUFFER_WD = shutil.get_terminal_size()[0]
BUFFER_HT = shutil.get_terminal_size()[1]

DEFAULT_RESULT_LIMIT = BUFFER_HT - 4

DEFAULT_DAY_H_BUFFER = BUFFER_WD - 4 if BUFFER_WD > 12 else 8

# TODO: keep one extra row on winXP / cmd.exe, it cuts off
DECREMENT = 1 if platform.system() == "Windows" else 0
DEFAULT_SORT_H_BUFFER = (
    BUFFER_WD - (38 + DECREMENT) if BUFFER_WD > 50 else (12 - DECREMENT)
)
DEFAULT_SEARCH_H_BUFFER = (
    BUFFER_WD - (50 + DECREMENT) if BUFFER_WD > 70 else (20 - DECREMENT)
)


################################################################################
# Nutrient IDs
################################################################################
NUTR_ID_KCAL = 208

NUTR_ID_PROTEIN = 203

NUTR_ID_CARBS = 205
NUTR_ID_SUGAR = 269
NUTR_ID_FIBER = 291

NUTR_ID_FAT_TOT = 204
NUTR_ID_FAT_SAT = 606
NUTR_ID_FAT_MONO = 645
NUTR_ID_FAT_POLY = 646

NUTR_IDS_FLAVONES = [
    710,
    711,
    712,
    713,
    714,
    715,
    716,
    734,
    735,
    736,
    737,
    738,
    731,
    740,
    741,
    742,
    743,
    745,
    749,
    750,
    751,
    752,
    753,
    755,
    756,
    758,
    759,
    762,
    770,
    773,
    785,
    786,
    788,
    789,
    791,
    792,
    793,
    794,
]

NUTR_IDS_AMINOS = [
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    508,
    509,
    510,
    511,
    512,
    513,
    514,
    515,
    516,
    517,
    518,
    521,
]
