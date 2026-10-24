"""Haunted House with a graphical interface.

Double-click this file on Windows (no console window opens), or run:  python HauntedHouseGUI.pyw
The classic terminal version is still:  python HauntedHouse.py
"""
import os
import sys

# make the haunted_house package importable however this file is started
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from haunted_house.gui import main


if __name__ == '__main__':
    main()
