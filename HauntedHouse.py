"""Haunted House - a text adventure in a haunted mansion, played in a window.

Run it with:            python HauntedHouse.py
Watch the walkthrough:  python HauntedHouse.py --autoplay [walkthrough.txt] [--delay SECONDS]

HauntedHouse.exe (built with tools/game-exe/build.sh) starts this same file.

The game lives in the haunted_house package:
    data.py        all game content (rooms, items, creatures, weapons, traps)
    game.py        the Game class: setup, main loop, ending
    entities.py    monsters and the player
    world.py       rooms and containers
    events.py      special room events (good deeds, poison)
    combat.py      encounters and fights
    gui.py         the window
    gui_state.py   what the window shows, and the bridge to the game
    ui.py          the interface between the game and whatever shows it
    walkthrough.py reading walkthrough files
    colors.py      text colors
"""
import argparse
import os
import sys

# make the haunted_house package importable however this file is started
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from haunted_house.walkthrough import DEFAULT_PATH


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Haunted House - a text adventure in a haunted mansion.')
    parser.add_argument('--autoplay', nargs='?', const=DEFAULT_PATH, metavar='WALKTHROUGH',
                        help='replay a walkthrough in the window (default: walkthrough.txt)')
    parser.add_argument('--delay', type=float, default=0.4,
                        help='seconds between autoplay commands (default 0.4)')
    return parser.parse_args(argv)


if __name__ == '__main__':
    args = parse_args()
    from haunted_house.gui import main
    main(autoplay=args.autoplay, delay=args.delay)
