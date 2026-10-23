"""Haunted House - a text adventure in a haunted mansion.

Run it with:  python HauntedHouse.py

The game lives in the haunted_house package:
    data.py      all game content (rooms, items, creatures, weapons, traps)
    game.py      the Game class: setup, main loop, ending
    entities.py  monsters and the player
    world.py     rooms and containers
    events.py    special room events (good deeds, poison)
    combat.py    encounters and fights
    colors.py    terminal colors
"""
import os
import sys

# make the haunted_house package importable however this file is started
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from haunted_house.game import Game


if __name__ == '__main__':
    Game().run()
