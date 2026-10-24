"""Reading walkthrough files: a "seed: N" line plus one command per line (# starts a comment)."""
import os

# walkthrough.txt sits next to HauntedHouse.py, one folder above this package
DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'walkthrough.txt')


def read_walkthrough(path=DEFAULT_PATH):
    """Returns (seed, commands). Raises ValueError if the file has no seed line."""
    seed, commands = None, []
    with open(path, encoding='utf-8') as f:
        for line in f:
            text = line.split('#', 1)[0].strip()
            if not text:
                continue
            if text.lower().startswith('seed:'):
                seed = int(text.split(':', 1)[1])
            else:
                commands.append(text)
    if seed is None:
        raise ValueError(os.path.basename(path) + ' has no "seed:" line, so the game cannot be replayed')
    return seed, commands
