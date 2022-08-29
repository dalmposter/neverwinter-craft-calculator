from typing import List, Tuple

from Modules.objects.item import CommissionItem
from Modules.objects.recipe import MWRecipe
from Modules.util import load_all_files

load_all_files()

commission_items = list(CommissionItem.OBJECTS.values())

rankings: List[Tuple[CommissionItem, MWRecipe, float]] = []
for commission_item in commission_items:
    rank = commission_item.calculate_rank()
    rankings.append([commission_item, rank[0], rank[1]])

rankings.sort(key=lambda rank: rank[2])

print(rankings[0][1].pretty_print())
for ranking in rankings[:10]:
    print(f"{round(ranking[2], 2)} AD/Credit: {ranking[0].pretty_print()}")