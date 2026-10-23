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
`tools/game-exe/build.sh` (see *Project structure*). The first start takes a few seconds
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

To watch it play, double-click **`HauntedHouseAutoplay.exe`**. It types each command
for you and hands control back at the end. It needs Python 3 installed and looks for
`HauntedHouse.py` and `walkthrough.txt` next to itself. From a terminal you can also
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

| File | Purpose |
|---|---|
| `HauntedHouse.py` | the whole game: classes (`Entity`, `Player`, `Container`, `Location`), combat, room data (`masterPlan`) and the main loop |
| `HousePlan.py` | standalone ASCII floor plan of both floors (not used by the game yet) |
| `walkthrough.txt` | seeded command list that completes 100% of the game |
| `autoplay.py` | plays the game from a walkthrough file |
| `HauntedHouseAutoplay.exe` | Windows launcher for `autoplay.py` (needs Python 3 installed) |
| `HauntedHouse.exe` | standalone Windows build of the game with Python bundled (git-ignored, ~10 MB) |
| `tools/game-exe/` | Go source of `HauntedHouse.exe` and `build.sh`, which downloads a portable Windows Python, trims it, bundles it with the current `HauntedHouse.py` and builds the exe (needs Go, curl and Python; on Windows run it from Git Bash). Rebuild after every game change |
| `tools/autoplay-exe/` | Go source of the launcher; rebuild with `GOOS=windows GOARCH=amd64 go build -o ../../HauntedHouseAutoplay.exe` after copying the latest `autoplay.py` into that folder |

## Changelog

**Latest**
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
- Initiative is a proper d20 (was 1–21); the Safe has its own map position

**Earlier**
- Ammunition system (shotgun shells and pistol bullets)
- Poisoned condition (tracked along other player statistics)
- Rooms with item requirements for progress
- Free player movement

## Known limitations

- Your attacks always hit: monsters have armor class 10 and your attack roll is fixed at 11 or 13.
- All monsters share the same stats (18 HP, armor class 10).
- Object names in a room must start with different letters, and not with B, R or E,
  because those letters are used for the backpack, leaving and escaping.
- Everything lives in one file and relies on global variables.

## Roadmap

1. Split the game into modules (data, entities, world, combat, game loop) and remove globals
2. Separate game logic from input/output so other interfaces can be added
3. Simple graphical interface (tkinter) with a live map built from `HousePlan.py`,
   an inventory panel and a stats bar
