# Neverwinter Craft Calculator

Tool for calculating masterwork crafting costs in Neverwinter, the D&D MMO.

The various scripts rely on the Input directory which contain CSV exports from Rainer's masterwork reference spreadsheets which can be found for free in read-only format on his Patreon https://www.patreon.com/RainerNW (Thank you Rainer for your amazing Neverwinter content!). Update the values contained in these CSVs to be consistent with current AH prices on your platform.

The Modules directory contains the main codebase. They contain classes representing everything involved in the crafting process. This is essentially the library for the scripts.

# Main Script
The most interesting script is calculator.py
Run this simply with
```
python calculator.py
```

Once it is running you can enter the name of any item and it will calculate the top 10 artisan/tool/supplement combos and print them to the screen along with their cost and ratio of normal to high quality outputs. Note the input files are currently rigged to only include the Forgehammer of Gond and no other tools. This is because I found the hammer to be the best tool for all recipes and having others in the pool clogged up the output.

Some calculations can take a few moments, particularly the first few (it caches any previous calculations within the same session), so I have made it print what it is doing to the screen so I can know what's taking so long. This is just 1 line of code, if you wanna disable it just comment out that line.

## Sample input:
```
Enter an item name: Fey'd Leaf Branches +1
```
## Sample output:
```
Fey'd Leaf Branches +1
---------------------------------------------------------------------------------------------
Teclel Jondrathal [Epic] (450/450 0.25r) + Hermit's Medicinal Tea +1 (0/150) +1 : 2.49 Attempts
0.62 Failures, 0.87 Normal Results, 1.0 High Quality Results

Materials used:
  54.78x Silvertongue Moss
  30.96x Shard of Dawn's Light
  45.21x Displacer Beast's Whisker
  25.62x Shadowdemon's Eyes
  2.13x Soulfire Flies
  71.87x Weeping Willow's Tears
  10.9x Terebinth
  17.08x Questionable Piece of Leather
  76.86x Dryad Hair
Material AD cost: 6,338,560

Supplements used:
  2.49x Hermit's Medicinal Tea +1
  19.06x Philosopher's Bounty
  2.18x Maker's Bounty
Materials consumed by supplements:
  33.11x Shadowdemon's Eyes
  27.59x Hardened Blight Bark
  16.55x Shade Leaves
  8.28x Honey
  8.28x Weeping Willow's Tears
  19.06x Philosopher's Bounty
  2.18x Maker's Bounty
Supplement AD cost: 203,438

Total AD cost: 6,541,998
---------------------------------------------------------------------------------------------
6,541,998 AD (0.87 Normal, 1.0 +1): Teclel Jondrathal [Epic] (450/450 0.25r) + Hermit's Medicinal Tea +1 (0/150) +1
7,164,815 AD (0.87 Normal, 1.0 +1): Clefra Niyelyn [Epic] (422/450) + Hermit's Medicinal Tea +1 (0/150) +1
7,286,011 AD (0.87 Normal, 1.0 +1): Isayel Kostrad [Epic] (405/450) + Hermit's Medicinal Tea +1 (0/150) +1
7,295,256 AD (1.1 Normal, 1.0 +1): Teclel Jondrathal [Epic] (450/450 0.25r) + Hermit's Medicinal Tea (0/125)
7,382,322 AD (0.96 Normal, 1.0 +1): Ekkla [Rare] (428/439 0.05r) + Hermit's Medicinal Tea +1 (0/150) +1
7,401,574 AD (0.96 Normal, 1.0 +1): Emmet Crocha [Epic] (439/439) + Hermit's Medicinal Tea +1 (0/150) +1
7,432,089 AD (1.15 Normal, 1.0 +1): Teclel Jondrathal [Epic] (450/450 0.25r) + Distilled Philosopher's Focus +1 (0/120 0.1r) +1
7,654,271 AD (1.02 Normal, 1.0 +1): Karmela Valeri [Epic] (433/433) + Hermit's Medicinal Tea +1 (0/150) +1
7,697,933 AD (0.96 Normal, 1.0 +1): Lem Eastgrass [Rare] (399/439) + Hermit's Medicinal Tea +1 (0/150) +1
7,697,933 AD (0.96 Normal, 1.0 +1): Longelen Ortuliel [Rare] (399/439) + Hermit's Medicinal Tea +1 (0/150) +1
```

As you can see it has highlighted the most cost effective way to craft the item and given a breakdown of the materials needed (on average). Then a summary of the top 10 combos are listed. This is useful if you lack some Artisans or Supplements. For the best recipe it gives the expected number of attempts, failures, normal outputs and high quality outputs. This is all based on averages so this is not the minimum or maximum cost for crafting an item, it is the **average** cost to make the inputted item.

You can tell it you want to craft a high quality item by putting +1 after the item name, as shown. When crafting a high quality item it assumes you want to receive 1 high quality version of the item so the cost listed includes all attempts needed (on average) to get 1 +1 output. The expected amount of normal outputs is listed as a side-effect (this is generally around 1).

When you tell it to craft a normal quality item it will also consider a +1 result acceptable so the listed cost covers the expected number of attempts to get a successful craft, regardless of quality. It will list the chance to get a normal or +1 in this case.

Please note that the inputted item name must match exactly the name of the item in-game (including capitalisation and any special characters like apostrophes). I've been too lazy to change this but if you want to modify this behaviour I will accept PRs :)


# Commission Calculator

There is another script, commissions.py

To run this simply use:
```
python commissions.py
```

and it will print to the console the top 10 commission items to craft as defined by having the lowest AD cost per Sharandar credit received from turning the item in.

## Crafters
crafters.py was my initial attempt at a crafting calculator but it simply told you the costs of using a given combination/stats. calculator.py is much better, it works out the best way for you.

## TODO
- Calculate gold cost for crafting items and include it in overall cost with a gold : AD input cost
- Calculate cost to craft an item using a specific combination of artisan/tool/supplement. This is currently possible internally, it is just not currently possible via command line input.
- Make it less picky with input (accept any capitalisation, ignore special characters, disregard whitespace)
- Refactor the input CSVs to be more readable directly (they are exports from google sheets, you may be able to import them to google sheets to read them more easily?)