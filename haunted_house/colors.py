"""Text colors.

The game marks colored text with ANSI color codes (the same codes a terminal understands).
The window turns them into real colors when it shows the text.
"""

COLORS = {'yellow': '\033[93m', 'blue': '\033[94m', 'red': '\033[91m'}


def colored(text, color):
    return COLORS[color] + text + '\033[0m'
