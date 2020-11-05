import numbers
import lookup
import baselines
import constants

def count_if(func, id):
    """
    Return a counter if func returns True.
    """
    if func (id) == True:
        return 1
    else:
        return 0


def is_hitscanner(id):
    """
    Test if id is a hitscanner monster.
    """
    return lookup.hitscanner.get(id, False)


def is_meaty(id):
    """
    Test if id is a meaty monster.
    """
    return lookup.meaty.get(id, False)


def hit_points_of(id):
    """
    Get the hit points of id (a monster).
    """
    return lookup.monster_hp.get(id, 0)

def health_points_of(id, with_bonus):
    """
    Get the health points of id.
    """
    total = lookup.health.get(id, 0)
    if with_bonus:
        total += lookup.health_bonus.get(id, 0)
    return total


def armor_points_of(id, with_bonus):
    """
    Get the armor points of id.
    """
    total = lookup.armor.get(id, 0)
    if with_bonus:
        total += lookup.armor_bonus.get(id, 0)
    return total


def shells_of(id):
    """
    Counts the number of shells of id.
    """
    return lookup.shells.get(id, 0)


def bullets_of(id):
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
        "monster hit points":0,
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


def extract_statistics(options):
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
            hit_points = hit_points_of(thing.type)

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
                    skill["monster hit points"] += hit_points

    # sum, calculate & derive answers
    if len(wad_data["map list"]) > 0:
        derive_answers(wad_data, options)
        derive_averages(wad_data, options)
        format_results(wad_data, options)

    return wad_data


def derive_averages(wad_data, options):
    """
    Sum the values from each skill and divide by
    the number of data points to get an average.
    """

    skill_order = ("easy", "medium", "hard")
    column_names = ("monsters", "hitscanners", "health points",
                    "armor points", "bullets", "shells", "monster hit points")

    # Take each stat from each map and compile them into grouped lists.
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

    # Sum each list into totals and get the average of each sum.
    # eg sums["easy"]["shells"] = 1000
    #     avg["easy"]["shells"] = 25.5
    sums = new_totals_object(column_names)
    avg = new_totals_object(column_names)
    for skill in skill_order:
        for col in column_names:
            sums[skill][col] = sum(map_counts[skill][col])
            data_points = float(len(map_counts[skill][col]))
            if data_points == 0:
                avg[skill][col] = 0
            else:
                avg[skill][col] = sums[skill][col] / data_points

    # Calculate ratios from our average values.
    for skill in skill_order:
        avg_mons = float(avg[skill]["monsters"])
        avg_mons_hp = float(avg[skill]["monster hit points"])
        # TODO: avg_mons_ap
        avg_hscan = avg[skill]["hitscanners"] / avg_mons
        avg_health = avg[skill]["health points"] / avg_mons #avg_mons_ap
        avg_armor = avg[skill]["armor points"] / avg_mons   #avg_mons_ap
        avg_bullets = (avg[skill]["bullets"] * constants.BULLET_DAMAGE) / avg_mons_hp
        avg_shells = (avg[skill]["shells"] * constants.SGPELLET_DAMAGE) / avg_mons_hp

        avg[skill]["hit scan %"] = round(avg_hscan * 100, 1)
        avg[skill]["health ratio"] = round(avg_health, 1)
        avg[skill]["armor ratio"] = round(avg_armor, 1)
        avg[skill]["bullet ratio"] = round(avg_bullets, 1)
        avg[skill]["shell ratio"] = round(avg_shells, 1)

    wad_data["totals"] = sums
    wad_data["data"]["AVERAGES"] = avg


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


def format_results(wad_data, options):
    """
    Build the results structure with numbers formatted as per options.
    """
    # Load baseline data
    baseline = load_baseline(options)
    # Create the results table
    wad_results = wad_data["results"] = {}
    # Add formatted results for all map statistics
    for map_name in wad_data["map list"] + ["AVERAGES",]:
        map_data = wad_data["data"][map_name]
        map_results = wad_results[map_name] = {}
        for skill in ["easy", "medium", "hard"]:
            skill_results = map_results[skill] = {}
            skill_data = map_data[skill]
            for i, key in enumerate(constants.TITLES):
                if key == "flags":
                    if skill_data.get(key):
                        skill_results[key] = skill_data[key]
                else:
                    skill_results[key] = format_stat(skill_data[key], baseline[skill][key], options)
            

def derive_monster_count(skill):
    """
    Count total number of monsters.
    """
    skill["monsters"] = skill["hitscanners"] + skill["meaty monsters"]


def derive_hitscanner_ratio(skill):
    """
    Calculate percentage of monsters that are hitscanners.
    """
    hitscan_count = skill["hitscanners"]
    monster_count = float(skill["monsters"])
    if monster_count > 0:
        hitscan_ratio = hitscan_count / monster_count * 100
    else:
        hitscan_ratio = 0
    skill["hit scan %"] = int(round(hitscan_ratio))


def derive_armor_and_health_ratio(skill):
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


def derive_ammo_ratio(skill):
    """
    Calculate ratio of ammo damage per monster hit points.
    """
    bullet_count = skill["bullets"]
    shell_count = skill["shells"]
    monster_hp = float(skill["monster hit points"])

    if monster_hp > 0:
        bullet_ratio = (bullet_count * constants.BULLET_DAMAGE) / monster_hp
        shell_ratio = (shell_count * constants.SGPELLET_DAMAGE) / monster_hp
    else:
        bullet_ratio = 0
        shell_ratio = 0

    skill["bullet ratio"] = round(bullet_ratio, 1)
    skill["shell ratio"] = round(shell_ratio, 1)


def derive_recommendations(map_data, skill, options):
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
    hitscan = map_data[skill]["hit scan %"]
    bl_health = baseline[skill]["health ratio"]
    bl_armor = baseline[skill]["armor ratio"]
    bl_bullet = baseline[skill]["bullet ratio"]
    bl_shell = baseline[skill]["shell ratio"]
    bl_hitscan = baseline[skill]["hit scan %"]

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


def load_baseline(options):
    code = options["--baseline"].upper()
    if code in baselines.lookup:
        return baselines.lookup.get(code, None)
    else:
        print("error: %s is not a valid baseline code" % (code))
        sys.exit(255)


def format_digit(number, options):
    """
    Format a number as integer of real.
    """
    if options["--fixed"] == True:
        return str(round(float(number),1))
    else:
        # If value rounds to zero return a float with leading zero sliced
        value = round(number, 1)
        int_value = int(round(number))
        if int_value == 0 and value != 0.0:
            return str(value)[1:]
        else:
            return str(int_value)


def format_stat(number, baseline_skill, options):
    """
    Format statistic per options, as difference to baseline or as comparison.
    """
    if isinstance(number, numbers.Number):
        diff_mode = options["--diff"]
        cmp_mode = options["--compare"]
        if diff_mode:
            # as the difference between the baseline
            delta = number - baseline_skill
            number = format_digit(delta, options)
            # prefix with the sign
            if delta > 0:
                number = "+" + number
        else:
            # numbers get formatted according to options
            number = format_digit(number, options)
            # include comparisons
            if cmp_mode:
                number += "/"
                number += format_digit(baseline_skill, options)
    return number
