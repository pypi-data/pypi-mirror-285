# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 23:07:30 2023

@author: shane
"""
import argparse
from enum import Enum

from ntclient import BUFFER_HT, BUFFER_WD
from ntclient.utils import colors


################################################################################
# CLI config class (settings & preferences / defaults)
################################################################################
class RdaColors(Enum):
    """
    Stores values for report colors.
    Default values:
        Acceptable     =Cyan
        Overage        =Magenta (Dim)
        Low            =Yellow
        Critically Low =Red (Dim)
    TODO: make configurable in SQLite or prefs.json
    """

    THRESH_WARN = 0.7
    THRESH_CRIT = 0.4
    THRESH_OVER = 1.9

    COLOR_WARN = colors.COLOR_WARN
    COLOR_CRIT = colors.COLOR_CRIT
    COLOR_OVER = colors.COLOR_OVER

    COLOR_DEFAULT = colors.COLOR_DEFAULT

    STYLE_RESET_ALL = colors.STYLE_RESET_ALL

    # Used in macro bars
    COLOR_YELLOW = colors.COLOR_YELLOW
    COLOR_BLUE = colors.COLOR_BLUE
    COLOR_RED = colors.COLOR_RED


# pylint: disable=too-few-public-methods,too-many-instance-attributes
class _CliConfig:
    """Mutable global store for configuration values"""

    def __init__(self, debug: bool = False, paging: bool = True) -> None:
        self.debug = debug
        self.paging = paging

        # TODO: respect a prefs.json, or similar config file.
        self.thresh_warn = RdaColors.THRESH_WARN.value
        self.thresh_crit = RdaColors.THRESH_CRIT.value
        self.thresh_over = RdaColors.THRESH_OVER.value

        self.color_warn = RdaColors.COLOR_WARN.value
        self.color_crit = RdaColors.COLOR_CRIT.value
        self.color_over = RdaColors.COLOR_OVER.value
        self.color_default = RdaColors.COLOR_DEFAULT.value

        self.style_reset_all = RdaColors.STYLE_RESET_ALL.value

        self.color_yellow = RdaColors.COLOR_YELLOW.value
        self.color_red = RdaColors.COLOR_RED.value
        self.color_blue = RdaColors.COLOR_BLUE.value

    def set_flags(self, args: argparse.Namespace) -> None:
        """
        Sets flags:
          {DEBUG, PAGING}
            from main (after arg parse). Accessible throughout package.
            Must be re-imported globally.
        """

        self.debug = args.debug
        self.paging = not args.no_pager

        if self.debug:
            print("Console size: %sh x %sw" % (BUFFER_HT, BUFFER_WD))


# Create the shared instance object
CLI_CONFIG = _CliConfig()


# TODO:
#  Nested nutrient tree, like:
#       http://www.whfoods.com/genpage.php?tname=nutrientprofile&dbid=132
#  Attempt to record errors in failed try/catch block (bottom of __main__.py)
#  Make use of argcomplete.warn(msg) ?


################################################################################
# Validation Enums
################################################################################
class Gender(Enum):
    """
    A validator and Enum class for gender inputs; used in several calculations.
    @note: floating point -1 to 1, or 0 to 1... for non-binary?
    """

    MALE = "m"
    FEMALE = "f"


class ActivityFactor(Enum):
    """
    Used in BMR calculations.
    Different activity levels: {0.200, 0.375, 0.550, 0.725, 0.900}

    Activity Factor\n
    ------------------------\n
    0.200 = sedentary (little or no exercise)

    0.375 = lightly active
        (light exercise/sports 1-3 days/week, approx. 590 Cal/day)

    0.550 = moderately active
        (moderate exercise/sports 3-5 days/week, approx. 870 Cal/day)

    0.725 = very active
        (hard exercise/sports 6-7 days a week, approx. 1150 Cal/day)

    0.900 = extremely active
        (very hard exercise/sports and physical job, approx. 1580 Cal/day)

    @todo: Verify the accuracy of these "names". Access by index?
    """

    SEDENTARY = {1: 0.2}
    MILDLY_ACTIVE = {2: 0.375}
    ACTIVE = {3: 0.55}
    HIGHLY_ACTIVE = {4: 0.725}
    INTENSELY_ACTIVE = {5: 0.9}


def activity_factor_from_index(activity_factor: int) -> float:
    """
    Gets ActivityFactor Enum by float value if it exists, else raise ValueError.
    Basically just verifies the float is among the allowed values, and re-returns it.
    """
    for enum_entry in ActivityFactor:
        if activity_factor in enum_entry.value:
            return float(enum_entry.value[activity_factor])
    # TODO: custom exception. And handle in main file?
    raise ValueError(  # pragma: no cover
        "No such ActivityFactor for value: %s" % activity_factor
    )
