"""All of the game's content: rooms, objects, creatures, weapons and traps.

Everything the player can find or meet lives here, separate from the game logic,
so new content can be added without touching the code that runs the game.
"""

# ROOMS
# Each room has:
#   map_code    - short label used on the floor plan (HousePlan.py)
#   position    - (floor, row, column) on the 7x7 floor plan; floor 1 or 2, row 0 is north
#   description - printed when the player enters
#   exits       - what lies NORTH/SOUTH/EAST/WEST: another room, a Wall, a Railing or Outside
#   containers  - up to 4 objects to search and the items inside them. Object names must
#                 start with different letters, and not with B, R or E (used for Backpack,
#                 Room and Escape)
# The order of rooms and containers matters: it decides where the random keys end up.
ROOMS = {
    'Foyer': {
        'map_code': 'Foyer',
        'position': (1, 6, 3),
        'description': '''
    You enter the foyer and immediately realize you are definitely 
    the first guest to do so after very many years. Dust covers 
    every nook and cranny, the floral-patterned drapes are long gone, 
    succeeded by mere strips of moth-eaten cloth ominously moving 
    in the cold breeze you let in through the front door. 
    The smell of mildew attacks your nostrils. 
    ''',
        'exits': {'NORTH': 'Grand hall', 'SOUTH': 'Outside', 'EAST': 'Wall', 'WEST': 'Wall'},
        'containers': {
            'Painting of lady and lord Durst': ['Bleached letter'],
            'Wardrobe': ['Bandage', 'Dusty duster'],
        },
    },
    'Grand hall': {
        'map_code': 'GrHal',
        'position': (1, 5, 3),
        'description': '''
    You find yourself in a huge open space. The floor is marble, the walls 
    covered in wooden mosaic tiles. A wide gallery runs around the hall 
    on the second floor and a majestic chandelier hangs above your head.
    However, the lightbulbs are long gone and shadows reign all around.
    ''',
        'exits': {'NORTH': 'Short hallway', 'SOUTH': 'Foyer', 'EAST': 'Wall', 'WEST': 'Drawing room'},
        'containers': {
            'Weapon cabinet': ['Flashbang', 'Rusty nail', 'Shotgun shell'],
            'Iron lockbox': ['Bag of coins', 'Polished emerald'],
            'Antique vase': ['Dried tulips', 'Wasp nest'],
        },
    },
    'Drawing room': {
        'map_code': 'DrawR',
        'position': (1, 5, 2),
        'description': '''
    This formally decorated place was undoubtedly used for greeting the guests
    of the house. A huge sofa and two massive armchairs surround a coffee table.
    A huge brown bear skin rug faces an open fireplace. To your surprise, 
    the room feels really cozy.  
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Wall', 'EAST': 'Grand hall', 'WEST': 'Ball room'},
        'containers': {
            'Porcelain teapot': ['Dead cockroach'],
            'Cigar box': ['Soaked cigar', 'Silver lighter'],
        },
    },
    'Ball room': {
        'map_code': 'BallR',
        'position': (1, 5, 1),
        'description': '''
    This vast space was once full of happy people. Now only bones litter the dance floor.
    Many of them bear toothmarks of tiny rodents.  
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Wall', 'EAST': 'Drawing room', 'WEST': 'Wall'},
        'containers': {
            'Old piano': ['Sheet music: "Lullaby for Lloyd"'],
            'Pile of bones': ['Diamond ring', 'Appetizing thighbone'],
        },
    },
    'Short hallway': {
        'map_code': 'ShHal',
        'position': (1, 4, 3),
        'description': '''
    The decor of the space around you tells a tale of a once proud family.
    Several framed photographs hang on the walls, each depicting a person
    of high status. However, time has manifested itself on the pictures
    and the faces looking back at you are downright ghastly. 
    ''',
        'exits': {'NORTH': 'Kitchen', 'SOUTH': 'Grand hall', 'EAST': 'Laboratory', 'WEST': 'Wall'},
        'containers': {
            'Ornate picture frame': ['Photograph of Benjamin Durst'],
        },
    },
    'Laboratory': {
        'map_code': 'Lab',
        'position': (1, 4, 4),
        'description': '''
    The tight space around you is cluttered with alchemical supplies 
    and strange contraptions. A number of jars sit on dusty shelves, each
    containing unknown substances.
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Wall', 'EAST': 'Secret stairs', 'WEST': 'Short hallway'},
        'containers': {
            'Wooden box': ['Bandage'],
            'Leather case': ['Mysterious glass vial', 'Antidote', 'Bandage'],
            'Shelf': ['Aged wine', 'Potion'],
        },
    },
    'Secret stairs': {
        'map_code': 'SecSt',
        'position': (1, 4, 5),
        'description': '''
    This secret stairway was probably used exclusively by the owners of the house 
    for quick and discreet movement through the innards of their home.
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Wall', 'EAST': 'Safe', 'WEST': 'Laboratory'},
        'containers': {
            'Hidden stash': ['Bullet', 'Shotgun shell', 'Hardtack'],
        },
    },
    'Kitchen': {
        'map_code': 'Kitch',
        'position': (1, 3, 3),
        'description': '''
    The lady of this house loved cooking. This fact is made known by a myriad
    of pans, pots and tools hanging all around the spacious kitchen. However, 
    rat droppings decorate most of the working surfaces now and you smell
    a foul stench of decomposing ingredients.
    ''',
        'exits': {'NORTH': 'Long hallway', 'SOUTH': 'Short hallway', 'EAST': 'Wall', 'WEST': 'Wall'},
        'containers': {
            'Shabby cupboard': ['Bandage', 'Worm-ridden bag of flour'],
            'Wooden box': ['Sack of turnips', 'Bunch of carrots'],
            'Kitchen counter': ['Severed head of lady Durst'],
            'Toolbox': ['Crowbar', 'Screwdriver'],
        },
    },
    'Long hallway': {
        'map_code': 'LoHal',
        'position': (1, 2, 3),
        'description': '''
    Walking along a carpeted hallway you notice a secret compartment behind rotten wallpaper.
    At the end of the hallway you find two doors. Soft growling can be heard from behind 
    the one on the left. This door seems to be reinforced with metal sheets. The door on 
    the right is covered in dark burgundy spots of dried blood.
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Kitchen', 'EAST': 'Stairs', 'WEST': 'Storage room'},
        'containers': {
            'Painting of a landscape': ['"Merry marshes" by Catherine Durst: oil on canvas'],
            'Secret stash': ['Huge ruby', 'Bloody ringfinger', 'Bullet'],
            'First aid lockbox': ['Bandage', 'Bandage', 'Antidote'],
        },
    },
    'Stairs': {
        'map_code': 'Stair',
        'position': (1, 2, 4),
        'description': '''
    The stairs are in a poor condition. Watch your step.
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Moldy hallway', 'EAST': 'Wall', 'WEST': 'Long hallway'},
        'containers': {},
    },
    'Storage room': {
        'map_code': 'Storg',
        'position': (1, 2, 2),
        'description': '''
    You open the door to a small storage room.
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Wall', 'EAST': 'Long hallway', 'WEST': 'Wall'},
        'containers': {
            'Old backpack': ['Shotgun shell', 'Antidote', 'Ancient coin', 'Hardtack', 'Hardtack'],
        },
    },
    'Moldy hallway': {
        'map_code': 'MoHal',
        'position': (2, 3, 4),
        'description': '''
    The roof is leaking somewhere above this hallway. The walls are covered by 
    a thick layer of mold and the air is filled with spores. 
    ''',
        'exits': {'NORTH': 'Stairs', 'SOUTH': 'Gallery NE', 'EAST': 'Wall', 'WEST': 'Wall'},
        'containers': {},
    },
    'Gallery NE': {
        'map_code': 'GalNE',
        'position': (2, 4, 4),
        'description': '''
    The gallery runs in a circle above the grand hall. The space around
    you is dominated by thick spiderwebs. 
    ''',
        'exits': {'NORTH': 'Moldy hallway', 'SOUTH': 'Gallery E', 'EAST': 'Wall', 'WEST': 'Gallery N'},
        'containers': {
            'Huge cocoon': ['Slimy eggsack', 'Half-digested cat'],
            'Small cocoon': ['Black sludge'],
            'Web-covered display case': ['Shotgun shell', 'Ceremonial dagger', 'Tribal leather bracelet'],
            'Loose brick': ['Dead rat'],
        },
    },
    'Gallery E': {
        'map_code': 'GalE',
        'position': (2, 5, 4),
        'description': '''
    The gallery overlooks the grand hall. The space around you is dominated by thick spiderwebs. 
    ''',
        'exits': {'NORTH': 'Gallery NE', 'SOUTH': 'Gallery SE', 'EAST': 'Study', 'WEST': 'Railing'},
        'containers': {
            'Small cocoon': ['Spiderling'],
        },
    },
    'Gallery SE': {
        'map_code': 'GalSE',
        'position': (2, 6, 4),
        'description': '''
    The gallery overlooks the grand hall. The space around you is dominated by thick spiderwebs. 
    ''',
        'exits': {'NORTH': 'Gallery E', 'SOUTH': 'Wall', 'EAST': 'Wall', 'WEST': 'Gallery S'},
        'containers': {},
    },
    'Gallery S': {
        'map_code': 'GalS',
        'position': (2, 6, 3),
        'description': '''
    This section of the gallery has stained-glass windows looking out on the front yard. 
    You see two children standing there, looking at you silently. You blink and they are gone. 
    ''',
        'exits': {'NORTH': 'Railing', 'SOUTH': 'Wall', 'EAST': 'Gallery SE', 'WEST': 'Gallery SW'},
        'containers': {
            'Web-covered shoe box': ['Brown teddy bear'],
        },
    },
    'Gallery SW': {
        'map_code': 'GalSW',
        'position': (2, 6, 2),
        'description': '''
    The west side of the gallery seems to be in a particularly bad shape. Almost looks like
    somebody destroyed the furniture with an axe, crushed the walls with a sledgehammer.    
    ''',
        'exits': {'NORTH': 'Gallery W', 'SOUTH': 'Wall', 'EAST': 'Gallery S', 'WEST': 'Wall'},
        'containers': {
            'Destroyed display cabinet': ['Golden necklace'],
        },
    },
    'Gallery W': {
        'map_code': 'GalW',
        'position': (2, 5, 2),
        'description': '''
    This section of the gallery is littered with rubble. 
    ''',
        'exits': {'NORTH': 'Gallery NW', 'SOUTH': 'Gallery SW', 'EAST': 'Railing', 'WEST': 'Master bedroom'},
        'containers': {},
    },
    'Master bedroom': {
        'map_code': 'MstrB',
        'position': (2, 5, 1),
        'description': '''
    The master bedroom is full of decadent luxury. Although everything is covered 
    under a thick layer of dust, the space resembles a king's suite. A person is
    lying in the huge bed. At closer inspection you realize it is in fact a well 
    preserved body of an older gentleman with two coins placed on his closed eyes.  
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Wall', 'EAST': 'Gallery W', 'WEST': 'Wall'},
        'containers': {},
    },
    'Childrens bedroom': {
        'map_code': 'ChldB',
        'position': (2, 3, 2),
        'description': '''
    Two small beds sit in the corners of this room. A small library with fairy-tale
    books also contains several empty picture frames and a ragged doll is discarded
    in the middle of the room. You notice smears of dried blood in several places 
    around you. 
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Gallery NW', 'EAST': 'Wall', 'WEST': 'Wall'},
        'containers': {
            'Toy chest': ['Wooden train', 'Tea set'],
            'Shoebox': ['Deck of playing cards', 'Bandage'],
        },
    },
    'Gallery NW': {
        'map_code': 'GalNW',
        'position': (2, 4, 2),
        'description': '''
    This section of the gallery is littered with rubble. 
    ''',
        'exits': {'NORTH': 'Childrens bedroom', 'SOUTH': 'Gallery W', 'EAST': 'Gallery N', 'WEST': 'Wall'},
        'containers': {},
    },
    'Gallery N': {
        'map_code': 'GalN',
        'position': (2, 4, 3),
        'description': '''
    This section of the gallery is littered with rubble. 
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Railing', 'EAST': 'Gallery NE', 'WEST': 'Gallery NW'},
        'containers': {
            'Discarded holster': ['Bandage', 'Shotgun shell'],
        },
    },
    'Study': {
        'map_code': 'Study',
        'position': (2, 5, 5),
        'description': '''
    The Study greets you with a smell of old parchment and cinnamon. Shelves full 
    of leather-bound books line the walls, the massive oaken table is covered 
    with dripped candle wax. You walk across the study on a thick red carpet.
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Wall', 'EAST': 'Vault', 'WEST': 'Gallery E'},
        'containers': {
            'Painting of a city panorama': ['"Smothering smog" by Catherine Durst: oil on canvas'],
            'Iron lockbox': ['Shotgun shell', 'Bullet', 'Bullet', 'Steel arrowhead'],
            'Shelves': ['"The king in yellow"', '"Victorian handbook of poisons"'],
        },
    },
    'Vault': {
        'map_code': 'Vault',
        'position': (2, 5, 6),
        'description': '''
    You enter a small room dominated by magnificent steel doors in the north wall. 
    This has to be the vault. You see four keyholes before you.
    ''',
        'exits': {'NORTH': 'Safe', 'SOUTH': 'Wall', 'EAST': 'Wall', 'WEST': 'Study'},
        'containers': {
            'Old pouch': ['Strange rune'],
        },
    },
    'Safe': {
        'map_code': 'Safe',
        'position': (2, 4, 6),
        'description': '''
    You open all the locks and enter. The safe looks really impressive. Two display cases
    stand against the east and west walls, you see a huge treasure chest and something 
    resembling a coffin in the center of the room.
    ''',
        'exits': {'NORTH': 'Wall', 'SOUTH': 'Vault', 'EAST': 'Wall', 'WEST': 'Secret stairs'},
        'containers': {
            'Glass display case': ['Strange clockwork device'],
            'Ornate display case': ['Jade statue'],
            'Treasure chest': ['Pile of gold coins', 'Assortment of precious stones'],
            'Stone coffin': ['Remains of Catherine Durst', 'Blood-soaked handkerchief'],
        },
    },
}

# START
START_ROOM = 'Foyer'
PLAYER_HP = 50
PLAYER_AC = 12
STARTING_BULLETS = 6
STARTING_SHELLS = 0

# KEYS - all four are hidden in random containers at the start of every game
KEY_TYPES = ['Brass key', 'Silver key', 'Copper key', 'Iron key']
KEYS_NEEDED = 4
KEY_FREE_ROOMS = ['Vault', 'Safe']  # never hide keys behind the door they open

# CREATURES - each appears at most once per game, except the Generic villain
CREATURES = [
    'Groggy ghost', 'Blob of goo', 'Ghastly ghoul', 'Poltergeist',
    'Panting pirate', 'Sad vampire', 'Lidless eye', 'Moaning monster',
    'Chucking woodchuck', 'Batswarm', 'Striga', 'Besny havko',
    'Creepy doll', 'Axe murderer', 'Norman Bates', 'Starving servant',
    'Desperate tester', 'Gelatinous cube', 'Constrictor vine', 'Debilitating devil',
    'Promiscuous python', 'Flying falchion', 'Mysterious mist', 'Generic villain',
]
REPEATABLE_CREATURE = 'Generic villain'
MONSTER_HP = 18
MONSTER_AC = 10

# WEAPONS - damage range (min, max)
WEAPONS = {
    'Fists': (1, 6),
    'Axe': (4, 10),
    'Revolver pistol': (10, 16),
    'Shotgun': (18, 20),
}

# TRAPS - damage each trap deals when it hits
TRAPS = {'Dart trap': 4, 'Poison gas': 8, 'Explosion': 12}

# ITEMS
USABLE_ITEMS = ['Bandage', 'Flashbang', 'Hardtack', 'Antidote', 'Mysterious glass vial']
HEALING_ITEMS = ['Bandage', 'Hardtack', 'Antidote']   # shown in blue
COMBAT_ITEMS = ['Flashbang', 'Shotgun shell', 'Bullet', 'vial']   # shown in red (matched anywhere in the name)
STATS_TRACKER = 'PST: Personal Statistics Tracker'   # always in the backpack, never counts as treasure
