"""The parts of the graphical interface that don't need a window, so they can be tested.

- snapshot(game): everything the panels show, as plain values, read from the game's state.
- GuiBridge: the UI the game talks to when it runs inside the window. The game runs in its
  own thread; the bridge passes everything it shows and asks to the window through a queue,
  and waits for the player's answer from the window.
- hint(...): the short "what can I type now" line under the game screen.
"""
import queue
import traceback

from . import data
from .ui import UI

DIRECTION_ORDER = ['NORTH', 'EAST', 'SOUTH', 'WEST']


def exit_info(game, target):
    """How an exit looks on the compass: (status, label).

    status is one of: open, locked, unlockable, wall, railing, outside
    """
    if target == 'Wall':
        return 'wall', 'wall'
    if target == 'Railing':
        return 'railing', 'railing'
    if target == 'Outside':
        return 'outside', 'Front door'
    need = data.LOCKED_DOORS.get(target)
    if need and target not in game.opened_doors:
        if need == 'keys':
            have = game.player is not None and game.player.number_of_keys >= data.KEYS_NEEDED
            return ('unlockable' if have else 'locked'), target + ' (needs 4 keys)'
        have = game.backpack is not None and need in game.backpack.contents
        return ('unlockable' if have else 'locked'), target + ' (needs ' + need.lower() + ')'
    return 'open', target


def snapshot(game, combat=None):
    """Plain values describing the game right now, for the panels."""
    player = game.player
    if player is None:
        return {'started': False}
    room = game.rooms[player.location]
    names = list(data.ROOMS[room.name]['containers'])
    bag = game.backpack.contents
    return {
        'started': True,
        'room': room.name,
        'map_code': room.map_code,
        'description': room.description.strip('\n'),
        'objects': [(name, room.objects[i] is None) for i, name in enumerate(names)],
        'exits': [(d,) + exit_info(game, room.exits[d]) for d in DIRECTION_ORDER],
        'name': player.name,
        'hp': max(player.HP, 0),
        'max_hp': player.maxHP,
        'condition': player.condition,
        'weapon': player.weapon or 'none yet',
        'bullets': player.bullets,
        'shells': player.shells,
        'keys': player.number_of_keys,
        'deeds': player.deeds,
        'kills': player.kills,
        'consumables': [(item, bag.count(item)) for item in data.USABLE_ITEMS if item in bag],
        'treasure': len(game.treasures()),
        'in_room': bool(player.in_room),
        'fighting': bool(player.fighting),
        'alive': bool(player.alive),
        'combat': combat,
    }


class GameAbandoned(Exception):
    """Raised inside the game thread when the window starts a new game, so the old one stops."""


ABANDON = object()      # put into from_window to stop a game that is waiting for an answer


class GuiBridge(UI):
    """The UI the game uses inside the window. It runs in the game's thread.

    to_window:   messages for the window: ('show', text, snapshot), ('ask', prompt, snapshot),
                 ('end', None, snapshot), ('error', traceback text, None)
    from_window: the player's answers (or ABANDON)
    """

    def __init__(self):
        self.game = None
        self.to_window = queue.Queue()
        self.from_window = queue.Queue()
        self.combat = None          # the current or last fight, see track_combat()

    def snap(self):
        return snapshot(self.game, dict(self.combat, log=list(self.combat['log'])) if self.combat else None)

    def show(self, *parts):
        text = ' '.join(str(p) for p in parts)
        self.track_combat(text)
        self.to_window.put(('show', text, self.snap()))

    def ask(self, prompt=''):
        self.to_window.put(('ask', prompt, self.snap()))
        answer = self.from_window.get()
        if answer is ABANDON:
            raise GameAbandoned()
        return answer

    def finished(self):
        self.to_window.put(('end', None, self.snap()))

    def run(self, game):
        """Runs a whole game (call this in the game thread). Errors are sent to the window
        instead of disappearing with the thread."""
        self.game = game
        try:
            game.run()
        except GameAbandoned:
            return
        except Exception:
            self.to_window.put(('error', traceback.format_exc(), None))
            return
        self.finished()

    def track_combat(self, text):
        """Follows the fight from what the game says, for the combat panel."""
        if 'you are attacked by a ' in text:
            monster = text.split('you are attacked by a ', 1)[1].rstrip('.')
            self.combat = {'monster': monster, 'round': 0, 'log': [], 'result': None,
                           'monster_hp': data.MONSTER_HP, 'monster_max_hp': data.MONSTER_HP}
            return
        fight = self.combat
        if fight is None or fight['result'] is not None:
            return
        line = text.strip()
        if not line or line.startswith(('You have the following weapons', '  ')) or line in data.WEAPONS:
            return
        if 'rolls for initiative:' in line:
            fight['round'] += 1
            line = 'Round %d - %s' % (fight['round'], line.strip('* '))
        fight['log'] = (fight['log'] + [line.strip('* ').strip()])[-7:]
        monster = self.game.monster
        if monster is not None:
            fight['monster_hp'] = max(monster.HP, 0)
        if fight['monster'] + ' is dead' in line:
            fight['result'] = 'won'
        elif 'you are dead' in line or 'taste death' in line:
            fight['result'] = 'lost'


def hint(prompt, snap):
    """A short line telling the player what they can type right now."""
    p = prompt.strip()
    if not snap.get('started'):
        return 'Type your name and press Enter.'
    if 'Press Enter' in p:
        return 'Press Enter to finish.'
    if 'Which weapon' in p:
        options = ['F fists', 'A axe']
        if snap['bullets']:
            options.append('R revolver (%d)' % snap['bullets'])
        if snap['shells']:
            options.append('S shotgun (%d)' % snap['shells'])
        return 'Choose a weapon: ' + ' | '.join(options)
    if 'Fight or Use' in p:
        return 'F fight | U use an item'
    if 'Select item' in p:
        letters = ['%s %s' % (item[0], item.lower()) for item, _ in snap['consumables']]
        return ' | '.join(letters + ['P check stats', 'C close the backpack'])
    if 'direction' in p or 'Where do you want' in p:
        open_dirs = [d[0] for d, status, _ in snap['exits'] if status in ('open', 'unlockable', 'outside')]
        return 'Move: ' + ', '.join(open_dirs) + '  (or click an exit)'
    if snap['in_room'] or 'chills' in p:
        objects = ['%s %s' % (name[0], name) for name, searched in snap['objects'] if not searched]
        rest = ['B backpack', 'R move on', 'E escape the house']
        return ' | '.join(objects + rest)
    if not p and not snap['in_room']:
        return 'Y to leave the house, anything else to stay.'
    return ''
