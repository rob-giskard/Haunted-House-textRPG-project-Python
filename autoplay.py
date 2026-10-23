"""Autoplay for Haunted House.

Runs HauntedHouse.py and types the commands from a walkthrough file for you.
The walkthrough's "seed:" line fixes the game's dice, so the same commands
always lead to the same game. When the commands run out you get control back.

Usage:
    python autoplay.py [walkthrough.txt] [--delay SECONDS] [--fast] [--game PATH]

HauntedHouseAutoplay.exe runs this same script.
"""
import argparse
import builtins
import os
import random
import runpy
import sys
import time

GREEN = '\033[92m'
GREY = '\033[90m'
RESET = '\033[0m'


def read_walkthrough(path):
    seed = None
    commands = []
    with open(path, encoding='utf-8') as f:
        for number, line in enumerate(f, 1):
            text = line.split('#', 1)[0].strip()
            if not text:
                continue
            if text.lower().startswith('seed:'):
                seed = int(text.split(':', 1)[1])
            else:
                commands.append(text)
    if seed is None:
        sys.exit('[autoplay] ' + path + ' has no "seed:" line, so the game cannot be replayed.')
    return seed, commands


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description='Play Haunted House from a walkthrough file.')
    parser.add_argument('walkthrough', nargs='?', default=os.path.join(here, 'walkthrough.txt'))
    parser.add_argument('--game', default=os.path.join(here, 'HauntedHouse.py'))
    parser.add_argument('--delay', type=float, default=0.4, help='seconds between commands (default 0.4)')
    parser.add_argument('--fast', action='store_true', help='no delay between commands')
    args = parser.parse_args()
    delay = 0 if args.fast else args.delay

    os.system('')  # switch on ANSI colors in the classic Windows console
    for path in (args.walkthrough, args.game):
        if not os.path.isfile(path):
            sys.exit('[autoplay] File not found: ' + path)

    seed, commands = read_walkthrough(args.walkthrough)
    print(GREY + '[autoplay] ' + os.path.basename(args.walkthrough) + ': seed ' + str(seed)
          + ', ' + str(len(commands)) + ' commands. Press Ctrl+C to stop.' + RESET + '\n')

    real_input = builtins.input
    remaining = iter(commands)
    state = {'auto': True}

    def auto_input(prompt=''):
        if state['auto']:
            try:
                command = next(remaining)
            except StopIteration:
                state['auto'] = False
                print(GREY + '\n[autoplay] Walkthrough finished - you have control now.' + RESET)
                return real_input(prompt)
            sys.stdout.write(prompt)
            sys.stdout.flush()
            time.sleep(delay)
            print(GREEN + '> ' + command + RESET)
            time.sleep(delay)
            return command
        return real_input(prompt)

    builtins.input = auto_input
    random.seed(seed)
    game = os.path.abspath(args.game)
    os.chdir(os.path.dirname(game))
    sys.argv = [game]
    try:
        runpy.run_path(game, run_name='__main__')
    except KeyboardInterrupt:
        print(GREY + '\n[autoplay] Stopped.' + RESET)


if __name__ == '__main__':
    main()
