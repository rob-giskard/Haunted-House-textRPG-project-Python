"""Runs all tests for Haunted House and appends the results to tests/stats/test_runs.csv.

Usage:
    python run_tests.py                     all tests, 200 simulated bot games
    python run_tests.py --games 1000        more simulated games (more fun statistics)
    python run_tests.py --quick             skip the slower tests (simulation and entry points)
    python run_tests.py --seed 12345        replay the simulated games of an earlier run
    python run_tests.py --update-snapshots  accept on-purpose changes to the game's text/behaviour

Only the Python standard library is needed. On Windows you can also double-click run_tests.bat.
"""
import argparse
import csv
import datetime
import os
import platform
import sys
import time
import unittest
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.join(ROOT, 'tests')
SHEET = os.path.join(TESTS, 'stats', 'test_runs.csv')

COLUMNS = [
    'date', 'time', 'python', 'system', 'result', 'tests_run', 'passed', 'failed', 'errors', 'skipped',
    'duration_s', 'failing_tests',
    'games_simulated', 'first_seed', 'completed_100pct', 'completion_rate_pct', 'survived', 'died',
    'killed_by_monsters', 'killed_by_traps', 'killed_by_poison',
    'deadliest_thing', 'deadliest_thing_kills', 'most_met_monster', 'monsters_fought', 'monsters_defeated',
    'traps_triggered', 'damage_taken_total', 'avg_damage_per_game', 'avg_commands_per_game',
    'fastest_100pct_commands', 'fastest_100pct_seed', 'luckiest_seed', 'luckiest_seed_hp',
    'quickest_death_commands', 'quickest_death_seed', 'quickest_death_by', 'treasure_items_carried_out',
]


class CountingResult(unittest.TextTestResult):
    """Remembers the names of passed tests too, to count them."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test)


def fun_stats(results, first_seed):
    if not results:
        return {}
    complete = [r for r in results if r['complete']]
    dead = [r for r in results if not r['alive']]
    killers = Counter(r['killed_by'] for r in dead)
    met = Counter(m for r in results for m in r['monsters_met'])
    # the Generic villain can appear again and again, so leave it out of "most common"
    met_once = Counter({m: n for m, n in met.items() if m != 'Generic villain'})
    damage = sum(r['damage_taken'] for r in results)
    fastest = min(complete, key=lambda r: r['commands']) if complete else None
    luckiest = max(complete, key=lambda r: r['final_hp']) if complete else None
    quickest_death = min(dead, key=lambda r: r['commands']) if dead else None
    causes = Counter(r['death_cause'] for r in dead)
    return {
        'games_simulated': len(results),
        'first_seed': first_seed,
        'completed_100pct': len(complete),
        'completion_rate_pct': round(100 * len(complete) / len(results)),
        'survived': len(results) - len(dead),
        'died': len(dead),
        'killed_by_monsters': causes['monster'],
        'killed_by_traps': causes['trap'],
        'killed_by_poison': causes['poison'],
        'deadliest_thing': killers.most_common(1)[0][0] if killers else '',
        'deadliest_thing_kills': killers.most_common(1)[0][1] if killers else 0,
        'most_met_monster': met_once.most_common(1)[0][0] if met_once else '',
        'monsters_fought': sum(met.values()),
        'monsters_defeated': sum(r['kills'] for r in results),
        'traps_triggered': sum(r['traps_triggered'] for r in results),
        'damage_taken_total': damage,
        'avg_damage_per_game': round(damage / len(results)),
        'avg_commands_per_game': round(sum(r['commands'] for r in results) / len(results)),
        'fastest_100pct_commands': fastest['commands'] if fastest else '',
        'fastest_100pct_seed': fastest['seed'] if fastest else '',
        'luckiest_seed': luckiest['seed'] if luckiest else '',
        'luckiest_seed_hp': luckiest['final_hp'] if luckiest else '',
        'quickest_death_commands': quickest_death['commands'] if quickest_death else '',
        'quickest_death_seed': quickest_death['seed'] if quickest_death else '',
        'quickest_death_by': quickest_death['killed_by'] if quickest_death else '',
        'treasure_items_carried_out': sum(r['treasure'] for r in results if r['alive']),
    }


def append_row(row):
    """Adds one row to the sheet. It uses ; as separator plus a 'sep=;' first line,
    so Excel opens it correctly whatever your regional settings are."""
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    new_file = not os.path.exists(SHEET)
    with open(SHEET, 'a', newline='', encoding='utf-8') as f:
        if new_file:
            f.write('sep=;\n')
        writer = csv.DictWriter(f, fieldnames=COLUMNS, delimiter=';', extrasaction='ignore')
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def count_runs():
    if not os.path.exists(SHEET):
        return 0
    with open(SHEET, encoding='utf-8') as f:
        return max(sum(1 for _ in f) - 2, 0)


def main():
    parser = argparse.ArgumentParser(description='Run the Haunted House tests.')
    parser.add_argument('--games', type=int, default=200, help='simulated bot games (default 200)')
    parser.add_argument('--quick', action='store_true', help='skip the simulation and entry-point tests')
    parser.add_argument('--seed', type=int, default=0, help='first seed of the simulated games')
    parser.add_argument('--update-snapshots', action='store_true', help='accept on-purpose game changes')
    parser.add_argument('--no-sheet', action='store_true', help="don't append to the statistics sheet")
    args = parser.parse_args()

    os.system('')  # colors in the classic Windows console
    sys.path.insert(0, TESTS)
    os.environ['HH_SIM_GAMES'] = str(args.games)
    if args.seed:
        os.environ['HH_SIM_SEED'] = str(args.seed)

    if args.update_snapshots:
        import test_snapshots
        changed, total = test_snapshots.update_snapshots()
        print('Snapshots updated: %d of %d recorded games now play differently.' % (changed, total))
        print('Run the tests again to check everything else still passes.')
        return 0

    loader = unittest.TestLoader()
    suite = loader.discover(TESTS, top_level_dir=TESTS)
    if args.quick:
        quick = unittest.TestSuite()
        for group in suite:
            for case_group in group:
                for test in getattr(case_group, '_tests', [case_group]):
                    if not any(slow in test.id() for slow in ('test_simulation', 'test_entry_points')):
                        quick.addTest(test)
        suite = quick

    print('Haunted House tests\n')
    start = time.time()
    runner = unittest.TextTestRunner(verbosity=1, resultclass=CountingResult)
    result = runner.run(suite)
    duration = time.time() - start

    sim = sys.modules.get('test_simulation')
    results = sim.RESULTS if sim else []
    stats = fun_stats(results, sim.FIRST_SEED if sim else '')

    failing = [t.id().split('.', 1)[-1] for t, _ in result.failures + result.errors]
    now = datetime.datetime.now()
    row = {
        'date': now.strftime('%Y-%m-%d'),
        'time': now.strftime('%H:%M:%S'),
        'python': platform.python_version(),
        'system': platform.system(),
        'result': 'PASS' if result.wasSuccessful() else 'FAIL',
        'tests_run': result.testsRun,
        'passed': len(result.passed),
        'failed': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped),
        'duration_s': round(duration),
        'failing_tests': ', '.join(failing),
        **stats,
    }

    if stats:
        print('\nFun facts from %d simulated games (seeds %d-%d):' % (
            stats['games_simulated'], stats['first_seed'], stats['first_seed'] + stats['games_simulated'] - 1))
        print('  The bot finished 100%% of the game %d times (%d%%) and died %d times.' % (
            stats['completed_100pct'], stats['completion_rate_pct'], stats['died']))
        if stats['deadliest_thing']:
            print('  Deadliest thing in the house: %s (%d victims).' % (stats['deadliest_thing'], stats['deadliest_thing_kills']))
        print('  Most common monster: %s. Monsters fought: %d, defeated: %d.' % (
            stats['most_met_monster'], stats['monsters_fought'], stats['monsters_defeated']))
        print('  Traps sprung: %d. Damage taken: %d HP in total.' % (stats['traps_triggered'], stats['damage_taken_total']))
        if stats['fastest_100pct_seed'] != '':
            print('  Fastest 100%% run: %s commands (seed %s). Luckiest run: seed %s, %s HP left.' % (
                stats['fastest_100pct_commands'], stats['fastest_100pct_seed'], stats['luckiest_seed'], stats['luckiest_seed_hp']))
        if stats['quickest_death_seed'] != '':
            print('  Quickest death: %s commands in, by %s (seed %s).' % (
                stats['quickest_death_commands'], stats['quickest_death_by'], stats['quickest_death_seed']))

    if not args.no_sheet:
        append_row(row)
        print('\nRun #%d added to %s' % (count_runs(), os.path.relpath(SHEET, ROOT)))
    print('\nResult: %s (%d passed, %d failed, %d errors in %ds)' % (
        row['result'], row['passed'], row['failed'], row['errors'], row['duration_s']))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
