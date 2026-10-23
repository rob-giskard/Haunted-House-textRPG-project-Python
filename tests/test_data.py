"""Checks that the game content in haunted_house/data.py is consistent and completable."""
import io
import unittest
from contextlib import redirect_stdout

from helpers import data

OPPOSITE = {'NORTH': 'SOUTH', 'SOUTH': 'NORTH', 'EAST': 'WEST', 'WEST': 'EAST'}
STEP = {'NORTH': (-1, 0), 'SOUTH': (1, 0), 'EAST': (0, 1), 'WEST': (0, -1)}
NOT_ROOMS = ('Wall', 'Railing', 'Outside')


class TestRooms(unittest.TestCase):

    def test_there_are_25_rooms(self):
        self.assertEqual(len(data.ROOMS), 25)

    def test_every_room_has_all_fields(self):
        for name, room in data.ROOMS.items():
            with self.subTest(room=name):
                self.assertEqual(set(room), {'map_code', 'position', 'description', 'exits', 'containers'})
                self.assertEqual(set(room['exits']), set(OPPOSITE))
                self.assertTrue(room['description'].strip())

    def test_exits_lead_somewhere_real(self):
        for name, room in data.ROOMS.items():
            for direction, target in room['exits'].items():
                with self.subTest(room=name, direction=direction):
                    self.assertTrue(target in data.ROOMS or target in NOT_ROOMS, target)

    def test_doors_work_both_ways(self):
        for name, room in data.ROOMS.items():
            for direction, target in room['exits'].items():
                if target in data.ROOMS:
                    with self.subTest(room=name, direction=direction):
                        self.assertEqual(data.ROOMS[target]['exits'][OPPOSITE[direction]], name)

    def test_neighbours_are_next_to_each_other_on_the_plan(self):
        for name, room in data.ROOMS.items():
            _, row, col = room['position']
            for direction, target in room['exits'].items():
                if target in data.ROOMS:
                    _, row2, col2 = data.ROOMS[target]['position']
                    dr, dc = STEP[direction]
                    with self.subTest(room=name, direction=direction):
                        self.assertEqual((row + dr, col + dc), (row2, col2))

    def test_positions_are_unique_and_on_the_grid(self):
        seen = {}
        for name, room in data.ROOMS.items():
            floor, row, col = room['position']
            with self.subTest(room=name):
                self.assertIn(floor, (1, 2))
                self.assertTrue(0 <= row < 7 and 0 <= col < 7)
                self.assertNotEqual((row, col), (0, 0), 'cell 0,0 holds the floor label')
                self.assertNotIn(room['position'], seen, 'same spot as ' + seen.get(room['position'], ''))
            seen[room['position']] = name

    def test_map_codes_fit_the_plan(self):
        codes = [room['map_code'] for room in data.ROOMS.values()]
        self.assertEqual(len(codes), len(set(codes)))
        for code in codes:
            self.assertLessEqual(len(code), 5)

    def test_exactly_one_way_out(self):
        exits = [(n, d) for n, r in data.ROOMS.items() for d, t in r['exits'].items() if t == 'Outside']
        self.assertEqual(exits, [(data.START_ROOM, 'SOUTH')])


class TestContainers(unittest.TestCase):

    def test_at_most_four_objects_per_room(self):
        for name, room in data.ROOMS.items():
            with self.subTest(room=name):
                self.assertLessEqual(len(room['containers']), 4)

    def test_object_letters_are_unique_and_not_reserved(self):
        for name, room in data.ROOMS.items():
            letters = [c[0].lower() for c in room['containers']]
            with self.subTest(room=name):
                self.assertEqual(len(letters), len(set(letters)), letters)
                for letter in letters:
                    self.assertNotIn(letter, 'bre', 'B, R and E are Backpack, Room and Escape')

    def test_no_item_is_mistaken_for_a_key(self):
        for room in data.ROOMS.values():
            for items in room['containers'].values():
                for item in items:
                    self.assertFalse(item.endswith(' key'), item + ' would count as a vault key')

    def test_quest_items_exist(self):
        all_items = [i for r in data.ROOMS.values() for items in r['containers'].values() for i in items]
        for item in ['Severed head of lady Durst', 'Remains of Catherine Durst', 'Photograph of Benjamin Durst',
                     'Brown teddy bear', 'Crowbar', 'Appetizing thighbone', 'Antidote', 'Bandage']:
            with self.subTest(item=item):
                self.assertIn(item, all_items)

    def test_house_can_be_completed(self):
        """Walks the house like a player would: the crowbar must be reachable without the crowbar,
        and with it every room except the Safe (which needs the keys) must be reachable."""
        def reachable(have_crowbar, have_keys):
            seen, todo = {data.START_ROOM}, [data.START_ROOM]
            while todo:
                for target in data.ROOMS[todo.pop()]['exits'].values():
                    if target not in data.ROOMS or target in seen:
                        continue
                    if target in ('Laboratory', 'Ball room') and not have_crowbar:
                        continue
                    if target == 'Safe' and not have_keys:
                        continue
                    seen.add(target)
                    todo.append(target)
            return seen

        start = reachable(False, False)
        crowbar_rooms = [n for n, r in data.ROOMS.items() if any('Crowbar' in i for i in r['containers'].values())]
        self.assertTrue(set(crowbar_rooms) & start, 'the crowbar is locked behind a crowbar door')
        self.assertEqual(reachable(True, False), set(data.ROOMS) - {'Safe'})
        self.assertEqual(reachable(True, True), set(data.ROOMS))
        key_rooms = [n for n in reachable(True, False) if n not in data.KEY_FREE_ROOMS and data.ROOMS[n]['containers']]
        self.assertGreaterEqual(sum(len(data.ROOMS[n]['containers']) for n in key_rooms), len(data.KEY_TYPES))


class TestOtherContent(unittest.TestCase):

    def test_weapons_have_sensible_damage(self):
        for weapon, (low, high) in data.WEAPONS.items():
            with self.subTest(weapon=weapon):
                self.assertLessEqual(1, low)
                self.assertLessEqual(low, high)

    def test_creatures_are_unique(self):
        self.assertEqual(len(data.CREATURES), len(set(data.CREATURES)))
        self.assertIn(data.REPEATABLE_CREATURE, data.CREATURES)

    def test_four_different_keys(self):
        self.assertEqual(len(set(data.KEY_TYPES)), data.KEYS_NEEDED)
        for key in data.KEY_TYPES:
            self.assertTrue(key.endswith(' key'))

    def test_house_plan_shows_every_room(self):
        import HousePlan
        out = io.StringIO()
        with redirect_stdout(out):
            house = HousePlan.House()
            print(house.drawFloor1())
            print(house.drawFloor2())
        for room in data.ROOMS.values():
            self.assertIn(room['map_code'], out.getvalue())


if __name__ == '__main__':
    unittest.main()
