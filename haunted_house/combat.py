"""Random encounters and fights."""
import random

from . import data
from .entities import Entity


def ambush(game, room):
    """A random creature attacks the player in this room. Returns the monster."""
    creature = random.choice(game.creatures)
    if creature != data.REPEATABLE_CREATURE:
        game.creatures.remove(creature)
    monster = Entity(creature, data.MONSTER_HP, data.MONSTER_AC, game.ui)
    game.monster = monster
    game.ui.show('\n    After entering the ' + room.name.lower() + ', you are attacked by a ' + monster.name + '.')
    game.player.fighting = 1
    game.player.chooses_weapon()
    return monster


def weapon_damage(player):
    low, high = data.WEAPONS[player.weapon]
    return random.randint(low, high)


def fire(player):
    if player.weapon == 'Shotgun':
        player.fires_shotgun()
    elif player.weapon == 'Revolver pistol':
        player.fires_pistol()


def monster_strikes(player, monster):
    player.is_attacked(monster.name, random.randint(5, 15), random.randint(2, 10))
    if not player.alive:
        player.fighting, player.in_house = 0, 0


def combat(game, monster):
    """Rounds of combat until the player or the monster is dead."""
    player = game.player
    while player.fighting:
        # out of ammo: the player has to pick another weapon
        if player.weapon == 'Shotgun' and player.shells == 0:
            game.ui.show('You spent all of your shells. Need to quickly swap weapons.')
            player.chooses_weapon()
        if player.weapon == 'Revolver pistol' and player.bullets == 0:
            game.ui.show('You spent all of your bullets. Quickly swapping weapons.')
            player.chooses_weapon()
        # every round starts with initiative
        if int(player.rolls_initiative()) > int(monster.rolls_initiative()):
            game.ui.show('\nYou react faster.')
            # the player won initiative: fight, or use an item
            if game.ui.ask('\nFight or Use item?').lower().startswith('f'):
                monster.is_attacked(13, weapon_damage(player))
                fire(player)
                if not monster.alive:
                    player.fighting = 0
                else:
                    monster_strikes(player, monster)
            else:
                player.checks_usables()
                if player.has_usables:
                    player.uses_item()
                if not player.alive:
                    player.fighting, player.in_house = 0, 0
                elif monster.stunned:
                    # a stunned monster can't fight back, so the player gets a free attack
                    monster.is_attacked(11, weapon_damage(player))
                    monster.stunned = 0
                    fire(player)
                    if not monster.alive:
                        player.fighting = 0
                else:
                    # using an item takes your turn, so the monster strikes
                    monster_strikes(player, monster)
        else:
            game.ui.show('\n' + monster.name + ' is too quick for you.')
            monster_strikes(player, monster)
            if player.alive:
                monster.is_attacked(11, weapon_damage(player))
                fire(player)
                if not monster.alive:
                    player.fighting = 0
    if not monster.alive:
        player.kills += 1
    return monster
