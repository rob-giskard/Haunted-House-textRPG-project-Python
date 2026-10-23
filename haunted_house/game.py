"""The game itself: sets up a fresh house, runs the main loop and shows the ending."""
import random

from . import data
from .combat import ambush, combat
from .entities import Player
from .ui import ConsoleUI
from .world import Container, build_rooms, hide_keys


class Game:
    """Everything one playthrough needs, in one place (no global variables).

    ui:   where the game shows text and reads answers (see ui.py); the console by default.
    seed: optional number that fixes the dice, so the same inputs give the same game.
    """

    def __init__(self, ui=None, seed=None):
        self.ui = ui if ui is not None else ConsoleUI()
        if seed is not None:
            random.seed(seed)
        self.rooms = build_rooms(self.ui)
        self.creatures = list(data.CREATURES)   # each creature is removed once it has appeared
        self.opened_doors = set()               # locked doors the player has opened
        self.monster = None                     # the monster currently fighting the player
        self.player = None
        self.backpack = None
        hide_keys(self.rooms)

    def run(self):
        self.intro()
        player = self.player
        while player.in_house and player.alive:
            player.explores()
            if not player.in_house:
                break
            player.moves()
            if not player.in_house:
                break
            if random.randrange(1, 100) < 20:
                monster = ambush(self, self.rooms[player.location])
                combat(self, monster)
        self.game_over()

    def intro(self):
        self.ui.show('Barry the Butler says: "Welcome to the haunted house."')
        self.ui.show('Barry the Butler says: "How would you like to be addressed?"')
        player_name = self.ui.ask()
        self.player = Player(self, player_name)
        self.backpack = Container('Backpack', self.ui)
        self.backpack.add(data.STATS_TRACKER)
        self.ui.show('Barry the Butler says: "' + self.player.name + ', the house holds many treasures."')
        self.ui.show('''
Barry the Butler says: "To navigate the premises and carry out actions, just type the capitalized letters.
                        You can choose directions by typing N, S, E or W. Notice that not all items
                        are usable - when inspecting your inventory, usable items will be highlighted."''')

        self.ui.show('''
Barry the Butler says: "And if you're looking for the vault, be warned - you need to collect 4 keys.
                        The keys, while not directly usable, are highlighted in yellow."''')
        self.ui.show('Barry the Butler says: "Enjoy your stay."')
        self.player.in_house = 1

    def treasures(self):
        return [item for item in self.backpack.contents if item != data.STATS_TRACKER]

    def game_over(self):
        # runs after every ending - death, escape or leaving through the front door
        player = self.player
        self.ui.show('\n                               #############')
        self.ui.show('                               # GAME OVER #')
        self.ui.show('                               #############')
        if not player.alive:
            self.ui.show('\n    The house claimed your soul. The treasures remain lost.')
        elif self.treasures():
            self.ui.show('\n    You escaped with the following treasure:\n')
            for item in self.treasures():
                self.ui.show('  ' + item)
        else:
            self.ui.show('\n    Unfortunately, you got out empty-handed.')

        if player.deeds == 0:
            self.ui.show('\n    ' + player.name + ', you accomplished no good deeds in the house.')
            self.ui.show('    There was more to be done, but who said it was your job...')
        elif player.deeds < 3:
            self.ui.show('\n    Good deeds accomplished: ' + str(player.deeds) + '.')
            self.ui.show("    " + player.name + ", the haunted house is still a restless place, but your visit won't be forgotten.")
        else:
            self.ui.show('\n    Congratulations, ' + player.name + '!')
            self.ui.show('''
    You proved hope always prevails. You reunited the lady and lord Durst,
    honored the memory of a troubled child and freed a tortured spirit from its cage.
    Thanks to you, the haunted house will rest in peace.
    ''')

        self.shows_final_stats()
        self.ui.ask('\n    Press Enter to leave the haunted house...')

    def shows_final_stats(self):
        player = self.player
        outcome = 'Escaped the house' if player.alive else 'Perished in the house'
        self.ui.show('\n    ==================== FINAL STATS ====================')
        self.ui.show('    Name:              ' + player.name)
        self.ui.show('    Outcome:           ' + outcome)
        self.ui.show('    Health:            ' + str(max(player.HP, 0)) + '/' + str(player.maxHP))
        self.ui.show('    Condition:         ' + player.condition)
        self.ui.show('    Monsters defeated: ' + str(player.kills))
        self.ui.show('    Keys found:        ' + str(player.number_of_keys) + '/4')
        self.ui.show('    Good deeds:        ' + str(player.deeds) + '/3')
        self.ui.show('    Items collected:   ' + str(len(self.treasures())))
        self.ui.show('    Bullets left:      ' + str(player.bullets) + ' | Shotgun shells left: ' + str(player.shells))
        self.ui.show('    =====================================================')
