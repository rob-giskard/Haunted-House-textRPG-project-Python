"""The house itself: containers to search, rooms to explore, and building them from data.py."""
import random

from . import data
from .colors import colored
from .events import room_event


class Container:
    """Something that holds items: an object in a room, or the player's backpack."""

    def __init__(self, name, ui):
        self.name = name
        self.ui = ui
        self.contents = []

    def contains(self):
        if self.contents != []:
            self.ui.show('\n' + self.name + ' contains:\n')
            for item in self.contents:
                if item.endswith(' key'):
                    self.ui.show('  ' + colored(item, 'yellow'))
                elif any(word in item for word in data.HEALING_ITEMS):
                    self.ui.show('  ' + colored(item, 'blue'))
                elif any(word in item for word in data.COMBAT_ITEMS):
                    self.ui.show('  ' + colored(item, 'red'))
                else:
                    self.ui.show('  ' + item)
        else:
            self.ui.show(self.name, 'is empty.')

    def add(self, item_in):
        self.contents.append(item_in)

    def remove(self, item_out):
        self.contents.remove(item_out)

    def is_looted(self):
        self.contents.clear()

    def is_trapped(self, player):
        # roughly a 60% chance; the trap's attack roll must beat the player's armor to hurt
        if random.randrange(1, 100) < 60:
            self.ui.show('The ' + self.name + ' is trapped!')
            trap = random.choice(list(data.TRAPS.keys()))
            self.ui.show(' * ' + trap + '! *')
            player.is_attacked(trap, random.randrange(10, 15), data.TRAPS[trap])
            if not player.alive:
                player.in_room, player.in_house = 0, 0


class Location:
    """A room of the house, with up to four objects to search."""

    def __init__(self, name, room_data, ui):
        self.name = name
        self.description = room_data['description']
        self.exits = room_data['exits']
        self.position = room_data['position']
        self.map_code = room_data['map_code']
        self.solved = 0
        # objects[i] is a Container, or None once it has been searched
        self.objects = []
        for container_name, items in room_data['containers'].items():
            container = Container(container_name, ui)
            for item in items:
                container.add(item)
            self.objects.append(container)
        # letters the player may type here: each object's first letter, plus Backpack, Room and Escape
        self.letters = [c.name[0].lower() for c in self.objects] + ['b', 'r', 'e']

    def __str__(self):
        return self.name

    def unsearched(self):
        return [c for c in self.objects if c is not None]

    def is_entered(self, game):
        # displays the name of the room and runs the room's special event, if it has one
        game.player.in_room = 1
        game.ui.show('\n                               ##' + len(self.name) * '#' + '##')
        game.ui.show('                               # ' + self.name + ' #')
        game.ui.show('                               ##' + len(self.name) * '#' + '##\n')
        game.ui.show(self.description)
        room_event(game, self)

    def is_explored(self, game):
        player = game.player
        while player.in_room:
            if self.unsearched():
                game.ui.show('\nThe following objects catch your eye:\n')
                for c in self.objects:
                    game.ui.show(c.name if c else '')
                game.ui.show('\nYou can also check your Backpack, push on to another Room or Escape screaming.')
            else:
                game.ui.show('\n    This room seems empty. Want to rummage through your Backpack or explore other Rooms?')
            room_choice = game.ui.ask().lower()
            while room_choice == '' or room_choice[0] not in self.letters:
                room_choice = game.ui.ask('The surrounding space gives you chills. What do you do?').lower()

            for i, container in enumerate(self.objects):
                if container is not None and room_choice[0] == container.name[0].lower():
                    container.is_trapped(player)
                    if not player.alive:
                        player.in_room, player.in_house = 0, 0
                        break
                    container.contains()
                    player.loots(container.contents)
                    container.is_looted()
                    self.objects[i] = None
            if not player.alive:
                break

            if room_choice[0] == 'b':
                player.checks_inventory()
                player.checks_usables()
                if player.has_usables:
                    player.uses_item()
            if room_choice[0] == 'r':
                room_exit_lines = ['\n    You push your luck and face another mystery.',
                                   '\n    You leave the area and journey deeper into the house.',
                                   '\n    Full of hope, you carry on.',
                                   '\n    You continue exploring.',
                                   '\n    Your footsteps echo in the quiet interior.']
                game.ui.show(random.choice(room_exit_lines))
                player.in_room = 0
                if player.condition == 'Poisoned':
                    game.ui.show(colored('\n    A toxin coursing through your body takes its toll. You feel your life energy draining.', 'red'))
                    player.HP -= 3
                    if player.HP <= 0:
                        game.ui.show(' * ' + player.name + ', you succumb to the toxic substance coursing in your veins. *')
                        player.alive = False
                        player.in_house = 0
            if room_choice[0] == 'e':
                player.in_room, player.in_house = 0, 0
                game.ui.show('    Smart. You left the house. Fresh air caresses your face once again.')


def build_rooms(ui):
    """Creates every room from data.ROOMS, in the same order."""
    return {name: Location(name, room, ui) for name, room in data.ROOMS.items()}


def hide_keys(rooms):
    """Puts each key in a different random container, never behind the door the keys open."""
    candidates = []
    for name, room in rooms.items():
        if name in data.KEY_FREE_ROOMS:
            continue
        candidates.extend(room.objects)
    for type_of_key, container in zip(data.KEY_TYPES, random.sample(candidates, len(data.KEY_TYPES))):
        container.add(type_of_key)
