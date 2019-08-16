# dmon

# INSTALLATION

You will need python 2.7 available in your environment.

*GNU / Linux*

Add an alias to your `.bash_profile`:

    alias dmon='python ~/path_to/dmon.py'

You can call `dmon` from any directory.

*Windows*

Add the dmon directory to your `%PATH%` environment variable
and call `dmon.bat` (or just `dmon`).


# USAGE

    $ dmon -h
    Dmon

    Usage:
      dmon <wad> [options]
      dmon <wad> <pattern> [options]
      dmon (-h | --help | --about | --license | --examples)

    Options:
      -h --help                 Show this screen.
      --version                 Show current version.
      --license                 Print the license.
      --about                   Show how this all works.
      --examples                Show me some examples.
      <pattern>                 match map name (E1M2 or MAP02)
                                '?' and '*' are wildcards eg:
                                    E1M* (all episode 1)
                                    MAP0[135] (MAP01, MAP03 and MAP05)
      -a, --average             Combine results into an average total.
      -b, --bonus               Include berserk, soulsphere and megesphere
                                as data points.
      -c, --compare             Show actual/baseline values for comparison.
      -f <fmt>, --format=<fmt>  Set the output format to "csv" or "json".
      --baseline=<bl>           Set the comparison baseline [Default: DOOM2]
                                Other values of <bl> are:
                                    DOOM, SIGIL, AV (Alien Vendetta),
                                    HR (HELL REVEALED)
      -l, --legend              Print the recommendation legend at the end.

# ABOUT

    $ dmon --about

    WAD analysis tool and toughness estimation of DOOM maps.

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
    Decide for yourself if this tool is useful (or not).

# GUIDE

We will now query E1M9 in doom.wad and examine each column:

    $ dmon doom.wad E1M9
    [doom.wad E1M9]
    SKILL    HSCAN%  HEALTH^   ARMOR^  BULLET^   SHELL^    FLAGS
    easy         24        7        4       14        2      HAs
    medium       36        3        2        6        2      HA!
    hard         33        2        1        4        2      HA!

**HSCAN%**
This column shows the percentage of monsters that are hitscanners.
More hitscanners generally makes play harder.

**HEALTH^**
Health ratio is the number of health points for every monster.

**ARMOR^**
Armor ratio is the number of armor points for every monster.

**BULLET^**
Bullet ratio is the number of bullets for every monster.

**SHELL^**
Shell ratio is the number of shells for every monster.

**FLAGS**
This column shows flags raised when results fall outside the baseline, which is DOOM2 by default.
If you add the `--legend` option then the recommendation legend prints at the end of the output:

    H: Health ratio is too low
    A: Armor ratio is too low
    b: Bullet ratio is too low
    s: Shell ratio is too low
    !: Hitscanner percentage is too high

When tweaking a map to meet the baseline, use the `--compare` option to print actual/baseline values.
Now we can see that E1M9 has less health and armor than the DOOM2 average:

    $ dmon doom.wad E1M9 --compare
    [doom.wad E1M9 versus DOOM2]
    SKILL    HSCAN%  HEALTH^   ARMOR^  BULLET^   SHELL^    FLAGS
    easy      24/39      7/8      4/6     14/8      2/4      HAs
    medium    36/35      3/4      2/3      6/4      2/2      HA!
    hard      33/32      2/3      1/2      4/3      2/2      HA!

Another view to distinguish variance is the `--diff` option, which shows the difference between actual and baseline:

    $ dmon doom.wad E1M9 --diff
    [doom.wad E1M9 versus DOOM2]
    SKILL    HSCAN%  HEALTH^   ARMOR^  BULLET^   SHELL^    FLAGS
    easy        -15       -1       -2       +6       -2      HAs
    medium       +1       -1       -1       +2        0      HA!
    hard         +1       -1       -1       +1       +0      HA!

This gives a clear difference, if you want to increase the precision add the `--fixed` option to enable fixed-point float numbers.

## MORE EXAMPLES

Average for all DOOM2 maps:

    $ dmon DOOM2.WAD --average

Show stats for maps 1-4 counting bonus items, with legend:

    $ dmon DOOM2.WAD MAP0[1234] --legend --bonus

Dump all values to csv:

    $ dmon DOOM2.WAD --format=csv

Show stats for all maps implemented in your PWAD, with baseline values
side-by-side for comparison - great for optimizing your map:

    $ dmon MYAWESOMEMAP.WAD --compare

# BASELINES

Generate a new baseline by giving the `--average --format=dump` options. The entry can be added to the `baselines.py` source file. Pull requests are welcome.

# TESTS

A small collection of unit tests are implemented for regression testing.

    $ python tests.py -v
    Baseline expected keys exist ... ok
    Baseline values are numbers ... ok
    Derive armor to monster ratio ... ok
    Derive average ratios ... ok
    Derive averages ... ok
    Derive bullet to monster ratio ... ok
    Derive health to monster ratio ... ok
    Derive hitscanner percentage ... ok
    Derive recommendation codes ... skipped 'not implemented'
    Derive shell to monster ratio ... ok
    Count armor points ... ok
    Count armor points including bonus items ... ok
    Count bullets ... ok
    Extraction returns statistics object ... ok
    Count health points ... ok
    Count health points including bonus items ... ok
    Count hitscanners ... ok
    Count meaty monsters ... ok
    Count shells ... ok
    Count items with varied skill flags ... ok

    ----------------------------------------------------------------------
    Ran 20 tests in 0.193s

    OK

# CREDITS

Credit to [Omgifol](https://sourceforge.net/projects/omgifol/), A Python library for manipulation of WAD files. Copyright (c) 2005 Fredrik Johansson

# LICENSE

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
