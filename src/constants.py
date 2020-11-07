LICENSE = """
Copyright (c) 2019 Wesley (beast) Werner

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
USE OR OTHER DEALINGS IN THE SOFTWARE.

Dmon uses Omgifol, A Python library for manipulation of WAD files.
Copyright (c) 2005 Fredrik Johansson, 2017 Devin Acker.
https://github.com/devinacker/omgifol"""


ABOUT = """WAD analysis tool that estimates the toughness of DOOM maps

It queries one or more maps in a WAD/PWAD and prints out some crunched
numbers to try and answer those hard questions.

It tries to help map creators answer:
 * The percentage of monsters that use hitscan attacks
 * How much health and armor pickups there are, relative to how much
   damage monsters can do to the player
 * The amount of damage the player can inflict on monsters, given the 
   amount of ammo

The following data points are gathered:
 1) sum damage and hit points of monsters, and how many use hitscan attacks
 2) sum health points for health bonus(1), stimpacks(10), medkits(25)
 3) sum armor points for armor bonus(1), green armor(100), blue armor(200)
 4) sum of ammunition rounds (including weapons and enemy drops)

These values are then derived:
 * Health and Armor bonus over median monster attack damage
 * Ammunitions damage over monster hit points

A shell damage of 1 indicates enough shells to kill each monster at least once,
assuming the median amount of damage is inflicted.

Bullet damage is the median for the Chaingun, per tap of the trigger.
Shell damage is the median for the shotgun, per shot.
Rocket damage is the median for the rocket launcher, per rocket.
Plasma damage is the median for the plasma gun, per shot.

To help put these numbers in perspective, they are compared to a baseline and
dmon makes recommendations based on the outcome.
The default baseline is DOOM2 and can be changed with the --baseline option.
If a metric falls outside the baseline a recommendation is made.
You can print the legend of these recommendations with the --legend option.

Note: Berserk(100), Soul sphere(100) and Megasphere(200) items are
not counted by default. To count these use the "--bonus" option.

Dmon uses Omgifol to read WAD files (see --license).

Indemnity: The metrics used here are subjective to personal opinion.
Decide for yourself if this tool is useful (or not)."""


"""
Recommendation codes.
"""
RECOMMENDS_HP = "H"
RECOMMENDS_AP = "A"
RECOMMENDS_HITSCANS = "!"
RECOMMENDS_BULLETS = "b"
RECOMMENDS_SHELLS = "s"
RECOMMENDS_ROCKETS = "r"
RECOMMENDS_PLASMA = "p"


"""
Skill titles.
"""
SKILLS = ("easy", "medium", "hard")


"""
Statistic titles.
"""
HITSCAN_COL = "hitscan %"
HEALTH_RATIO_COL = "health/AP"
ARMOR_RATIO_COL = "armor/AP"
BULLET_DMG_COL = "bullet/HP"
SHELL_DMG_COL = "shell/HP"
ROCKET_DMG_COL = "rocket/HP"
PLASMA_DMG_COL = "plasma/HP"


"""
Ordered list of statistics to calculate and print.
"""
TITLES = (
    HITSCAN_COL,
    HEALTH_RATIO_COL,
    ARMOR_RATIO_COL,
    BULLET_DMG_COL,
    SHELL_DMG_COL,
    ROCKET_DMG_COL,
    PLASMA_DMG_COL,
    "flags"
)


"""
Bullet damage.
Taken as the median damage done by the Chaingun per tap of the trigger.
https://doomwiki.org/wiki/Chaingun#Data
"""
BULLET_DAMAGE = 20


"""
Shell damage.
Taken as the median damage done by the shotgun per attack.
This choice over the super shotgun is due to the commonality of the weapon
across DOOM I and II. The difference in damage may be significant,
but what is important is that the same metric is used consistently against
baselines, providing a constant comparison.
https://doomwiki.org/wiki/Shotgun#Data
"""
SHELL_DAMAGE = 75


"""
Rocket damage.
Taken as the median damage done by the rocket launcher per direct hit (no blast damage).
https://doomwiki.org/wiki/Rocket_launcher#Data
"""
ROCKET_DAMAGE = 100


"""
Plasma damage.
Taken as the median damage done by the plasma gun per shot.
https://doomwiki.org/wiki/Plasma_gun#Data
"""
PLASMA_DAMAGE = 25

