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

__version__ = constants.VERSION


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
    if fmt is not None:
        fmt = fmt.upper()
    
    if len(wad_data["map list"]) == 0:
        map_pattern = options["<pattern>"] or "*"
        print("No maps in WAD, or none matched pattern '%s'."
        " An Imp tears your arm off." % (map_pattern))
    elif fmt is None:
        if options["--average"] == True:
            print(to_tabular(wad_data, options, True))
        else:
            print(to_tabular(wad_data, options, False))
    elif fmt == "CSV":
        print(to_csv(wad_data, options))
    elif fmt == "JSON":
        print(to_json(wad_data))
    elif fmt == "DUMP":
        print(to_baseline_dump(wad_data))
    else:
        print("Invalid output format '%s'."
        " A Demon bites your face off." % (fmt))

    if options["--legend"] == True:
        print_legend_flags(options)


def format_as_table(columns, rows, first_column_width=6, other_column_width=12):
    """
    Formats fixed-width columns.
    """
    fmts = ""
    for i, c in enumerate(columns):
        if i == 0:
            # first column is left-aligned
            fmts += "{:<"+str(first_column_width)+"}"
        else:
            # others right-aligned
            fmts += "{:>"+str(other_column_width)+"}"
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

    # column titles for each skill
    column_titles = ["", "EASY", "MEDIUM", "HARD"]
    
    # Format width of first column.
    # This will be smaller for pivoted output.
    first_column_width = 14
    other_column_width = 8

    cmp_mode = options["--compare"]
    diff_mode = options["--diff"]
    pivoted_mode = options["--pivot"]
    output = ""
    
    # Increase other columns for compare mode
    if cmp_mode:
        other_column_width = 12
    
    # List of maps to print
    map_list = wad_data["map list"]
    
    # Overwrite the map list when printing averages
    if list_averages:
        map_list = ["AVERAGES",]

    for map_name in map_list:
        map_data = wad_data["results"][map_name]
        
        # Print file and map names
        if cmp_mode or diff_mode:
            fmt_values = (wad_data["filename"], map_name, options["--baseline"])
            output += "\n[%s %s versus %s]\n" % fmt_values
        else:
            fmt_values = (wad_data["filename"], map_name)
            output += "\n[%s %s]\n" % fmt_values

        rows = []
        
        if pivoted_mode:
            # List statistics as columns
            column_titles = ("skill",) + constants.TITLES
            # Adjust column sizes for pivoted output
            first_column_width = 6
            other_column_width = 14
            for skill in constants.SKILLS:
                # Add the skill title
                this_row = [skill,]
                for i, title in enumerate(constants.TITLES):
                    # Average row has no flags, default to blank
                    stat_value = map_data[skill].get(title) or ""
                    this_row.append(stat_value)
                rows.append(this_row)
        else:
            # List statistic as rows
            for i, title in enumerate(constants.TITLES):
                # Add the stat title
                this_row = [title,]
                # Add the values for this stat from each skill level
                for skill in constants.SKILLS:
                    # Average row has no flags, default to blank
                    stat_value = map_data[skill].get(title) or ""
                    this_row.append(stat_value)
                rows.append(this_row)

        output += format_as_table(column_titles, rows,
                    first_column_width, other_column_width)

    return output


def to_csv(wad_data, options):
    """
    Output statistics as CSV data.
    """

    csv = (
        "FILE,MAP,"
        "SKILL,"
        "MONSTERS,"
        "HITSCANNERS,"
        "HEALTH POINTS,"
        "ARMOR POINTS,"
        "BULLETS,"
        "SHELLS,"
        "ROCKETS,"
        "CELLS,"
    )
    
    # Add derived stat columns
    for col in constants.TITLES:
        if col != "flags":
            csv += col.upper() + ","

    # Trim trailing comma and end the line
    csv = csv[:-1] + "\n"

    # Add each map and skill as a row
    for map_name in wad_data["map list"]:
        map_data = wad_data["data"][map_name]
        for skill in constants.SKILLS:
            skill_data = map_data[skill]
            csv += wad_data["filename"] + ","
            csv += map_name + ","
            csv += skill + ","
            csv += str(skill_data["monsters"]) + ","
            csv += str(skill_data["hitscanners"]) + ","
            csv += str(skill_data["health points"]) + ","
            csv += str(skill_data["armor points"]) + ","
            csv += str(skill_data["bullets"]) + ","
            csv += str(skill_data["shells"]) + ","
            csv += str(skill_data["rockets"]) + ","
            csv += str(skill_data["plasma cells"]) + ","
            # Add each derived value
            for col in constants.TITLES:
                if col != "flags":
                    csv += str(skill_data[col]) + ","
            # Trim trailing comma and end the line
            csv = csv[:-1] + "\n"

    return csv


def to_json(wad_data):
    """
    Output statistics as raw data.
    """
    import json
    return json.dumps(wad_data, indent=2)


def to_baseline_dump(wad_data):
    """
    Output as baseline-structured dump.
    """
    average_data = wad_data["data"]["AVERAGES"]
    for skill in constants.SKILLS:
        for key, value in average_data[skill].items():
            average_data[skill][key] = round(value, 1)

    import json
    return json.dumps(average_data, indent=4)


def print_legend_flags(options):
    """
    Print the list of recommendation flags with baseline values.
    """
    print("AP: Monster attack points   HP: Monster hit points")
    print(" %s: Health ratio too low     %s: Armor ratio too low"
        % (constants.RECOMMENDS_HP, constants.RECOMMENDS_AP))
    print(" %s: Bullet ratio too low     %s: Shell ratio too low"
        % (constants.RECOMMENDS_BULLETS, constants.RECOMMENDS_SHELLS))
    print(" %s: Rocket ratio too low     %s: Plasma ratio too low"
        % (constants.RECOMMENDS_ROCKETS, constants.RECOMMENDS_PLASMA))
    print(" %s: Hitscan %% too high" % (constants.RECOMMENDS_HITSCANS))


def process_help_and_about_options(options):

    if options["--license"] == True:
        print(constants.LICENSE)
        return True

    if options["--about"] == True:
        print(constants.ABOUT)
        return True

    return False


def valid_baseline_specified(options):
    code = options["--baseline"].upper()
    if code in baselines.lookup:
        return True
    else:
        print("%s is not a valid baseline. "
        "A Cyberdemon blasts you to pieces." % (code))
        return False


def main():
    options = docopt(__doc__, version=__version__)
    if isinstance(options, dict):
        if not valid_baseline_specified(options):
            sys.exit(255)

        if not process_help_and_about_options(options):
            process_wad(options)
    else:
        print(options)


if __name__ == "__main__":
    main()
