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

Credit to Omgifol, A Python library for manipulation of WAD files.
Copyright (c) 2005 Fredrik Johansson
https://sourceforge.net/projects/omgifol/"""


ABOUT = """WAD analysis tool that estimates the toughness of DOOM maps

It queries one or more maps in a WAD/PWAD and prints out some crunched
numbers to try and answer those hard questions.

It tries to help map creators answer these questions:
 * How many monsters are hitscanners?
 * How many health and armor pickups are there?
 * How much damage can the player inflict on all monsters given the 
   amount of ammo in a map?

To accomplish this the following data points are gathered:
 1) count of monsters that are meaty versus hitscanners
 2) sum of health points for health bonus(1), stimpacks(10), medkits(25)
 3) sum of armor points for armor bonus(1), green armor(100), blue armor(200)
 4) count of ammo rounds (including those that enemies will drop)

These numbers are then derived from the gathered data:
 * Health ratio: number of health points per monster
 * Armor ratio: number of armor points per monster
 * Bullet ratio: Damage all bullets can inflict vs total monster hit points.
 * Shell ratio: Damage all shells can inflict vs total monster hit points.

Note: bullet and shell damage is taken as the minimum damage possible per round.
For shells the damage is measured per pellet. This is a known common metric for
both the shotgun and super shotgun.

A bullet ratio of 1 means there are enough bullets to kill every monster at
least once, assuming the round does the least amount of damage possible.

To assist the mapper in making sense of these values, a baseline
of recommended values can be used for comparison.
The default baseline is DOOM2, and can be changed with the -b option.
If a metric falls outside the baseline a recommendation is made.

Note: Berserk(100), Soulsphere(100) and Megasphere(200) items are
NOT counted by default. To count these use the "--bonus" option.

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
HITSCAN_COL = "hit scan %"
HEALTH_RATIO_COL = "health bon^"
ARMOR_RATIO_COL = "armor bon^"
BULLET_DMG_COL = "bullet dmg^"
SHELL_DMG_COL = "shell dmg^"
ROCKET_DMG_COL = "rocket dmg^"
PLASMA_DMG_COL = "plasma dmg^"


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
across DOOM versions I and II. The difference in damage may be significant,
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

