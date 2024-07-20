# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 14:15:21 2024

@author: shane
"""
from ntclient.services.bugs import insert as bug_insert
from ntclient.utils import CLI_CONFIG


def handle_runtime_exception(args: list, exception: Exception) -> None:
    """
    Handles exceptions raised during runtime.
    """
    print("ERROR: Exception: %s" % exception)
    bug_insert(args, exception)
    if CLI_CONFIG.debug:
        raise exception
