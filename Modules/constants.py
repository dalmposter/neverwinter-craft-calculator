from typing import List, Tuple

PROFESSIONS = [
    "Alchemy",
    "Armorsmithing",
    "Artificing",
    "Blacksmithing",
    "Jewelcrafting",
    "Leatherworking",
    "Tailoring"
]

ARTISAN_TYPES = {
    "Alchemy": "Alchemist",
    "Armorsmithing": "Armorer",
    "Artificing": "Artificer",
    "Blacksmithing": "Blacksmith",
    "Jewelcrafting": "Jeweler",
    "Leatherworking": "Leatherworker",
    "Tailoring": "Tailor"
}

FOCUS_MULTIPLIER = 1/430

Recipe = List[Tuple[float, str]]
"""A list of objects and the quantity required."""