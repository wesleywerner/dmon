"""
TEST.WAD object breakdown:

[MAP01]

* 5 hitscanners (including spider mastermind, ss trooper)

* 13 meaty monsters (including cyberdemon)

* shells: 48
    8: shotgun
    8: ssg
    4: shells
    20: box of shells
    4: backpack
    4: shotgun guy

* bullets: 145
    50: player start
    20: chaingun
    10: clip
    50: Box of bullets
    10: backpack
    5: trooper

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

* easy: 32 shells (4 shotguns * 8)
* medium: 24 shells (3 shotguns * 8)
* hard: 16 shells (2 shotguns * 8)
"""

# Remove redundant verbose test lines
from unittest.runner import TextTestResult
TextTestResult.getDescription = lambda _, test: test.shortDescription()

import unittest
import baselines
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
        expected = 145
        actual = easy_data["bullets"]
        self.assertEqual(actual, expected)

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


class TestDerivingMethods(unittest.TestCase):

    def test_hitscanner_percentage(self):
        """Derive hitscanner percentage"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 28   # round(5 / 18.0 * 100)
        actual = easy_data["hitscanner%"]
        self.assertEqual(actual, expected)

    def test_armor_ratio(self):
        """Derive armor to monster ratio"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 16.7   # armor points / monsters (301 / 18)
        actual = easy_data["armor ratio"]
        self.assertEqual(actual, expected)

    def test_health_ratio(self):
        """Derive health to monster ratio"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 2   # health points / monsters (36 / 18)
        actual = easy_data["health ratio"]
        self.assertEqual(actual, expected)

    def test_bullet_ratio(self):
        """Derive bullet to monster ratio"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 8.1   # bullets / monsters (145 / 18)
        actual = easy_data["bullet ratio"]
        self.assertEqual(actual, expected)

    def test_shell_ratio(self):
        """Derive shell to monster ratio"""
        options = dmon.docopt(dmon.__doc__, argv=["test.wad", "MAP01"])
        wad_stats = dmoncommon.extract_statistics(options)
        map_data = wad_stats["data"]["MAP01"]
        easy_data = map_data["easy"]
        expected = 2.7   # shells / monsters (48 / 18)
        actual = easy_data["shell ratio"]
        self.assertEqual(actual, expected)

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
        avg = wad_stats["average"]
        expected_hitscan = 35.0
        expected_health = 1.8
        expected_armor = 15.1
        expected_bullet = 10.2
        expected_shell = 4.0
        self.assertEqual(avg["easy"]["hitscanner%"], expected_hitscan)
        self.assertEqual(avg["easy"]["health ratio"], expected_health)
        self.assertEqual(avg["easy"]["armor ratio"], expected_armor)
        self.assertEqual(avg["easy"]["bullet ratio"], expected_bullet)
        self.assertEqual(avg["easy"]["shell ratio"], expected_shell)

    @unittest.skip("not implemented")
    def test_recommendations(self):
        """Derive recommendation codes"""
        pass


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
                data[skill]["hitscanner%"]
                data[skill]["health ratio"]
                data[skill]["armor ratio"]
                data[skill]["bullet ratio"]
                data[skill]["shell ratio"]


if __name__ == '__main__':
    unittest.main()
