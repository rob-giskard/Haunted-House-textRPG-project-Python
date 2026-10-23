"""Checks that every way the game can end shows the Game Over screen, the final stats,
and waits for Enter instead of closing."""
import unittest
from unittest import mock

from helpers import new_game, play
from haunted_house.game import Game
from haunted_house.ui import ScriptedUI


class TestEndings(unittest.TestCase):

    def assertProperEnding(self, game, ui, outcome):
        text = ui.text()
        self.assertIn('# GAME OVER #', text)
        self.assertIn('FINAL STATS', text)
        self.assertIn('Outcome:           ' + outcome, text)
        self.assertIn('Press Enter', ui.prompts[-1], 'the last thing the game does is wait for Enter')

    def test_escaping_from_a_room(self):
        game, ui = play(['Tester', 'e'])
        self.assertProperEnding(game, ui, 'Escaped the house')
        self.assertIn('got out empty-handed', ui.text())

    def test_leaving_through_the_front_door(self):
        with mock.patch('random.randrange', return_value=99):      # no traps, no monsters
            game, ui = play(['Tester', 'w', 'r', 's', 'y'])
        self.assertProperEnding(game, ui, 'Escaped the house')
        self.assertIn('Bandage', ui.text().split('escaped with the following treasure')[1])

    def test_drinking_the_vial(self):
        ui = ScriptedUI(['Tester', 'b', 'm'], on_empty='')
        game = Game(ui=ui, seed=1)
        original_intro = game.intro

        def intro_with_vial():
            original_intro()
            game.backpack.add('Mysterious glass vial')
        game.intro = intro_with_vial
        game.run()
        self.assertProperEnding(game, ui, 'Perished in the house')
        self.assertIn('taste death', ui.text())

    def test_dying_to_a_trap(self):
        ui = ScriptedUI(['Tester', 'w'], on_empty='')
        game = Game(ui=ui, seed=1)
        original_intro = game.intro

        def weak_intro():
            original_intro()
            game.player.HP = 1
        game.intro = weak_intro
        with mock.patch('random.randrange', side_effect=lambda a, b: 1 if (a, b) == (1, 100) else 14):
            game.run()
        self.assertProperEnding(game, ui, 'Perished in the house')

    def test_dying_in_combat(self):
        ui = ScriptedUI(['Tester', 'r', 'n', 'f'] + ['f'] * 200, on_empty='')
        game = Game(ui=ui, seed=3)
        original_intro = game.intro

        def weak_intro():
            original_intro()
            game.player.HP = 3
        game.intro = weak_intro
        with mock.patch('random.randrange', side_effect=lambda a, b: 1 if (a, b) == (1, 100) else a):
            game.run()
        self.assertProperEnding(game, ui, 'Perished in the house')
        self.assertIn('you are dead', ui.text())

    def test_dying_of_poison(self):
        ui = ScriptedUI(['Tester', 'r'], on_empty='')
        game = Game(ui=ui, seed=1)
        original_intro = game.intro

        def poisoned_intro():
            original_intro()
            game.player.HP, game.player.condition = 2, 'Poisoned'
        game.intro = poisoned_intro
        game.run()
        self.assertProperEnding(game, ui, 'Perished in the house')
        self.assertIn('succumb to the toxic substance', ui.text())

    def test_final_stats_show_the_numbers(self):
        game, ui = new_game(['', ''])
        game.player.kills, game.player.deeds, game.player.number_of_keys = 2, 1, 3
        game.backpack.add('Diamond ring')
        game.game_over()
        text = ui.text()
        for line in ['Monsters defeated: 2', 'Keys found:        3/4', 'Good deeds:        1/3', 'Items collected:   1']:
            self.assertIn(line, text)
        self.assertIn('Good deeds accomplished: 1', text)

    def test_all_three_deeds_give_the_special_ending(self):
        game, ui = new_game([''])
        game.player.deeds = 3
        game.game_over()
        self.assertIn('Congratulations, Tester!', ui.text())


if __name__ == '__main__':
    unittest.main()
