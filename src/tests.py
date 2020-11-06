"""
TEST.WAD object breakdown:

[MAP01]

* 5 hitscanners (including spider mastermind, ss trooper)
* 13 meaty monsters (including cyberdemon)

No  SKILL   HIT POINTS      MONSTER                 TOTAL = 11760
1   emh     3000            spider mastermind
1   emh     30              shotgun guy
1   emh     4000            cyberdemon
1   emh     150             spectre
1   emh     700             archvile
1   emh     70              commando/chaingunner
1   emh     30              revenant
1   emh     600             mancubus
1   emh     500             arachnotron
1   emh     500             hell knight
1   emh     400             pain elemental
1   emh     50              ss guy
1   emh     60              imp
1   emh     150             demon
1   emh     1000            baron of hell
1   emh     20              zombieman
1   emh     400             cacodemon
1   emh     100             lost soul

* shells: 48
    8: shotgun
    8: ssg
    4: shells
    20: box of shells
    4: backpack
    4: shotgun guy

* bullets: 5145
    50: player start
    20: chaingun
    10: clip
    5050: 101 Boxes of bullets
    10: backpack
    5: trooper

* plasma (medium & hard): 200
    40: plasma rifle
    20: cell
    100: cell pack
    40: BFG

* plasma (easy): 800
    40: plasma rifle
    20: cell
    700: 7 cell packs
    40: BFG

* health: 36
    10: stimpack
    25: medkit
    1: bonus

* health (bonus): 436
    10: stimpack
    25: medkit
    1: bonus
    100: berserk
    100: soulsphere
    200: megasphere

* armor: 301
    1: bonus
    100: green
    200: blue

* armor (bonus): 501
    1: bonus
    100: green
    200: blue
    200: megasphere

[MAP02]

* easy: 2 hitscanners
* medium: 3 hitscanners
* hard: 5 hitscanners

No  SKILL   HIT POINTS      MONSTER     TOTAL
2   e       20              zombieman   40
3   m       20              zombieman   60
5   h       20              zombieman   100

* easy: 32 shells (4 shotguns * 8)
* medium: 24 shells (3 shotguns * 8)
* hard: 16 shells (2 shotguns * 8)

* 5 rockets, all skills
"""

# Remove redundant verbose test lines
from unittest.runner import TextTestResult
TextTestResult.getDescription = lambda _, test: test.shortDescription()

import unittest
import baselines
import constants
import dmoncommon
import dmon

class TestWADExtractionMethods(unittest.TestCase):

    def test_extraction_returns_stats(self):
        """Extraction returns statistics object"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        self.assertIsNotNone(wad_stats, "extract_statistics gave back None")
        self.assertIsNotNone(wad_stats["map list"])

    def test_hitscanners(self):
        """Count hitscanners"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 5
        actual = easy_data["hitscanners"]
        self.assertEqual(actual, expected)

    def test_meaty(self):
        """Count meaty monsters"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 13
        actual = easy_data["meaty monsters"]
        self.assertEqual(actual, expected)

    def test_shells(self):
        """Count shells"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 48
        actual = easy_data["shells"]
        self.assertEqual(actual, expected)

    def test_bullets(self):
        """Count bullets"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 5145
        actual = easy_data["bullets"]
        self.assertEqual(actual, expected)

    def test_rockets(self):
        """Count rockets"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 8    # Launcher + rocket + box of rockets
        actual = easy_data["rockets"]
        self.assertEqual(actual, expected)

    def test_plasma(self):
        """Count plasma"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        hard_data = map_data["hard"]
        easy_expected = 800 # rifle + cell + 7 packs + BFG
        hard_expected = 200 # rifle + cell + pack + BFG
        easy_actual = easy_data["plasma cells"]
        hard_actual = hard_data["plasma cells"]
        self.assertEqual(easy_actual, easy_expected)
        self.assertEqual(hard_actual, hard_expected)

    def test_health_points(self):
        """Count health points"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 36
        actual = easy_data["health points"]
        self.assertEqual(actual, expected)

    def test_health_points_with_bonus(self):
        """Count health points including bonus items"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01", "--bonus"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 436
        actual = easy_data["health points"]
        self.assertEqual(actual, expected)

    def test_armor_points(self):
        """Count armor points"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 301
        actual = easy_data["armor points"]
        self.assertEqual(actual, expected)

    def test_armor_points_with_bonus(self):
        """Count armor points including bonus items"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01", "--bonus"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 501
        actual = easy_data["armor points"]
        self.assertEqual(actual, expected)

    def test_skill_variances(self):
        """Count items with varied skill flags"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP02"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP02"]
        easy_data = map_data["easy"]
        medium_data = map_data["medium"]
        hard_data = map_data["hard"]
        expected_easy = 32
        expected_medium = 24
        expected_hard = 16
        actual_easy = easy_data["shells"]
        actual_medium = medium_data["shells"]
        actual_hard = hard_data["shells"]
        self.assertEqual(actual_easy, expected_easy)
        self.assertEqual(actual_medium, expected_medium)
        self.assertEqual(actual_hard, expected_hard)
        
    def test_monster_hit_points(self):
        """Count monster hit points"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad"])
        wad_stats = dmoncommon.extract_statistics(options)
        map1_data = wad_stats["data"]["MAP01"]
        map2_data = wad_stats["data"]["MAP02"]
        map3_data = wad_stats["data"]["MAP03"]
        self.assertEqual(map1_data["easy"]["monster hit points"], 11760)
        self.assertEqual(map1_data["medium"]["monster hit points"], 11760)
        self.assertEqual(map1_data["hard"]["monster hit points"], 11760)
        self.assertEqual(map2_data["easy"]["monster hit points"], 40)
        self.assertEqual(map2_data["medium"]["monster hit points"], 60)
        self.assertEqual(map2_data["hard"]["monster hit points"], 100)


class TestDerivingMethods(unittest.TestCase):

    def test_hitscanner_percentage(self):
        """Derive hitscanner percentage"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 28   # round(5 / 18.0 * 100)
        actual = easy_data[constants.HITSCAN_COL]
        self.assertEqual(actual, expected)

    def test_armor_ratio(self):
        """Derive armor to monster ratio"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 16.7   # armor points / monsters (301 / 18)
        actual = easy_data[constants.ARMOR_RATIO_COL]
        self.assertEqual(actual, expected)

    def test_health_ratio(self):
        """Derive health to monster ratio"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 2   # health points / monsters (36 / 18)
        actual = easy_data[constants.HEALTH_RATIO_COL]
        self.assertEqual(actual, expected)

    def test_bullet_ratio(self):
        """
        Derive bullet damage to monster hit points ratio.
        = (bullets * damage) / monster hit points
        = (5145 * 20) / 11760
        = 8.75
        """
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 8.8
        actual = easy_data[constants.BULLET_DMG_COL]
        self.assertEqual(actual, expected)

    def test_shell_ratio(self):
        """
        Derive shell damage to monster hit points ratio.
        = (shells * damage) / monster hit points
        = (32 * 75) / 40
        = 60.0
        """
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP02"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP02"]
        easy_data = map_data["easy"]
        expected = 60
        actual = easy_data[constants.SHELL_DMG_COL]
        self.assertEqual(actual, expected)

    def test_rocket_ratio(self):
        """
        Derive rocket damage to monster hit points ratio.
        = (rockets * damage) / monster hit points
        = (5 * 100) / 40
        = 12.5
        """
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP02"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP02"]
        easy_data = map_data["easy"]
        expected = 12.5
        actual = easy_data[constants.ROCKET_DMG_COL]
        self.assertEqual(actual, expected)

    def test_plasma_ratio(self):
        """
        Derive plasma damage to monster hit points ratio.
        = (cells * damage) / monster hit points
        [EASY]
        = (800 * 25) / 11760
        = 1.7
        [HARD]
        = (200 * 25) / 11760
        = 0.42
        """
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        hard_data = map_data["hard"]
        easy_expected = 1.7
        hard_expected = 0.4
        easy_actual = easy_data[constants.PLASMA_DMG_COL]
        hard_actual = hard_data[constants.PLASMA_DMG_COL]
        self.assertEqual(easy_actual, easy_expected)
        self.assertEqual(hard_actual, hard_expected)

    def test_averages(self):
        """Derive averages"""
        args = ["test.wad", "--average", "MAP0[12]"]
        options = dmon.docopt(dmon.__doc__, argv=args)
        wad_stats = dmoncommon.extract_statistics(options)
        totals = wad_stats["totals"]
        expected_easy = 80
        expected_medium = 72
        expected_hard = 64
        actual_easy = totals["easy"]["shells"]
        actual_medium = totals["medium"]["shells"]
        actual_hard = totals["hard"]["shells"]
        self.assertEqual(actual_easy, expected_easy)
        self.assertEqual(actual_medium, expected_medium)
        self.assertEqual(actual_hard, expected_hard)

    def test_average_ratios(self):
        """Derive average ratios"""
        #~ [test.wad]
        #~ SKILL    HSCAN%  HEALTH^   ARMOR^  BULLET^   SHELL^
        #~ easy       35.0      1.8     15.1     10.3      4.0
        #~ medium     38.1      1.7     14.3     10.0      3.4
        #~ hard       43.5      1.6     13.1      9.6      2.8
        args = ["test.wad", "--average", "MAP0[12]"]
        options = dmon.docopt(dmon.__doc__, argv=args)
        wad_stats = dmoncommon.extract_statistics(options)
        avg = wad_stats["data"]["AVERAGES"]
        expected_hitscan = 35.0
        expected_health = 1.8
        expected_armor = 15.1
        expected_bullet = 8.8
        expected_shell = 0.5
        self.assertEqual(avg["easy"][constants.HITSCAN_COL], expected_hitscan)
        self.assertEqual(avg["easy"][constants.HEALTH_RATIO_COL], expected_health)
        self.assertEqual(avg["easy"][constants.ARMOR_RATIO_COL], expected_armor)
        self.assertEqual(avg["easy"][constants.BULLET_DMG_COL], expected_bullet)
        self.assertEqual(avg["easy"][constants.SHELL_DMG_COL], expected_shell)


class TestBaselineData(unittest.TestCase):

    def test_baselines_values_are_numbers(self):
        """Baseline values are numbers"""
        skill_order = ("easy", "medium", "hard")
        for baseline_name, data in baselines.lookup.items():
            for skill in skill_order:
                for property_name, value in data[skill].items():
                    is_int = type(value) is int
                    is_float = type(value) is float
                    self.assertTrue(is_int or is_float,
                                    baseline_name
                                     + " has invalid value for "
                                     + property_name)

    def test_baselines_expected_keys(self):
        """Baseline expected keys exist"""
        skill_order = ("easy", "medium", "hard")
        for baseline_name, data in baselines.lookup.items():
            for skill in skill_order:
                for col in constants.TITLES:
                    if col != "flags":
                        baseline_value = data[skill].get(col)
                        self.assertIsNotNone(baseline_value,
                            "expected baseline to have row for %s" % (col,))


if __name__ == '__main__':
    unittest.main()
