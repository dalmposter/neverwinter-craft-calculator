import os
import logging
import traceback
from Modules.objects.recipe import *
from Modules.util import find_mw_object, load_all_files

cwd = os.path.dirname(__file__)
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)

load_all_files()

supplements = list(Supplement.OBJECTS.values())
artisans = Artisan.OBJECTS.get("Leatherworker")

balm = Supplement.OBJECTS.get("Wintergreen Balm +1")
bounty = Supplement.OBJECTS.get("Distilled Philosopher's Bounty")
hammer = Tool.OBJECTS.get("Forgehammer of Gond")

find_mw_object("Living Feywood").craft(
    Artisan.OBJECTS.get("Artificer")[0],
    hammer,
    Supplement.OBJECTS.get("Maker's Bounty")
)

# Take command line input to find base cost of given item
while True:
    try:
        input_name = input("\nEnter an item name: ").strip()
        if input_name == "q":
            print("Exiting.")
            break
        else:
            high_quality = False
            if input_name[-3:] == " +1":
                high_quality = True
                input_name = input_name[:-3]
            # Check for item by name
            item = find_mw_object(input_name, assume_resource=False)
            if item is None:
                logger.error(f"Invalid input {input_name}")
                continue
            else:
                # Found item by name. Print it's recipe
                result: List[MWRecipe] = item.get_optimal_recipes(high_quality=high_quality)
                MWRecipe.pretty_print_list(result)
    except Exception as e:
        print(f"Error: {e}.")
        traceback.format_exc()