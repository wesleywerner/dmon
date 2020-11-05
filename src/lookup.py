"""
A lookup table for hitscanner types.
"""
hitscanner = {
    7: True, # spider mastermind
    9: True, # shotgun guy
    65: True, # commando/chaingunner
    3004: True, # zombieman
    84: True # ss guy
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
    16: True # cyberdemon
}


"""
Lookup table for health item by points.
"""
health = {
    2011: 10, # stimpack
    2012: 25, # medikit
    2014: 1 # health bonus
}


health_bonus = {
    2023: 100, # "berserk"
    2013: 100, # "supercharge"
    83: 200 # "megasphere"
}


"""
Lookup table for armor item by points.
"""
armor = {
    2015: 1, # armor bonus
    2018: 100, # green armor
    2019: 200 # blue armor
}


armor_bonus = {
    83: 200 # "megasphere"
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
    8: 4 # backpack
}


"""
Count of bullets per thing.
"""
bullets = {
    2002: 20, # chaingun
    2007: 10, # ammo clip
    2048: 50, # ammo box
    3004: 5, # zombie - drops clip on death
    8: 10 # backpack
}

"""
Monster hit points lookup.
"""
monster_hp = {
    7: 3000, # spider mastermind
    9: 30, # shotgun guy
    16: 4000, # cyberdemon
    58: 150, # spectre
    64: 700, # archvile
    65: 70, # commando/chaingunner
    66: 30, # revenant
    67: 600, # mancubus
    68: 500, # arachnotron
    69: 500, # hell knight
    71: 400, # pain elemental
    84: 50, # ss guy
    3001: 60, # imp
    3002: 150, # demon
    3003: 1000, # baron of hell
    3004: 20, # zombieman
    3005: 400, # cacodemon
    3006: 100 # lost soul
}