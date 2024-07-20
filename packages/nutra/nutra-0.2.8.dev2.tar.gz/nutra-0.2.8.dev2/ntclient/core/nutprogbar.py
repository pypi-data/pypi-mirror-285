"""Temporary [wip] module for more visual (& colorful) RDA output"""

from typing import Mapping

from ntclient.utils import CLI_CONFIG


def nutrient_progress_bars(
    _food_amts: Mapping[int, float],
    _food_analyses: list,
    _nutrients: Mapping[int, tuple],
    # grams: float = 100,
    # width: int = 50,
) -> Mapping[int, float]:
    """
    Returns progress bars, colorized, for foods analyses
    @TODO add option to scale up to 2000 kcal (or configured RDA value)
    @TODO consider organizing the numbers into a table, with the colored bar in one slot
    """

    def print_bars() -> int:
        """Print the progress bars, return n_skipped"""
        n_skipped = 0
        for nut in nut_amts.items():
            nutr_id, nutr_val = nut

            # Skip if nutr_val == 0.0
            if not nutr_val:
                n_skipped += 1
                continue

            # Print bars
            print_nutrient_bar(nutr_id, nutr_val, _nutrients)

        return n_skipped

    # Organize data into a dict<food_id, dict<nutr_id, nutr_val>>
    food_analyses_dict = {
        int(x[0]): {int(y[1]): float(y[2]) for y in _food_analyses if y[0] == x[0]}
        # NOTE: each analysis is a list of tuples, i.e. (11233, 203, 2.92)
        for x in _food_analyses
    }

    # Tally the nutrient totals
    nut_amts = {}
    for food_id in _food_amts.keys():
        analysis = food_analyses_dict[food_id]
        for nutrient_id, amt in analysis.items():
            if nutrient_id not in nut_amts:
                nut_amts[int(nutrient_id)] = amt
            else:  # pragma: no cover
                # nut_amts[int(nutrient_id)] += amt
                raise ValueError("Not implemented yet, need to sum up nutrient amounts")

    print_bars()
    return nut_amts


def print_nutrient_bar(
    _n_id: int, _amount: float, _nutrients: Mapping[int, tuple]
) -> tuple:
    """Print a single color-coded nutrient bar"""
    nutrient = _nutrients[_n_id]
    rda = nutrient[1]
    tag = nutrient[3]
    unit = nutrient[2]
    # anti = nutrient[5]
    # hidden = nutrient[...?]

    # TODO: get RDA values from nt DB, tree node nested organization
    if not rda:
        return False, nutrient
    attain = _amount / rda
    perc = round(100 * attain, 1)

    if attain >= CLI_CONFIG.thresh_over:
        color = CLI_CONFIG.color_over
    elif attain <= CLI_CONFIG.thresh_crit:
        color = CLI_CONFIG.color_crit
    elif attain <= CLI_CONFIG.thresh_warn:
        color = CLI_CONFIG.color_warn
    else:
        color = CLI_CONFIG.color_default

    # Print
    detail_amount = "{0}/{1} {2}".format(round(_amount, 1), rda, unit).ljust(18)
    detail_amount = "{0} -- {1}".format(detail_amount, tag)
    left_index = 20
    left_pos = round(left_index * attain) if attain < 1 else left_index
    print(" {0}<".format(color), end="")
    print("=" * left_pos + " " * (left_index - left_pos) + ">", end="")
    print(" {0}%\t[{1}]".format(perc, detail_amount), end="")
    print(CLI_CONFIG.style_reset_all)

    return True, perc


def print_macro_bar(
    _fat: float, _net_carb: float, _pro: float, _kcals_max: float, _buffer: int = 0
) -> None:
    """Print macro-nutrients bar with details."""
    _kcals = _fat * 9 + _net_carb * 4 + _pro * 4

    p_fat = (_fat * 9) / _kcals
    p_car = (_net_carb * 4) / _kcals
    p_pro = (_pro * 4) / _kcals

    # TODO: handle rounding cases, tack on to, or trim off FROM LONGEST ?
    mult = _kcals / _kcals_max
    n_fat = round(p_fat * _buffer * mult)
    n_car = round(p_car * _buffer * mult)
    n_pro = round(p_pro * _buffer * mult)

    # Headers
    f_buf = " " * (n_fat // 2) + "Fat" + " " * (n_fat - n_fat // 2 - 3)
    c_buf = " " * (n_car // 2) + "Carbs" + " " * (n_car - n_car // 2 - 5)
    p_buf = " " * (n_pro // 2) + "Pro" + " " * (n_pro - n_pro // 2 - 3)
    print(
        "  "
        + CLI_CONFIG.color_yellow
        + f_buf
        + CLI_CONFIG.color_blue
        + c_buf
        + CLI_CONFIG.color_red
        + p_buf
        + CLI_CONFIG.style_reset_all
    )

    # Bars
    print(" <", end="")
    print(CLI_CONFIG.color_yellow + "=" * n_fat, end="")
    print(CLI_CONFIG.color_blue + "=" * n_car, end="")
    print(CLI_CONFIG.color_red + "=" * n_pro, end="")
    print(CLI_CONFIG.style_reset_all + ">")

    # Calorie footers
    k_fat = str(round(_fat * 9))
    k_car = str(round(_net_carb * 4))
    k_pro = str(round(_pro * 4))
    f_buf = " " * (n_fat // 2) + k_fat + " " * (n_fat - n_fat // 2 - len(k_fat))
    c_buf = " " * (n_car // 2) + k_car + " " * (n_car - n_car // 2 - len(k_car))
    p_buf = " " * (n_pro // 2) + k_pro + " " * (n_pro - n_pro // 2 - len(k_pro))
    print(
        "  "
        + CLI_CONFIG.color_yellow
        + f_buf
        + CLI_CONFIG.color_blue
        + c_buf
        + CLI_CONFIG.color_red
        + p_buf
        + CLI_CONFIG.style_reset_all
    )


def print_header(_header: str) -> None:
    """Print a colorized header"""
    print(CLI_CONFIG.color_default, end="")
    print("=" * (len(_header) + 2 * 5))
    print("-->  %s  <--" % _header)
    print("=" * (len(_header) + 2 * 5))
    print(CLI_CONFIG.style_reset_all)
