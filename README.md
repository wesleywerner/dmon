# dmon

dmon is a WAD analysis tool that estimates the toughness of DOOM maps. It does this by adding up all health bonuses, ammo pickups and monster counts, then it compares those numbers against a preset baseline. This is useful for balancing your maps to closely match the said baseline.

The default baseline is DOOM II, however this can changed with options. See USAGE below.

# INSTALLATION

dmon is written in Python and targets version `3.8`, however it does run under Python `2.7` if you absolutely need it to.


*GNU / Linux or Mac*

You will need [Python](https://www.python.org/) installed.

Download and extract the latest source from [dmon/releases](https://github.com/wesleywerner/dmon/releases/latest), then run `python dmon.py` to invoke the magic.

You can alias this command in your favorite shell to make this command available anywhere:

```
alias dmon='python ~/path_to/dmon.py'
```

*Windows*

You can run from source or use the pre-built executable:

*Windows Executable*

Download and extract the latest build from [dmon/releases](https://github.com/wesleywerner/dmon/releases/latest). Create a new application shortcut with the below command. It runs a console window with dmon in its path:

```
cmd.exe /k set PATH=C:\Path\To\dmon-1.1_win;%PATH%
```

*Windows Source*

To run from source you need [Python](https://www.python.org/). Either install the official package, or use [WinPython](http://winpython.github.io) for an install-free experience. *Be sure to include Python in your PATH environment*, or use the `WinPython Command Prompt`.

Add the extracted Dmon `src` directory to your `PATH` environment variable and run `dmon`. There is a `dmon.bat` file that acts as the launcher to run from source in Windows.

# ISSUES

Please report any issues in the [issue tracker](https://github.com/wesleywerner/dmon/issues) or on the Doomworld forums.

# USAGE

```
$ dmon -h
Dmon

Usage:
  dmon <wad> [options]
  dmon <wad> <pattern> [options]
  dmon (-h | --help | --about | --license)

Options:
  -h --help                 Show this screen.
  --version                 Show current version.
  --license                 Print the license.
  --about                   Show how this all works.
  <pattern>                 match map name (E1M2 or MAP02)
                            '?' and '*' are wildcards eg:
                                E1M* (all episode 1)
                                MAP0[135] (MAP01, MAP03 and MAP05)
  -a, --average             Combine results from multiple maps into
                            average amounts.
  -u, --bonus               Include berserk, soulsphere and megesphere
                            as data points.
  -f <fmt>, --format=<fmt>  Set output format to: csv, json, dump
  -b, --baseline=<bl>       Set comparison baseline [Default: DOOM2]
                            where <bl> can be:
                                DOOM, DOOM2, SIGIL,
                                AV (Alien Vendetta),
                                HR (HELL REVEALED),
                                DTWID (Doom the Way id Did)
  -c, --compare             Show actual/baseline values for comparison.
  -d, --diff                Display the difference between actual and
                            baseline values.
  -x, --fixed               Display fixed-point numbers (otherwise
                            numbers are rounded up).
  -l, --legend              Print the recommendation legend at the end.
```

# ABOUT

```
$ dmon --about

WAD analysis tool that estimates the toughness of DOOM maps

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
Decide for yourself if this tool is useful (or not).
```

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

dmon uses [Omgifol](https://github.com/devinacker/omgifol), A Python library for manipulation of WAD files. Copyright (c) 2005 Fredrik Johansson, 2017 Devin Acker.

# LICENSE

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
