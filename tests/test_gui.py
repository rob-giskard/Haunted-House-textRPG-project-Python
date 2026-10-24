"""Checks the graphical interface.

Most of it is tested without opening a window: what the panels show (snapshot), the bridge
between the window and the game thread, and the hint line. The last test opens a hidden
window and plays the whole walkthrough through it; it is skipped where no display or no
tkinter is available.
"""
import queue
import threading
import time
import unittest

from helpers import data, new_game, read_walkthrough
from haunted_house.game import Game
from haunted_house.gui_state import ABANDON, GuiBridge, hint, snapshot


def exits_of(snap):
    return {direction: (status, label) for direction, status, label in snap['exits']}


class TestSnapshot(unittest.TestCase):

    def test_before_the_name_is_typed(self):
        game = Game(ui=GuiBridge(), seed=1)
        self.assertEqual(snapshot(game), {'started': False})

    def test_room_objects_and_exits(self):
        game, _ = new_game()
        snap = snapshot(game)
        self.assertEqual(snap['room'], 'Foyer')
        self.assertEqual(snap['objects'], [('Painting of lady and lord Durst', False), ('Wardrobe', False)])
        exits = exits_of(snap)
        self.assertEqual(exits['NORTH'], ('open', 'Grand hall'))
        self.assertEqual(exits['SOUTH'], ('outside', 'Front door'))
        self.assertEqual(exits['EAST'][0], 'wall')

    def test_searched_objects_are_marked(self):
        game, _ = new_game()
        game.rooms['Foyer'].objects[1] = None
        self.assertEqual(snapshot(game)['objects'][1], ('Wardrobe', True))

    def test_locked_doors(self):
        game, _ = new_game()
        game.player.location = 'Short hallway'
        self.assertEqual(exits_of(snapshot(game))['EAST'][0], 'locked')
        game.backpack.add('Crowbar')
        self.assertEqual(exits_of(snapshot(game))['EAST'], ('unlockable', 'Laboratory (needs crowbar)'))
        game.opened_doors.add('Laboratory')
        self.assertEqual(exits_of(snapshot(game))['EAST'], ('open', 'Laboratory'))

    def test_the_safe_needs_keys(self):
        game, _ = new_game()
        game.player.location = 'Vault'
        self.assertEqual(exits_of(snapshot(game))['NORTH'][0], 'locked')
        game.player.number_of_keys = data.KEYS_NEEDED
        self.assertEqual(exits_of(snapshot(game))['NORTH'][0], 'unlockable')

    def test_railings(self):
        game, _ = new_game()
        game.player.location = 'Gallery E'
        self.assertEqual(exits_of(snapshot(game))['WEST'][0], 'railing')

    def test_consumables_are_counted(self):
        game, _ = new_game()
        game.backpack.contents.extend(['Bandage', 'Rusty nail', 'Bandage', 'Antidote'])
        self.assertEqual(snapshot(game)['consumables'], [('Bandage', 2), ('Antidote', 1)])


class TestBridge(unittest.TestCase):

    def test_plays_the_walkthrough_through_the_bridge(self):
        seed, commands = read_walkthrough()
        bridge = GuiBridge()
        game = Game(ui=bridge, seed=seed)
        thread = threading.Thread(target=bridge.run, args=(game,), daemon=True)
        thread.start()
        answers = iter(commands + [''])
        fights, last = [], None
        while True:
            kind, text, snap = bridge.to_window.get(timeout=10)
            last = snap
            if kind == 'ask':
                bridge.from_window.put(next(answers))
            fight = snap.get('combat') if snap.get('started') else None
            if fight and fight['result'] and (not fights or fights[-1] != fight['monster']):
                fights.append(fight['monster'])
            if kind == 'end':
                break
        thread.join(timeout=5)
        self.assertFalse(thread.is_alive())
        self.assertEqual((last['keys'], last['deeds'], last['alive']), (4, 3, True))
        self.assertEqual(len(fights), 5, 'the combat panel followed every fight')

    def test_a_waiting_game_can_be_abandoned(self):
        bridge = GuiBridge()
        thread = threading.Thread(target=bridge.run, args=(Game(ui=bridge, seed=1),), daemon=True)
        thread.start()
        self.assertEqual(bridge.to_window.get(timeout=5)[0], 'show')
        bridge.from_window.put(ABANDON)
        thread.join(timeout=5)
        self.assertFalse(thread.is_alive())

    def test_errors_reach_the_window(self):
        bridge = GuiBridge()
        game = Game(ui=bridge, seed=1)
        game.intro = lambda: 1 / 0
        bridge.run(game)
        messages = []
        while not bridge.to_window.empty():
            messages.append(bridge.to_window.get())
        self.assertEqual(messages[-1][0], 'error')
        self.assertIn('ZeroDivisionError', messages[-1][1])

    def test_combat_tracking(self):
        game, _ = new_game()
        bridge = GuiBridge()
        bridge.game = game
        bridge.track_combat('\n    After entering the kitchen, you are attacked by a Batswarm.')
        self.assertEqual(bridge.combat['monster'], 'Batswarm')
        bridge.track_combat('\n * Tester rolls for initiative: 12. *')
        bridge.track_combat(' * Batswarm is dead. *')
        self.assertEqual(bridge.combat['round'], 1)
        self.assertEqual(bridge.combat['result'], 'won')
        self.assertIn('Round 1 - Tester rolls for initiative: 12.', bridge.combat['log'])


class TestHints(unittest.TestCase):

    def setUp(self):
        self.game, _ = new_game()
        self.game.player.in_room = 1

    def hint(self, prompt):
        return hint(prompt, snapshot(self.game))

    def test_room_choices(self):
        self.assertEqual(self.hint(''), 'P Painting of lady and lord Durst | W Wardrobe | B backpack | R move on | E escape the house')

    def test_directions_list_only_open_exits(self):
        self.game.player.in_room = 0
        self.assertTrue(self.hint('Choose a direction to move to.').startswith('Move: N, S'))

    def test_weapons_show_ammo(self):
        self.assertIn('R revolver (6)', self.hint('Which weapon to use?'))
        self.assertNotIn('shotgun', self.hint('Which weapon to use?'))

    def test_items_list_what_is_in_the_backpack(self):
        self.game.backpack.add('Bandage')
        self.assertTrue(self.hint('\nSelect item to use, check PST or Close the backpack.').startswith('B bandage'))

    def test_name_and_end(self):
        game = Game(ui=GuiBridge(), seed=1)
        self.assertIn('name', hint('', snapshot(game)))
        self.assertIn('Enter', self.hint('\n    Press Enter to leave the haunted house...'))


def hidden_window(test):
    try:
        import tkinter as tk
        root = tk.Tk()
    except Exception as error:          # no tkinter, or no display
        test.skipTest('no window available: %s' % error)
    root.withdraw()
    return root


def run_until(root, condition, seconds=60):
    deadline = time.time() + seconds
    while not condition() and time.time() < deadline:
        root.update()
        time.sleep(0.002)


class TestWindow(unittest.TestCase):
    """Opens hidden windows and plays games through them."""

    def test_autoplay_in_the_window(self):
        root = hidden_window(self)
        try:
            from haunted_house.gui import HauntedHouseApp
            from haunted_house.walkthrough import DEFAULT_PATH
            app = HauntedHouseApp(root, autoplay=DEFAULT_PATH, delay=0)
            run_until(root, lambda: app.auto_commands is None and app.prompt is not None and 'Press Enter' in app.prompt)
            log = app.log.get('1.0', 'end')
            self.assertIn('Walkthrough finished', log)
            self.assertIn('Enter', app.hint_label.cget('text'), 'the hint goes back to normal after autoplay')
            self.assertIn('Good deeds:        3/3', log)
        finally:
            root.destroy()

    def test_new_game_button_starts_over(self):
        root = hidden_window(self)
        try:
            from haunted_house.gui import HauntedHouseApp
            app = HauntedHouseApp(root, seed=1)
            run_until(root, lambda: app.prompt is not None)
            first = app.bridge
            app.restart()
            run_until(root, lambda: app.prompt is not None)
            self.assertIsNot(app.bridge, first)
            self.assertNotIn('Tester', app.log.get('1.0', 'end'))
            self.assertIn('How would you like to be addressed', app.log.get('1.0', 'end'))
        finally:
            root.destroy()

    def test_walkthrough_typed_in_the_window(self):
        root = hidden_window(self)
        try:
            from haunted_house.gui import HauntedHouseApp
            seed, commands = read_walkthrough()
            app = HauntedHouseApp(root, seed=seed)
            answers = list(commands) + ['']
            deadline = time.time() + 60
            while not app.game_over and time.time() < deadline:
                root.update()
                if app.prompt is not None and answers:
                    app.entry.insert(0, answers.pop(0))
                    app.submit()
            self.assertTrue(app.game_over, 'the game did not finish in the window')
            log = app.log.get('1.0', 'end')
            self.assertIn('FINAL STATS', log)
            self.assertIn('FOYER', app.room_text.get('1.0', 'end'))
            self.assertIn('3/3', app.gear_text.get('1.0', 'end'))
        finally:
            root.destroy()


if __name__ == '__main__':
    unittest.main()
