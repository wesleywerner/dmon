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
Decide for yourself if this tool is useful (or not).
```

# GUIDE

This short guide will walk you through a practical example: E1M9 in `doom.wad`.

```
[doom.wad E1M9]
                  EASY  MEDIUM    HARD
hitscan %           24      36      33
health/AP           .5      .2      .1
armor/AP            .3      .1      .1
bullet/HP            4       2       1
shell/HP             2       2       2
rocket/HP           .6      .2      .2
plasma/HP            0       0       0
flags                p      p!      p!
```

**hitscan %**
This shows the percentage of monsters that use a hitscan attack. More hitscanners generally makes play harder, as these attacks cannot be dodged.

**health/AP**
This ratio is the total health pickups over total monster attack points. If this number is 1 it indicates the player can fully heal if every monster on the map gets one attack against the player, assuming median damage is dealt.

In E1M9 there is enough health items to heal 50% if all monsters attacked the player once for the easy skill, 20% on medium skill and 10% on hard.

**armor/AP**
This ratio is the total armor pickups over total monster attack points. If this number is 1 it indicates one armor point for every monster attack point on the map.

It should be noted that armor class (security/combat) is not factored in, and this ratio is strictly for comparative purposes to the baseline.

**bullet/HP, shell/HP, rocket/HP, plasma/HP**
Total damage for each munition type, over total monster hit points. A value of 1 indicates enough ammunition to kill each monster on the map at least once, assuming the median amount of damage is inflicted.

In E1M9 there are enough shells (factor of `2`) to kill each monster twice over.

**recommendation flags**
These are raised when the results fall outside the baseline. Use the `--legend` option to print the legend with the output.

```
AP: Monster attack points   HP: Monster hit points
 H: Health ratio too low     A: Armor ratio too low
 b: Bullet ratio too low     s: Shell ratio too low
 r: Rocket ratio too low     p: Plasma ratio too low
 !: Hitscan % too high
```

When tweaking a map to meet the baseline, use the `--compare` option to print `actual/baseline` values side-by-side:

```
$ dmon doom.wad E1M9 --compare
[doom.wad E1M9 versus DOOM2]
                  EASY  MEDIUM    HARD
hitscan %        24/38   36/35   33/32
health/AP        .5/.3   .2/.2   .1/.1
armor/AP         .3/.2   .1/.1   .1/.1
bullet/HP          4/1    2/.6    1/.4
shell/HP           2/2     2/1    2/.8
rocket/HP        .6/.5   .2/.2   .2/.2
plasma/HP          0/2    0/.8    0/.6
flags                p      p!      p!
```

Another way to distinguish variance is with the `--diff` option, which prints the difference between actual and baseline:

```
$ dmon doom.wad E1M9 --diff
[doom.wad E1M9 versus DOOM2]
                  EASY  MEDIUM    HARD
hitscan %          -14      +1     +.7
health/AP          +.2    -.03    +.02
armor/AP           +.1       0    -.03
bullet/HP           +3      +1     +.8
shell/HP           +.5      +1     +.9
rocket/HP          +.1       0       0
plasma/HP           -2      -1      -1
flags                p      p!      p!
```

## MORE EXAMPLES

Average for all DOOM2 maps:

    $ dmon DOOM2.WAD --average

Show stats for maps 1-4, counting bonus items, and print the legend:

    $ dmon DOOM2.WAD MAP0[1234] --legend --bonus

Dump all values to csv:

    $ dmon DOOM2.WAD --format=csv

# TESTS

A collection of unit tests are implemented for regression testing.

```
$ python tests.py -v
Baseline expected keys exist ... ok
Baseline values are numbers ... ok
Derive armor to monster ratio ... ok
Derive average ratios ... ok
Derive averages ... ok
Derive bullet damage to monster hit points ratio. ... ok
Derive health to monster ratio ... ok
Derive hitscanner percentage ... ok
Derive plasma damage to monster hit points ratio. ... ok
Derive rocket damage to monster hit points ratio. ... ok
Derive shell damage to monster hit points ratio. ... ok
Count armor points ... ok
Count armor points including bonus items ... ok
Count bullets ... ok
Extraction returns statistics object ... ok
Count health points ... ok
Count health points including bonus items ... ok
Count hitscanners ... ok
Count meaty monsters ... ok
Count monster hit points ... ok
Count plasma ... ok
Count rockets ... ok
Count shells ... ok
Count items with varied skill flags ... ok

----------------------------------------------------------------------
Ran 24 tests in 0.159s
```

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
