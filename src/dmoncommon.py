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


def rockets_of(id):
    """
    Counts the number of rockets of id.
    """
    return lookup.rockets.get(id, 0)


def plasma_of(id):
    """
    Counts the number of plasma cells of id.
    """
    return lookup.plasma.get(id, 0)


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
        "rockets":0,
        "plasma cells":0
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
            hitscan_counter = count_if(is_hitscanner, thing.type)
            meaty_counter = count_if(is_meaty, thing.type)
            health_points = health_points_of(thing.type, options["--bonus"])
            armor_points = armor_points_of(thing.type, options["--bonus"])
            shells_inc = shells_of(thing.type)
            bullets_inc = bullets_of(thing.type)
            hit_points = hit_points_of(thing.type)
            rockets_inc = rockets_of(thing.type)
            plasma_inc = plasma_of(thing.type)

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
                    skill["rockets"] += rockets_inc
                    skill["plasma cells"] += plasma_inc

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
                    "armor points", "bullets", "shells", "rockets",
                    "plasma cells",
                    "monster hit points")

    # Take each stat from each map and compile them into grouped lists.
    # eg grouped_values["easy"]["shells"] = [10, 20, ...]
    #    grouped_values["medium"]["shells"] = [30, 10, ...]
    grouped_values = new_totals_object(column_names)
    for map_name in wad_data["map list"]:
        map_data = wad_data["data"][map_name]
        for skill in skill_order:
            s_data = map_data[skill]
            values = grouped_values[skill]
            for col in column_names:
                values[col].append(s_data[col])

    # Sum each list into totals and get the average of each sum.
    # eg sums["easy"]["shells"] = 1000
    #     avg["easy"]["shells"] = 25.5
    sums = new_totals_object(column_names)
    avg = new_totals_object(column_names)
    for skill in skill_order:
        for col in column_names:
            sums[skill][col] = sum(grouped_values[skill][col])
            data_points = float(len(grouped_values[skill][col]))
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
        avg_shells = (avg[skill]["shells"] * constants.SHELL_DAMAGE) / avg_mons_hp
        avg_rockets = (avg[skill]["rockets"] * constants.ROCKET_DAMAGE) / avg_mons_hp
        avg_plasma = (avg[skill]["plasma cells"] * constants.PLASMA_DAMAGE) / avg_mons_hp

        avg[skill][constants.HITSCAN_COL] = round(avg_hscan * 100, 1)
        avg[skill][constants.HEALTH_RATIO_COL] = round(avg_health, 1)
        avg[skill][constants.ARMOR_RATIO_COL] = round(avg_armor, 1)
        avg[skill][constants.BULLET_DMG_COL] = round(avg_bullets, 1)
        avg[skill][constants.SHELL_DMG_COL] = round(avg_shells, 1)
        avg[skill][constants.ROCKET_DMG_COL] = round(avg_rockets, 1)
        avg[skill][constants.PLASMA_DMG_COL] = round(avg_plasma, 1)

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
                    skill_results[key] = format_stat(skill_data.get(key,0), baseline[skill].get(key,0), options)
            

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
    skill[constants.HITSCAN_COL] = int(round(hitscan_ratio))


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

    skill[constants.HEALTH_RATIO_COL] = round(health_ratio, 1)
    skill[constants.ARMOR_RATIO_COL] = round(armor_ratio, 1)


def derive_ammo_ratio(skill):
    """
    Calculate ratio of ammo damage per monster hit points.
    """
    bullet_count = skill["bullets"]
    shell_count = skill["shells"]
    rocket_count = skill["rockets"]
    plasma_count = skill["plasma cells"]
    monster_hp = float(skill["monster hit points"])

    bullet_ratio = 0
    shell_ratio = 0
    rocket_ratio = 0
    plasma_ratio = 0

    if monster_hp > 0:
        bullet_ratio = (bullet_count * constants.BULLET_DAMAGE) / monster_hp
        shell_ratio = (shell_count * constants.SHELL_DAMAGE) / monster_hp
        rocket_ratio = (rocket_count * constants.ROCKET_DAMAGE) / monster_hp
        plasma_ratio = (plasma_count * constants.PLASMA_DAMAGE) / monster_hp
    # else:

    skill[constants.BULLET_DMG_COL] = round(bullet_ratio, 1)
    skill[constants.SHELL_DMG_COL] = round(shell_ratio, 1)
    skill[constants.ROCKET_DMG_COL] = round(rocket_ratio, 1)
    skill[constants.PLASMA_DMG_COL] = round(plasma_ratio, 1)


def derive_recommendations(map_data, skill, options):
    """
    Gets recommendation codes.
    """

    rec_codes = ""
    map_data[skill]["flags"] = rec_codes
    baseline = load_baseline(options)

    # Get map values
    health_ratio = map_data[skill][constants.HEALTH_RATIO_COL]
    armor_ratio = map_data[skill][constants.ARMOR_RATIO_COL]
    bullet_ratio = map_data[skill][constants.BULLET_DMG_COL]
    shell_ratio = map_data[skill][constants.SHELL_DMG_COL]
    hitscan = map_data[skill][constants.HITSCAN_COL]
    rocket_ratio = map_data[skill][constants.ROCKET_DMG_COL]
    plasma_ratio = map_data[skill][constants.PLASMA_DMG_COL]
    
    # Get baseline values
    bl_health = baseline[skill].get(constants.HEALTH_RATIO_COL, 0)
    bl_armor = baseline[skill].get(constants.ARMOR_RATIO_COL, 0)
    bl_bullet = baseline[skill].get(constants.BULLET_DMG_COL, 0)
    bl_shell = baseline[skill].get(constants.SHELL_DMG_COL, 0)
    bl_hitscan = baseline[skill].get(constants.HITSCAN_COL, 0)
    bl_rocket = baseline[skill].get(constants.ROCKET_DMG_COL, 0)
    bl_plasma = baseline[skill].get(constants.PLASMA_DMG_COL, 0)

    # Format the values
    # TODO: investigate removing rounding
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
        bl_rocket = int(round(bl_rocket))
        bl_plasma = int(round(bl_plasma))

    if health_ratio < bl_health:
        rec_codes += constants.RECOMMENDS_HP

    if armor_ratio < bl_armor:
        rec_codes += constants.RECOMMENDS_AP

    if bullet_ratio < bl_bullet:
        rec_codes += constants.RECOMMENDS_BULLETS

    if shell_ratio < bl_shell:
        rec_codes += constants.RECOMMENDS_SHELLS

    if rocket_ratio < bl_rocket:
        rec_codes += constants.RECOMMENDS_ROCKETS
        
    if plasma_ratio < bl_plasma:
        rec_codes += constants.RECOMMENDS_PLASMA

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
        # If value rounds to zero: return a float with leading zero sliced.
        # Returns either 1 or 2 decimal float, depending which one is not 0.
        # This gives fractions like .2 and .05
        value1 = round(number, 1)
        value2 = round(number, 2)
        int_value = int(round(number))
        if int_value == 0 and value1 != 0.0:
            # Rounded to 1 decimal has value
            return str(value1)[1:]
        elif int_value == 0 and value2 != 0.0:
            # Rounded to 2 decimals has value
            return str(value2)[1:]
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
