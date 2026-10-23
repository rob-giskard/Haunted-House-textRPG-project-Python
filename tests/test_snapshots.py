"""Snapshot tests: replays recorded games and checks the game still shows exactly the same text.

snapshots.json holds 60 recorded games (seed + every command typed) from three kinds of players:
a sensible bot, a random explorer and a key-masher. For each game it stores a fingerprint of
everything the game showed. Any change to the game's text or behaviour changes a fingerprint.

When you change the game ON PURPOSE (new text, new rooms, balance changes), refresh them with:
    python run_tests.py --update-snapshots
"""
import hashlib
import json
import os
import unittest

from helpers import play

SNAPSHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'snapshots.json')


def fingerprint(seed, commands):
    game, ui = play(commands, seed=seed, on_empty='')
    text = '\n'.join(line.rstrip() for line in ui.text().splitlines())
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def update_snapshots():
    with open(SNAPSHOTS, encoding='utf-8') as f:
        snapshots = json.load(f)
    changed = 0
    for snap in snapshots:
        new = fingerprint(snap['seed'], snap['commands'])
        changed += new != snap['fingerprint']
        snap['fingerprint'] = new
    save(snapshots)
    return changed, len(snapshots)


def save(snapshots):
    # one game per line keeps the file readable
    with open(SNAPSHOTS, 'w', encoding='utf-8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(s) for s in snapshots) + '\n]\n')


class TestSnapshots(unittest.TestCase):

    def test_recorded_games_play_out_exactly_the_same(self):
        with open(SNAPSHOTS, encoding='utf-8') as f:
            snapshots = json.load(f)
        self.assertGreater(len(snapshots), 0)
        for snap in snapshots:
            with self.subTest(game=snap['name']):
                self.assertEqual(fingerprint(snap['seed'], snap['commands']), snap['fingerprint'],
                                 'this game now plays differently - if that was on purpose, '
                                 'run: python run_tests.py --update-snapshots')


if __name__ == '__main__':
    unittest.main()
