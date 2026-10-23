"""Checks that walkthrough.txt still completes 100% of the game.

If you change the game in a way that affects the dice or the rooms, this test fails:
the walkthrough then needs to be regenerated.
"""
import unittest

from helpers import data, play, read_walkthrough, rooms_visited


class TestWalkthrough(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed, commands = read_walkthrough()
        cls.seed, cls.commands = seed, commands
        cls.game, cls.ui = play(commands, seed=seed)

    def test_has_a_seed(self):
        self.assertIsNotNone(self.seed)

    def test_uses_every_command_and_waits_for_enter_at_the_end(self):
        self.assertEqual(self.ui.commands, [], 'the game ended before the walkthrough did')
        self.assertIn('Press Enter', self.ui.prompts[-1])
        self.assertEqual(len(self.ui.prompts), len(self.commands) + 1, 'walkthrough stopped one step early')

    def test_survives(self):
        self.assertTrue(self.game.player.alive)

    def test_finds_all_keys_and_does_all_good_deeds(self):
        self.assertEqual(self.game.player.number_of_keys, data.KEYS_NEEDED)
        self.assertEqual(self.game.player.deeds, 3)
        self.assertIn('Safe', self.game.opened_doors)

    def test_visits_every_room_and_searches_everything(self):
        self.assertEqual(rooms_visited(self.ui.text()), set(data.ROOMS))
        for room in self.game.rooms.values():
            self.assertEqual(room.unsearched(), [], room.name)

    def test_no_wasted_commands(self):
        text = self.ui.text()
        for complaint in ['Invalid direction', 'gives you chills', 'You bump into a wall', 'Item not usable']:
            self.assertNotIn(complaint, text)


if __name__ == '__main__':
    unittest.main()
