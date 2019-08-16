"""Dmon

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

"""


import sys
import os.path
from docopt import docopt
import constants
import lookup
import baselines

__version__ = "dmon 1.0 (August 2019)"


def count_if (func, id):
    """
    Return a counter if func returns True.
    """
    if func (id) == True:
        return 1
    else:
        return 0


def is_hitscanner (id):
    """
    Test if id is a hitscanner monster.
    """
    return lookup.hitscanner.get(id, False)


def is_meaty (id):
    """
    Test if id is a meaty monster.
    """
    return lookup.meaty.get(id, False)


def health_points_of (id, with_bonus):
    """
    Get the health points of id.
    """
    total = lookup.health.get(id, 0)
    if with_bonus:
        total += lookup.health_bonus.get(id, 0)
    return total


def armor_points_of (id, with_bonus):
    """
    Get the armor points of id.
    """
    total = lookup.armor.get(id, 0)
    if with_bonus:
        total += lookup.armor_bonus.get(id, 0)
    return total


def shells_of (id):
    """
    Counts the number of shells of id.
    """
    return lookup.shells.get(id, 0)


def bullets_of (id):
    """
    Counts the number of bullets of id.
    """
    return lookup.bullets.get(id, 0)


def new_map_data_object():
    """Return a new blank map data object."""

    # stats are categorized by skill
    n = { "easy": {}, "medium": {}, "hard": {} }

    # default properties of skill objects
    # (player starts with 50 bullets)
    required_properties = {
        "monsters": 0,
        "hitscanners":0,
        "meaty monsters":0,
        "health points":0,
        "armor points":0,
        "shells": 0,
        "bullets": 50,
        }

    for key, value in required_properties.items():
        n["easy"][key] = value
        n["medium"][key] = value
        n["hard"][key] = value

    return n

def new_totals_object(columns):
    """Return a new blank totals object."""

    # stats are categorized by skill
    n = { "easy": {}, "medium": {}, "hard": {} }

    for key in columns:
        n["easy"][key] = []
        n["medium"][key] = []
        n["hard"][key] = []

    return n


def extract_statistics (options):
    """Perform statistics extraction on a wad."""

    filename = options["<wad>"]
    map_pattern = options["<pattern>"] or "*"

    # store all stats for the wad in here.
    # map list: ordered list of map names in this data object.
    wad_data = {
        "filename": filename,
        "map list": [],
        "data": {}
    }

    # open the wad
    from omg import omg
    wad = omg.WAD()
    wad.from_file(filename)

    # iterate each map in the map pattern
    for map_name in wad.maps.find(map_pattern):

        # store the map data in wad stat
        map_data = new_map_data_object()
        wad_data["map list"].append(map_name)
        wad_data["data"][map_name] = map_data

        # alias for efficient iteration
        all_skills = {
            "easy": map_data["easy"],
            "medium": map_data["medium"],
            "hard": map_data["hard"]
            }

        # use the map editor object to interrogate things
        edit = omg.MapEditor(wad.maps[map_name])

        for thing in edit.things:

            # grab the traits of this thing
            hitscan_counter = count_if (is_hitscanner, thing.type)
            meaty_counter = count_if (is_meaty, thing.type)
            health_points = health_points_of (thing.type, options["--bonus"])
            armor_points = armor_points_of (thing.type, options["--bonus"])
            shells_inc = shells_of (thing.type)
            bullets_inc = bullets_of (thing.type)

            # store traits into skill groups
            for skill_name, skill in all_skills.items():
                is_easy = thing.easy and skill_name == "easy"
                is_medium = thing.medium and skill_name == "medium"
                is_hard = thing.hard and skill_name == "hard"
                if is_easy or is_medium or is_hard:
                    skill["hitscanners"] += hitscan_counter
                    skill["meaty monsters"] += meaty_counter
                    skill["health points"] += health_points
                    skill["armor points"] += armor_points
                    skill["shells"] += shells_inc
                    skill["bullets"] += bullets_inc

    # sum, calculate & derive answers
    derive_answers(wad_data, options)
    derive_averages(wad_data, options)
    return wad_data


def derive_averages(wad_data, options):
    """
    Sum the values from each skill and divide by
    the number of data points to get an average.
    """

    if options["--average"] == False:
        return

    skill_order = ("easy", "medium", "hard")
    column_names = ("monsters", "hitscanners", "health points",
                    "armor points", "bullets", "shells")

    # Make lists of the item and monster counts per skill
    # eg map_counts["easy"]["shells"] = [10, 20, ...]
    #    map_counts["medium"]["shells"] = [30, 10, ...]
    map_counts = new_totals_object(column_names)
    for map_name in wad_data["map list"]:
        map_data = wad_data["data"][map_name]
        for skill in skill_order:
            s_data = map_data[skill]
            values = map_counts[skill]
            for col in column_names:
                values[col].append(s_data[col])

    # sum the lists into totals and
    # average each list
    # eg sums["easy"]["shells"] = 1000
    #     avg["easy"]["shells"] = 25.5
    sums = new_totals_object(column_names)
    avg = new_totals_object(column_names)
    for skill in skill_order:
        for col in column_names:
            sums[skill][col] = sum(map_counts[skill][col])
            # number of summed values
            data_points = float(len(map_counts[skill][col]))
            avg[skill][col] = sums[skill][col] / data_points

    # calculate ratios
    for skill in skill_order:
        avg_mons = float(avg[skill]["monsters"])
        avg_hscan = avg[skill]["hitscanners"] / avg_mons
        avg_health = avg[skill]["health points"] / avg_mons
        avg_armor = avg[skill]["armor points"] / avg_mons
        avg_bullets = avg[skill]["bullets"] / avg_mons
        avg_shells = avg[skill]["shells"] / avg_mons

        avg[skill]["hitscanner%"] = round(avg_hscan * 100, 1)
        avg[skill]["health ratio"] = round(avg_health, 1)
        avg[skill]["armor ratio"] = round(avg_armor, 1)
        avg[skill]["bullet ratio"] = round(avg_bullets, 1)
        avg[skill]["shell ratio"] = round(avg_shells, 1)

    wad_data["totals"] = sums
    wad_data["average"] = avg


def derive_answers(wad_data, options):
    """
    Look at extracted values to derive statistics.
    """
    for map_name in wad_data["map list"]:
        map_data = wad_data["data"][map_name]
        for skill in ["easy", "medium", "hard"]:
            derive_monster_count(map_data[skill])
            derive_hitscanner_ratio(map_data[skill])
            derive_armor_and_health_ratio(map_data[skill])
            derive_ammo_ratio(map_data[skill])
            derive_recommendations(map_data, skill, options)


def derive_monster_count (skill):
    """
    Count total number of monsters.
    """
    skill["monsters"] = skill["hitscanners"] + skill["meaty monsters"]


def derive_hitscanner_ratio (skill):
    """
    Calculate percentage of monsters that are hitscanners.
    """
    hitscan_count = skill["hitscanners"]
    monster_count = float(skill["monsters"])
    if monster_count > 0:
        hitscan_ratio = hitscan_count / monster_count * 100
    else:
        hitscan_ratio = 0
    skill["hitscanner%"] = int(round(hitscan_ratio))


def derive_armor_and_health_ratio (skill):
    """
    Calculate ratios of health and armor bonuses.
    """
    health_points = skill["health points"]
    armor_points = skill["armor points"]
    monster_count = float(skill["monsters"])

    if monster_count > 0:
        health_ratio = health_points / monster_count
        armor_ratio = armor_points / monster_count
    else:
        health_ratio = 0
        armor_ratio = 0

    skill["health ratio"] = round(health_ratio, 1)
    skill["armor ratio"] = round(armor_ratio, 1)


def derive_ammo_ratio (skill):
    """
    Calculate ratio of ammo per monster.
    """
    monster_count = float(skill["monsters"])
    bullet_count = skill["bullets"]
    shell_count = skill["shells"]

    if monster_count > 0:
        bullet_ratio = bullet_count / monster_count
        shell_ratio = shell_count / monster_count
    else:
        bullet_ratio = 0
        shell_ratio = 0

    skill["bullet ratio"] = round(bullet_ratio, 1)
    skill["shell ratio"] = round(shell_ratio, 1)


def derive_recommendations (map_data, skill, options):
    """
    Gets recommendation codes.
    """

    rec_codes = ""
    map_data[skill]["flags"] = rec_codes

    baseline = load_baseline(options)
    if baseline is None:
        return

    health_ratio = map_data[skill]["health ratio"]
    armor_ratio = map_data[skill]["armor ratio"]
    bullet_ratio = map_data[skill]["bullet ratio"]
    shell_ratio = map_data[skill]["shell ratio"]
    hitscan = map_data[skill]["hitscanner%"]
    bl_health = baseline[skill]["health ratio"]
    bl_armor = baseline[skill]["armor ratio"]
    bl_bullet = baseline[skill]["bullet ratio"]
    bl_shell = baseline[skill]["shell ratio"]
    bl_hitscan = baseline[skill]["hitscanner%"]

    if options["--fixed"] == False:
        health_ratio = int(round(health_ratio))
        armor_ratio = int(round(armor_ratio))
        bullet_ratio = int(round(bullet_ratio))
        shell_ratio = int(round(shell_ratio))
        hitscan = int(round(hitscan))
        bl_health = int(round(bl_health))
        bl_armor = int(round(bl_armor))
        bl_bullet = int(round(bl_bullet))
        bl_shell = int(round(bl_shell))
        bl_hitscan = int(round(bl_hitscan))

    if health_ratio < bl_health:
        rec_codes += constants.RECOMMENDS_HP

    if armor_ratio < bl_armor:
        rec_codes += constants.RECOMMENDS_AP

    if bullet_ratio < bl_bullet:
        rec_codes += constants.RECOMMENDS_BULLETS

    if shell_ratio < bl_shell:
        rec_codes += constants.RECOMMENDS_SHELLS

    if hitscan > bl_hitscan:
        rec_codes += constants.RECOMMENDS_HITSCANS

    map_data[skill]["flags"] = rec_codes


def test_file_exists(options):
    filename = options["<wad>"]
    exists = os.path.isfile(filename)
    if not exists:
        print("WAD not found: %s" % (filename))
    return exists


def process_wad(options):

    if not test_file_exists(options):
        return

    wad_data = extract_statistics(options)

    fmt = options["--format"]
    if fmt is None:
        if options["--average"] == True:
            print(to_tabular_average(wad_data, options))
        else:
            print(to_tabular(wad_data, options))
    elif fmt == "csv":
        print(to_csv(wad_data, options))
    elif fmt == "json":
        print(to_json(wad_data))
    elif fmt == "dump":
        print(to_baseline_dump(wad_data))
    else:
        print("Invalid output format '%s'."
        " A demon bites your face off." % (fmt))

    if options["--legend"] == True:
        print_legend_flags(options)


def load_baseline(options):
    code = options["--baseline"].upper()
    return baselines.lookup.get(code, None)


def format_as_table (columns, rows):
    """Formats fixed width columns."""
    # build the format string that pads and aligns our columns
    fmts = ""
    for i, c in enumerate(columns):
        if i == 0:
            # first column is left-aligned
            fmts += "{:<6}"
        else:
            # others right-aligned
            fmts += "{:>9}"
    output = fmts.format(*columns) + "\n"
    for values in rows:
        output += fmts.format(*values) + "\n"
    return output


def format_digit (number, options):
    if options["--fixed"] == True:
        return str(float(number))
    else:
        return str(int(round(number)))


def to_tabular (wad_data, options):

    columns = ["SKILL", "HSCAN%", "HEALTH^", "ARMOR^",
               "BULLET^", "SHELL^", "FLAGS"]

    # load the baseline stats
    baseline = load_baseline(options)

    # order of skills printed
    skill_order = ("easy", "medium", "hard")

    output = ""

    for map_name in wad_data["map list"]:
        map_data = wad_data["data"][map_name]

        # title
        if options["--compare"] and baseline:
            output += ("[%s %s versus %s]\n" %
                (wad_data["filename"], map_name, options["--baseline"]))
        else:
            output += ("[%s %s]\n" % (wad_data["filename"], map_name))

        # each skill row
        rows = []
        for skill in skill_order:
            skill_data = map_data[skill]

            sk_hitscan = format_digit(skill_data["hitscanner%"], options)
            sk_health = format_digit(skill_data["health ratio"], options)
            sk_armor = format_digit(skill_data["armor ratio"], options)
            sk_bullet = format_digit(skill_data["bullet ratio"], options)
            sk_shell = format_digit(skill_data["shell ratio"], options)
            sk_recom = skill_data["flags"]

            # add limit value
            if baseline and options["--compare"]:
                bl_hitscan = format_digit(baseline[skill]["hitscanner%"], options)
                bl_health = format_digit(baseline[skill]["health ratio"], options)
                bl_armor = format_digit(baseline[skill]["armor ratio"], options)
                bl_bullet = format_digit(baseline[skill]["bullet ratio"], options)
                bl_shell = format_digit(baseline[skill]["shell ratio"], options)

                sk_hitscan += "/" + bl_hitscan
                sk_health += "/" + bl_health
                sk_armor += "/" + bl_armor
                sk_bullet += "/" + bl_bullet
                sk_shell += "/" + bl_shell

            rows.append([skill, sk_hitscan, sk_health,
                      sk_armor, sk_bullet, sk_shell, sk_recom])

        output += format_as_table(columns, rows)

    return output


def to_tabular_average (wad_data, options):

    columns = ["SKILL", "HSCAN%", "HEALTH^", "ARMOR^",
                "BULLET^", "SHELL^"]

    # load the baseline stats
    baseline = load_baseline(options)

    # order of skills printed
    skill_order = ("easy", "medium", "hard")

    output = ""

    # title
    if options["--compare"] and baseline:
        output += ("[%s versus %s]\n" %
            (wad_data["filename"], options["--baseline"]))
    else:
        output += ("[%s]\n" % (wad_data["filename"]))

    # each skill row
    rows = []
    for skill in skill_order:
        avg_data = wad_data["average"][skill]

        sk_hitscan = str(format_digit(avg_data["hitscanner%"], options))
        sk_health = str(format_digit(avg_data["health ratio"], options))
        sk_armor = str(format_digit(avg_data["armor ratio"], options))
        sk_bullet = str(format_digit(avg_data["bullet ratio"], options))
        sk_shell = str(format_digit(avg_data["shell ratio"], options))

        # add limit value
        if baseline and options["--compare"]:
            bl_hitscan = str(format_digit(baseline[skill]["hitscanner%"], options))
            bl_health = str(format_digit(baseline[skill]["health ratio"], options))
            bl_armor = str(format_digit(baseline[skill]["armor ratio"], options))
            bl_bullet = str(format_digit(baseline[skill]["bullet ratio"], options))
            bl_shell = str(format_digit(baseline[skill]["shell ratio"], options))

            sk_hitscan += "/" + bl_hitscan
            sk_health += "/" + bl_health
            sk_armor += "/" + bl_armor
            sk_bullet += "/" + bl_bullet
            sk_shell += "/" + bl_shell

        rows.append([skill, sk_hitscan, sk_health,
                  sk_armor, sk_bullet, sk_shell])

    output += format_as_table(columns, rows)

    return output


def to_csv (wad_data, options):
    """
    Output statistics as CSV data.
    """

    skill_order = ("easy", "medium", "hard")

    csv = ("FILE,MAP,SKILL,MONSTERS,HITSCANNERS,HITSCANNER%,HEALTH POINTS,HEALTH RATIO,"
           "ARMOR POINTS,ARMOR RATIO,BULLETS,"
           "BULLET RATIO,SHELLS,SHELL RATIO\n")

    for map_name in wad_data["map list"]:
        map_data = wad_data["data"][map_name]
        for skill in skill_order:
            skill_data = map_data[skill]
            csv += wad_data["filename"] + ","
            csv += map_name + ","
            csv += skill + ","
            csv += str(skill_data["monsters"]) + ","
            csv += str(skill_data["hitscanners"]) + ","
            csv += str(skill_data["hitscanner%"]) + ","
            csv += str(skill_data["health points"]) + ","
            csv += str(skill_data["health ratio"]) + ","
            csv += str(skill_data["armor points"]) + ","
            csv += str(skill_data["armor ratio"]) + ","
            csv += str(skill_data["bullets"]) + ","
            csv += str(skill_data["bullet ratio"]) + ","
            csv += str(skill_data["shells"]) + ","
            csv += str(skill_data["shell ratio"])
            csv += "\n"

    return csv


def to_json(wad_data):
    """
    Output statistics as raw data.
    """
    import json
    return json.dumps(wad_data)


def to_baseline_dump(wad_data):
    """
    Output as baseline-structured dump.
    """
    if not "average" in wad_data:
        return "error: baseline dump only works with --average option."

    skills = ("easy", "medium", "hard")

    for skill in skills:
        for key, value in wad_data["average"][skill].items():
            wad_data["average"][skill][key] = round(value, 1)

    import json
    return json.dumps(wad_data["average"], indent=4)


def print_legend_flags(options):
    """
    Print the list of recommendation flags with baseline values.
    """
    baseline = load_baseline(options)
    if not baseline:
        return
    print("%s: Health ratio is too low" % (constants.RECOMMENDS_HP))
    print("%s: Armor ratio is too low" % (constants.RECOMMENDS_AP))
    print("%s: Bullet ratio is too low" % (constants.RECOMMENDS_BULLETS))
    print("%s: Shell ratio is too low" % (constants.RECOMMENDS_SHELLS))
    print("%s: Hitscanner percentage is too high" % (constants.RECOMMENDS_HITSCANS))


def process_help_and_about_options(options):

    if options["--license"] == True:
        print(constants.LICENSE)
        return True

    if options["--about"] == True:
        print(constants.ABOUT)
        return True

    return False


def main():
    options = docopt(__doc__, version=__version__)
    if isinstance(options, dict):
        if not process_help_and_about_options(options):
            process_wad(options)
    else:
        print(options)


if __name__ == "__main__":
    main()
