# -*- coding: utf-8 -*-
"""
Home to persistence and storage utilities.
Used to have a prefs.json, but was deleted and is planned to be maintained
    in sqlite.

Created on Sat Mar 23 13:09:07 2019

@author: shane
"""
import configparser
import os

from ntclient import NUTRA_HOME

PREFS_FILE = os.path.join(NUTRA_HOME, "prefs.ini")

os.makedirs(NUTRA_HOME, 0o755, exist_ok=True)

if not os.path.isfile(PREFS_FILE):  # pragma: no cover
    print("INFO: Generating prefs.ini file")
    config = configparser.ConfigParser()
    with open(PREFS_FILE, "w", encoding="utf-8") as _prefs_file:
        config.write(_prefs_file)
