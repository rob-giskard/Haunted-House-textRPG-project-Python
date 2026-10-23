"""Creatures of the house: the Entity base class (monsters) and the Player."""
import random

from . import data


class Entity:
    """Anything that fights: has hit points (HP) and an armor class (AC).

    HP is how healthy the entity is, AC is how hard it is to hit.
    Monsters are plain Entities; the Player builds on this class.
    """

    def __init__(self, name, maxHP, AC, ui):
        self.name = name
        self.ui = ui            # where this entity's messages are shown
        self.maxHP = maxHP
        self.HP = maxHP
        self.AC = AC
        self.alive = 1
        self.has_usables = 0
        self.stunned = 0
        self.shells = data.STARTING_SHELLS
        self.bullets = data.STARTING_BULLETS
        self.number_of_keys = 0
        self.condition = 'Stable'
        self.weapon = ''
        self.wants_end = 0          # not used yet
        self.in_house = 1
        self.in_room = 0
        self.location = data.START_ROOM
        self.fighting = 0
        self.deeds = 0
        self.kills = 0

    def __str__(self):
        return ('This ' + self.name + ' has ' + str(self.HP) + ' HP and ' + str(self.AC) + ' AC.')

    def rolls_initiative(self):
        initiative = random.randint(1, 20)
        self.ui.show(' * ' + self.name + ' rolls for initiative, gets ' + str(initiative) + '. *')
        return initiative

    def is_attacked(self, incoming_hit, incoming_damage):
        if incoming_hit >= self.AC:
            self.HP -= incoming_damage
            self.ui.show(' * You hit.', self.name + ' takes ' + str(incoming_damage) + ' damage. * ')
            if self.HP <= 0:
                self.ui.show(' * ' + self.name + ' is dead. *')
                self.alive = False
        else:
            self.ui.show(' * ' + self.name + ' avoids the attack. *')

    def is_stunned(self):
        self.ui.show(' * ' + self.name + " is STUNNED! Doesn't attack this turn. *")
        self.stunned = 1

    def is_immobilized(self):
        # not used yet - meant for a future fleeing/chasing mechanic
        self.ui.show(self.name + " is IMMOBILIZED. Can't chase its opponent.")

    def rests(self):
        # not used yet - meant for a future "rest" action
        shortrest = random.randint(6, 13)
        self.HP += shortrest
        if self.HP > self.maxHP:
            self.HP = self.maxHP
        self.ui.show(self.name + ' has rested. Currently has ' + str(self.HP) + ' out of ' + str(self.maxHP) + ' hit points.')


class Player(Entity):
    """The player. Knows the game it belongs to, to reach the backpack, rooms and the current monster."""

    def __init__(self, game, name):
        super().__init__(name, data.PLAYER_HP, data.PLAYER_AC, game.ui)
        self.game = game

    @property
    def backpack(self):
        return self.game.backpack

    def checks_inventory(self):
        self.backpack.contains()
        if self.number_of_keys >= data.KEYS_NEEDED:
            self.ui.show('''
    As you go over your inventory, you realize you have four ancient keys.
    You should be able to open the rumored vault now. Only one thing remains.
    You need to find it.
                        ''')

    def loots(self, container_to_loot):
        if len(container_to_loot) != 0:
            for item in container_to_loot:
                if 'Shotgun shell' in item:
                    self.shells += 1
                elif 'Bullet' in item:
                    self.bullets += 1
                elif item.endswith(' key'):
                    self.number_of_keys += 1
                    self.backpack.add(item)
                else:
                    self.backpack.add(item)
            self.ui.show('\n -> Stuff moved to your backpack.')

    def chooses_weapon(self):
        self.ui.show('\nYou have the following weapons at your disposal:')
        for key in data.WEAPONS.keys():
            self.ui.show('  ' + key)
        weapon_type = ''
        while weapon_type == '':
            weapon_type = self.ui.ask('Which weapon to use?').lower()
            if weapon_type.startswith('f'):
                self.weapon = 'Fists'
            elif weapon_type.startswith('a'):
                self.weapon = 'Axe'
            elif weapon_type.startswith('r'):
                self.weapon = 'Revolver pistol'
                if self.bullets == 0:
                    self.ui.show('Your gun is empty.')
                    weapon_type = ''
            elif weapon_type.startswith('s'):
                if self.shells == 0:
                    self.ui.show("Damn, seems you're out of shotgun shells.")
                    weapon_type = ''
                else:
                    self.weapon = 'Shotgun'
            else:
                self.ui.show("You don't have that. Using your fists for now.")
                self.weapon = 'Fists'

    def is_attacked(self, attacker_name, incoming_hit, incoming_damage):
        if incoming_hit >= self.AC:
            self.HP -= incoming_damage
            self.ui.show('\n * You are hit and take ' + str(incoming_damage) + ' damage. *')
            self.ui.show('\n * ' + self.name + ', you have ' + str(self.HP) + ' HP left. *')
            if self.HP <= 0:
                self.ui.show('\n * ' + self.name + ', you are dead. *')
                self.alive = False
        else:
            self.ui.show('\n * ' + attacker_name + ' attacks but you avoid the strike. *')

    def rolls_initiative(self):
        initiative = random.randint(1, 20)
        self.ui.show('\n * ' + self.name + ' rolls for initiative: ' + str(initiative) + '. *')
        return initiative

    def checks_usables(self):
        # compares backpack contents against the list of usable items
        self.has_usables = 0
        for i in data.USABLE_ITEMS:
            if i in self.backpack.contents:
                self.has_usables = 1
        if self.has_usables:
            self.ui.show('\nUsable items:')
            for i in data.USABLE_ITEMS:
                if i in self.backpack.contents:
                    self.ui.show('  ' + i)
        else:
            self.ui.show('\n * Whoopsie, you are all out of usable items. * \n')
            self.checks_stats()

    def uses_item(self):
        backpack = self.backpack
        item_to_use = ''
        while item_to_use == '':
            item_to_use = self.ui.ask('\nSelect item to use, check PST or Close the backpack.').lower()
        if item_to_use.startswith('b') and 'Bandage' in backpack.contents:
            self.HP += random.randint(6, 12)
            if self.HP > self.maxHP:
                self.HP = self.maxHP
            self.ui.show('    You tend to your wounds and are healed to ' + str(self.HP) + ' HP.')
            backpack.remove('Bandage')
        elif item_to_use.startswith('f') and 'Flashbang' in backpack.contents:
            if self.fighting:
                self.game.monster.is_stunned()
            else:
                self.ui.show('\n    The flashbang discharges in your hand leaving you momentarily dazed. Well played.')
            backpack.remove('Flashbang')
        elif item_to_use.startswith('h') and 'Hardtack' in backpack.contents:
            self.HP += 2
            if self.HP > self.maxHP:
                self.HP = self.maxHP
            self.ui.show('\n    The hardtack tastes bland but you recover some strength.')
            backpack.remove('Hardtack')
        elif item_to_use.startswith('a') and 'Antidote' in backpack.contents:
            if self.condition == 'Poisoned':
                self.condition = 'Stable'
                self.ui.show('\n    The antidote is working. You feel better immediately.')
            else:
                self.ui.show('\n    The liquid tastes funny but does nothing.')
            backpack.remove('Antidote')
        elif item_to_use.startswith('m') and 'Mysterious glass vial' in backpack.contents:
            self.ui.show('\n    You drink the unknown liquid and taste death. Everything fades to black.')
            backpack.remove('Mysterious glass vial')
            self.alive, self.in_house, self.in_room, self.fighting = 0, 0, 0, 0
        elif item_to_use.startswith('p'):
            self.checks_stats()
        elif item_to_use.startswith('c'):
            pass
        else:
            self.ui.show('***Item not usable.***')

    def sees_exits(self):
        exits = self.game.rooms[self.location].exits
        for possible_exit in ['NORTH', 'SOUTH', 'EAST', 'WEST']:
            if exits[possible_exit] not in ['Wall', 'Railing']:
                self.ui.show('    ' + possible_exit)

    def moves(self):
        move_chosen = 0
        self.ui.show('\nFrom your current location you can move:')
        self.sees_exits()
        while not move_chosen:
            direction = self.ui.ask('Choose a direction to move to.').lower()
            while len(direction) == 0 or direction[0] not in ['n', 's', 'e', 'w']:
                direction = self.ui.ask('Invalid direction. Where do you want to go?').lower()
            dest = {'n': 'NORTH', 's': 'SOUTH', 'e': 'EAST', 'w': 'WEST'}[direction[0]]
            target = self.game.rooms[self.location].exits[dest]
            opened = self.game.opened_doors

            if target == 'Wall':
                self.ui.show('\n    You bump into a wall.')
            elif target == 'Outside':
                self.ui.show('\n    You turn to the door leading back outside. Want to leave?')
                leave = self.ui.ask().lower()
                if leave.startswith('y'):
                    self.in_house, move_chosen = 0, 1
            elif target == 'Railing':
                self.ui.show('\n    The railings prevent you from falling off the gallery.')
            elif target == 'Safe' and 'Safe' not in opened:
                if self.number_of_keys < data.KEYS_NEEDED:
                    self.ui.show('''
    You are missing the necessary keys and are not able to open all of the locks.
    Try to explore more of the house and return later.
                                ''')
                else:
                    self.ui.show('\n    One by one you open all of the four locks and move ' + dest)
                    opened.add('Safe')
                    self.location = target
                    move_chosen = 1
            elif target == 'Laboratory' and 'Laboratory' not in opened:
                if 'Crowbar' not in self.backpack.contents:
                    self.ui.show('''
    The heavy wooden door seems nailed shut with sturdy planks. It won't budge.
    Would you kindly pick up a crowbar or something?
                            ''')
                else:
                    self.ui.show('\n    You discard the planks barring the door and move ' + dest)
                    self.location = target
                    opened.add('Laboratory')
                    move_chosen = 1
            elif target == 'Ball room' and 'Ball room' not in opened:
                if 'Crowbar' not in self.backpack.contents:
                    self.ui.show('''
    The double door before you is jammed. Your attempts to progress in this
    direction seem futile. This will require an instrument of some sort.
                            ''')
                else:
                    self.ui.show('\n    You use the crowbar as a lever and move ' + dest)
                    self.location = target
                    opened.add('Ball room')
                    move_chosen = 1
            else:
                self.ui.show('\n    You move ' + dest + '.')
                self.location = target
                move_chosen = 1

    def explores(self):
        room = self.game.rooms[self.location]
        room.is_entered(self.game)
        room.is_explored(self.game)

    def checks_stats(self):
        self.ui.show('Your PST reads:')
        self.ui.show('Health: ' + str(self.HP) + '/' + str(self.maxHP) + ' | Heart BPM: ' + str(random.randint(120, 180)) + '| Condition: ' + self.condition)
        self.ui.show('Revolver pistol bullets: ' + str(self.bullets) + ' | Shotgun shells: ' + str(self.shells))

    def fires_shotgun(self):
        self.shells -= 1

    def fires_pistol(self):
        self.bullets -= 1
