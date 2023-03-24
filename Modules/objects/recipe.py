from __future__ import annotations
from abc import abstractstaticmethod
from copy import deepcopy, copy
import csv
from random import random, seed
from typing import List, Dict, Tuple
from Modules.constants import Recipe
import Modules.objects.item as item

from Modules.util import aggregate_tuple_lists, find_mw_object

seed(1)

class Tool():
    
    OBJECTS: Dict[str, "Tool"] = {}
    
    def __init__(self, data: List[str]):
        super().__init__()
        self.profession = data[0]
        self.name = data[1]
        self.proficiency = float(data[2])
        self.focus = float(data[3])
        # Extract the special ability of this tool (if any)
        self.dab_hand_chance = float(data[4]) / 100 if data[5] == "Dab Hand" else 0
        self.recycle_chance = float(data[4]) / 100 if data[5] == "Recycle" else 0
    
    @classmethod
    def load_csv(cls, file_loc):
        cls.OBJECTS = {}
        with open(file_loc) as f:
            csvreader = csv.reader(f)
            header = next(csvreader)
            for row in csvreader:
                new_tool = Tool(row)
                cls.OBJECTS[new_tool.name] = new_tool
    
    def pretty_print(self):
        """
        Print this tools stats.
        
        Returns:
            str: The formatted stats for this tool.
        """
        if self.dab_hand_chance > 0:
            ability_str = f" {self.dab_hand_chance}d"
        elif self.recycle_chance > 0:
            ability_str = f" {self.recycle_chance}r"
        else:
            ability_str = ""
        return f"{self.name} ({int(self.proficiency)}/{int(self.focus)}{ability_str})"

class Supplement():
    
    OBJECTS: Dict[str, "Supplement"] = {}
    
    def __init__(self, data: List[str]):
        super().__init__()
        if data[0][-3:] == " +1":
            self.high_quality = True
        else:
            self.high_quality = False
        self.name = data[0]
        self.proficiency = float(data[1])
        self.focus = float(data[2])
        self.dab_hand_chance = float(data[3]) / 100 if data[4] == "Dab Hand" else 0
        self.recycle_chance = float(data[3]) / 100 if data[4] == "Recycle" else 0
        self.object: item.MWObject = find_mw_object(self.name)
        
        self.supplement_recipe: MWRecipe = None

    @classmethod
    def load_csv(cls, file_loc):
        cls.OBJECTS = {}
        with open(file_loc) as f:
            csvreader = csv.reader(f)
            header = next(csvreader)
            for row in csvreader:
                new_supplement = Supplement(row)
                cls.OBJECTS[new_supplement.name] = new_supplement
    
    def pretty_print(self) -> str:
        """
        Print this supplements stats.
        
        Returns:
            str: The formatted stats of this supplement.
        """
        if self.dab_hand_chance > 0:
            supplement_ability_str = f" {self.dab_hand_chance}d"
        elif self.recycle_chance > 0:
            supplement_ability_str = f" {self.recycle_chance}r"
        else:
            supplement_ability_str = ""
        out = f"{self.name} ({int(self.proficiency)}/{int(self.focus)}{supplement_ability_str})"
        if self.high_quality:
            out = out + " +1"
        return out

    def craft(self, quantity: float = 1) -> MWRecipe:
        """
        Calculate the resource costs for crafting this supplement.
        
        Hard coded to use Beatrice (best +1 recycle crafter), Gond Hammer, and Wintergreen
        Tea +1. Intentionally never using any MW supplements to prevent recursion in
        calculations. This is the best setup for crafting supplements without using a MW
        supplement to do it.
        
        Returns:
            MWRecipe: A recipe representing the costs to craft this supplement.
        """
        if self.supplement_recipe is None:
            self.supplement_recipe = self.object.craft(
                    next(x for x in Artisan.OBJECTS.get("Alchemist") if x.name == "Beatrice"),
                    Tool.OBJECTS.get("Forgehammer of Gond"),
                    Supplement.OBJECTS.get("Wintergreen Tea +1"),
                    1, self.high_quality
            )
        rand = random()
        #print(f"[{rand}]: crafting {quantity} of {self.name}. Current recipe {self.supplement_recipe.materials}")
        out = self.supplement_recipe.multiply(quantity/self.supplement_recipe.quantity)
        #print(f"[{rand}]: crafting {quantity} of {self.name}. New recipe {out.materials}")
        return out

    def craft_by_stats(self, quantity: float = 1, success_chance: float = 1,
            dab_chance: float = 0, recycle_chance: float = 0,
            auxillary_success_chance: float = None, auxillary_dab_chance: float = None,
            auxillary_recycle_chance:float = None) -> Recipe:
        """
        Deprecated function.
        
        Returns the result of crafting this supplement with fixed stats.
        
        Returns:
            Recipe: The list of materials used to craft this supplement.
        """
        return self.object.craft_by_stats(
            quantity, success_chance,
            dab_chance, recycle_chance,
            auxillary_success_chance,
            auxillary_dab_chance,
            auxillary_recycle_chance
        )

class Artisan():
    
    OBJECTS: Dict[str, List["Artisan"]] =  {
        "Adventurer": [],
        "Alchemist": [],
        "Armorer": [],
        "Artificer": [],
        "Blacksmith": [],
        "Jeweler": [],
        "Leatherworker": [],
        "Tailor": []
    }
    
    def __init__(self, data: List[str]):
        super().__init__()
        self.profession = data[0]
        self.name = data[1]
        self.rarity = data[2]
        self.dab_hand_chance = float(data[4]) / 100 if data[3] == "Dab Hand" else 0
        self.recycle_chance = float(data[4]) / 100 if data[3] == "Recycle" else 0
        self.proficiency = float(data[7])
        self.focus = float(data[8])
    
    @classmethod
    def load_csv(cls, file_loc):
        cls.OBJECTS = {}
        with open(file_loc) as f:
            csvreader = csv.reader(f)
            header = next(csvreader)
            for row in csvreader:
                new_artisan = Artisan(row)
                if new_artisan.profession == "Any":
                    for key in cls.OBJECTS.keys():
                        cls.OBJECTS[key].append(new_artisan)
                elif new_artisan.profession in cls.OBJECTS:
                    cls.OBJECTS[new_artisan.profession].append(new_artisan)
                else:
                    cls.OBJECTS[new_artisan.profession] = [new_artisan]
    
    def pretty_print(self) -> str:
        """
        Return the details of this artisan, nicely formatted for printed.
        
        Returns:
            str: The formatted artisan details.
        """
        if self.dab_hand_chance > 0:
            artisan_ability_str = f" {self.dab_hand_chance}d"
        elif self.recycle_chance > 0:
            artisan_ability_str = f" {self.recycle_chance}r"
        else:
            artisan_ability_str = ""
        return f"{self.name} [{self.rarity}] ({int(self.proficiency)}/{int(self.focus)}{artisan_ability_str})"

class MWRecipe:
    """
    Represents a way of crafting a given item, and the associated costs.
    
    Contains the artisan, tool, and supplement used, as well as the material cost to craft
    the given quantity including the material cost for all supplements that would be
    consumed. Also provides stats about the crafting such as how many failures would be
    expected, how many normal or +1 results would be made as a by-product.
    """
    def __init__(self, result: item.MWItem = None, quantity = 1, artisan: Artisan = None,
                 tool: Tool = None, supplement: Supplement = None, high_quality: bool = False):
        self.result: item.MWItem = result
        self.quantity: float = quantity
        self.artisan: Artisan = artisan
        self.tool: Tool = tool
        self.supplement: Supplement = supplement
        self.materials: Recipe = []
        self.supplements: Recipe = []
        self.supplement_materials: Recipe = [] #TODO: Replace this with cost of supplements
        self.high_quality: bool = high_quality
        self.failures: float = None
        self.normal_results: float = None
        self.high_quality_results: float = None
        self.attempts: float = None
    
    def get_cost(self) -> float:
        """
        Calculates the total cost of this recipe.
        
        Returns:
            float: the total cost in AD to craft this recipe.
        """
        cost: float = 0.0
        for entry in self.materials:
            cost += entry[0] * find_mw_object(entry[1]).price
        for supplement_mat_entry in self.supplement_materials:
            cost += supplement_mat_entry[0] * find_mw_object(supplement_mat_entry[1]).price
        return cost
    
    def multiply(self, quantity: float) -> MWRecipe:
        """
        Multiply the contents of a recipe by a number.
        """
        # TODO: Implement custom copy and deepcopy function to replace this
        output: MWRecipe = MWRecipe()
        output.result = self.result
        output.quantity = self.quantity
        output.artisan = self.artisan
        output.tool = self.tool
        output.supplement = self.supplement
        output.materials = deepcopy(self.materials)
        output.supplements = deepcopy(self.supplements)
        output.supplement_materials = deepcopy(self.supplement_materials)
        output.high_quality = self.high_quality
        
        #output = deepcopy(self)
        output.quantity = output.quantity * quantity
        for mat_entry in output.materials:
            mat_entry[0] = mat_entry[0] * quantity
        for sup_entry in output.supplements:
            sup_entry[0] = sup_entry[0] * quantity
        for sup_mat_entry in output.supplement_materials:
            sup_mat_entry[0] = sup_mat_entry[0] * quantity
        return output
    
    def absorb(self, recipe: MWRecipe):
        """Add a recipes entries to this one."""
        aggregate_tuple_lists(self.materials, recipe.materials)
        aggregate_tuple_lists(self.supplements, recipe.supplements)
        aggregate_tuple_lists(self.supplement_materials, recipe.supplement_materials)
    
    @abstractstaticmethod
    def pretty_print_list(input: List[Tuple['MWRecipe', float]]):
        """
        Print details for a list of recipes one after the other.
        
        The first one will have a full pretty print, while the rest will have a more
        concise output.
        """
        input[0][0].pretty_print()
        print("------------------------------------------------------------------------------------------------------------------------------------------------")
        for recipe_rank in input:
            print(f"{'{:,}'.format(round(recipe_rank[1]))} AD ({round(recipe_rank[0].normal_results, 2)} Normal, {round(recipe_rank[0].high_quality_results, 2)} +1): {recipe_rank[0].artisan.pretty_print()} + {recipe_rank[0].supplement.pretty_print()}")
    
    def quick_print(self):
        """
        Print in the console a summary of the artisan and supplement used.
        """
        print(f"\n{self.result.name}: {self.artisan.pretty_print()} + {self.supplement.pretty_print()}")
    
    def pretty_print(self):
        """
        Print in the console a pretty representation of this recipe.
        
        Includes the Aritsan and supplement used (tool is always assumed to be Gond Hammer).
        Also shows the normal:+1 result ratio and the full list of materials consumed and
        their overall cost.
        """
        print(f"\n{self.result.name}{' +1' if self.high_quality else ''}")
        print("------------------------------------------------------------------------------------------------------------------------------------------------")
        print(f"{self.artisan.pretty_print()} + {self.supplement.pretty_print()} : {round(self.attempts, 2)} Attempts")
        print(f"{round(self.failures, 2)} Failures, {round(self.normal_results, 2)} Normal Results, {round(self.high_quality_results, 2)} High Quality Results")
        print("\nMaterials used:")
        cost: float = 0.0
        for entry in self.materials:
            rounded_quantity = round(entry[0], 2)
            print(f"  {rounded_quantity}x {entry[1]}")
            cost += entry[0] * find_mw_object(entry[1]).price
        print(f"Material AD cost: {'{:,}'.format(round(cost))}")
        print(f"\nSupplements used:")
        for supplement_entry in self.supplements:
            rounded_quantity = round(supplement_entry[0], 2)
            print(f"  {rounded_quantity}x {supplement_entry[1]}")
        supplement_cost: float = 0.0
        print(f"Materials consumed by supplements:")
        for supplement_mat_entry in self.supplement_materials:
            rounded_quantity = round(supplement_mat_entry[0], 2)
            print(f"  {rounded_quantity}x {supplement_mat_entry[1]}")
            supplement_cost += supplement_mat_entry[0] * find_mw_object(supplement_mat_entry[1]).price
        print(f"Supplement AD cost: {'{:,}'.format(round(supplement_cost))}")
        print(f"\nTotal AD cost: {'{:,}'.format(round(cost + supplement_cost))}")