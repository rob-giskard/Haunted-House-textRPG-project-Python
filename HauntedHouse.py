import random
import sys





#CLASSES ARE DEFINED HERE


class Entity:
#instances of this class are created with a number of hit points (HP)
    #determines how healthy is the entity
#and a value of armor class (AC)
    #determines how hard it is to hit the entity
    def __init__(self, name, maxHP, AC):
        self.name = name
        self.maxHP = maxHP
        self.HP = maxHP
        self.AC = AC
        self.alive = 1
        self.has_usables = 0
        self.stunned = 0
        self.shells = 0
        self.bullets = 6
        self.number_of_keys = 0
        self.condition = 'Stable'
        self.weapon = ''
        self.wants_end = 0
        self.in_house = 1
        self.in_room = 0
        self.location = 'Foyer'
        self.fighting = 0
        self.deeds = 0

    def __str__(self):
        return ('This ' + self.name + ' has ' + str(self.HP) + ' HP and '+ str(self.AC) + ' AC.') 
    
    def rolls_initiative(self):
        initiative = random.randint(1,21)
        print (' * ' + self.name + ' rolls for initiative, gets ' + str(initiative) + '. *') 
        return initiative 
        
    def is_attacked(self,incoming_hit,incoming_damage):
        if incoming_hit >= self.AC:
            self.HP -= incoming_damage
            print (' * You hit.',self.name + ' takes ' + str(incoming_damage) + ' damage. * ')
            if self.HP <= 0:
                print (' * ' + self.name + ' is dead. *')
                self.alive = False
        else:
            print (' * ' + self.name + ' avoids the attack. *')
    
    def is_stunned(self):
        print (' * ' + self.name + ' is STUNNED! Doesn`t attack this turn. *')
        self.stunned = 1
        
    def is_immobilized(self):
        print (self.name + ' is IMMOBILIZED. Can`t chase its opponent.')
        
    def rests(self):
        shortrest = random.randint(6,13)
        self.HP += shortrest
        if self.HP > self.maxHP:
            self.HP = self.maxHP
        print (self.name + ' has rested. Currently has ' + str(self.HP) + ' out of ' + str(self.maxHP) + ' hit points.') 
    

class Player(Entity):
             
    def checks_inventory(self):
        backpack.contains()
        if self.number_of_keys >= 4:
            print('''
    As you go over your inventory, you realize you have four ancient keys. 
    You should be able to open the rumored vault now. Only one thing remains. 
    You need to find it.
                        ''')
    def loots(self, container_to_loot):
        if len(container_to_loot) != 0: 
            for item in container_to_loot:
                if 'Shotgun shell' in item:
                    player.shells += 1
                elif 'Bullet' in item:
                    player.bullets += 1
                elif 'key' in item:
                    self.number_of_keys+=1
                    backpack.add(item)
                else:
                    backpack.add(item)
            print ('\n -> Stuff moved to your backpack.')
            
    def chooses_weapon(self):
        print('\nYou have the following weapons at your disposal:')
        for key in weapon_arsenal.keys():
            print('  ' + key)
        weapon_type = ''
        while weapon_type == '':
            weapon_type = input('Which weapon to use?').lower()
            if weapon_type.startswith('f'): 
                self.weapon = 'Fists'
            elif weapon_type.startswith('a'): 
                self.weapon = 'Axe'
            elif weapon_type.startswith('r'):
                self.weapon = 'Revolver pistol'
                if self.bullets == 0:
                    print('Your gun is empty.')
                    weapon_type = ''    
                else:
                    self.weapon = 'Revolver pistol'
            elif weapon_type.startswith('s'): 
                if self.shells == 0: 
                    print("Damn, seems you're out of shotgun shells.")
                    weapon_type = ''
                else:
                    self.weapon = 'Shotgun'
            else:
                print("You don't have that. Using your fists for now.")
                self.weapon = 'Fists'

    def is_attacked(self,attacker_name,incoming_hit,incoming_damage):
        if incoming_hit >= self.AC:
            self.HP -= incoming_damage
            print('\n * You are hit and take ' + str(incoming_damage) + ' damage. *')
            print('\n * ' + self.name + ', you have ' + str(self.HP) + ' HP left. *')
            if self.HP <= 0:
                print ('\n * ' + self.name + ', you are dead. *')
                self.alive = False
        else:
            print ('\n * ' + attacker_name + ' attacks but you avoid the strike. *')
    
    def rolls_initiative(self):
        initiative = random.randint(1,21)
        print ('\n * ' + self.name + ' rolls for initiative: ' + str(initiative) + '. *') 
        return initiative 
   
    def checks_usables(self):
        #compares backpack contents against a list of usable items
        #modifies has_usables class attribute
        usables = ['Bandage','Flashbang','Hardtack','Antidote','Mysterious glass vial']
        for i in usables:    
            if i in backpack.contents:
                self.has_usables = 1
        if self.has_usables:        
            print('\nUsable items:')
            for i in usables:
                if i in backpack.contents:
                    print ('  ' + i)
        else:
            print('\n * Whoopsie, you are all out of usable items. * \n')
            self.has_usables = 0
            player.checks_stats()
    
    def uses_item(self):
        item_to_use = ''
        while item_to_use == '':
            item_to_use = input('\npSelect item to use, check PST or Close the backpack.').lower()
        if item_to_use.startswith('b') and 'Bandage' in backpack.contents:
            self.HP += random.randint(6,12)
            if self.HP > self.maxHP:
                self.HP = self.maxHP
            print('    You tend to your wounds and are healed to ' + str(self.HP) + ' HP.')
            backpack.remove('Bandage')
        elif item_to_use.startswith('f') and 'Flashbang' in backpack.contents:
            if player.fighting:
                monster.is_stunned()
            else:
                print('\n    The flashbang discharges in your hand leaving you momentarily dazed. Well played.')
            backpack.remove('Flashbang')
        elif item_to_use.startswith('h') and 'Hardtack' in backpack.contents:
            self.HP += 2
            if self.HP > self.maxHP:
                self.HP = self.maxHP
            print('\n    The hardtack tastes bland but you recover some strength.')
            backpack.remove('Hardtack')
        elif item_to_use.startswith('a') and 'Antidote' in backpack.contents:
            if self.condition == 'Poisoned':
                self.condition = 'Stable'
                print('\n    The antidote is working. You feel better immediately.')
            else: print('\n    The liquid tastes funny but does nothing.')
            backpack.remove('Antidote')
        elif item_to_use.startswith('m'):
            print('\n    You drink the unknown liquid and taste death. Everything fades to black.')
            backpack.remove('Mysterious glass vial')
            player.alive, player.in_house = 0,0
        elif item_to_use.startswith('p'):
            player.checks_stats()
        elif item_to_use.startswith('c'):
            pass
        else: 
            print('***Item not usable.***')
    
    def sees_exits(self):
         exits = ['NORTH','SOUTH','EAST','WEST']
         for possible_exit in exits:
            if masterPlan[self.location][possible_exit] not in ['Wall','Railing']:
                print('    ' + possible_exit)
          
    def moves(self):
        move_chosen = 0
        print('\nFrom your current location you can move:')
        player.sees_exits()
        while not move_chosen:
            direction = input('Choose a direction to move to.').lower()
            while len(direction) == 0 or direction.lower()[0] not in ['n','s','e','w']:
                direction = input('Invalid direction. Where do you want to go?').lower()
            if direction.startswith('n'): dest = 'NORTH'
            elif direction.startswith('s'): dest = 'SOUTH'
            elif direction.startswith('e'): dest = 'EAST'
            elif direction.startswith('w'): dest = 'WEST'
            
            if masterPlan[self.location][dest] == 'Wall': print('\n    You bump into a wall.')
            elif masterPlan[self.location][dest] == 'Outside': 
                print('\n    You turn to the door leading back outside. Want to leave?')
                leave = input().lower()
                if leave.startswith('y'): player.in_house,move_chosen = 0,1
            elif masterPlan[self.location][dest] == 'Railing': 
                print('\n    The railings prevent you from falling off the gallery.')     
            elif masterPlan[self.location][dest] == 'Safe' and vault.solved == 0:
                if self.number_of_keys < 4:
                     print('''
    You are missing the necessary keys and are not able to open all of the locks. 
    Try to explore more of the house and return back later.
                                ''')
                else: 
                    print('\n    One by one you open all of the four locks and move ' + dest)
                    vault.solved = 1
                    self.location = masterPlan[self.location][dest]
                    move_chosen = 1
            elif masterPlan[self.location][dest] == 'Laboratory' and shortHallway.solved == 0:
                if 'Crowbar' not in backpack.contents:
                    print('''
    The heavy wooden door seems nailed shut with sturdy planks. It won't budge.
    Would you kindly pick up a crowbar or something?            
                            ''')
                else:
                    print('\n    You discard the planks barring the door and move ' + dest)
                    self.location = masterPlan[self.location][dest]
                    shortHallway.solved = 1
                    move_chosen = 1
            elif masterPlan[self.location][dest] == 'Ball room' and grandHall.solved == 0:
                if 'Crowbar' not in backpack.contents:
                    print('''
    The double door before you is jammed. Your attempts to progress in this 
    direction seem futile. This will require an instrument of some sorts.             
                            ''')
                else:
                    print('\n    You use the crowbar as a lever and move ' + dest)
                    self.location = masterPlan[self.location][dest]
                    grandHall.solved = 1
                    move_chosen = 1
            else: 
                print('\n    You move ' + dest + '.')
                self.location = masterPlan[self.location][dest]
                move_chosen = 1
    
    def explores(self):
        masterPlan[self.location]['VARIABLE'].is_entered()
        masterPlan[self.location]['VARIABLE'].is_explored()
            
    def enters_location(self):
        pass
                          
    def checks_stats(self):
        print('Your PST reads:')
        print('Health: ' + str(player.HP) +'/'+ str(player.maxHP) + ' | Heart BPM: ' + str(random.randint(120,180)) + '| Condition: ' + player.condition)
        print('Revolver pistol bullets: ' + str(player.bullets) + ' | Shotgun shells: ' + str(player.shells))

    def fires_shotgun(self):
        player.shells-=1
            
    def fires_pistol(self):
        player.bullets -= 1

key_types = ['Brass key', 'Silver key', 'Copper key', 'Iron key']

class Container:
#container can be filled with items, trapped, hiding a key and looted by player
    def __init__(self,name):
        self.name = name
        self.contents = []
        
    def contains(self):
        if self.contents != []:
            print('\n' + self.name + ' contains:\n')
            for item in self.contents:
                if 'key' in item:
                    print ('  ' + item, 'yellow')
                elif 'Bandage' in item or 'Hardtack' in item or 'Antidote' in item:
                    print ('  ' + item, 'blue')
                elif 'Flashbang' in item or 'Shotgun shell' in item or 'Bullet' in item or 'vial' in item:
                    print ('  ' + item, 'red')
                else:
                    print('  ' + item)
        else:
            print(self.name,'is empty.')
        
    def add(self, item_in):
        self.contents.append(item_in)

    def remove(self,item_out):
        self.contents.remove(item_out)

    def is_looted(self):
        self.contents.clear()

    def is_trapped(self):
        if random.randrange(1,100) < 60:
            print('The '+ self.name + ' is trapped!')
            traps = {'Dart trap':4, 'Poison gas':8, 'Explosion':12}
            #is_attacked(self,attacker_name,incoming_hit,incoming_damage)
            #incoming_hit is randrange
            #incoming_dmg is tied to randomly chosen element from dict traps
            player.is_attacked(random.choice(list(traps.keys())),
                               random.randrange(10,15), traps[random.choice(list(traps.keys()))])
            if not player.alive:
                player.in_room, player.in_house = 0,0

    def hides_key(self):
        if random.randrange(1,100) < 20 and len(key_types)!=0:
            type_of_key = random.choice(key_types)
            self.contents.append(type_of_key)
            key_types.remove(type_of_key)

            
class Location:
#locations are created with empty self.containers
#which are filled by what_in_room()
    def __init__(self,name):
        self.name = name
        self.container0 = ''
        self.container1 = ''
        self.container2 = ''
        self.container3 = ''
        self.container4 = ''
        self.description = masterPlan[self.name]['DESCRIPTION']
        self.containers = []
        self.conts_abb = []
        self.conts_list = []
        self.solved = 0
        
    def __str__(self):
        return self.name

    def is_entered(self):
    #displays the name of the room
    #checks if player meets conditions for interactions in certain rooms    
        player.in_room = 1
        print('\n                               ##' + len(self.name)*'#' + '##')
        print('                               # ' + self.name + ' #')
        print('                               ##' + len(self.name)*'#' + '##\n')
        print(self.description)
        
        if self.name == 'Master bedroom' and not self.solved:
            if 'Severed head of lady Durst' in backpack.contents and 'Remains of Catherine Durst' in backpack.contents:
                self.solved = 1
                player.deeds += 1
                print('''
    You place the remains of lady Durst beside the dead man and position 
    her head on the pillow. A deep sigh penetrates the whole house and 
    you can almost hear a happy couple laughing together. Suddenly, the 
    space around you seems a little less grim.
                            ''')
            else:
                print('\n    It seems you are missing a crucial item here.')

        elif self.name == 'Childrens bedroom' and not self.solved:
            if 'Photograph of Benjamin Durst' in backpack.contents and 'Brown teddy bear' in backpack.contents:
                self.solved = 1
                player.deeds += 1
                print('''
    You place the photograph of Benjamin Durst in one of the empty picture 
    frames and arrange the brown teddy bear so it sits among the other stuffed 
    animals on one of the beds. The room is filled with laughter and a half-transparent
    image of a young boy is standing beside you. He nods at you with joy in his eyes
    and slowly fades away. Suddenly, several more rays of sunshine find their way into
    the house.
                            ''')
            else:
                print('\n    It seems you are missing a crucial item here.')
        
        elif self.name == 'Moldy hallway' and player.condition != 'Poisoned':
            player.condition = 'Poisoned'
            print ('''
    You start coughing uncontrollably. Better hope you didn't breathe in too many
    of the microscopic particles swirling around you. Otherwise, your health could
    be in serious danger.            
                        ''')

        elif self.name == 'Storage room' and not self.solved:
            print('''
    You find yourself facing a caged animal. It resembles a wolf with open wounds 
    on various parts of its body. At first glance, its threatening presence 
    shocks you. But examining it further, you see sadness and an unspoken
    plea for help in its eyes. The cage is sealed with heavy chains.

    It seems you are missing a crucial item here.         
            ''')
            if 'Crowbar' in backpack.contents and 'Appetizing thighbone' in backpack.contents:
                self.solved = 1
                player.deeds += 1
                print('''
    You throw the huge bone inside the cage and it immediately picks it up. Then you
    take your window of opportunity and twist the chain with the crowbar until it snap.
    The cage opens. The hound looks at you and considers having a more nutritious meal.
    However, it nods at you in a distinctly human-like manner, expressing gratitude.
    Then it bolts out of the storage room towards the front door. 
                ''')
            elif 'Crowbar' in backpack.contents and not 'Appetizing thighbone' in backpack.contents:
                print('''
    You realize you could free the beast using your crowbar. However, it would be 
    extremely dangerous to approach the cage with the starving beast still inside.
    You are still missing a crucial item here.            
                ''')

    def has_enemy(self):    
        creatures = ['Groggy ghost','Blob of goo','Ghastly ghoul','Poltergeist',
                     'Panting pirate','Sad vampire','Lidless eye','Moaning monster',
                     'Chucking woodchuck','Batswarm','Striga','Besny havko',
                     'Creepy doll','Axe murderer','Norman Bates','Starving servant',
                     'Desperate tester','Gelatinous cube','Constrictor vine',
                     'Debilitating devil','Promiscuous python','Flying falchion',
                     'Mysterious mist','Generic villain'
                    ]
        creature = random.choice(creatures)
        if creature != 'Generic villain':
             creatures.remove(creature)
        monster = Entity(creature,18,10)

        print('\n    After entering the ' + self.name.lower() + ', you are attacked by a '+ monster.name +'.')
        player.fighting = 1
        player.chooses_weapon()
        return monster 
            
    def what_in_room(self,item_dic):   
    # argument is a disctionary of containers and their items - up to 4 containers and no limit on number of items
    # {'CONTAINER':['ITEM1','ITEM2','ITEM3',...]}
    # keys in item_dic should not start with the same letter or letter B,R,E    
        
        for key in item_dic.keys(): self.containers.append(key), self.conts_list.append(key), self.conts_abb.append(key[0].lower())
        self.conts_abb += ['b','r','e']
        try:
            self.container0 = Container(self.containers[0])
            self.container0.hides_key()
            for item in item_dic[self.containers[0]]:
                self.container0.add(item)        
        except IndexError: pass
        try:
            self.container1 = Container(self.containers[1])
            self.container1.hides_key()
            for item in item_dic[self.containers[1]]:
                self.container1.add(item)
        except IndexError: pass
        try:
            self.container2 = Container(self.containers[2])
            self.container2.hides_key()
            for item in item_dic[self.containers[2]]:
                self.container2.add(item)
        except IndexError: pass
        try:
            self.container3 = Container(self.containers[3])
            self.container3.hides_key()
            for item in item_dic[self.containers[3]]:
                self.container3.add(item)
        except IndexError: pass    
       
    def is_explored(self):
        while player.in_room:
            if len(self.conts_list) != 0:
                print('\nThe following objects catch your eye:\n')
                for c in self.containers: print(c)
                print('\nYou can also check your Backpack, push on to another Room or Escape screaming.')

            else:
                print('\n    This room seems empty. Want to rummage through your Backpack or explore other Rooms?')
            room_choice = input().lower()
            while room_choice == '' or room_choice[0] not in self.conts_abb:
                room_choice = input('The surrounding space gives you chills. What do you do?').lower()
            try:    
                if room_choice[0] == self.containers[0][0].lower():
                    self.container0.is_trapped()
                    if not player.alive: 
                        player.in_room, player.in_house = 0,0
                        break 
                    self.container0.contains()
                    player.loots(self.container0.contents)
                    self.container0.is_looted()
                    self.containers[0] = '' 
                    self.conts_list.remove(self.container0.name) 
            except IndexError: pass
            try:
                if room_choice[0] == self.containers[1][0].lower():
                    self.container1.is_trapped()
                    if not player.alive: 
                        player.in_room, player.in_house = 0,0
                        break
                    self.container1.contains()
                    player.loots(self.container1.contents)
                    self.container1.is_looted()
                    self.containers[1] = ''  
                    self.conts_list.remove(self.container1.name)
            except IndexError: pass
            try:
                if room_choice[0] == self.containers[2][0].lower():
                    self.container2.is_trapped()
                    if not player.alive: 
                        player.in_room, player.in_house = 0,0
                        break
                    self.container2.contains()
                    player.loots(self.container2.contents)
                    self.container2.is_looted()
                    self.containers[2] = ''
                    self.conts_list.remove(self.container2.name)
            except IndexError: pass
            try:
                if room_choice[0] == self.containers[3][0].lower():
                    self.container3.is_trapped()
                    if not player.alive: 
                        player.in_room, player.in_house = 0,0
                        break
                    self.container3.contains()
                    player.loots(self.container3.contents)
                    self.container3.is_looted()
                    self.containers[3] = ''
                    self.conts_list.remove(self.container3.name)
            except IndexError: pass
            if room_choice[0] == 'b':
                player.checks_inventory()
                player.checks_usables()
                if player.has_usables:
                    player.uses_item()
            if room_choice[0] == 'r':
                room_exit_lines = ['\n    You push your luck and face another mystery.', 
                            '\n    You leave the area and journey deeper into the house.',
                            '\n    Full of hopes, you carry on.',
                            '\n    You continue exploring.',
                            '\n    Your footsteps echo in the quiet interior.']     
                room_exit_line = random.choice(room_exit_lines)
                print(room_exit_line)
                player.in_room = 0
                if player.condition == 'Poisoned':
                    print('\n    A toxin coursing through your body takes its toll. You feel your life energy draining.','red')
                    player.HP -= 3
                    if player.HP <= 0:
                        print (' * ' + self.name + ', you succumb to the toxic substance coursing in your veins. *')
                        player.alive = False
                        player.in_house = 0
            if room_choice == 'e':
                player.in_room, player.in_house = 0,0
                print('    Smart. You left the house. Fresh air caresses your face once again.')       
                
#COMBAT IS DEFINED HERE
#player.fighting is set to '1' in Location.has_enemy()
#combat is looping while player or enemy is alive, then .fighting is set to '0'

def combat(player,monster):
    while player.fighting:
        #if player chose shotgun or pistol, checks for ammo, lets him choose again
        if player.weapon == 'Shotgun' and player.shells == 0:
            print('You spent all of your shells. Need to quickly swap weapons.')
            player.chooses_weapon()
        if player.weapon == 'Revolver pistol' and player.bullets == 0:
            print('You spent all of your bullets. Quickly swapping weapons.')
            player.chooses_weapon()
        #every round of combat starts with initiative
        if int(player.rolls_initiative()) > int(monster.rolls_initiative()):
            print ('\nYou react faster.')
            ###if player wins initiative, lets him choose to fight or check inventory and use item
            if input('\nFight or Use item?').lower().startswith('f'):
                monster.is_attacked(13,random.randint(weapon_arsenal[player.weapon][0],weapon_arsenal[player.weapon][1]))
                if player.weapon == 'Shotgun': player.fires_shotgun()
                elif player.weapon== 'Revolver pistol': player.fires_pistol()
                if not monster.alive:
                    player.fighting = 0
                else:
                    player.is_attacked(monster.name,random.randint(5,15),random.randint(2,10))
                    if not player.alive:
                        player.fighting, player.in_house = 0,0    
            else:
                player.checks_usables()
                if player.has_usables:
                    player.uses_item()
                    if monster.stunned:
                        monster.is_attacked(11,random.randint(weapon_arsenal[player.weapon][0],weapon_arsenal[player.weapon][1]))
                        monster.stunned = 0
                    if player.weapon == 'Shotgun': player.fires_shotgun()
                    elif player.weapon == 'Revolver pistol': player.fires_pistol()
                    if not monster.alive:
                        player.fighting = 0
                else:
                    player.is_attacked(monster.name,random.randint(5,15),random.randint(2,10))
                    if not player.alive:
                        player.fighting, player.in_house = 0,0
        else:
            print ('\n' + monster.name + ' is too quick for you.')
            player.is_attacked(monster.name,random.randint(5,15),random.randint(2,10))
            if not player.alive:
                player.fighting, player.in_house = 0,0
            else:
                monster.is_attacked(11,random.randint(weapon_arsenal[player.weapon][0],weapon_arsenal[player.weapon][1]))
                if player.weapon == 'Shotgun': player.fires_shotgun()
                elif player.weapon == 'Revolver pistol': player.fires_pistol()
                if not monster.alive:
                    player.fighting = 0
    return player, monster    

#LOCATIONS ARE DEFINED HERE
#nested dictionary contains variable name of objects from Location class, position on map,
#description printed when Location.is_entered() 
#and possible exits for Entity.moves()

masterPlan = {
    'Foyer': {
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[6][3]',   
        'DESCRIPTION': '''
    You enter the foyer and immediatly realize you are definitely 
    the first guest to do so after very many years. Dust covers 
    every nook and cranny, the floral-patterned drapes are long gone, 
    succeeded by mere strips of moth-eaten cloth ominously moving 
    in the cold breeze you let in through the front door. 
    The smell of mildew attacks your nostrils. 
    ''',
        'NORTH': 'Grand hall',
        'SOUTH': 'Outside',
        'EAST': 'Wall',
        'WEST': 'Wall'
    }, 
    'Grand hall':{
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[5][3]',
        'DESCRIPTION': '''
    You find yourself in a huge open space. The floor is marble, the walls 
    covered in wooden mosaic tiles. A wide gallery runs around the hall 
    on the second floor and a majestic chandelier hangs above your head.
    However, the lightbulbs are long gone and shadows reign all around.
    ''',
        'NORTH': 'Short hallway',
        'SOUTH': 'Foyer',
        'EAST': 'Wall',
        'WEST': 'Drawing room'    
    },
    'Drawing room':{
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[5][2]',
        'DESCRIPTION': '''
    This formally decorated place was undoubtedly used for greeting the guests
    of the house. A huge sofa and two massive armchairs surround a coffee table.
    A huge brown bear skin rug faces an open fireplace. To your surprise, 
    the room feels really cozy.  
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Wall',
        'EAST': 'Grand hall',
        'WEST': 'Ball room'    
    },
    'Ball room':{
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[5][1]',
        'DESCRIPTION': '''
    This vast space was once full of happy people. Now only bones litter the dance floor.
    Many of them bear toothmarks of tiny rodents.  
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Wall',
        'EAST': 'Drawing room',
        'WEST': 'Wall'    
    },
    'Short hallway':{
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[4][3]',
        'DESCRIPTION': '''
    The decor of the space around you tells a tale of a once proud family.
    Several framed photographs hang on the walls, each depicting a person
    of high status. However, time has manifested itself on the pictures
    and the faces looking back at you are downright ghastly. 
    ''',
        'NORTH': 'Kitchen',
        'SOUTH': 'Grand hall',
        'EAST': 'Laboratory',
        'WEST': 'Wall'    
    },
    'Laboratory':{
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[4][4]',
        'DESCRIPTION': '''
    The space tight space around you is cluttered with alchemical supplies 
    and strange contraptions. A number of jars sit on dusty shelves, each
    containing unknown substances.
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Wall',
        'EAST': 'Secret stairs',
        'WEST': 'Short hallway'
    },    
    'Secret stairs':{
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[4][5]',
        'DESCRIPTION': '''
    This secret stairway was probably used exclusively by the owners of the house 
    for quick and discreet movement through the innards of their home.
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Wall',
        'EAST': 'Safe',
        'WEST': 'Laboratory'
    },    
    'Kitchen':{
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[3][3]',
        'DESCRIPTION': '''
    The lady of this house loved cooking. This fact is made known by a myriad
    of pans, pots and tools hanging all around the spacious kitchen. However, 
    rat droppings decorate most of the working surfaces now and you smell
    a foul stench of decomposing ingredients.
    ''',
        'NORTH': 'Long hallway',
        'SOUTH': 'Short hallway',
        'EAST': 'Wall',
        'WEST': 'Wall'    
    },
    'Long hallway':{
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[2][3]',
        'DESCRIPTION': '''
    Walking along a carpeted hallway you notice a secret compartment behind a rotten wallpaper.
    At the end of the hallway you find two doors. Soft growling can be heard from behind 
    the one on the left. This door seem to be reinforced with metal sheets. The door on 
    the right is covered in dark burgundy spots of dried blood.
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Kitchen',
        'EAST': 'Stairs',
        'WEST': 'Storage room'    
    },
    'Stairs':{
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[2][4]',
        'DESCRIPTION': '''
    The stairs are in a poor condition. Watch your step.
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Moldy hallway',
        'EAST': 'Wall',
        'WEST': 'Long hallway'    
    },
    'Storage room':{
        'VARIABLE': '',
        'POSITION': 'house.firstFloor[2][2]',
        'DESCRIPTION': '''
    You open the door to a small storage room.
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Wall',
        'EAST': 'Long hallway',
        'WEST': 'Wall'  
    },
    'Moldy hallway':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[3][4]',
        'DESCRIPTION': '''
    The roof is leaking somewhere above this hallway. The walls are covered by 
    a thick layer of mold and the air is filled with spores. 
    ''',
        'NORTH': 'Stairs',
        'SOUTH': 'Gallery NE',
        'EAST': 'Wall',
        'WEST': 'Wall'    
    },
    'Gallery NE':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[4][4]',
        'DESCRIPTION': '''
    The gallery runs in a circle above the grand hall. The space around
    you is dominated by thick spiderwebs. 
    ''',
        'NORTH': 'Moldy hallway',
        'SOUTH': 'Gallery E',
        'EAST': 'Wall',
        'WEST': 'Gallery N'    
    },
    'Gallery E':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[5][4]',
        'DESCRIPTION': '''
    The gallery overlooks the grand hall. The space around you is dominated by thick spiderwebs. 
    ''',
        'NORTH': 'Gallery NE',
        'SOUTH': 'Gallery SE',
        'EAST': 'Study',
        'WEST': 'Railing'    
    },
    'Gallery SE':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[6][4]',
        'DESCRIPTION': '''
    The gallery overlooks the grand hall. The space around you is dominated by thick spiderwebs. 
    ''',
        'NORTH': 'Gallery E',
        'SOUTH': 'Wall',
        'EAST': 'Wall',
        'WEST': 'Gallery S'    
    },
    'Gallery S':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[6][3]',
        'DESCRIPTION': '''
    This section of the gallery has stained-glass windows looking out on the front yard. 
    You see two children standing there, looking at you silently. You blink and they are gone. 
    ''',
        'NORTH': 'Railing',
        'SOUTH': 'Wall',
        'EAST': 'Gallery SE',
        'WEST': 'Gallery SW'    
    },
    'Gallery SW':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[6][2]',
        'DESCRIPTION': '''
    The west side of the gallery seems to be in a particularly bad shape. Almost looks like
    somebody destroyed the furniture with an axe, crushed the walls with a sledgehammer.    
    ''',
        'NORTH': 'Gallery W',
        'SOUTH': 'Wall',
        'EAST': 'Gallery S',
        'WEST': 'Wall'    
    },
    'Gallery W':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[5][2]',
        'DESCRIPTION': '''
    This section of the gallery is littered with rubble. 
    ''',
        'NORTH': 'Gallery NW',
        'SOUTH': 'Gallery SW',
        'EAST': 'Railing',
        'WEST': 'Master bedroom'    
    },
    'Master bedroom':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[5][1]',
        'DESCRIPTION': '''
    The master bedroom is full of decadent luxury. Altough everything is covered 
    under a thick layer of dust, the space resembles a king's suite. A person is
    lying in the huge bed. At closer inspection you realize it is in fact a well 
    preserved body of an older gentleman with two coins placed on his closed eyes.  
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Wall',
        'EAST': 'Gallery W',
        'WEST': 'Wall'    
    }, 
    'Childrens bedroom':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[3][2]',
        'DESCRIPTION': '''
    Two small beds sit in the corners of this room. A small library with fairy-tale
    books also contains several empty picture frames and a ragged doll is discarded
    in the middle of the room. You notice smears of dried blood on several places 
    around you. 
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Gallery NW',
        'EAST': 'Wall',
        'WEST': 'Wall'   
    },
    'Gallery NW':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[4][2]',
        'DESCRIPTION': '''
    This section of the gallery is littered with rubble. 
    ''',
        'NORTH': 'Childrens bedroom',
        'SOUTH': 'Gallery W',
        'EAST': 'Gallery N',
        'WEST': 'Wall'    
    },
    'Gallery N':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[4][3]',
        'DESCRIPTION': '''
    This section of the gallery is littered by rubble. 
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Railing',
        'EAST': 'Gallery NE',
        'WEST': 'Gallery NW'    
    },
    'Study':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[5][5]',
        'DESCRIPTION': '''
    The Study greets you with a smell of old parchment and cinnamon. Shelves full 
    of leather-bound books line the walls, the massive oaken table is covered 
    with dripped candle wax. You walk across the study on a thick red carpet.
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Wall',
        'EAST': 'Vault',
        'WEST': 'Gallery E'    
    },
    'Vault':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[5][6]',
        'DESCRIPTION': '''
    You enter a small room dominated by magnificient steel doors in the north wall. 
    This has to be the vault. You see four keyholes before you.
    ''',
        'NORTH': 'Safe',
        'SOUTH': 'Wall',
        'EAST': 'Wall',
        'WEST': 'Study'    
    },
    'Safe':{
        'VARIABLE': '',
        'POSITION': 'house.secondFloor[5][6]',
        'DESCRIPTION': '''
    You open all the locks and enter. The safe looks really impressive. Two display cases
    stand at the east and the west wall, you see a huge treasure chest and something 
    resembling a coffin in the center of the room.
    ''',
        'NORTH': 'Wall',
        'SOUTH': 'Vault',
        'EAST': 'Wall',
        'WEST': 'Secret stairs'    
    }
}

#LOCATIONS ARE CREATED AND FILLED WITH CONTAINERS HERE
#container names should not start with the same letter or letter B,R,E

foyer = Location('Foyer')
masterPlan['Foyer']['VARIABLE'] = foyer
foyer.what_in_room({'Painting of lady and lord Durst':['Bleached letter'],
                'Wardrobe':['Bandage','Dusty duster']
                })
grandHall = Location('Grand hall')
masterPlan['Grand hall']['VARIABLE'] = grandHall
grandHall.what_in_room({'Weapon cabinet':['Flashbang','Rusty nail','Shotgun shell'],
                'Iron lockbox':['Bag of coins','Polished emerald'],
                'Antique vase':['Dried tulips','Wasp nest']
                })
drawingRoom = Location('Drawing room')
masterPlan['Drawing room']['VARIABLE'] = drawingRoom
drawingRoom.what_in_room({'Porcelain teapot':['Dead cockroach'],
                'Cigar box':['Soaked cigar','Silver lighter'],
                })
ballRoom = Location('Ball room')
masterPlan['Ball room']['VARIABLE'] = ballRoom
ballRoom.what_in_room({'Old piano':['Sheet music: "Lullaby for Lloyd"'],
                'Pile of bones':['Diamond ring','Appetizing thighbone'],
                })
shortHallway = Location('Short hallway')
masterPlan['Short hallway']['VARIABLE'] = shortHallway
shortHallway.what_in_room({'Ornate picture frame':['Photograph of Benjamin Durst'],
                        })
laboratory = Location('Laboratory')
masterPlan['Laboratory']['Variable'] = laboratory
laboratory.what_in_room({'Wooden box':['Bandage'],
                    'Leather case':['Mysterious glass vial','Antidote','Bandage'],
                    'Toolbox':['Crowbar','Screwdriver'],
                    'Shelf':['Aged wine','Potion']
                        })
secretStairs = Location('Secret stairs')
masterPlan['Secret stairs']['VARIABLE'] = secretStairs
secretStairs.what_in_room({'Hidden stash':['Bullet','Shotgun shell','Hardtack']
                        })
kitchen = Location('Kitchen')
masterPlan['Kitchen']['VARIABLE'] = kitchen
kitchen.what_in_room({'Shabby cupboard':['Bandage','Worm-ridden bag of flour'],
                'Wooden box':['Sack of turnips','Bunch of carrots'],
                'Kitchen counter':['Severed head of lady Durst']
                })
longHallway = Location('Long hallway')
masterPlan['Long hallway']['VARIABLE'] = longHallway
longHallway.what_in_room({'Painting of a landscape':['"Merry marshes" by Catherine Durst: oil on canvas'],
                'Secret stash':['Huge ruby','Bloody ringfinger','Bullet'],
                'First aid lockbox':['Bandage','Bandage','Antidote']
                })
storageRoom = Location('Storage room')
masterPlan['Storage room']['VARIABLE'] = storageRoom
storageRoom.what_in_room({'Old backpack':['Shotgun shell','Antidote','Ancient coin',
                'Hardtack','Hardtack'],
                })
stairs = Location('Stairs')
masterPlan['Stairs']['VARIABLE'] = stairs
stairs.what_in_room({
                })
moldyHallway = Location('Moldy hallway')
masterPlan['Moldy hallway']['VARIABLE'] = moldyHallway
moldyHallway.what_in_room({
                        })
galleryNE = Location('Gallery NE')
masterPlan['Gallery NE']['VARIABLE'] = galleryNE
galleryNE.what_in_room({'Huge cocoon':['Slimy eggsack','Half-digested cat'],
                'Small cocoon':['Black sludge'],
                'Web-covered display case':['Shotgun shell','Ceremonial dagger','Tribal leather bracelet'],
                'Loose brick':['Dead rat']
                })
galleryE = Location('Gallery E')
masterPlan['Gallery E']['VARIABLE'] = galleryE
galleryE.what_in_room({'Small cocoon':['Spiderling']
                    })
gallerySE = Location('Gallery SE')
masterPlan['Gallery SE']['VARIABLE'] = gallerySE
gallerySE.what_in_room({
                    })
galleryS = Location('Gallery S')
masterPlan['Gallery S']['VARIABLE'] = galleryS
galleryS.what_in_room({'Web-covered shoe box':['Brown teddy bear']
                    })
gallerySW = Location('Gallery SW')
masterPlan['Gallery SW']['VARIABLE'] = gallerySW
gallerySW.what_in_room({'Destroyed display cabinet':['Golden necklace']
                    })
galleryW = Location('Gallery W')
masterPlan['Gallery W']['VARIABLE'] = galleryW
galleryW.what_in_room({
                    })
galleryNW = Location('Gallery NW')
masterPlan['Gallery NW']['VARIABLE'] = galleryNW
galleryNW.what_in_room({
                    })
childrensBedroom = Location('Childrens bedroom')
masterPlan['Childrens bedroom']['VARIABLE'] = childrensBedroom
galleryN = Location('Gallery N')
childrensBedroom.what_in_room({'Toy chest':['Wooden train','Tea set'],
                            'Shoebox':['Deck of playing cards','Bandage']
                            })
masterPlan['Gallery N']['VARIABLE'] = galleryN
galleryN.what_in_room({'Discarded holster':['Bandage','Shotgun shell']
                    })
masterBedroom = Location('Master bedroom')
masterPlan['Master bedroom']['VARIABLE'] = masterBedroom
masterBedroom.what_in_room({
                        })
study = Location('Study')
masterPlan['Study']['VARIABLE'] = study
study.what_in_room({'Painting of a city panorama':['"Smothering smog" by Catherine Durst: oil on canvas'],
                'Iron lockbox':['Shotgun shell','Bullet','Bullet','Steel arrowhead'],
                'Shelves':['"The king in yellow"','"Victorian handbook of poisons"']
                }) 
vault = Location('Vault')
masterPlan['Vault']['VARIABLE'] = vault
vault.what_in_room({'Old pouch':['Strange rune']
                }) 
safe = Location('Safe')
masterPlan['Safe']['VARIABLE'] = safe
safe.what_in_room({'Glass display case':['Strange clockwork device'],
                'Ornate display case':['Jade statue'],
                'Treasure chest':['Pile of gold coins','Assortment of precious stones'],
                'Stone coffin':['Remains of Catherine Durst','Blood-soaked handkerchief']
                }) 

#GAMEPLAY STARS HERE
'''
speech = 'Barry the Butler says: "Welcome to the haunted house.'
sys.stdout(speech)
for char in speech:
    sys.stdout.write(char)
    sys.stdout.flush()
    time.sleep(0.05)
'''
print('Barry the Butler says: "Welcome to the haunted house."')
print('Barry the Butler says: "How would you like to be addressed?."')
player_name = input()
player = Player(player_name, 50, 12)
backpack = Container('Backpack')
backpack.add('PST: Personal Statistics Tracker')
print('Barry the Butler says: "' + player.name + ', the house holds many treasures."')
print('''
Barry the Butler says: "To navigate the premises and carry out actions, just type the capitalized letters.
                        You can choose directions by typing N, S, E or W. Notice that not all items 
                        are usable - when inspecting your inventory, usable items will be highlighted."''')

print('''
Barry the Butler says: "And if you`re looking for the vault, be warned - you need to collect 4 keys.'
                        The keys, while not directly usable, are highlighted in yellow."''')
print('Barry the Butler says: "Enjoy your stay."')
player.in_house = 1
weapon_arsenal = {'Fists':[1,6], 
                  'Axe':[4,10],
                  'Revolver pistol':[10,16],
                  'Shotgun':[18,20]}

while player.in_house and player.alive:
    player.explores()
    if not player.in_house: break
    player.moves()
    if not player.in_house: break
    if random.randrange(1,100) < 20:
            monster = masterPlan[player.location]['VARIABLE'].has_enemy()
            player,monster = combat(player,monster) 

if not player.in_house:
    if not player.alive:
        print('\n    The house claimed your soul. The treasures remain lost.')
    elif len(backpack.contents) > 1:
        print('\n    You escaped with the following treasure:/n')
        for item in backpack.contents:
            if item == 'PST: Personal Statistics Tracker':
                continue
            else:
                print('  ' + item)
    else:
        print('\n    Unfortunately, you got out empty-handed.')

    if player.deeds == 0:
        print('\n    ' + player.name + ', you accomplished no good deeds in the house.') 
        print('    There was more to be done, but who said it was your job...')
    elif player.deeds > 0 and player.deeds < 3:
        print('\n    Good deeds accomplished: ' + str(player.deeds) + '.')
        print("    " + player.name + ", the haunted house is still a restless place, but your visit won't be forgotten.")
    elif player.deeds == 3:
        print('\n    Congratulations, ' + player.name + '!')
        print('''
    You proved hope always prevails. You reunited the lady and lord Durst,
    honored the memory of a troubled child and freed a tortured spirit from its cage.
    Thanks to you, the haunted house will rest in peace. 
    ''')
