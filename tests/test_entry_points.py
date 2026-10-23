"""Starts the real programs the way a player would, as separate processes."""
import os
import subprocess
import sys
import unittest

from helpers import ROOT


def run(args, typed):
    result = subprocess.run([sys.executable] + args, input=typed, cwd=ROOT, capture_output=True,
                            text=True, timeout=120)
    return result.returncode, result.stdout + result.stderr


class TestEntryPoints(unittest.TestCase):

    def test_the_game_starts_and_ends(self):
        code, out = run(['HauntedHouse.py'], 'Tester\ne\n\n')
        self.assertEqual(code, 0, out)
        self.assertIn('Welcome to the haunted house', out)
        self.assertIn('FINAL STATS', out)

    def test_autoplay_plays_the_walkthrough(self):
        code, out = run(['autoplay.py', '--fast'], '\n')
        self.assertEqual(code, 0, out)
        self.assertIn('Good deeds:        3/3', out)
        self.assertIn('Walkthrough finished', out)

    def test_house_plan_draws(self):
        code, out = run(['HousePlan.py'], '')
        self.assertEqual(code, 0, out)
        self.assertIn('Foyer', out)


if __name__ == '__main__':
    unittest.main()
