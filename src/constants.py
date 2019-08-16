"""
The recommendation codes.
"""
RECOMMENDS_HP = "H"
RECOMMENDS_AP = "A"
RECOMMENDS_HITSCANS = "!"
RECOMMENDS_BULLETS = "b"
RECOMMENDS_SHELLS = "s"

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

ABOUT = """WAD analysis tool and toughness estimation of DOOM maps.

It queries one or more maps in a WAD/PWAD and prints out the number of
hitscanners, health, armor, and ammo items.

It goes further to help map creators answer these questions:
 * how many health and armor points compared to the number of monsters?
 * how many ammo rounds are there for each monster?
 * how many monsters are hitscanners?

To accomplish this the following data points are gathered:
 1) count of monsters that are hitscanners
 2) sum of health points for health bonus(1), stimpacks(10), medkits(25)
 3) sum of armor points for armor bonus(1), green armor(100), blue armor(200)
 4) count of ammo rounds (including rounds that enemies will drop)

These metrics are then derived from the gathered data:
 * Health ratio: number of health points per monster
 * Armor ratio: number of armor points per monster
 * Bullet ratio: bullets per monster
 * Shell ratio: shells per monster

To assist the mapper in making sense of these values, we built a baseline
of recommended values to compare against. The baseline was sampled from DOOM2.

The tool compares the map metrics against the baseline, and if a metric
falls outside the baseline a recommendation is made.

Note: Berserk(100), Soulsphere(100) and Megasphere(200) items are
NOT counted by default. To count these use the "--bonus" option.

Dmon uses Omgifol to read WAD files (see --license)

Indemnity: The metrics used here are subjective to personal opinion.
Decide for yourself if this tool is useful (or not)."""
