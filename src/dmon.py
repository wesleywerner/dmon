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
import os.path
from docopt import docopt
import constants
import baselines
import dmoncommon

__version__ = "dmon 1.1 (August 2019)"


def test_file_exists(options):
    filename = options["<wad>"]
    exists = os.path.isfile(filename)
    if not exists:
        print("WAD not found: %s" % (filename))
    return exists


def process_wad(options):

    if not test_file_exists(options):
        return

    wad_data = dmoncommon.extract_statistics(options)

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


def format_as_table(columns, rows, first_column_width=6):
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


def to_tabular(wad_data, options, list_averages):
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
    baseline = dmoncommon.load_baseline(options)
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
                this_row = dmoncommon.format_row (map_data[skill], column_names, options, baseline[skill])
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
                    skill_data = dmoncommon.format_row(map_data[skill], column_names, options, baseline[skill])
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


def to_csv(wad_data, options):
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
    baseline = dmoncommon.load_baseline(options)
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
