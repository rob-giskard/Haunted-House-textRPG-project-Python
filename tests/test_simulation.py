"""Lets a bot play many random games and checks that nothing ever breaks.

The bot plays sensibly (searches everything, does the good deeds, heals when hurt), so these
games go through almost every part of the game. Each run uses new random seeds, so over time
the tests explore more and more different games. The results feed the fun statistics that
run_tests.py appends to tests/stats/test_runs.csv.

Number of games: set HH_SIM_GAMES (run_tests.py does this for you; default 100).
"""
import os
import random
import time
import unittest

from helpers import bot_game, data

RESULTS = []                    # one dict per simulated game, read by run_tests.py
FIRST_SEED = None


def simulate():
    global FIRST_SEED
    if RESULTS:
        return RESULTS
    games = int(os.environ.get('HH_SIM_GAMES', '100'))
    FIRST_SEED = int(os.environ.get('HH_SIM_SEED', '0')) or random.Random(time.time()).randint(1, 10**6)
    for seed in range(FIRST_SEED, FIRST_SEED + games):
        RESULTS.append(bot_game(seed))
    return RESULTS


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.results = simulate()

    def test_every_game_ends_properly(self):
        # bot_game would raise if a game crashed or never ended
        self.assertEqual(len(self.results), int(os.environ.get('HH_SIM_GAMES', '100')))

    def test_the_bot_never_gets_an_unexpected_question(self):
        for r in self.results:
            with self.subTest(seed=r['seed']):
                self.assertEqual(r['problems'], [])

    def test_dead_players_know_what_killed_them(self):
        for r in self.results:
            if not r['alive']:
                with self.subTest(seed=r['seed']):
                    self.assertIn(r['death_cause'], ('monster', 'trap', 'poison', 'vial'))
                    self.assertTrue(r['killed_by'])

    def test_numbers_stay_in_range(self):
        for r in self.results:
            with self.subTest(seed=r['seed']):
                self.assertLessEqual(r['keys'], data.KEYS_NEEDED)
                self.assertLessEqual(r['deeds'], 3)
                self.assertLessEqual(r['final_hp'], data.PLAYER_HP)
                self.assertLessEqual(r['rooms_visited'], len(data.ROOMS))
                self.assertLessEqual(len(r['monsters_met']), len(data.CREATURES) + r['monsters_met'].count(data.REPEATABLE_CREATURE))

    def test_survivors_finished_everything(self):
        # the bot only leaves once everything is done, so every survivor is a 100% game
        for r in self.results:
            if r['alive']:
                with self.subTest(seed=r['seed']):
                    self.assertTrue(r['complete'])


if __name__ == '__main__':
    unittest.main()
