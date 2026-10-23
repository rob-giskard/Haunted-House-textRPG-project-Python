# Haunted-House-textRPG-project-Python

The game takes the player on a text based adventure situated in a haunted house.
Defeat monsters, loot treasures and collect keys to advance.

## How to run

You need Python 3 and nothing else (only the standard library is used).

```
python HauntedHouse.py
```

Or build **`HauntedHouse.exe`**, a standalone Windows version that needs nothing installed
(it carries its own Python). It is not committed to git, so build it yourself with
`tools/game-exe/build.sh` (see *Building the exes*). The first start takes a few seconds
while it unpacks Python into `%LOCALAPPDATA%\HauntedHouse`; after that it starts instantly.

Item colors use ANSI codes. They work in Windows Terminal, the classic Windows console,
macOS and Linux terminals.

## Controls

Everything is done by typing the **first letter** of what you want and pressing Enter.

| Where | Input | Action |
|---|---|---|
| In a room | first letter of an object | search it (it may be trapped) |
| In a room | `B` | open your backpack and use items |
| In a room | `R` | leave the room and pick a direction |
| In a room | `E` | escape the house screaming (ends the game) |
| Moving | `N` / `S` / `E` / `W` | walk in that direction |
| Backpack | first letter of an item | use it |
| Backpack | `P` | read your PST (Personal Statistics Tracker) |
| Backpack | `C` | close the backpack |
| Combat | `F` / `U` | fight or use an item |
| Combat | `F` / `A` / `R` / `S` | choose Fists, Axe, Revolver or Shotgun |

## Goal

Explore the house, collect treasure and get out alive. You can leave at any time
through the front door (south of the Foyer) or by escaping from any room.
How well you did depends on three things:

- **Treasure** you carry out
- **Good deeds** you accomplish (0 to 3)
- **Survival**: if the house kills you, the treasure stays lost

Every ending shows a **Game Over** screen with your final stats (outcome, health,
condition, monsters defeated, keys found, good deeds, items collected, ammo left)
and waits for Enter before closing.

## Gameplay

### Exploring and looting
Each room has a description and up to four objects to search. Everything you find
goes into your backpack; bullets and shotgun shells go straight into your ammo count.
Each object has roughly a 60% chance to be **trapped**:

| Trap | Damage |
|---|---|
| Dart trap | 4 |
| Poison gas | 8 |
| Explosion | 12 |

A trap only hurts you if its attack roll beats your armor.

Item colors: **yellow** = keys, **blue** = healing items, **red** = ammo and combat items.

### Locked doors
- The **Laboratory** door is nailed shut and the **Ball room** door is jammed. Both need a **Crowbar**.
- The **Safe** has four locks. You need all **four keys** (Brass, Silver, Copper, Iron).
  The keys are hidden in random objects around the house every game, and all four are
  always placed somewhere you can reach.

### Combat
After each move there is about a 1 in 5 chance that a monster attacks. There are 24
different monsters and each appears at most once per game (except the Generic villain).
Every monster has 18 HP.

Each round both sides roll a d20 for initiative:
- **You win:** choose to fight or use an item. Using an item takes your turn, so the
  monster strikes back, unless you stunned it with a flashbang, in which case you get a free attack.
- **The monster wins:** it attacks first, then you strike back.

| Weapon | Damage | Ammo |
|---|---|---|
| Fists | 1–6 | none |
| Axe | 4–10 | none |
| Revolver pistol | 10–16 | bullets (you start with 6) |
| Shotgun | 18–20 | shotgun shells (you start with 0) |

When a gun runs dry mid-fight you are asked to switch weapons.

### Your character
You start with **50 HP** and **armor class 12**. Monsters hit for 2–10 damage.

| Usable item | Effect |
|---|---|
| Bandage | heals 6–12 HP |
| Hardtack | heals 2 HP |
| Antidote | cures poison |
| Flashbang | stuns a monster for one round (don't use it outside combat) |
| Mysterious glass vial | better not... |

### Poison
The spores in the **Moldy hallway** poison you. While poisoned you lose 3 HP every time
you leave a room, until you drink an antidote. Poison can kill you.

### Good deeds
Three restless spirits can be put at peace, each by bringing the right two items to the
right room. Solving all three earns a special ending.

<details>
<summary>Spoilers: how to solve the good deeds</summary>

- **Lord and lady Durst:** bring the *Severed head of lady Durst* (Kitchen) and the
  *Remains of Catherine Durst* (Safe) to the Master bedroom.
- **Benjamin:** bring the *Photograph of Benjamin Durst* (Short hallway) and the
  *Brown teddy bear* (Gallery S) to the Children's bedroom.
- **The caged beast:** bring a *Crowbar* (Kitchen) and the *Appetizing thighbone*
  (Ball room) to the Storage room.

</details>

## Autoplay: the 100% walkthrough

`walkthrough.txt` is a list of commands that completes everything the game has to offer:
all 25 rooms visited, every object searched, all 4 keys found, the Safe opened,
all 3 good deeds done, and an escape with the treasure (5 monsters defeated on the way).

The game is random, so the walkthrough starts with a `seed:` line that fixes the dice.
The same seed plus the same commands always gives the same game. Typing the commands
into a normal game won't work, because that game rolls different dice.

To watch it play, run `python autoplay.py`, or double-click **`HauntedHouseAutoplay.exe`**
(build it with `tools/autoplay-exe/build.sh`; it is not stored in git). It types each command
for you and hands control back at the end. The exe needs Python 3 installed and looks for
`HauntedHouse.py`, the `haunted_house` folder and `walkthrough.txt` next to itself. From a terminal you can also
change the speed or use another walkthrough:

```
HauntedHouseAutoplay.exe --fast
HauntedHouseAutoplay.exe --delay 1
HauntedHouseAutoplay.exe my_walkthrough.txt
python autoplay.py --fast          (same tool without the exe)
```

Walkthrough format: one command per line, `#` starts a comment, and one `seed: N` line.

> **Note:** the walkthrough matches the current version of the game. Any change that
> affects the dice or the rooms (new items, containers, monsters...) means it has to be
> regenerated.

Windows may show a SmartScreen warning the first time, because the exe isn't signed.
Choose *More info → Run anyway*, or use `python autoplay.py` instead.

## The house

`HousePlan.py` draws a floor plan of the house. It is a standalone script and is not
used by the game yet; it is the starting point for an in-game map. Run it with
`python HousePlan.py`:

```
-----------------------------------------------------------------------
|  Flor1  |         |         |         |         |         |         |
|---------------------------------------------------------------------|
|         |         |         |         |         |         |         |
|---------------------------------------------------------------------|
|         |         |  Storg  |  LoHal  |  Stair  |         |         |
|---------------------------------------------------------------------|
|         |         |         |  Kitch  |         |         |         |
|---------------------------------------------------------------------|
|         |         |         |  ShHal  |  Lab    |  SecSt  |         |
|---------------------------------------------------------------------|
|         |  BallR  |  DrawR  |  GrHal  |         |         |         |
|---------------------------------------------------------------------|
|         |         |         |  Foyer  |         |         |         |
-----------------------------------------------------------------------


-----------------------------------------------------------------------
|  Flor2  |         |         |         |         |         |         |
|---------------------------------------------------------------------|
|         |         |         |         |         |         |         |
|---------------------------------------------------------------------|
|         |         |         |         |         |         |         |
|---------------------------------------------------------------------|
|         |         |  ChldB  |         |  MoHal  |         |         |
|---------------------------------------------------------------------|
|         |         |  GalNW  |  GalN   |  GalNE  |         |  Safe   |
|---------------------------------------------------------------------|
|         |  MstrB  |  GalW   |         |  GalE   |  Study  |  Vault  |
|---------------------------------------------------------------------|
|         |         |  GalSW  |  GalS   |  GalSE  |         |         |
-----------------------------------------------------------------------
```

| Code | Room | Code | Room |
|---|---|---|---|
| Foyer | Foyer (entrance) | MoHal | Moldy hallway |
| GrHal | Grand hall | GalN/NE/E/SE/S/SW/W/NW | Gallery sections |
| DrawR | Drawing room | ChldB | Children's bedroom |
| BallR | Ball room | MstrB | Master bedroom |
| ShHal | Short hallway | Study | Study |
| Lab | Laboratory | Vault | Vault |
| SecSt | Secret stairs | Safe | Safe |
| Kitch | Kitchen | | |
| LoHal | Long hallway | | |
| Storg | Storage room | | |
| Stair | Stairs | | |

North is up. The empty square in the middle of the second floor is the open space above
the Grand hall, ringed by the gallery. The floors connect in two places: the **Stairs**
lead down south into the Moldy hallway, and the **Secret stairs** lead east into the Safe.

## Project structure

```
HauntedHouse.py          start the game here
haunted_house/           the game itself
    data.py              all game content: rooms, objects, items, creatures, weapons, traps
    game.py              Game class: sets up a fresh house, main loop, ending and final stats
    entities.py          Entity (monsters) and Player
    world.py             Location (rooms) and Container (objects and the backpack)
    events.py            special room events: the good deeds and the poison
    combat.py            ambushes and fights
    ui.py                how the game talks to the player (console, scripted, ...)
    colors.py            terminal colors
HousePlan.py             draws the floor plan from data.py
autoplay.py              plays the game from a walkthrough file
walkthrough.txt          seeded command list that completes 100% of the game
run_tests.py             runs all tests and appends the results to the statistics sheet
run_tests.bat            the same, by double-clicking on Windows
tests/                   the tests (see Testing below)
tools/game-exe/          builds HauntedHouse.exe (standalone, Python bundled)
tools/autoplay-exe/      builds HauntedHouseAutoplay.exe
CHANGELOG.md             what changed, step by step
```

### How the code fits together

`HauntedHouse.py` creates a `Game` and runs it. The `Game` object holds everything one
playthrough needs: the player, the backpack, the rooms, the creatures that haven't appeared
yet and the doors that have been opened. There are no global variables.

The game never calls `print()` or `input()` itself. It uses a UI object with two methods,
`show(text)` and `ask(prompt)`. `ConsoleUI` plays in the terminal; the tests use `ScriptedUI`
to play a list of commands and read back everything the game showed; autoplay has its own UI
that types the walkthrough. A graphical interface will be another UI with the same two methods.

```python
from haunted_house.game import Game
from haunted_house.ui import ScriptedUI

ui = ScriptedUI(['Tester', 'e', ''])     # name, escape, press Enter
Game(ui=ui, seed=1).run()
print(ui.text())
```

To add content (a room, an item, a creature), edit `haunted_house/data.py`; the comments there
explain the format. Then run the tests.

### Building the exes

Both exes are git-ignored; build them when you need them (needs Go; on Windows use Git Bash):

- `tools/game-exe/build.sh` → `HauntedHouse.exe`: downloads a portable Windows Python, trims it,
  bundles it with the current game files and builds the exe (also needs curl and Python).
  Rebuild after every game change.
- `tools/autoplay-exe/build.sh` → `HauntedHouseAutoplay.exe`: copies the current `autoplay.py`
  in and builds the exe.

## Testing

Run all tests with:

```
python run_tests.py
```

or double-click `run_tests.bat` on Windows. Only the standard library is needed (the tests
also work with `python -m unittest discover -s tests` or pytest).

| Test file | What it checks |
|---|---|
| `test_data.py` | the content: exits lead somewhere and work both ways, positions match the floor plan, object letters are valid, the house can be completed (crowbar reachable, keys outside the Safe) |
| `test_mechanics.py` | keys, looting, colors, traps, every usable item, poison, locked doors, the three good deeds, monsters, initiative |
| `test_combat.py` | fight turns, items in combat, flashbang stuns, running out of ammo, dying in combat |
| `test_endings.py` | every ending (escape, front door, vial, trap, combat, poison) shows Game Over and the final stats and waits for Enter |
| `test_walkthrough.py` | `walkthrough.txt` still completes 100% of the game |
| `test_snapshots.py` | 60 recorded games still play out with exactly the same text |
| `test_simulation.py` | a bot plays 200 new random games per run and nothing ever breaks |
| `test_entry_points.py` | `HauntedHouse.py`, `autoplay.py` and `HousePlan.py` start and finish as real programs |

Options:

```
python run_tests.py --quick             skip the simulation and entry-point tests
python run_tests.py --games 1000        simulate more games
python run_tests.py --seed 783148       replay the simulated games of an earlier run
python run_tests.py --update-snapshots  accept an on-purpose change to the game's text or behaviour
```

### The statistics sheet

Every run appends a row to **`tests/stats/test_runs.csv`** (it opens in Excel). Besides the test
results (passed, failed, duration, which tests failed) it records fun facts from the simulated
games: how often the bot finished 100%, what killed it (monsters, traps, poison), the deadliest
thing in the house, the most common monster, traps sprung, damage taken, the fastest 100% run and
the luckiest seed. Any seed in the sheet can be replayed with `Game(seed=...)`.

The sheet uses `;` as separator with a `sep=;` first line, so Excel opens it correctly with any
regional settings.

> If you change the game on purpose, two tests will tell you: the walkthrough needs regenerating
> if the dice or rooms changed, and `python run_tests.py --update-snapshots` accepts new text.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for every change, step by step.

## Known limitations

- Your attacks always hit: monsters have armor class 10 and your attack roll is fixed at 11 or 13.
- All monsters share the same stats (18 HP, armor class 10).
- Object names in a room must start with different letters, and not with B, R or E,
  because those letters are used for the backpack, leaving and escaping.

## Roadmap

Done:

1. ~~Move the game content into its own file~~ (`haunted_house/data.py`)
2. ~~Split the game into modules and remove global variables~~
3. ~~Put input and output behind an interface~~ (`haunted_house/ui.py`)

Next:

4. Make the game command-driven: one method that takes a single command and returns what to
   show, instead of loops that wait inside `ask()`. Graphical interfaces work this way.
5. Simple graphical interface (tkinter) with a live map built from the room positions,
   an inventory panel and a stats bar
