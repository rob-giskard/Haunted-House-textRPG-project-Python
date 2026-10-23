"""Checks fights: turns, items in combat, ammo and kills."""
import itertools
import unittest
from unittest import mock

from helpers import data, new_game
from haunted_house.combat import combat
from haunted_house.entities import Entity


def fight(commands, backpack=(), weapon='Shotgun', shells=3, player_hp=50, monster_hp=18, player_rolls=20, monster_rolls=1):
    """A fight where the player always wins initiative (unless told otherwise) and every
    other roll is the highest possible (so attacks always hit for maximum damage)."""
    game, ui = new_game(commands)
    player = game.player
    player.weapon, player.shells, player.HP, player.fighting = weapon, shells, player_hp, 1
    game.backpack.contents.extend(backpack)
    monster = Entity('Dummy', monster_hp, data.MONSTER_AC, game.ui)
    game.monster = monster
    initiative = itertools.cycle([player_rolls, monster_rolls])
    with mock.patch('random.randint', side_effect=lambda a, b: next(initiative) if (a, b) == (1, 20) else b):
        combat(game, monster)
    return game, ui, monster


class TestCombat(unittest.TestCase):

    def test_shotgun_kills_in_one_hit(self):
        game, ui, monster = fight(['f'])
        self.assertFalse(monster.alive)
        self.assertEqual(game.player.kills, 1)
        self.assertEqual(game.player.shells, 2, 'firing uses a shell')

    def test_using_a_bandage_costs_your_turn(self):
        game, ui, monster = fight(['u', 'b', 'f'], backpack=['Bandage'], player_hp=20)
        after_bandage = ui.text().split('tend to your wounds')[1]
        before_next_round = after_bandage.split('rolls for initiative')[0]
        self.assertIn('You are hit and take 10 damage', before_next_round)
        self.assertEqual(game.player.shells, 2, 'only the real attack used a shell')

    def test_flashbang_gives_a_free_attack(self):
        game, ui, monster = fight(['u', 'f'], backpack=['Flashbang'])
        self.assertIn('is STUNNED', ui.text())
        self.assertFalse(monster.alive)
        self.assertNotIn('You are hit', ui.text(), 'a stunned monster cannot strike back')

    def test_out_of_ammo_forces_a_weapon_swap(self):
        game, ui, monster = fight(['a', 'f', 'f', 'f', 'f'], shells=0, monster_hp=30)
        self.assertIn('You spent all of your shells', ui.text())
        self.assertEqual(game.player.weapon, 'Axe')
        self.assertFalse(monster.alive)

    def test_empty_guns_cannot_be_chosen(self):
        game, ui = new_game(['r', 's', 'x'])
        game.player.bullets = game.player.shells = 0
        game.player.chooses_weapon()
        self.assertIn('Your gun is empty', ui.text())
        self.assertIn('out of shotgun shells', ui.text())
        self.assertEqual(game.player.weapon, 'Fists')

    def test_losing_initiative_means_the_monster_strikes_first(self):
        game, ui, monster = fight([], player_rolls=1, monster_rolls=20)
        text = ui.text()
        self.assertIn('Dummy is too quick for you', text)
        self.assertLess(text.index('You are hit'), text.index('You hit.'))

    def test_dying_in_combat_ends_the_game(self):
        game, ui, monster = fight(['f'], weapon='Fists', player_hp=5, monster_hp=99)
        self.assertFalse(game.player.alive)
        self.assertEqual((game.player.fighting, game.player.in_house), (0, 0))
        self.assertEqual(game.player.kills, 0)


if __name__ == '__main__':
    unittest.main()
