from __future__ import annotations
import csv
import logging
from typing import List, Dict

from Modules.objects.item import MWItem

logger = logging.getLogger(__name__)

class MWWeapon():
    
    OBJECTS: Dict[str, List[MWItem]] = {}
    
    @classmethod
    def load_csv(cls, file_loc):
        cls.OBJECTS = {}
        with open(file_loc) as f:
            csvreader = csv.reader(f)
            header = next(csvreader)
            for row in csvreader:
                mw = row[1]
                name = row[2]
                class_name = row[5]
                slot = row[6]
                if mw == "Chultan MW" or slot not in ["Weapon", "Off-hand"]:
                    # If the item comes from chultan mw, ignore it.
                    continue
                item_object = MWItem.OBJECTS.get(name)
                if class_name in cls.OBJECTS:
                    cls.OBJECTS[class_name].append(item_object)
                else:
                    cls.OBJECTS[class_name] = [item_object]