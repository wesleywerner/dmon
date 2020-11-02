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
  -b <bl>, --baseline=<bl>  Set comparison baseline [Default: DOOM2]
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
  -p, --pivot               Pivot the output so that statistics are listed
                            as columns instead of rows.
                            Only applies when --format is not set.
  --verbose                 Output debug messages.

"""


import sys
import numbers
import os.path
from docopt import docopt
import constants
import lookup
import baselines

__version__ = "dmon 1.1 (August 2019)"


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

        if options["--verbose"]:
            print("Loading map " + map_name)

        # use the map editor object to interrogate things
        try:
            edit = omg.MapEditor(wad.maps[map_name])
        except KeyError:
            if options["--verbose"]:
                print("Skipping {map_name} Lump".format(map_name=map_name))
            continue

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
            print(to_tabular(wad_data, options, True))
        else:
            print(to_tabular(wad_data, options, False))
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
    if code in baselines.lookup:
        return baselines.lookup.get(code, None)
    else:
        print("error: %s is not a valid baseline code" % (code))
        sys.exit(255)


def format_as_table (columns, rows, first_column_width=6):
    """Formats fixed width columns."""
    # build the format string that pads and aligns our columns
    fmts = ""
    for i, c in enumerate(columns):
        if i == 0:
            # first column is left-aligned
            fmts += "{:<"+str(first_column_width)+"}"
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


def format_row (row_data, column_names, options, baseline_skill):
    """
    Formats multiple data columns into a row object.
    eg returns [1.2, 3.5, 4.2, ...] (for fixed-point format)
               [1, 4, 4, ...] (for defafult format)
               [1/2, 4/4, 4/2, ...] (for comparison format)
    """
    row = []
    diff_mode = options["--diff"]
    cmp_mode = options["--compare"]
    for col_key in column_names:
        value = row_data[col_key]
        if isinstance(value, numbers.Number):
            if diff_mode:
                # as the difference between the baseline
                delta = value - baseline_skill[col_key]
                value = format_digit(delta, options)
                # prefix with the sign
                if delta > 0:
                    value = "+" + value
            else:
                # numbers get formatted according to options
                value = format_digit(value, options)
                # include comparisons
                if cmp_mode:
                    value += "/"
                    value += format_digit(baseline_skill[col_key], options)
        row.append(value)
    return row


def to_tabular (wad_data, options, list_averages):
    """
    Generates a tabular output string from generated statistics.
    Each map is generated in turn (where PATTERN is matched).
    If list_averages is Truthy then the average data is used and
    the map loop is broken early.
    """

    # titles for all statistics
    row_titles = ["HIT SCAN %", "HEALTH ^", "ARMOR ^",
                    "BULLETS ^", "SHELLS ^", "FLAGS"]
    
    # column titles for horizontal output
    h_column_titles = ["SKILL", "HSCAN%", "HEALTH^", "ARMOR^",
                    "BULLET^", "SHELL^", "FLAGS"]
    
    # column titles for each skill
    column_titles = ["", "EASY", "MEDIUM", "HARD"]
    
    # keys of statistics data structure that map to each title
    column_names = ("hitscanner%", "health ratio", "armor ratio",
                    "bullet ratio", "shell ratio")
    
    # Format width of first column.
    # This will be smaller for pivoted output.
    first_column_width = 12

    cmp_mode = options["--compare"]
    diff_mode = options["--diff"]
    pivoted_mode = options["--pivot"]
    baseline = load_baseline(options)
    skill_order = ("easy", "medium", "hard")

    output = ""

    for map_name in wad_data["map list"]:
        map_data = wad_data["data"][map_name]
        
        # Override the map dataset if listing averages.
        if list_averages:
            map_data = wad_data["average"]

        # Print file and map names
        if cmp_mode or diff_mode:
            fmt_values = (wad_data["filename"], map_name, options["--baseline"])
            output += "\n[%s %s versus %s]\n" % fmt_values
        else:
            fmt_values = (wad_data["filename"], map_name)
            output += "\n[%s %s]\n" % fmt_values

        rows = []
        
        # Pivot the output so that statistics are listed
        # as columns instead of rows.
        if pivoted_mode:
            # Switch the column titles for horizontal display
            column_titles = h_column_titles
            first_column_width = 6
            # Averages don't have FLAGS, remove the column
            if list_averages:
                column_titles.pop()
            for skill in skill_order:
                this_row = format_row (map_data[skill], column_names, options, baseline[skill])
                # Insert the skill name
                this_row.insert(0, skill)
                # Append FLAGS when not listing averages
                if not list_averages:
                    this_row.append(map_data[skill]["flags"])
                rows.append(this_row)
        else:
            # List each statistic as a row
            for i, column in enumerate(column_names):
                # Add the stat title
                this_row = [row_titles[i],]
                # Add the values for this stat from each skill level
                for skill in skill_order:
                    skill_data = format_row(map_data[skill], column_names, options, baseline[skill])
                    this_row.append(skill_data[i])
                rows.append(this_row)

            # Append FLAGS when not listing averages
            if not list_averages:
                flags_row = ["FLAGS"]
                for skill in skill_order:
                    flags_row.append(map_data[skill]["flags"])
                rows.append(flags_row)
                
        output += format_as_table(column_titles, rows, first_column_width)

        # Stop processing if listing averages, as it only has one set of values.
        if list_averages:
            break

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
