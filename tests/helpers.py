"""Shared tools for the tests: scripted games, a bot that plays sensibly, and game statistics."""
import os
import sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from haunted_house import data                      # noqa: E402
from haunted_house.game import Game                 # noqa: E402
from haunted_house.ui import ScriptedUI, UI         # noqa: E402
from haunted_house.walkthrough import read_walkthrough as _read_walkthrough  # noqa: E402

WALKTHROUGH = os.path.join(ROOT, 'walkthrough.txt')
DIRECTIONS = {'NORTH': 'n', 'SOUTH': 's', 'EAST': 'e', 'WEST': 'w'}


def new_game(commands=(), seed=1, name='Tester', on_empty='raise'):
    """A game that has finished the intro, ready for unit tests to poke at."""
    ui = ScriptedUI([name] + list(commands), on_empty=on_empty)
    game = Game(ui=ui, seed=seed)
    game.intro()
    return game, ui


def play(commands, seed=1, on_empty=''):
    """Plays a whole game with the given commands. By default an empty answer is given
    once the commands run out, so any game reaches its end (unless it loops forever)."""
    ui = ScriptedUI(commands, on_empty=on_empty)
    game = Game(ui=ui, seed=seed)
    game.run()
    return game, ui


def read_walkthrough(path=WALKTHROUGH):
    return _read_walkthrough(path)


def rooms_visited(transcript_text):
    """Room names from the '# Room #' banners the game prints on entering."""
    found = set()
    for line in transcript_text.splitlines():
        line = line.strip()
        if line.startswith('# ') and line.endswith(' #') and line != '# GAME OVER #':
            found.add(line[2:-2])
    return found


class BotUI(UI):
    """A player that makes sensible choices by looking at the game's state.

    It searches every room, opens locked doors once it can, does the good deeds,
    heals when hurt and leaves when everything is done. It also keeps statistics.
    """

    def __init__(self, max_commands=2000):
        self.game = None
        self.max_commands = max_commands
        self.commands = []
        self.queued_item = []
        self.visited = set()
        self.problems = []          # prompts the bot did not expect (a sign of a bug)
        self.stats = {
            'monsters_met': [], 'killed_by': None, 'death_cause': None,
            'traps_triggered': 0, 'damage_taken': 0, 'last_trap': None,
        }

    # --- what the game shows -------------------------------------------------
    def show(self, *parts):
        text = ' '.join(str(p) for p in parts)
        s = self.stats
        if 'you are attacked by a ' in text:
            s['monsters_met'].append(text.split('you are attacked by a ', 1)[1].rstrip('.'))
        if ' is trapped!' in text:
            s['traps_triggered'] += 1
        for trap in data.TRAPS:
            if text.strip() == '* ' + trap + '! *':
                s['last_trap'] = trap
        if 'You are hit and take ' in text:
            s['damage_taken'] += int(text.split('take ', 1)[1].split(' ')[0])
        if 'you are dead' in text:
            player = self.game.player
            if player.fighting and self.game.monster is not None:
                s['death_cause'], s['killed_by'] = 'monster', self.game.monster.name
            else:
                s['death_cause'] = 'trap'
                s['killed_by'] = s['last_trap']
        if 'you succumb to the toxic substance' in text:
            s['death_cause'], s['killed_by'] = 'poison', 'Mold spores'
        if 'taste death' in text:
            s['death_cause'], s['killed_by'] = 'vial', 'Mysterious glass vial'
        if 'A toxin coursing through your body' in text:
            s['damage_taken'] += 3

    # --- choosing answers ----------------------------------------------------
    def say(self, command):
        self.commands.append(command)
        if len(self.commands) > self.max_commands:
            raise RuntimeError('bot gave up: too many commands')
        return command

    def ask(self, prompt=''):
        game = self.game
        if 'Press Enter' in prompt:
            return self.say('')
        if game.player is None:
            return self.say('Bot')
        player, bag = game.player, game.backpack.contents
        for bad in ('Invalid', 'chills', 'not usable'):
            if bad in prompt:
                self.problems.append(prompt)
        if 'Which weapon' in prompt:
            if player.shells > 0:
                return self.say('s')
            if player.bullets > 0:
                return self.say('r')
            return self.say('a')
        if 'Fight or Use' in prompt:
            if player.HP <= 10 and 'Bandage' in bag:
                self.queued_item.append('b')
                return self.say('u')
            return self.say('f')
        if 'Select item' in prompt:
            return self.say(self.queued_item.pop(0) if self.queued_item else 'c')
        if 'Choose a direction' in prompt:
            return self.say(self.next_direction())
        if prompt == '' and not player.in_room and not player.fighting:
            return self.say('y')        # the front door: only reached when everything is done
        if prompt == '' and player.in_room:
            return self.say(self.room_choice())
        self.problems.append(prompt)
        return self.say('c')

    def room_choice(self):
        game, player = self.game, self.game.player
        bag = game.backpack.contents
        room = game.rooms[player.location]
        self.visited.add(room.name)
        heal = player.HP <= 25 and ('Bandage' in bag or 'Hardtack' in bag)
        cure = player.condition == 'Poisoned' and 'Antidote' in bag and player.HP <= 40
        if heal or cure:
            if cure:
                self.queued_item.append('a')
            elif 'Bandage' in bag:
                self.queued_item.append('b')
            else:
                self.queued_item.append('h')
            return 'b'
        left = room.unsearched()
        if left:
            return left[0].name[0].lower()
        return 'r'

    # --- route finding -------------------------------------------------------
    def can_enter(self, target):
        game, bag = self.game, self.game.backpack.contents
        if target not in game.rooms:
            return False
        if target in ('Laboratory', 'Ball room') and target not in game.opened_doors:
            return 'Crowbar' in bag
        if target == 'Safe' and target not in game.opened_doors:
            return game.player.number_of_keys >= data.KEYS_NEEDED
        return True

    def paths(self, start):
        previous = {start: None}
        queue = deque([start])
        while queue:
            here = queue.popleft()
            for direction, target in self.game.rooms[here].exits.items():
                if target not in previous and self.can_enter(target):
                    previous[target] = (here, direction)
                    queue.append(target)
        return previous

    def deed_ready(self, name):
        game, bag = self.game, self.game.backpack.contents
        room = game.rooms[name]
        if room.solved:
            return False
        if name == 'Master bedroom':
            return 'Severed head of lady Durst' in bag and 'Remains of Catherine Durst' in bag
        if name == 'Childrens bedroom':
            return 'Photograph of Benjamin Durst' in bag and 'Brown teddy bear' in bag
        if name == 'Storage room':
            return 'Crowbar' in bag and 'Appetizing thighbone' in bag
        return False

    def next_direction(self):
        here = self.game.player.location
        previous = self.paths(here)

        def distance(room):
            steps = 0
            while previous[room]:
                room = previous[room][0]
                steps += 1
            return steps

        goals = [r for r in previous if r != here and
                 (r not in self.visited or self.game.rooms[r].unsearched() or self.deed_ready(r))]
        if not goals:
            if here == data.START_ROOM:
                return 's'      # everything done: out through the front door
            goals = [data.START_ROOM]
        goal = min(goals, key=distance)
        while previous[goal][0] != here:
            goal = previous[goal][0]
        return DIRECTIONS[previous[goal][1]]


def bot_game(seed):
    """Lets the bot play one game. Returns a dict describing how it went."""
    ui = BotUI()
    game = Game(ui=ui, seed=seed)
    ui.game = game
    game.run()
    player = game.player
    all_searched = all(not room.unsearched() for room in game.rooms.values())
    complete = (bool(player.alive) and player.deeds == 3 and
                player.number_of_keys == data.KEYS_NEEDED and
                ui.visited >= set(game.rooms) and all_searched)
    return {
        'seed': seed,
        'alive': bool(player.alive),
        'complete': complete,
        'commands': len(ui.commands),
        'final_hp': max(player.HP, 0),
        'kills': player.kills,
        'keys': player.number_of_keys,
        'deeds': player.deeds,
        'treasure': len(game.treasures()),
        'rooms_visited': len(ui.visited),
        'problems': ui.problems,
        **ui.stats,
    }
