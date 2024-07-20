# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 19:43:55 2020

@author: shane

@todo
Think about all the use cases for the "nested" nutrient tree.  Analyzing a recipe,
a food, meal. How to display the data, or filter, reverse search, sort, etc.
"""


# pylint: disable=too-few-public-methods
class Nutrient:
    """Tracks properties of nutrients; used in the tree structure of nutrient groups"""

    def __init__(self, nut_id: int, name: str, hidden: bool = False):
        self.nut_id = nut_id
        self.name = name
        self.hidden = hidden
        self.rounded_rda = 0  # TODO: round day/recipe analysis to appropriate digit


nnest = {
    # "basics": ["Protein", "Carbs", "Fats", "Fiber", "Calories"],
    "basics": {
        # 203: {"name": "Protein", "hidden": False},
        203: Nutrient(203, "Protein"),
        205: "Carbs",
        204: "Fats",
        291: "Fiber",
        208: "Calories (kcal)",
    },
    "macro_details": {"Carbs": {}, "Fat": {}},
    "micro_nutrients": {
        "Vitamins": {"Water-Soluble": {}, "Fat-Soluble": {}},
        "Minerals": [],
    },
    "fatty_acids": {},
    "amino_acids": set(),
    "other_components": {},
}
