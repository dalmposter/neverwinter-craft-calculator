import json
import os
import logging
import traceback
import itertools
from Modules.objects.item import CommissionItem, MWItem, MWResource
from Modules.objects.material import MWMaterial

from Modules.objects.recipe import *
from Modules.util import find_mw_object, load_all_files

cwd = os.path.dirname(__file__)
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)

load_all_files()

# Output materials
materials = list(MWMaterial.OBJECTS.values())
with open("./output/materials.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="|")
    writer.writerow([
        "name",
        "quantity",
        "canDabHand",
        "proficiency",
        "focus",
        "unlock",
        "profession",
        "commission",
        "recipe"
    ])
    for material in materials:
        writer.writerow([
            material.name,
            material.quantity,
            material.can_dab_hand,
            material.proficiency,
            material.focus,
            material.unlock,
            material.profession,
            material.commission,
            f"{material.recipe}"
        ])

# Output artisans
artisans = list(itertools.chain(*Artisan.OBJECTS.values()))
with open("./output/artisans.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="|")
    writer.writerow([
        "profession",
        "name",
        "rarity",
        "dabHandChance",
        "recycleChance",
        "proficiency",
        "focus"
    ])
    for artisan in artisans:
        writer.writerow([
            artisan.profession,
            artisan.name,
            artisan.rarity,
            artisan.dab_hand_chance,
            artisan.recycle_chance,
            artisan.proficiency,
            artisan.focus
        ])

# Output commissions
commissions = list(CommissionItem.OBJECTS.values())
with open("./output/commissions.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="|")
    writer.writerow(["name","commissionValue"])
    for commission in commissions:
        writer.writerow([commission.name, commission.commission_value])

# Output items
items = list(MWItem.OBJECTS.values())
with open("./output/items.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="|")
    writer.writerow([
        "name",
        "quantity",
        "canDabHand",
        "proficiency",
        "focus",
        "unlock",
        "profession",
        "commission",
        "recipe"
    ])
    for item in items:
        writer.writerow([
            item.name,
            item.quantity,
            item.can_dab_hand,
            item.proficiency,
            item.focus,
            item.unlock,
            item.profession,
            item.commission,
            json.dumps(item.recipe)
        ])

# Output resources
resources = list(MWResource.OBJECTS.values())
with open("./output/resources.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="|")
    writer.writerow(["name", "price"])
    for resource in resources:
        writer.writerow([resource.name, resource.price])

# Output supplements
supplements = list(Supplement.OBJECTS.values())
with open("./output/supplements.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="|")
    writer.writerow([
        "name",
        "highQuality",
        "proficiency",
        "focus",
        "dabHandChance",
        "recycleChance"
    ])
    for supplement in supplements:
        writer.writerow([
            supplement.name,
            supplement.high_quality,
            supplement.proficiency,
            supplement.focus,
            supplement.dab_hand_chance,
            supplement.recycle_chance
        ])

# Output tools
tools = list(Tool.OBJECTS.values())
with open("./output/tools.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="|")
    writer.writerow([
        "profession",
        "name",
        "proficiency",
        "focus",
        "dabHandChance",
        "recycleChance"
    ])
    for tool in tools:
        writer.writerow([
            tool.profession,
            tool.name,
            tool.proficiency,
            tool.focus,
            tool.dab_hand_chance,
            tool.recycle_chance
        ])