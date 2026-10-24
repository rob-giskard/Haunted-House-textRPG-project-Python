"""Starts the real programs the way a player or developer would."""
import os
import subprocess
import sys
import unittest

from helpers import ROOT
from haunted_house.walkthrough import DEFAULT_PATH


def run(args):
    result = subprocess.run([sys.executable] + args, cwd=ROOT, capture_output=True, text=True, timeout=120)
    return result.returncode, result.stdout + result.stderr


class TestEntryPoints(unittest.TestCase):

    def test_the_game_explains_its_options(self):
        code, out = run(['HauntedHouse.py', '--help'])
        self.assertEqual(code, 0, out)
        self.assertIn('--autoplay', out)

    def test_autoplay_options(self):
        sys.path.insert(0, ROOT)
        import HauntedHouse
        self.assertIsNone(HauntedHouse.parse_args([]).autoplay)
        self.assertEqual(HauntedHouse.parse_args(['--autoplay']).autoplay, DEFAULT_PATH)
        args = HauntedHouse.parse_args(['--autoplay', 'mine.txt', '--delay', '0'])
        self.assertEqual((args.autoplay, args.delay), ('mine.txt', 0.0))

    def test_house_plan_draws(self):
        code, out = run(['HousePlan.py'])
        self.assertEqual(code, 0, out)
        self.assertIn('Foyer', out)


if __name__ == '__main__':
    unittest.main()
