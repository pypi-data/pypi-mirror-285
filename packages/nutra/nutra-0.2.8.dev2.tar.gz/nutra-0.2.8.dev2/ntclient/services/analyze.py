# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 23:57:03 2018

@author: shane
"""

import csv
from collections import OrderedDict
from typing import Mapping, Sequence

from tabulate import tabulate

from ntclient import (
    BUFFER_WD,
    NUTR_ID_CARBS,
    NUTR_ID_FAT_TOT,
    NUTR_ID_FIBER,
    NUTR_ID_KCAL,
    NUTR_ID_PROTEIN,
)
from ntclient.core.nutprogbar import (
    nutrient_progress_bars,
    print_header,
    print_macro_bar,
    print_nutrient_bar,
)
from ntclient.persistence.sql.usda.funcs import (
    sql_analyze_foods,
    sql_food_details,
    sql_nutrients_overview,
    sql_servings,
)
from ntclient.utils import CLI_CONFIG


##############################################################################
# Foods
##############################################################################
def foods_analyze(food_ids: set, grams: float = 100) -> tuple:
    """
    Analyze a list of food_ids against stock RDA values
    (NOTE: only supports a single food for now... add compare foods support later)
    TODO: support flag -t (tabular/non-visual output)
    TODO: support flag -s (scale to 2000 kcal)
    """

    ##########################################################################
    # Get analysis
    ##########################################################################
    raw_analyses = sql_analyze_foods(food_ids)
    analyses = {}
    for analysis in raw_analyses:
        food_id = int(analysis[0])
        anl = (int(analysis[1]), float(round(analysis[2] * grams / 100, 2)))
        # Add values to list
        if food_id not in analyses:
            analyses[food_id] = [anl]
        else:
            analyses[food_id].append(anl)

    serving = sql_servings(food_ids)
    food_des_rows = sql_food_details(food_ids)
    food_des = {x[0]: x for x in food_des_rows}
    nutrients = sql_nutrients_overview()
    rdas = {x[0]: x[1] for x in nutrients.values()}

    ##########################################################################
    # Food-by-food analysis (w/ servings)
    ##########################################################################
    servings_rows = []
    nutrients_rows = []
    for food_id, nut_val_tuples in analyses.items():
        # Print food name
        food_name = food_des[food_id][2]
        if len(food_name) > 45:
            food_name = food_name[:45] + "..."
        print(
            "\n============================================================\n"
            + "==> {0} ({1})\n".format(food_name, food_id)
            + "============================================================\n"
        )

        ######################################################################
        # Serving table
        ######################################################################
        print_header("SERVINGS")
        headers = ["msre_id", "msre_desc", "grams"]
        serving_rows = [(x[1], x[2], x[3]) for x in serving if x[0] == food_id]
        # Print table
        servings_table = tabulate(serving_rows, headers=headers, tablefmt="presto")
        print(servings_table)
        servings_rows.append(serving_rows)

        # Show refuse (aka waste) if available
        refuse = next(
            ((x[7], x[8]) for x in food_des.values() if x[0] == food_id and x[7]), None
        )
        if refuse:
            print_header("REFUSE")
            print(refuse[0])
            print("    ({0}%, by mass)".format(refuse[1]))

        ######################################################################
        # Nutrient colored RDA tree-view
        ######################################################################
        print_header("NUTRITION")
        nutrient_rows = []
        # TODO: skip small values (<1% RDA), report as color bar if RDA is available
        for nutrient_id, amount in nut_val_tuples:
            # Skip zero values
            if not amount:
                continue

            # Get name and unit
            nutr_desc = nutrients[nutrient_id][4] or nutrients[nutrient_id][3]
            unit = nutrients[nutrient_id][2]

            # Insert RDA % into row
            if rdas[nutrient_id]:
                rda_perc = float(round(amount / rdas[nutrient_id] * 100, 1))
            else:
                rda_perc = None
            row = [nutrient_id, nutr_desc, rda_perc, round(amount, 2), unit]

            # Add to list
            nutrient_rows.append(row)

        # Add to list of lists
        nutrients_rows.append(nutrient_rows)

        # Print view
        # TODO: either make this function singular, or handle plural logic here
        _food_id = list(food_ids)[0]
        nutrient_progress_bars(
            {_food_id: grams},
            [(_food_id, x[0], x[1]) for x in analyses[_food_id]],
            nutrients,
        )
        # TODO: make this into the `-t` or `--tabular` branch of the function
        # headers = ["id", "nutrient", "rda %", "amount", "units"]
        # table = tabulate(nutrient_rows, headers=headers, tablefmt="presto")
        # print(table)

    return 0, nutrients_rows, servings_rows


##############################################################################
# Day
##############################################################################
def day_analyze(day_csv_paths: Sequence[str], rda_csv_path: str = str()) -> tuple:
    """Analyze a day optionally with custom RDAs, examples:

       ./nutra day tests/resources/day/human-test.csv

       nutra day ~/.nutra/rocky.csv -r ~/.nutra/dog-rdas-18lbs.csv

    TODO: Should be a subset of foods_analyze (encapsulate/abstract/reuse code)
    """

    # Get user RDAs from CSV file, if supplied
    if rda_csv_path:
        with open(rda_csv_path, encoding="utf-8") as file_path:
            rda_csv_input = csv.DictReader(
                row for row in file_path if not row.startswith("#")
            )
            rdas = list(rda_csv_input)
    else:
        rdas = []

    # Get daily logs from CSV file
    logs = []
    food_ids = set()
    for day_csv_path in day_csv_paths:
        with open(day_csv_path, encoding="utf-8") as file_path:
            rows = [row for row in file_path if not row.startswith("#")]
            day_csv_input = csv.DictReader(rows)
            log = list(day_csv_input)
        for entry in log:
            if entry["id"]:
                food_ids.add(int(entry["id"]))
        logs.append(log)

    # Inject user RDAs, if supplied (otherwise fall back to defaults)
    nutrients_lists = [list(x) for x in sql_nutrients_overview().values()]
    for rda in rdas:
        nutrient_id = int(rda["id"])
        _rda = float(rda["rda"])
        for _nutrient in nutrients_lists:
            if _nutrient[0] == nutrient_id:
                _nutrient[1] = _rda
                if CLI_CONFIG.debug:
                    substr = "{0} {1}".format(_rda, _nutrient[2]).ljust(12)
                    print("INJECT RDA: {0} -->  {1}".format(substr, _nutrient[4]))
    nutrients = {int(x[0]): tuple(x) for x in nutrients_lists}
    print(nutrients)

    # Analyze foods
    foods_analysis = {}
    for food in sql_analyze_foods(food_ids):
        food_id = food[0]
        anl = food[1], food[2]
        if food_id not in foods_analysis:
            foods_analysis[food_id] = [anl]
        else:
            foods_analysis[food_id].append(anl)

    # Compute totals
    nutrients_totals = []
    for log in logs:
        nutrient_totals = OrderedDict()  # NOTE: dict()/{} is NOT ORDERED before 3.6/3.7
        for entry in log:
            if entry["id"]:
                food_id = int(entry["id"])
                grams = float(entry["grams"])
                for _nutrient2 in foods_analysis[food_id]:
                    nutr_id = _nutrient2[0]
                    nutr_per_100g = _nutrient2[1]
                    nutr_val = grams / 100 * nutr_per_100g
                    if nutr_id not in nutrient_totals:
                        nutrient_totals[nutr_id] = nutr_val
                    else:
                        nutrient_totals[nutr_id] += nutr_val
        nutrients_totals.append(nutrient_totals)

    # Print results
    buffer = BUFFER_WD - 4 if BUFFER_WD > 4 else BUFFER_WD
    for analysis in nutrients_totals:
        day_format(analysis, nutrients, buffer=buffer)
    return 0, nutrients_totals


def day_format(
    analysis: Mapping[int, float],
    nutrients: Mapping[int, tuple],
    buffer: int = 0,
) -> None:
    """Formats day analysis for printing to console"""

    # Actual values
    kcals = round(analysis[NUTR_ID_KCAL])
    pro = analysis[NUTR_ID_PROTEIN]
    net_carb = analysis[NUTR_ID_CARBS] - analysis[NUTR_ID_FIBER]
    fat = analysis[NUTR_ID_FAT_TOT]
    kcals_449 = round(4 * pro + 4 * net_carb + 9 * fat)

    # Desired values
    kcals_rda = round(nutrients[NUTR_ID_KCAL][1])
    pro_rda = nutrients[NUTR_ID_PROTEIN][1]
    net_carb_rda = nutrients[NUTR_ID_CARBS][1] - nutrients[NUTR_ID_FIBER][1]
    fat_rda = nutrients[NUTR_ID_FAT_TOT][1]

    # Print calories and macronutrient bars
    print_header("Macro-nutrients")
    kcals_max = max(kcals, kcals_rda)
    rda_perc = round(kcals * 100 / kcals_rda, 1)
    print(
        "Actual:    {0} kcal ({1}% RDA), {2} by 4-4-9".format(
            kcals, rda_perc, kcals_449
        )
    )
    print_macro_bar(fat, net_carb, pro, kcals_max, _buffer=buffer)
    print(
        "\nDesired:   {0} kcal ({1} kcal)".format(
            kcals_rda, "%+d" % (kcals - kcals_rda)
        )
    )
    print_macro_bar(
        fat_rda,
        net_carb_rda,
        pro_rda,
        kcals_max,
        _buffer=buffer,
    )

    # Nutrition detail report
    print_header("Nutrition detail report")
    for nutr_id, nutr_val in analysis.items():
        print_nutrient_bar(nutr_id, nutr_val, nutrients)
    # TODO: actually filter and show the number of filtered fields
    print(
        "work in progress...",
        "some minor fields with negligible data, they are not shown here",
    )
