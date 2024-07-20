# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 14:35:43 2022

@author: shane

Wrapper for colorama. Used to default to white text if it wasn't installed,
but it's available on virtually all systems now so why not.
"""
from colorama import Fore, Style
from colorama import init as colorama_init

# Made it this far, so run the init function (which is needed on Windows)
colorama_init()

# Styles
STYLE_BRIGHT = Style.BRIGHT
STYLE_DIM = Style.DIM
STYLE_RESET_ALL = Style.RESET_ALL

# Colors for Progress / RDA bar
COLOR_WARN = Fore.YELLOW
COLOR_CRIT = Style.DIM + Fore.RED
COLOR_OVER = Style.DIM + Fore.MAGENTA
COLOR_DEFAULT = Fore.CYAN

# Used in macro bars
COLOR_YELLOW = Fore.YELLOW
COLOR_BLUE = Fore.BLUE
COLOR_RED = Fore.RED

# Used by `tree.py` utility
COLOR_GREEN = Fore.GREEN
COLOR_CYAN = Fore.CYAN
