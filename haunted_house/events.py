"""Special things that happen when the player enters certain rooms: the good deeds and the poison."""


def room_event(game, room):
    handler = ROOM_EVENTS.get(room.name)
    if handler:
        handler(game, room)


def master_bedroom(game, room):
    if room.solved:
        return
    backpack = game.backpack
    if 'Severed head of lady Durst' in backpack.contents and 'Remains of Catherine Durst' in backpack.contents:
        room.solved = 1
        game.player.deeds += 1
        game.ui.show('''
    You place the remains of lady Durst beside the dead man and position 
    her head on the pillow. A deep sigh penetrates the whole house and 
    you can almost hear a happy couple laughing together. Suddenly, the 
    space around you seems a little less grim.
                            ''')
        backpack.remove('Severed head of lady Durst')
        backpack.remove('Remains of Catherine Durst')
    else:
        game.ui.show('\n    It seems you are missing a crucial item here.')


def childrens_bedroom(game, room):
    if room.solved:
        return
    backpack = game.backpack
    if 'Photograph of Benjamin Durst' in backpack.contents and 'Brown teddy bear' in backpack.contents:
        room.solved = 1
        game.player.deeds += 1
        game.ui.show('''
    You place the photograph of Benjamin Durst in one of the empty picture 
    frames and arrange the brown teddy bear so it sits among the other stuffed 
    animals on one of the beds. The room is filled with laughter and a half-transparent
    image of a young boy is standing beside you. He nods at you with joy in his eyes
    and slowly fades away. Suddenly, several more rays of sunshine find their way into
    the house.
                            ''')
        backpack.remove('Photograph of Benjamin Durst')
        backpack.remove('Brown teddy bear')
    else:
        game.ui.show('\n    It seems you are missing a crucial item here.')


def moldy_hallway(game, room):
    if game.player.condition != 'Poisoned':
        game.player.condition = 'Poisoned'
        game.ui.show('''
    You start coughing uncontrollably. Better hope you didn't breathe in too many
    of the microscopic particles swirling around you. Otherwise, your health could
    be in serious danger.            
                        ''')


def storage_room(game, room):
    if room.solved:
        return
    backpack = game.backpack
    game.ui.show('''
    You find yourself facing a caged animal. It resembles a wolf with open wounds 
    on various parts of its body. At first glance, its threatening presence 
    shocks you. But examining it further, you see sadness and an unspoken
    plea for help in its eyes. The cage is sealed with heavy chains.
            ''')
    if 'Crowbar' in backpack.contents and 'Appetizing thighbone' in backpack.contents:
        room.solved = 1
        game.player.deeds += 1
        game.ui.show('''
    You throw the huge bone inside the cage and it immediately picks it up. Then you
    take your window of opportunity and twist the chain with the crowbar until it snaps.
    The cage opens. The hound looks at you and considers having a more nutritious meal.
    However, it nods at you in a distinctly human-like manner, expressing gratitude.
    Then it bolts out of the storage room towards the front door. 
                ''')
        backpack.remove('Appetizing thighbone')
    elif 'Crowbar' in backpack.contents:
        game.ui.show('''
    You realize you could free the beast using your crowbar. However, it would be 
    extremely dangerous to approach the cage with the starving beast still inside.
    You are still missing a crucial item here.            
                ''')
    else:
        game.ui.show('\n    It seems you are missing a crucial item here.')


ROOM_EVENTS = {
    'Master bedroom': master_bedroom,
    'Childrens bedroom': childrens_bedroom,
    'Moldy hallway': moldy_hallway,
    'Storage room': storage_room,
}
