# TODO Add "backpack":8 to lookups

"""
A lookup table for hitscanner types.
"""
hitscanner = {
    7: True, # spider mastermind
    9: True, # shotgun guy
    65: True, # commando/chaingunner
    3004: True, # zombie
    84: True, # ss guy
    }


"""
A lookup table for non-hitscanner types.
"""
meaty = {
    3001: True, # imp
    3002: True, # demon
    58: True, # spectre
    3006: True, # lost soul
    3005: True, # cacodemon
    69: True, # hell knight
    3003: True, # baron of hell
    66: True, # revenant
    67: True, # mancubus
    68: True, # arachnotron
    71: True, # pain elemental
    64: True, # archvile
    16: True, # cyberdemon
    }


"""
Lookup table for health item by points.
"""
health = {
    2011: 10, # stimpack
    2012: 25, # medikit
    2014: 1, # health bonus
    #2023: 100, # berserk
    #2013: 100, # supercharge
    #83: 200, # megasphere
    }


health_bonus = {
    2023: 100, # "berserk"
    2013: 100, # "supercharge"
    83: 200, # "megasphere"
    }


"""
Lookup table for armor item by points.
"""
armor = {
    2015: 1, # armor bonus
    2018: 100, # green armor
    2019: 200, # blue armor
    }


armor_bonus = {
    83: 200, # "megasphere"
    }


"""
Count of shells per thing.
"""
shells = {
    2008: 4, # 4 shells
    2049: 20, # shell box
    2001: 8, # shotgun
    82: 8, # super shotgun
    9: 4, # shotgun guy - drops weapon on death
    8: 4, # backpack
    }


"""
Count of bullets per thing.
"""
bullets = {
    2002: 20, # chaingun
    2007: 10, # ammo clip
    2048: 50, # ammo box
    3004: 5, # zombie - drops clip on death
    8: 10, # backpack
    }

# weapons = ThingCategory({
  # rocket launcher":2003,
  # plasma gun":2004,
  # chainsaw":2005,
  # bfg 9000":2006
# })

# ammo = ThingCategory({
  # rocket":2010,
  # rocket box":2046,
  # cell charge":2047,
  # cell pack":17,
  # backpack":8
# })
