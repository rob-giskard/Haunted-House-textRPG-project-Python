# Changelog

All notable changes to Haunted House, newest first. Each section matches one step of the work.

## Step 5 - Tests and the statistics sheet

- New `tests/` folder with 75 tests (standard library only), run with `python run_tests.py`
  or by double-clicking `run_tests.bat`. They also work with `python -m unittest discover -s tests` and pytest.
  - `test_data.py` - the game content is consistent and the house can be completed
  - `test_mechanics.py` - keys, looting, colors, traps, items, poison, doors, good deeds, monsters
  - `test_combat.py` - fight turns, items in combat, ammo, dying
  - `test_endings.py` - every ending shows Game Over and the stats and waits for Enter
  - `test_walkthrough.py` - the walkthrough still completes 100%
  - `test_snapshots.py` - 60 recorded games still play out with exactly the same text
    (`python run_tests.py --update-snapshots` accepts on-purpose changes)
  - `test_simulation.py` - a bot plays 200 new random games every run
  - `test_entry_points.py` - the real programs start and finish
- Every run appends a row to `tests/stats/test_runs.csv`: test results plus fun facts from the
  simulated games (completion rate, causes of death, deadliest thing, most common monster,
  traps sprung, damage taken, fastest 100% run, luckiest and unluckiest seeds).
- `ScriptedUI` has a safety limit: a game stuck in a loop fails its test instead of hanging the test run.
- `.gitattributes` keeps `.bat` files with Windows line endings; both `build.sh` scripts are executable.
- README rewritten for the new structure: project layout, how the code fits together, testing,
  the statistics sheet, building the exes and the updated roadmap. The changelog moved here.

## Step 4 - Input and output behind an interface (roadmap step 3)

- New `haunted_house/ui.py`. The game no longer calls `print()` or `input()` anywhere; it calls
  `ui.show()` and `ui.ask()` on a UI object it is given:
  - `ConsoleUI` plays in the terminal (the default).
  - `ScriptedUI` plays a list of commands and records everything the game shows (used by the tests).
  - Anything else with `show()` and `ask()` can run the game - this is what the planned
    graphical interface will plug into.
- `Game(ui=..., seed=...)` takes the UI and the optional seed.
- `autoplay.py` now drives the game through its own `AutoplayUI` instead of patching Python's
  built-in `input()`. Its output is unchanged.
- `HauntedHouse.exe` now bundles the whole `haunted_house` package (packed into `game.zip` by
  `tools/game-exe/build.sh`) and unpacks each game version into its own folder.
- No gameplay changes: the same 380 recorded playthroughs give identical output.

## Step 3 - Split into modules, no more global variables (roadmap step 2)

- The game logic moved out of `HauntedHouse.py` into the `haunted_house` package:

  | Module | What it does |
  |---|---|
  | `game.py` | `Game` class: sets up a fresh house, runs the main loop, shows the ending and final stats |
  | `entities.py` | `Entity` (monsters) and `Player`: movement, items, weapons, taking damage |
  | `world.py` | `Location` (rooms) and `Container` (objects and the backpack), building rooms from `data.py`, hiding the keys |
  | `events.py` | special room events: the three good deeds and the poison in the Moldy hallway |
  | `combat.py` | random ambushes and fight rounds |
  | `colors.py` | terminal colors |

- `HauntedHouse.py` is now a short entry point that starts a `Game`. `python HauntedHouse.py` works as before.
- No global variables: one `Game` object holds the player, backpack, rooms, remaining creatures and
  opened doors, and everything that needs them gets them from there. The flashbang now stuns
  `game.monster` instead of relying on a global `monster` variable.
- Rooms keep their objects in a list instead of the copy-pasted `container0` to `container3`
  blocks (about 100 repeated lines removed).
- Opened doors (Laboratory, Ball room, Safe) are tracked in `game.opened_doors` instead of
  borrowing the `solved` flag of unrelated rooms.
- `Game(seed=...)` fixes the dice for a reproducible game (used by autoplay and the tests).
- The unused `rests()` and `is_immobilized()` are kept and marked "not used yet"; the empty
  `enters_location()` stub was removed.
- No gameplay changes: the same 380 recorded playthroughs give identical output.

## Step 2 - Game content moved into its own file (roadmap step 1)

- New package folder `haunted_house/`. Its `data.py` holds all game content: the 25 rooms
  (description, exits, objects and items, floor-plan label and position), the creatures,
  weapons, traps, keys and item categories.
- Room positions are now real `(floor, row, column)` values instead of strings like
  `'house.firstFloor[5][3]'`, ready for drawing a map.
- `HauntedHouse.py` builds the rooms from that data instead of 400 lines of hand-written
  dictionaries and `what_in_room` calls (1,160 lines down to about 740).
- `HousePlan.py` now draws the plan from `data.py`, so it can never drift out of sync with the
  game again. Its output is unchanged.
- No gameplay changes: 380 recorded playthroughs give exactly the same output as before.

## Step 1 - Cleanup

- `HauntedHouseAutoplay.exe` is no longer tracked by git (it is git-ignored like `HauntedHouse.exe`),
  so rebuilding it doesn't add megabytes to the repo history.
- `tools/autoplay-exe/autoplay.py` is no longer a hand-maintained duplicate: the new
  `tools/autoplay-exe/build.sh` copies the current `autoplay.py` in at build time (the copy is git-ignored).
- Typos fixed in game text: "immediately", "magnificent", "Although", "until it snaps",
  "The tight space", "This door seems", "addressed?", "of some sort", "Full of hope",
  "in several places", real apostrophes instead of backticks, and a stray quote in Barry's vault hint.
- Keys are recognised only by names ending in " key", so a future item like "Monkey paw"
  can't be mistaken for a vault key.

## Before the steps above

**Game update (bug fixes and tools)**
- Standalone `HauntedHouse.exe` build (bundles its own Python; git-ignored)
- 100% walkthrough (`walkthrough.txt`) and an autoplay tool (`HauntedHouseAutoplay.exe` / `autoplay.py`)
- Game over screen with final stats; the game waits for Enter instead of closing
- Item colors actually display (they used to print the word "yellow" next to the item)
- Monsters no longer repeat within one game
- Using an item in combat now costs your turn (flashbang stuns give a free attack instead)
- Quest items are used up when you complete a good deed instead of counting as treasure
- Fixed: the game crashed on entering the Laboratory
- Fixed: the Crowbar was locked inside the Laboratory, which itself needs the Crowbar to open (it now lies in the Kitchen)
- Fixed: the four vault keys were not always placed, so the Safe could be impossible to open
- Fixed: drinking the vial didn't end the game; typing "m" without the vial crashed it
- Fixed: trap names didn't match their damage, the poison death message used the room's name,
  escaping from a room required typing exactly "e", the Storage room said an item was missing
  even when you had both, and the item menu kept appearing after you ran out of items
- Initiative is a proper d20 (was 1-21); the Safe has its own map position

**Earlier**
- Ammunition system (shotgun shells and pistol bullets)
- Poisoned condition (tracked along other player statistics)
- Rooms with item requirements for progress
- Free player movement
