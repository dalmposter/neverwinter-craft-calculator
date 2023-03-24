
import logging
import os
from typing import List, Tuple

import Modules.objects.item as item

logger = logging.getLogger(__name__)

def find_mw_object(name: str, assume_resource: bool = True) -> "item.MWObject":
    """
    Find a MW item by name.
    
    Searches the following lists in order:
        MW Items (gear etc)
        MW Materials (crafted materials)
        MW Resources (raw materials)
    If no corresponding item is found it is assumed to be a resource with 0 value.
    
    Returns:
        MWObject: The fetched MW object.
    """
    from Modules.objects.material import MWMaterial
    from Modules.objects.item import MWItem, MWResource

    if name[-3:] == " +1":
        name = name[:-3]
    if name in MWItem.OBJECTS:
        return MWItem.OBJECTS.get(name)
    if name in MWMaterial.OBJECTS:
        return MWMaterial.OBJECTS.get(name)
    if name in MWResource.OBJECTS:
        return MWResource.OBJECTS.get(name)
    # If it's not found, treat it as a resource and assume it's value is 0
    if assume_resource: return MWResource(name=name)
    
    return None

def aggregate_tuple_lists(target: List[Tuple], source: List[Tuple]):
    """
    Combine two lists of Tuple[float, str] by adding the number for matching strings.
    """
    for source_entry in source:
                matches = list(filter(lambda output_entry: output_entry[1] == source_entry[1], target))
                if len(matches) > 0:
                    matches[0][0] += source_entry[0]
                else:
                    target.append(source_entry)

def load_all_files():
    """
    Loads all the data files containing resources, recipes, artisans etc.
    """
    from Modules.objects.recipe import Artisan, Tool, Supplement
    from Modules.objects.item import MWItem, MWResource
    from Modules.objects.material import MWMaterial
    from Modules.objects.weapon import MWWeapon
    
    cwd = os.path.dirname(os.path.dirname(__file__))
    
    # Load resources
    resource_loc = f"{cwd}/Input/Resources.csv"
    logger.info(f"Loading resources from {resource_loc}.")
    MWResource.load_csv(resource_loc)

    # Load materials
    material_loc = f"{cwd}/Input/MW Recipes.csv"
    logger.info(f"Loading materials from {material_loc}.")
    MWMaterial.load_csv(material_loc)

    # Load items
    items_loc = f"{cwd}/Input/MW Recipes.csv"
    logger.info(f"Loading materials from {items_loc}.")
    MWItem.load_csv(items_loc)

    # Load weapons
    weapons_loc = f"{cwd}/Input/MW Items.csv"
    logger.info(f"Loading weapons from {weapons_loc}.")
    MWWeapon.load_csv(weapons_loc)

    # Load artisans
    artisan_loc = f"{cwd}/Input/Artisans.csv"
    logger.info(f"Loading artisans from {artisan_loc}.")
    Artisan.load_csv(artisan_loc)

    # Load tools
    tools_loc = f"{cwd}/Input/Tools.csv"
    logger.info(f"Loading tools from {tools_loc}.")
    Tool.load_csv(tools_loc)

    # Load supplements
    supplement_loc = f"{cwd}/Input/Supplements.csv"
    logger.info(f"Loading supplements from {supplement_loc}.")
    Supplement.load_csv(supplement_loc)
    
    # Load commission items
    commission_loc = f"{cwd}/Input/Commissions.csv"
    logger.info(f"Loading commissions from {commission_loc}.")
    item.CommissionItem.load_csv(commission_loc)