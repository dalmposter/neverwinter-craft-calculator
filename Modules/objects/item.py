from __future__ import annotations
from abc import ABCMeta, abstractclassmethod, abstractmethod
import csv
import logging
from threading import Lock, Thread
from typing import List, Dict, Tuple

from Modules.constants import ARTISAN_TYPES, FOCUS_MULTIPLIER, PROFESSIONS, Recipe
import Modules.objects.recipe as recipe
from Modules.util import aggregate_tuple_lists, find_mw_object

logger = logging.getLogger(__name__)

class MWObject(metaclass=ABCMeta):
    """A generic Masterwork object.
    
    Could represent a resource, material, or item.
    """
    
    OBJECTS: Dict[str, "MWObject"] = {}
    
    def __init__(self):
        self.name: str = None
        self.price: float = None
    
    @abstractclassmethod
    def load_csv(cls):
        """Load the list of this classes objects from a CSV file."""
        pass
    
    @abstractmethod
    def craft(self, artisan: 'recipe.Artisan' = None, tool: 'recipe.Tool' = None,
              supplement: 'recipe.Supplement' = None, quantity: float = 1,
              high_quality: bool = False) -> 'recipe.MWRecipe':
        """Return a recipe representing the cost to craft this item.
        
        Recursively crafts this items input resources if any are
        crafted materials instead of base resources.
        """
        output = recipe.MWRecipe(self, quantity, artisan, tool, supplement, high_quality)
        return output
    
    @abstractmethod
    def craft_by_stats(self, quantity: float = 1, success_chance: float = 1,
              dab_chance: float = 0, recycle_chance: float = 0,
              auxillary_success_chance: float = None,
              auxillary_dab_chance: float = None, auxillary_recycle_chance:float = None) -> Recipe:
        """Return this items list of input resources.
        
        Recursively crafts this items input resources if any are
        crafted materials instead of base resources.
        """
        pass

class MWItem(MWObject):
    
    OBJECTS: Dict[str, "MWItem"] = {}
    
    def __init__(self, data: List[List[str]]):
        super().__init__()
        # Name is on the first column
        self.name = data[0][1]
        self.quantity = float(data[0][5][:-1])
        self.can_dab_hand: bool = data[0][17] == "Yes"
        self.proficiency: int = int(data[0][7])
        self.focus: int = int(data[0][8])
        self.unlock: str = data[0][18]
        self.profession: str = None
        for profession in PROFESSIONS:
            if profession in self.unlock:
                self.profession = profession
        # Each row contains one entry of the recipe
        self.recipe: Recipe = []
        for row in data:
            quantity = float(row[3][:-1])
            item_name = row[4]
            self.recipe.append([quantity, item_name])
        #self.commission: float = float(data[0][16])
        
        self.optimal_recipes: List[Tuple[recipe.MWRecipe, float]] = None
        self.hq_optimal_recipes: List[Tuple[recipe.MWRecipe, float]] = None
        
        self.lock = Lock()
    
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
                    if not can_dab_hand and current_item != []:
                        # If the item can't be dab handed it is an item and not a material
                        new_item = MWItem(current_item)
                        cls.OBJECTS[new_item.name] = MWItem(current_item)
                    # Collect data for next recipe
                    can_dab_hand = row[17] == "Yes"
                    current_item = [row]
                else:
                    current_item.append(row)
            # Flush the last item
            if can_dab_hand:
                # If the item can't be dab handed it is an item and not a material
                new_item = MWItem(current_item)
                cls.OBJECTS[new_item.name] = MWItem(current_item)
    
    def get_optimal_recipes(self, high_quality: bool) -> List[Tuple[recipe.MWRecipe, float]]:
        """
        Calculate the most cost effective setup for crafting this item.
        
        Returns:
            List[Tuple[MWRecipe, float]]: A list of the top recipes and their overall cost.
        """
        RECIPE_QUANTITY = 10
        """Quantity of recipes to output. Default: Top 10."""
        if high_quality and self.hq_optimal_recipes is not None:
            return self.hq_optimal_recipes[:RECIPE_QUANTITY]
        if not high_quality and self.optimal_recipes is not None:
            return self.optimal_recipes[:RECIPE_QUANTITY]
        else:
            self.get_optimal_recipe(high_quality)
            if high_quality:
                return self.hq_optimal_recipes[:RECIPE_QUANTITY]
            else:
                return self.optimal_recipes[:RECIPE_QUANTITY]
    
    def get_optimal_recipe(self, high_quality: bool) -> recipe.MWRecipe:
        """
        Determine the optimal setup for crafting this item.
        
        Attempt to craft this item with every known combination of artisan, tool and
        supplement. Then rank the results by lowest cost.
        In the process it will also calculate the optimal recipe for all required
        materials, and use the best one in calculating this recipe.
        
        Returns:
            MWRecipe: A recipe representing the setup used and material cost to craft this.
        """
        with self.lock:
            # First check if we already calculated the optimal recipes for this item
            # To prevent massive runtimes we cache the best recipes once calculated.
            if high_quality and self.hq_optimal_recipes is not None:
                return self.hq_optimal_recipes[0][0]
            if not high_quality and self.optimal_recipes is not None:
                return self.optimal_recipes[0][0]
            else:
                print(f"Calculating optimal recipe for {self.name}.")
                # Determine the best artisan, tool and supplement to use
                artisans = recipe.Artisan.OBJECTS.get(ARTISAN_TYPES.get(self.profession))
                tools = list(recipe.Tool.OBJECTS.values())
                supplements = list(recipe.Supplement.OBJECTS.values())
                
                ranking_list: List[Tuple[recipe.MWRecipe, float]] = []
                # Generate a thread for each combination of artisan tool and supplement
                threads: List[Thread] = []
                # Define function for threads to execute
                def add_craft_to_list(artisan, tool, supplement, quantity, hq):
                    """Craft self with the given setup and append to the output list."""
                    new_recipe = self.craft(artisan, tool, supplement, quantity, hq)
                    ranking_list.append([new_recipe, new_recipe.get_cost()])
                for artisan in artisans:
                    for tool in tools:
                        for supplement in supplements:
                            if supplement.name == self.name:
                                # Don't allow use of this item as a supplement to avoid infinite recursion
                                continue
                            thread = Thread(target=lambda: add_craft_to_list(artisan, tool, supplement, 1, high_quality))
                            thread.start()
                            threads.append(thread)
                
                # Wait for all the threads
                for thread in threads:
                    thread.join()
                
                ranking_list.sort(key=lambda recipe: recipe[1])
                if high_quality:
                    self.hq_optimal_recipes = ranking_list
                    return ranking_list[0][0]
                else:
                    self.optimal_recipes = ranking_list
                    return ranking_list[0][0]
                        
    
    def craft(self, artisan: recipe.Artisan = None, tool: recipe.Tool = None,
              supplement: recipe.Supplement = None,
              quantity: float = 1, high_quality: bool = False) -> recipe.MWRecipe:
        """
        Craft a given quantity of this item using the given artisan, tool and supplement.
        
        If no setup is provided, it will instead return the optimal recipe for this item.
        
        Returns:
            MWRecipe: A recipe representing the setup and cost to craft this item.
        """
        if artisan is None and tool is None and supplement is None:
            optimal_recipe = self.get_optimal_recipe(high_quality)
            return optimal_recipe.multiply(quantity)
        output = super().craft(artisan, tool, supplement, quantity, high_quality)
        
        success_chance = (artisan.proficiency + tool.proficiency + supplement.proficiency)/self.proficiency
        focus_differential = self.focus - artisan.focus - tool.proficiency - supplement.focus
        high_quality_chance = max(
            1 - (FOCUS_MULTIPLIER * focus_differential),
            0.0000001
        )
        recycle_chance = 1 - ((1-artisan.recycle_chance) * (1-supplement.recycle_chance) * (1-tool.recycle_chance))
        dab_hand_chance = 1 - ((1-artisan.dab_hand_chance) * (1-supplement.dab_hand_chance) * (1-tool.recycle_chance))
    
        # Calculate expected number of attempts to get a success of any quality
        expected_attempts = 1 / success_chance
        
        if self.can_dab_hand:
            # If the recipe can dab hand divide the expected attempts appropriately
            expected_attempts = expected_attempts / (1+dab_hand_chance)
            
        # Calculate cost multiplier factoring in recycle chance
        quantity_multiplier = (1 + ((expected_attempts - 1) * (1 - recycle_chance)))
        
        if high_quality:
            # If we're crafting +1 version, divide multiplier by +1 chance
            # This must be done after calculating quantity multiplier
            # because you can only recycle actual failures, not normal results
            quantity_multiplier = quantity_multiplier / high_quality_chance
            expected_attempts = expected_attempts / high_quality_chance
        # Adjust multiplier based on quantity to craft and quantity output by the recipe
        quantity_multiplier = quantity_multiplier * quantity / self.quantity

        # Start with the supplements needed for final craft
        output.supplements = [[expected_attempts * quantity / self.quantity, supplement.name]]
        # Go through all items in the recipe and add up their costs
        for recipe_entry in self.recipe:
            recipe_entry_name = recipe_entry[1]
            recipe_entry_quantity = recipe_entry[0]
            this_output = find_mw_object(recipe_entry_name).craft(
                quantity=recipe_entry_quantity * quantity_multiplier,
                high_quality=False
            )
            output.absorb(this_output)
            # Clear the supplement materials. They are summed up fresh at the end
            output.supplement_materials = []

        # Go through all supplements and sum up their costs
        for supplement_entry in output.supplements:
            supplement_entry_name = supplement_entry[1]
            supplement_entry_quantity = supplement_entry[0]
            supplement_object = recipe.Supplement.OBJECTS.get(supplement_entry_name)
            overall_quantity = supplement_entry_quantity * quantity
            this_output: recipe.MWRecipe = supplement_object.craft(
                quantity=overall_quantity
            )
            #print(f"[{rand}]: Crafted {supplement_entry_quantity}*{quantity} {supplement_entry_name}: {this_output.materials}")
            #print(f"[{rand}]: Current supplement_materials: {output.supplement_materials}")
            aggregate_tuple_lists(output.supplement_materials, this_output.materials)
        
        #print(f"[{rand}]: Summed supplements for {quantity} quantity {output.supplements}: {output.supplement_materials}")
        
        # Add meta-data to recipe
        output.attempts = expected_attempts
        output.failures = expected_attempts * (1-success_chance)
        output.normal_results = expected_attempts * (success_chance * (1-high_quality_chance)) * (1+dab_hand_chance)
        output.high_quality_results = expected_attempts * (success_chance * high_quality_chance) * (1+dab_hand_chance)
        
        return output
    
    def craft_by_stats(self, quantity: float = 1, success_chance: float = 1,
              dab_chance: float = 0, recycle_chance: float = 0,
              auxillary_success_chance: float = None,
              auxillary_dab_chance: float = None, auxillary_recycle_chance:float = None) -> Recipe:
        """
        Deprecated function.
        
        Returns the result of crafting this item with fixed stats.
        
        Returns:
            Recipe: The list of materials used to craft this item.
        """
        # Auxillary chances used to craft previous items in the chain
        # Default to given chances for this craft if not present
        if auxillary_success_chance is None:
            auxillary_success_chance = success_chance
        if auxillary_dab_chance is None:
            auxillary_dab_chance = dab_chance
        if auxillary_recycle_chance is None:
            auxillary_recycle_chance = recycle_chance
        
        if self.can_dab_hand:
            quantity_multiplier = (1 + (((1/auxillary_success_chance) - 1) * (1-auxillary_recycle_chance)))
            quantity_multiplier = quantity_multiplier / (1 + auxillary_dab_chance)
        else:
            quantity_multiplier = (1 + (((1/success_chance) - 1) * (1-recycle_chance)))
        quantity_multiplier = quantity_multiplier * quantity / self.quantity
        #logger.debug(f"Crafting {self.name}")
        output = []
        # Cycle through entries in our recipe and sum up their costs recursively
        for recipe_entry in self.recipe:
            recipe_entry_name = recipe_entry[1]
            recipe_entry_quantity = recipe_entry[0]
            this_output = find_mw_object(recipe_entry_name).craft_by_stats(
                quantity=recipe_entry_quantity * quantity_multiplier,
                success_chance=success_chance,
                dab_chance=dab_chance,
                recycle_chance=recycle_chance,
                auxillary_success_chance=auxillary_success_chance,
                auxillary_dab_chance=auxillary_dab_chance,
                auxillary_recycle_chance=auxillary_recycle_chance
            )
            aggregate_tuple_lists(output, this_output)
                
        return output

class MWResource(MWObject):
    """A raw material used in crafting."""
    
    OBJECTS: Dict[str, "MWResource"] = {}
    
    def __init__(self, data: List[str] = None, name = None):
        super().__init__()
        self.price = 0
        if name is not None:
            self.name = name
        if data is not None:
            self.name = data[1]
            self.price = float(data[4].replace(",", "")) if data[4] != "" else 0
    
    @classmethod
    def load_csv(cls, file_loc):
        cls.OBJECTS = {}
        with open(file_loc) as f:
            csvreader = csv.reader(f)
            header = next(csvreader)
            for row in csvreader:
                source = row[6]
                if any(prof in source for prof in PROFESSIONS):
                    # If the item comes from any profession it is actually a material.
                    # Do not add it to the resources list.
                    continue
                new_resource = MWResource(row)
                cls.OBJECTS[new_resource.name] = new_resource
                
    def craft(self, artisan: 'recipe.Artisan' = None, tool: 'recipe.Tool' = None,
              supplement: 'recipe.Supplement' = None,
              quantity: float = 1, high_quality: bool = False) -> 'recipe.MWRecipe':
        output = super().craft(artisan, tool, supplement, quantity, high_quality)
        # Resources are only gathered. They cannot be failed, dabbed, or recycled.
        output.materials = [[quantity, self.name]]
        return output
    
    def craft_by_stats(self, quantity: float = 1, success_chance: float = 1,
              dab_chance: float = 0, recycle_chance: float = 0,
              auxillary_success_chance: float = None,
              auxillary_dab_chance: float = None, auxillary_recycle_chance:float = None) -> Recipe:
        # Resources are only gathered. They cannot be failed, dabbed, or recycled.
        return [[quantity, self.name]]

class CommissionItem():
    """A crafted item requested by Stryker Bronzepin/"""
    
    OBJECTS: Dict[str, "CommissionItem"] = {}
    
    def __init__(self, data: List[str]):
        from Modules.objects.item import MWObject
        self.name = data[2][4:-1]
        self.commission_value: float = float(data[3])
        self.object: MWObject = find_mw_object(self.name)
    
    @classmethod
    def load_csv(cls, file_loc):
        cls.OBJECTS = {}
        with open(file_loc) as f:
            csvreader = csv.reader(f)
            header = next(csvreader)
            for row in csvreader:
                new_item = CommissionItem(row)
                cls.OBJECTS[new_item.name] = new_item
    
    def calculate_rank(self) -> Tuple['recipe.MWRecipe', float]:
        recipe = self.object.craft()
        commission_per_ad = recipe.get_cost() / self.commission_value
        rank = [recipe, commission_per_ad]
        return rank

    def pretty_print(self) -> str:
        out = f"{self.name} ({self.commission_value})"
        return out