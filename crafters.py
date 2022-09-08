import os
import logging
from typing import List, Tuple

from Modules.constants import FOCUS_MULTIPLIER
from Modules.objects.recipe import *

cwd = os.path.dirname(__file__)
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)

artisan_loc = f"{cwd}/Input/Artisans.csv"
logger.info(f"Loading artisans from {artisan_loc}.")
Artisan.load_csv(artisan_loc)

# Load tools
tools_loc = f"{cwd}/Input/Tools.csv"
logger.info(f"Loading tools from {tools_loc}.")
Tool.load_csv(tools_loc)

supplement_loc = f"{cwd}/Input/Supplements.csv"
logger.info(f"Loading supplements from {supplement_loc}.")
Supplement.load_csv(supplement_loc)

def calculate_multiplier(artisan: Artisan, tool: Tool, supplement: Supplement,
                                 can_dab_hand: bool = True, high_quality: bool = False):
    PROFICIENCY_REQUIREMENT = 1400
    FOCUS_REQUIREMENT = 1400
    TOOL_PROFICIENCY = tool.proficiency
    TOOL_FOCUS = tool.focus
    success_chance = (artisan.proficiency + TOOL_PROFICIENCY + supplement.proficiency)/PROFICIENCY_REQUIREMENT # Rigged for 1400 max only
    high_quality_chance = max(1 - (FOCUS_MULTIPLIER * (FOCUS_REQUIREMENT - artisan.focus - 600 - supplement.focus)), 0.0001) # rigged for 1400 max only
    recycle_chance = artisan.recycle_chance + supplement.recycle_chance
    dab_hand_chance = artisan.dab_hand_chance + supplement.dab_hand_chance
    if not can_dab_hand:
        dab_hand_chance = 0
    normal_multiplier = (1 + (((1/success_chance - 1) * (1-recycle_chance))))/(1+dab_hand_chance)
    high_quality_multiplier = normal_multiplier / high_quality_chance
    # Take average of both multipliers, with a bias towards the normal quality one
    # This is because it is generaly about 2-2.5x lower than the high quality multiplier
    # (a sort of normalisation)
    aggregate_multiplier = ((normal_multiplier * 3) + high_quality_multiplier) / 4
    if high_quality is None:
        return aggregate_multiplier
    if high_quality:
        return high_quality_multiplier
    else:
        return normal_multiplier

# Take command line input to find best artisan + supplement combo for given profession
config_can_dab = True
config_high_quality = True
while True:
    input_name = input("\nEnter a type of artisan: ").strip()
    if input_name == "q":
        break
    if input_name == "config":
        config_can_dab = input("Enter whether your recipe can dab hand (t/f): ").strip() == "t"
        config_high_quality = input("Enter whether you are aiming for +1 (t/f): ").strip() == "t"
    if input_name in Artisan.OBJECTS:
        artisans = Artisan.OBJECTS.get(input_name)
        tools = list(Tool.OBJECTS.values())
        supplements = list(Supplement.OBJECTS.values())
        for high_quality_setting in [False, True, None]:
            ranking_list_dab_hand: List[Tuple[Artisan, Tool, Supplement, float]] = []
            ranking_list_no_dab_hand: List[Tuple[Artisan, Tool, Supplement, float]] = []
                
            for artisan in artisans:
                tool = Tool.OBJECTS.get("Forgehammer of Gond")
                ranking_list_dab_hand += list(map(
                    lambda supplement:
                        [artisan, tool, supplement, calculate_multiplier(artisan, tool, supplement, True, high_quality_setting)],
                    supplements
                ))
                ranking_list_no_dab_hand += list(map(
                    lambda supplement:
                        [artisan, tool, supplement, calculate_multiplier(artisan, tool, supplement, False, high_quality_setting)],
                    supplements
                ))
            # Sort it in reverse by the cost multiplier (lower is better)
            ranking_list_dab_hand.sort(key=lambda entry: entry[3])
            ranking_list_no_dab_hand.sort(key=lambda entry: entry[3])
            if high_quality_setting is None:
                high_quality_str = "Aggregate quality"
            elif high_quality_setting:
                high_quality_str = "High quality"
            else:
                high_quality_str = "Normal quality"
            print(f"\n {format(f'Can Dab Hand ({high_quality_str}):', '<100')} No Dab Hand ({high_quality_str}):")
            print("".join(["-" * 90]) + "".join([" " * 10]) + "".join(["-" * 90]))
            for i in range(10):
                dab_hand_line = (f" {format(str(round(ranking_list_dab_hand[i][3], 3)), '<5')} - {ranking_list_dab_hand[i][0].pretty_print()} + {ranking_list_dab_hand[i][2].pretty_print()}")
                no_hand_line = (f" {format(str(round(ranking_list_no_dab_hand[i][3], 3)), '<5')} - {ranking_list_no_dab_hand[i][0].pretty_print()} + {ranking_list_no_dab_hand[i][2].pretty_print()}")
                print(f"{format(dab_hand_line, '<100')} {no_hand_line}")
    else: 
        print(f"Unrecognised artisan type {input_name}.")