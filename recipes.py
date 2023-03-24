"""
Prototype cost calculating script.

Takes as input the chances involved and calculates the cost to craft.
Superceded by calculator.py
"""

import os
import logging
from Modules.objects.recipe import *
from Modules.constants import Recipe
from Modules.objects.item import MWItem, MWObject, MWResource
from Modules.objects.material import MWMaterial
from Modules.objects.weapon import MWWeapon
from Modules.util import find_mw_object

cwd = os.path.dirname(__file__)
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)

def print_name_with_recipe(name: str, recipe: Recipe):
    print(f"\n {name}")
    print("-------------------------------------")
    cost: float = 0.0
    for entry in recipe:
        rounded_quantity = round(entry[0], 1)
        print(f"  {rounded_quantity}x {entry[1]}")
        cost += entry[0] * find_mw_object(entry[1]).price
    print(f"\nTotal AD cost: {'{:,}'.format(round(cost))}")

# Success and +1 chances.
# Low means not using a related supplement. High means using the best related supplement
SUCCESS_HIGH = 0.8
SUCCESS_LOW = 0.7
HQ_HIGH = 0.4
HQ_LOW = 0.1

# Load resources
resource_loc = f"{cwd}/Input/Resources.csv"
logger.info(f"Loading resources from {resource_loc}.")
MWResource.load_csv(resource_loc)
resource = list(MWResource.OBJECTS.values())[0]

# Load materials
material_loc = f"{cwd}/Input/MW Recipes.csv"
logger.info(f"Loading materials from {material_loc}.")
MWMaterial.load_csv(material_loc)
mat = list(MWMaterial.OBJECTS.values())[0]

# Load items
items_loc = f"{cwd}/Input/MW Recipes.csv"
logger.info(f"Loading materials from {items_loc}.")
MWItem.load_csv(items_loc)
item = list(MWItem.OBJECTS.values())[0]

# Load weapons
weapons_loc = f"{cwd}/Input/MW Items.csv"
logger.info(f"Loading weapons from {weapons_loc}.")
MWWeapon.load_csv(weapons_loc)

# Take command line input to find base cost of given item
success_chance = 0.71
dab_chance = 0
recycle_chance = 0.30
auxillary_success_chance = 0.8
auxillary_dab_chance = 0.25
auxillary_recycle_chance = 0
while True:
    try:
        input_name = input("\nEnter an item name: ").strip()
        if input_name == "q":
            print("Exiting.")
            break
        if input_name == "config":
            # Prompt for input to configure each constant
            success_chance = float(input("Enter the chance to succeed this step: ").strip())
            dab_chance = float(input("Enter the chance to dab hand this step: ").strip())
            recycle_chance = float(input("Enter the chance to recycle this step: ").strip())
            auxillary_success_chance = float(input("Enter the chance to succeed previous steps: ").strip())
            auxillary_dab_chance = float(input("Enter the chance to dab hand previous steps: ").strip())
            auxillary_recycle_chance = float(input("Enter the chance to recycle previous steps: ").strip())
        else:
            # Check for item by name
            item = find_mw_object(input_name, assume_resource=False)
            if item is None:
                # Check for weapons by class
                class_name = input_name
                if class_name == "*":
                    # Sum weapons for all classes
                    weapon_list = [j for sub in MWWeapon.OBJECTS.values() for j in sub]
                else:
                    # Fetch specific classes weapons
                    weapon_list = MWWeapon.OBJECTS.get(class_name)
                if weapon_list is None:
                    logger.error(f"Invalid input {input_name}")
                else:
                    # Print the sum recipe for the main and off-hand for chosen class
                    output = []
                    for weapon in weapon_list:
                        this_recipe = weapon.craft_by_stats(
                            success_chance=success_chance,
                            dab_chance=dab_chance,
                            recycle_chance=recycle_chance,
                            auxillary_success_chance=auxillary_success_chance,
                            auxillary_dab_chance=auxillary_dab_chance,
                            auxillary_recycle_chance=auxillary_recycle_chance
                        )
                        for base_entry in this_recipe:
                            matches = list(filter(lambda output_entry: output_entry[1] == base_entry[1], output))
                            if len(matches) > 0:
                                matches[0][0] += base_entry[0]
                            else:
                                output.append(base_entry)
                    print_name_with_recipe(f"{' + '.join(list(map(lambda weapon: weapon.name, weapon_list)))}", output)
            else:
                # Found item by name. Print it's recipe
                print_name_with_recipe(
                    item.name,
                    item.craft_by_stats(
                        success_chance=success_chance,
                        dab_chance=dab_chance,
                        recycle_chance=recycle_chance,
                        auxillary_success_chance=auxillary_success_chance,
                        auxillary_dab_chance=auxillary_dab_chance,
                        auxillary_recycle_chance=auxillary_recycle_chance
                    )
                )
    except Exception as e:
        print(f"Error: {e}.")