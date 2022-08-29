from __future__ import annotations
import csv
from typing import List, Dict

from Modules.objects.item import MWItem

class MWMaterial(MWItem):
    
    OBJECTS: Dict[str, "MWMaterial"] = {}
    
    @classmethod
    def load_csv(cls, file_loc):
        cls.OBJECTS = {}
        with open(file_loc) as f:
            csvreader = csv.reader(f)
            header = next(csvreader)
            current_item: List[List[str]] = []
            can_dab_hand = False
            for row in csvreader:
                if row[2] is not None and row[2] != "":
                    # If the name (col 6) is not empty then this is the start of a recipe
                    # Create object for the previous recipe
                    if can_dab_hand and current_item != []:
                        # If the item can be dab handed it is a material and not an item
                        new_item = MWMaterial(current_item)
                        cls.OBJECTS[new_item.name] = MWMaterial(current_item)
                    # Collect data for next recipe
                    can_dab_hand = row[17] == "Yes"
                    current_item = [row]
                else:
                    current_item.append(row)
            # Flush the last item
            if can_dab_hand:
                # If the item can't be dab handed it is an item and not a material
                new_item = MWMaterial(current_item)
                cls.OBJECTS[new_item.name] = MWMaterial(current_item)