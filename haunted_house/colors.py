"""Terminal colors (ANSI codes)."""
import os

# os.system('') switches on ANSI color support in the classic Windows console
os.system('')

COLORS = {'yellow': '\033[93m', 'blue': '\033[94m', 'red': '\033[91m'}


def colored(text, color):
    return COLORS[color] + text + '\033[0m'
