"""Checks individual game mechanics: keys, looting, items, traps, poison, doors, good deeds, monsters."""
import random
import unittest
from unittest import mock

from helpers import data, new_game
from haunted_house.combat import ambush
from haunted_house.world import Container


def all_keys(game):
    """(room, container, key) for every key hidden in the house."""
    found = []
    for name, room in game.rooms.items():
        for container in room.objects:
            for item in container.contents:
                if item.endswith(' key'):
                    found.append((name, container.name, item))
    return found


class TestKeys(unittest.TestCase):

    def test_all_four_keys_are_hidden_every_game(self):
        for seed in range(300):
            game, _ = new_game(seed=seed)
            keys = all_keys(game)
            with self.subTest(seed=seed):
                self.assertEqual(sorted(k for _, _, k in keys), sorted(data.KEY_TYPES))
                self.assertEqual(len({(r, c) for r, c, _ in keys}), 4, 'two keys in one container')
                for room, _, _ in keys:
                    self.assertNotIn(room, data.KEY_FREE_ROOMS)

    def test_only_real_keys_count_as_keys(self):
        game, _ = new_game()
        game.player.loots(['Monkey paw', 'Brass key', 'Turkey leg'])
        self.assertEqual(game.player.number_of_keys, 1)


class TestLooting(unittest.TestCase):

    def test_ammo_goes_to_the_ammo_count(self):
        game, _ = new_game()
        player = game.player
        player.loots(['Shotgun shell', 'Bullet', 'Bullet', 'Dusty duster'])
        self.assertEqual((player.shells, player.bullets), (1, data.STARTING_BULLETS + 2))
        self.assertIn('Dusty duster', game.backpack.contents)
        self.assertNotIn('Bullet', game.backpack.contents)

    def test_searched_objects_disappear(self):
        game, _ = new_game(['p', 'r', 's', 'y'])
        with mock.patch('random.randrange', return_value=99):      # no traps
            game.player.explores()
        foyer = game.rooms['Foyer']
        self.assertEqual([c.name for c in foyer.unsearched()], ['Wardrobe'])

    def test_colors(self):
        game, ui = new_game()
        box = Container('Box', game.ui)
        for item in ['Brass key', 'Bandage', 'Bullet', 'Dusty duster']:
            box.add(item)
        box.contains()
        text = ui.text().split('Box contains:')[1]
        self.assertIn('\033[93mBrass key', text)      # yellow
        self.assertIn('\033[94mBandage', text)        # blue
        self.assertIn('\033[91mBullet', text)         # red
        self.assertIn('  Dusty duster', text)
        self.assertNotIn('yellow', text)


class TestTraps(unittest.TestCase):

    def test_trap_name_matches_its_damage(self):
        game, ui = new_game()
        for i in range(300):
            game.player.HP, game.player.alive = 999, 1
            before = len(ui.transcript)
            Container('Box', game.ui).is_trapped(game.player)
            lines = ui.transcript[before:]
            trap = [t for t in data.TRAPS for line in lines if line.strip() == '* ' + t + '! *']
            hit = [line for line in lines if 'You are hit and take' in line]
            if trap and hit:
                self.assertIn('take %d damage' % data.TRAPS[trap[0]], hit[0])

    def test_a_trap_can_kill(self):
        game, _ = new_game()
        game.player.HP = 1
        with mock.patch('random.randrange', side_effect=[1, 14]), mock.patch('random.choice', return_value='Explosion'):
            Container('Box', game.ui).is_trapped(game.player)
        self.assertFalse(game.player.alive)
        self.assertEqual(game.player.in_house, 0)


class TestItems(unittest.TestCase):

    def use(self, item_letter, backpack, **player_state):
        game, ui = new_game([item_letter])
        game.backpack.contents.extend(backpack)
        for k, v in player_state.items():
            setattr(game.player, k, v)
        game.player.uses_item()
        return game, ui

    def test_bandage_heals_but_not_above_max(self):
        game, _ = self.use('b', ['Bandage'], HP=10)
        self.assertTrue(16 <= game.player.HP <= 22)
        game, _ = self.use('b', ['Bandage'], HP=49)
        self.assertEqual(game.player.HP, data.PLAYER_HP)
        self.assertNotIn('Bandage', game.backpack.contents)

    def test_hardtack_heals_two(self):
        game, _ = self.use('h', ['Hardtack'], HP=30)
        self.assertEqual(game.player.HP, 32)

    def test_antidote_cures_poison(self):
        game, _ = self.use('a', ['Antidote'], condition='Poisoned')
        self.assertEqual(game.player.condition, 'Stable')
        game, ui = self.use('a', ['Antidote'])
        self.assertIn('tastes funny', ui.text())

    def test_flashbang_outside_combat_only_dazes_you(self):
        game, ui = self.use('f', ['Flashbang'])
        self.assertIn('momentarily dazed', ui.text())
        self.assertNotIn('Flashbang', game.backpack.contents)

    def test_the_vial_kills(self):
        game, ui = self.use('m', ['Mysterious glass vial'], in_room=1)
        self.assertFalse(game.player.alive)
        self.assertEqual((game.player.in_house, game.player.in_room), (0, 0))

    def test_typing_m_without_the_vial_is_harmless(self):
        game, ui = self.use('m', [])
        self.assertTrue(game.player.alive)
        self.assertIn('Item not usable', ui.text())

    def test_usable_flag_resets_when_items_run_out(self):
        game, _ = new_game()
        game.backpack.add('Bandage')
        game.player.checks_usables()
        self.assertTrue(game.player.has_usables)
        game.backpack.remove('Bandage')
        game.player.checks_usables()
        self.assertFalse(game.player.has_usables)


class TestPoison(unittest.TestCase):

    def test_moldy_hallway_poisons(self):
        game, ui = new_game(['r'])
        game.player.location = 'Moldy hallway'
        game.player.explores()
        self.assertEqual(game.player.condition, 'Poisoned')
        self.assertEqual(game.player.HP, data.PLAYER_HP - 3, 'leaving the room costs 3 HP')

    def test_poison_can_kill(self):
        game, ui = new_game(['r'])
        game.player.condition, game.player.HP = 'Poisoned', 2
        game.player.explores()
        self.assertFalse(game.player.alive)
        self.assertIn('Tester, you succumb', ui.text())


class TestDoors(unittest.TestCase):

    def test_laboratory_needs_the_crowbar(self):
        game, ui = new_game(['e', 'n'])
        game.player.location = 'Short hallway'
        game.player.moves()
        self.assertIn('nailed shut', ui.text())
        self.assertEqual(game.player.location, 'Kitchen')
        game, ui = new_game(['e'])
        game.player.location = 'Short hallway'
        game.backpack.add('Crowbar')
        game.player.moves()
        self.assertEqual(game.player.location, 'Laboratory')
        self.assertIn('Laboratory', game.opened_doors)

    def test_ball_room_needs_the_crowbar(self):
        game, ui = new_game(['w', 'e'])
        game.player.location = 'Drawing room'
        game.player.moves()
        self.assertIn('jammed', ui.text())
        self.assertEqual(game.player.location, 'Grand hall')

    def test_safe_needs_four_keys(self):
        game, ui = new_game(['n', 'w'])
        game.player.location = 'Vault'
        game.player.number_of_keys = 3
        game.player.moves()
        self.assertIn('missing the necessary keys', ui.text())
        game, ui = new_game(['n'])
        game.player.location = 'Vault'
        game.player.number_of_keys = 4
        game.player.moves()
        self.assertEqual(game.player.location, 'Safe')

    def test_walls_and_railings_stop_you(self):
        game, ui = new_game(['s', 'n'])
        game.player.location = 'Gallery SE'
        game.player.moves()
        self.assertIn('You bump into a wall', ui.text())
        self.assertEqual(game.player.location, 'Gallery E')
        game, ui = new_game(['w', 'n'])
        game.player.location = 'Gallery E'
        game.player.moves()
        self.assertIn('railings prevent you', ui.text())
        self.assertEqual(game.player.location, 'Gallery NE')


class TestGoodDeeds(unittest.TestCase):

    def enter(self, room, backpack):
        game, ui = new_game()
        game.backpack.contents.extend(backpack)
        game.rooms[room].is_entered(game)
        return game, ui

    def test_lord_and_lady_durst(self):
        game, _ = self.enter('Master bedroom', ['Severed head of lady Durst', 'Remains of Catherine Durst', 'Diamond ring'])
        self.assertEqual(game.player.deeds, 1)
        self.assertEqual(game.treasures(), ['Diamond ring'], 'quest items are used up')

    def test_benjamin(self):
        game, _ = self.enter('Childrens bedroom', ['Photograph of Benjamin Durst', 'Brown teddy bear'])
        self.assertEqual(game.player.deeds, 1)
        self.assertEqual(game.treasures(), [])

    def test_the_caged_beast(self):
        game, ui = self.enter('Storage room', ['Crowbar', 'Appetizing thighbone'])
        self.assertEqual(game.player.deeds, 1)
        self.assertNotIn('missing a crucial item', ui.text())
        self.assertEqual(game.treasures(), ['Crowbar'], 'the bone is used up, the crowbar kept')

    def test_beast_with_crowbar_but_no_bone(self):
        game, ui = self.enter('Storage room', ['Crowbar'])
        self.assertEqual(game.player.deeds, 0)
        self.assertIn('starving beast still inside', ui.text())

    def test_missing_items(self):
        for room in ['Master bedroom', 'Childrens bedroom', 'Storage room']:
            with self.subTest(room=room):
                game, ui = self.enter(room, [])
                self.assertEqual(game.player.deeds, 0)
                self.assertIn('missing a crucial item', ui.text())

    def test_a_deed_counts_only_once(self):
        game, _ = self.enter('Master bedroom', ['Severed head of lady Durst', 'Remains of Catherine Durst'])
        game.backpack.contents.extend(['Severed head of lady Durst', 'Remains of Catherine Durst'])
        game.rooms['Master bedroom'].is_entered(game)
        self.assertEqual(game.player.deeds, 1)


class TestMonsters(unittest.TestCase):

    def test_monsters_never_repeat_except_the_generic_villain(self):
        game, _ = new_game(['f'] * 100)
        names = [ambush(game, game.rooms['Foyer']).name for _ in range(40)]
        others = [n for n in names if n != data.REPEATABLE_CREATURE]
        self.assertEqual(len(others), len(set(others)))
        self.assertEqual(len(others), len(data.CREATURES) - 1, 'every creature shows up before running out')

    def test_initiative_is_a_d20(self):
        game, _ = new_game()
        random.seed(5)
        rolls = [game.player.rolls_initiative() for _ in range(3000)]
        self.assertEqual((min(rolls), max(rolls)), (1, 20))


if __name__ == '__main__':
    unittest.main()
