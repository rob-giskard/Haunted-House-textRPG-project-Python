"""The graphical interface: a game screen with panels on top and a terminal below.

    +--------------------------------------------------------------+
    | HAUNTED HOUSE                      Name   HP [######----] 31  |
    +-------------------------------+------------------------------+
    | ROOM: name, description,      | EXITS: compass with the four  |
    | objects (searched or not)     | directions                    |
    |                               | GEAR: weapon, ammo, items,    |
    |                               | keys, good deeds              |
    +-------------------------------+------------------------------+
    | COMBAT: monster, both health bars, the last moves of the fight |
    +--------------------------------------------------------------+
    | terminal: everything the game says                            |
    | hint: what you can type now                                   |
    | > your command                                                |
    +--------------------------------------------------------------+

The game itself runs unchanged in a background thread and talks to the window through
GuiBridge (see gui_state.py). Start it with:  python HauntedHouse.py

Autoplay: the "watch walkthrough" button (or HauntedHouse.py --autoplay) replays
walkthrough.txt in the window, typing each command for you. Esc takes over.
"""
import queue
import re
import threading
import tkinter as tk
import tkinter.font as tkfont

from . import data
from .game import Game
from .gui_state import ABANDON, GuiBridge, hint
from .walkthrough import DEFAULT_PATH as WALKTHROUGH, read_walkthrough

# --- look -------------------------------------------------------------------
BG = '#0b0b0b'          # window
PANEL = '#111111'       # panels
EDGE = '#262626'        # panel borders
TEXT = '#c9c9c9'
DIM = '#6a6a6a'
GREEN = '#86d77f'
YELLOW = '#e5c07b'
RED = '#e06c75'
BLUE = '#61afef'
TITLE = '#9a9a9a'

ANSI = {'93': YELLOW, '94': BLUE, '91': RED, '92': GREEN, '90': DIM}
ANSI_RE = re.compile('\033\\[(\\d+)m')
EXIT_COLORS = {'open': GREEN, 'unlockable': YELLOW, 'locked': RED, 'outside': BLUE,
               'wall': DIM, 'railing': DIM}


def pick_font(root, size):
    families = set(tkfont.families(root))
    for name in ('Consolas', 'Cascadia Mono', 'DejaVu Sans Mono', 'Menlo', 'Courier New'):
        if name in families:
            return (name, size)
    return ('Courier', size)


def bar(value, maximum, width=20):
    """A health bar like [##########----------], in plain characters every font has."""
    filled = 0 if maximum <= 0 else max(0, min(width, round(width * value / maximum)))
    return '[' + '#' * filled + '-' * (width - filled) + ']'


def plural(count, word):
    return '%d %s%s' % (count, word, '' if count == 1 else 's')


class Panel(tk.Frame):
    """A dark box with a small grey title, like a section of a terminal dashboard."""

    def __init__(self, parent, title, font):
        super().__init__(parent, bg=PANEL, highlightthickness=1, highlightbackground=EDGE)
        tk.Label(self, text=title, bg=PANEL, fg=TITLE, font=font, anchor='w').pack(fill='x', padx=10, pady=(6, 2))


def readonly_text(parent, font, height, **kw):
    t = tk.Text(parent, bg=PANEL, fg=TEXT, font=font, height=height, wrap='word', bd=0,
                highlightthickness=0, padx=10, pady=4, cursor='arrow', insertwidth=0, **kw)
    for name, color in [('dim', DIM), ('green', GREEN), ('yellow', YELLOW), ('red', RED), ('blue', BLUE),
                        ('bright', '#ffffff')]:
        t.tag_configure(name, foreground=color)
    t.configure(state='disabled')
    return t


def set_text(widget, parts):
    """Replaces a read-only Text's content. parts: list of (text, tag) pairs."""
    widget.configure(state='normal')
    widget.delete('1.0', 'end')
    for text, tag in parts:
        widget.insert('end', text, tag or ())
    widget.configure(state='disabled')


class HauntedHouseApp:
    """The window. seed fixes the dice (optional); autoplay is a walkthrough file to replay
    right away; delay is the pause between autoplay keystrokes, in seconds."""

    def __init__(self, root, seed=None, autoplay=None, delay=0.4):
        self.root = root
        self.seed = seed
        self.delay_ms = int(delay * 1000)
        self.prompt = None          # the question the game is waiting on, or None
        self.game_over = False
        self.history = []
        self.history_pos = 0
        self.bridge = None
        self.auto_commands = None   # remaining walkthrough commands while autoplay runs
        self.auto_job = None
        self.last_snap = {'started': False}

        root.title('Haunted House')
        root.configure(bg=BG)
        root.geometry('1080x800')
        root.minsize(900, 660)
        self.font = pick_font(root, 11)
        self.small = (self.font[0], 9)
        self.big = (self.font[0], 13, 'bold')
        self.build()
        if autoplay:
            self.start_autoplay(autoplay)
        else:
            self.new_game()
        self.root.after(30, self.poll)

    # --- layout -----------------------------------------------------------
    def build(self):
        root, font, small = self.root, self.font, self.small
        outer = tk.Frame(root, bg=BG)
        outer.pack(fill='both', expand=True, padx=12, pady=10)

        # header
        header = tk.Frame(outer, bg=BG)
        header.pack(fill='x', pady=(0, 8))
        tk.Label(header, text='HAUNTED HOUSE', bg=BG, fg=TEXT, font=self.big).pack(side='left')
        for text, action in [('new game', self.restart), ('watch walkthrough', lambda: self.start_autoplay(WALKTHROUGH))]:
            button = tk.Label(header, text='[ ' + text + ' ]', bg=BG, fg=DIM, font=small, cursor='hand2')
            button.pack(side='left', padx=(14, 0))
            button.bind('<Button-1>', lambda e, a=action: a())
            button.bind('<Enter>', lambda e, b=button: b.configure(fg=GREEN))
            button.bind('<Leave>', lambda e, b=button: b.configure(fg=DIM))
        self.status = readonly_text(header, font, 1, width=60)
        self.status.configure(bg=BG, padx=0)
        self.status.tag_configure('right', justify='right')
        self.status.pack(side='right')

        # game screen: room on the left, exits and gear on the right
        screen = tk.Frame(outer, bg=BG)
        screen.pack(fill='x')
        screen.columnconfigure(0, weight=3, uniform='cols')
        screen.columnconfigure(1, weight=2, uniform='cols')
        screen.rowconfigure(0, weight=1)

        room = Panel(screen, 'ROOM', small)
        room.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        self.room_text = readonly_text(room, font, 11)
        self.room_text.pack(fill='both', expand=True, pady=(0, 8))

        side = tk.Frame(screen, bg=BG)
        side.grid(row=0, column=1, sticky='nsew')
        exits = Panel(side, 'EXITS', small)
        exits.pack(fill='x')
        compass = tk.Frame(exits, bg=PANEL)
        compass.pack(fill='x', padx=10, pady=(2, 10))
        for c in range(3):
            compass.columnconfigure(c, weight=1, uniform='compass')
        self.exit_labels = {}
        spots = {'NORTH': (0, 1), 'WEST': (1, 0), 'EAST': (1, 2), 'SOUTH': (2, 1)}
        for direction, (r, c) in spots.items():
            label = tk.Label(compass, bg=PANEL, fg=DIM, font=font, justify='center', wraplength=150, height=2)
            label.grid(row=r, column=c, sticky='nsew', pady=2)
            label.bind('<Button-1>', lambda e, d=direction: self.click_exit(d))
            self.exit_labels[direction] = label
        self.here_label = tk.Label(compass, bg=PANEL, fg=TEXT, font=(font[0], font[1], 'bold'), text='[ ]')
        self.here_label.grid(row=1, column=1)

        gear = Panel(side, 'GEAR', small)
        gear.pack(fill='both', expand=True, pady=(8, 0))
        self.gear_text = readonly_text(gear, font, 8)
        self.gear_text.pack(fill='both', expand=True, pady=(0, 8))

        # combat
        combat = Panel(outer, 'COMBAT', small)
        combat.pack(fill='x', pady=(8, 0))
        self.combat_text = readonly_text(combat, font, 6)
        self.combat_text.pack(fill='x', pady=(0, 8))

        # terminal
        term = tk.Frame(outer, bg='#000000', highlightthickness=1, highlightbackground=EDGE)
        term.pack(fill='both', expand=True, pady=(8, 0))
        self.log = tk.Text(term, bg='#000000', fg=TEXT, font=font, height=10, wrap='word', bd=0,
                           highlightthickness=0, padx=10, pady=6, cursor='arrow', insertwidth=0)
        scroll = tk.Scrollbar(term, command=self.log.yview, bg='#000000', troughcolor='#000000',
                              bd=0, highlightthickness=0, width=10)
        self.log.configure(yscrollcommand=scroll.set)
        for code, color in ANSI.items():
            self.log.tag_configure('ansi' + code, foreground=color)
        self.log.tag_configure('typed', foreground=GREEN)
        self.log.tag_configure('prompt', foreground=TEXT)
        self.log.configure(state='disabled')
        scroll.pack(side='right', fill='y')
        self.log.pack(side='top', fill='both', expand=True)

        self.hint_label = tk.Label(outer, bg=BG, fg=DIM, font=small, anchor='w')
        self.hint_label.pack(fill='x', pady=(6, 2))
        line = tk.Frame(outer, bg='#000000', highlightthickness=1, highlightbackground=EDGE)
        line.pack(fill='x')
        tk.Label(line, text='>', bg='#000000', fg=GREEN, font=font).pack(side='left', padx=(10, 4))
        self.entry = tk.Entry(line, bg='#000000', fg=GREEN, insertbackground=GREEN, font=font, bd=0,
                              highlightthickness=0, disabledbackground='#000000')
        self.entry.pack(side='left', fill='x', expand=True, ipady=6)
        self.entry.bind('<Return>', self.submit)
        self.entry.bind('<Up>', lambda e: self.recall(-1))
        self.entry.bind('<Down>', lambda e: self.recall(1))
        root.bind('<Escape>', lambda e: self.stop_autoplay(take_over=True))
        self.entry.focus_set()

    # --- running the game ---------------------------------------------------
    def new_game(self, seed=None):
        """Starts a fresh game, stopping the current one if it is still running."""
        if self.bridge is not None and not self.game_over:
            self.bridge.from_window.put(ABANDON)     # the old game thread stops at its next question
        self.game_over = False
        self.prompt = None
        self.clear_log()
        self.bridge = GuiBridge()
        game = Game(ui=self.bridge, seed=seed if seed is not None else self.seed)
        self.thread = threading.Thread(target=self.bridge.run, args=(game,), daemon=True)
        self.thread.start()

    def restart(self):
        self.stop_autoplay()
        self.new_game()
        self.entry.focus_set()

    # --- autoplay -----------------------------------------------------------
    def start_autoplay(self, path):
        """Replays a walkthrough: same seed, and each command typed in for you."""
        self.stop_autoplay()
        try:
            seed, commands = read_walkthrough(path)
        except (OSError, ValueError) as error:
            self.write('\n[ Cannot start autoplay: %s ]\n' % error, 'ansi91')
            return
        self.new_game(seed=seed)
        self.auto_commands = list(commands)
        self.write('[ Autoplay: %d commands from %s, seed %d. Press Esc to take over. ]\n\n'
                   % (len(commands), path.replace('\\', '/').split('/')[-1], seed), 'ansi90')

    def stop_autoplay(self, take_over=False):
        if self.auto_job is not None:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None
        if self.auto_commands is not None and take_over:
            self.write('\n[ Autoplay stopped - you have control now. ]\n', 'ansi90')
            if self.prompt is not None:
                self.hint_label.configure(text=hint(self.prompt, self.last_snap))
        self.auto_commands = None
        self.entry.delete(0, 'end')

    def autoplay_step(self):
        """Types the next walkthrough command into the input, then sends it."""
        self.auto_job = None
        if self.auto_commands is None or self.prompt is None:
            return
        if not self.auto_commands:
            self.auto_commands = None
            self.write('\n[ Walkthrough finished - you have control now. ]\n', 'ansi90')
            self.hint_label.configure(text=hint(self.prompt, self.last_snap))
            return
        command = self.auto_commands.pop(0)
        self.entry.delete(0, 'end')
        self.entry.insert(0, command)
        self.auto_job = self.root.after(max(self.delay_ms // 2, 1), lambda: self.submit(auto=True))

    def poll(self):
        """Picks up everything the game said since last time (runs every 30 ms)."""
        try:
            while True:
                kind, text, snap = self.bridge.to_window.get_nowait()
                if kind == 'error':
                    self.write('\n[ Something went wrong inside the game: ]\n' + text, 'ansi91')
                    self.game_over = True
                    self.hint_label.configure(text='Press Enter for a new game.')
                    continue
                if kind == 'show':
                    self.write(text + '\n')
                elif kind == 'ask':
                    self.prompt = text
                    if text.strip():
                        self.write(text.lstrip('\n'), 'prompt')
                    self.hint_label.configure(text=hint(text, snap))
                    if self.auto_commands is not None:
                        self.hint_label.configure(text='Autoplay is typing for you - press Esc to take over.')
                        self.auto_job = self.root.after(max(self.delay_ms // 2, 1), self.autoplay_step)
                elif kind == 'end':
                    self.game_over = True
                    self.prompt = None
                    self.write('\n[ The game is over. Press Enter to play again, or close the window. ]\n', 'typed')
                    self.hint_label.configure(text='Press Enter for a new game.')
                self.last_snap = snap
                self.refresh(snap)
        except queue.Empty:
            pass
        self.root.after(30, self.poll)

    def submit(self, event=None, auto=False):
        if auto:
            self.auto_job = None
        elif self.auto_commands is not None:
            return 'break'          # autoplay is typing; Esc takes over
        answer = self.entry.get()
        if self.game_over:
            self.entry.delete(0, 'end')
            self.new_game()
            return 'break'
        if self.prompt is None:
            return 'break'          # the game is busy, not asking anything
        self.entry.delete(0, 'end')
        if answer.strip():
            self.history.append(answer)
        self.history_pos = len(self.history)
        if not self.prompt.strip():
            self.write('> ', 'typed')          # the game asked without a question: start a new line
        elif not self.prompt.endswith(' '):
            self.write(' ')
        self.write(answer + '\n', 'typed')
        self.prompt = None
        self.hint_label.configure(text='')
        self.bridge.from_window.put(answer)
        return 'break'

    def click_exit(self, direction):
        """Clicking an exit on the compass types its letter, when the game asks for a direction."""
        prompt = self.prompt or ''
        if self.auto_commands is None and ('direction' in prompt or prompt.startswith('Invalid')):
            self.entry.delete(0, 'end')
            self.entry.insert(0, direction[0].lower())
            self.submit()

    def recall(self, step):
        if not self.history:
            return 'break'
        self.history_pos = max(0, min(len(self.history), self.history_pos + step))
        self.entry.delete(0, 'end')
        if self.history_pos < len(self.history):
            self.entry.insert(0, self.history[self.history_pos])
        return 'break'

    # --- terminal -----------------------------------------------------------
    def write(self, text, tag=None):
        """Adds text to the terminal, turning the game's ANSI color codes into colors."""
        self.log.configure(state='normal')
        color = None
        for i, piece in enumerate(ANSI_RE.split(text)):
            if i % 2 == 1:                  # an ANSI code
                color = None if piece == '0' else 'ansi' + piece
            elif piece:
                self.log.insert('end', piece, tuple(t for t in (tag, color) if t))
        self.log.configure(state='disabled')
        self.log.see('end')

    def clear_log(self):
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.configure(state='disabled')

    # --- panels -------------------------------------------------------------
    def refresh(self, s):
        if not s.get('started'):
            set_text(self.room_text, [('Barry the Butler is waiting at the door...', 'dim')])
            return
        self.refresh_status(s)
        self.refresh_room(s)
        self.refresh_exits(s)
        self.refresh_gear(s)
        self.refresh_combat(s)

    def refresh_status(self, s):
        ratio = s['hp'] / s['max_hp']
        color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
        self.status.tag_configure('hp', foreground=color)
        condition = s['condition'] if s['alive'] else 'Dead'
        set_text(self.status, [
            (s['name'] + '   ', 'bright'),
            ('HP ', 'dim'), (bar(s['hp'], s['max_hp']), 'hp'), (' %d/%d   ' % (s['hp'], s['max_hp']), 'hp'),
            (condition, 'red' if condition != 'Stable' else 'green'),
        ])
        self.status.tag_add('right', '1.0', 'end')

    def refresh_room(self, s):
        parts = [(s['room'].upper() + '\n\n', 'bright')]
        # the descriptions are written with line breaks for an 80-column terminal; joining them
        # lets the panel wrap the text to its own width
        parts.append((' '.join(line.strip() for line in s['description'].splitlines() if line.strip()) + '\n\n', None))
        if s['objects']:
            for name, searched in s['objects']:
                if searched:
                    parts.append(('  -  %s  (searched)\n' % name, 'dim'))
                else:
                    parts.append(('  %s  ' % name[0].upper(), 'green'))
                    parts.append((name + '\n', None))
        else:
            parts.append(('Nothing here to search.\n', 'dim'))
        set_text(self.room_text, parts)

    def refresh_exits(self, s):
        self.here_label.configure(text='[ you ]')
        for direction, status, label in s['exits']:
            text = direction[0] + '\n' + (label if status not in ('wall', 'railing') else '-')
            self.exit_labels[direction].configure(text=text, fg=EXIT_COLORS[status],
                                                  cursor='hand2' if status not in ('wall', 'railing') else '')

    def refresh_gear(self, s):
        bullets, shells = plural(s['bullets'], 'bullet'), plural(s['shells'], 'shell')
        ammo = {'Revolver pistol': bullets, 'Shotgun': shells}
        parts = [('Weapon     ', 'dim'), (s['weapon'], 'bright')]
        if s['weapon'] in ammo:
            parts.append(('  (' + ammo[s['weapon']] + ')', 'dim'))
        parts += [('\nAmmo       ', 'dim'), (bullets + ', ' + shells, None),
                  ('\nItems      ', 'dim')]
        if s['consumables']:
            for i, (item, count) in enumerate(s['consumables']):
                tag = 'blue' if item in data.HEALING_ITEMS else 'red'
                parts.append(((',  ' if i else '') + item + ('(%d)' % count if count > 1 else ''), tag))
        else:
            parts.append(('none', 'dim'))
        keys = s['keys']
        parts += [('\nKeys       ', 'dim'), ('K ' * keys, 'yellow'),
                  ('- ' * (data.KEYS_NEEDED - keys), 'dim'), (' %d/%d' % (keys, data.KEYS_NEEDED), 'dim'),
                  ('\nGood deeds ', 'dim'), ('%d/3' % s['deeds'], 'green' if s['deeds'] else None),
                  ('\nDefeated   ', 'dim'), (plural(s['kills'], 'monster'), None),
                  ('\nTreasure   ', 'dim'), (plural(s['treasure'], 'item'), None)]
        set_text(self.gear_text, parts)

    def refresh_combat(self, s):
        fight = s['combat']
        if not fight:
            set_text(self.combat_text, [('No enemies in sight. For now.', 'dim')])
            return
        over = fight['result'] is not None or not s['fighting']
        if over and not s['fighting'] and fight['result'] is None:
            fight['result'] = 'over'
        parts = []
        if not over:
            parts += [(fight['monster'].upper(), 'red'), ('   round %d\n' % max(fight['round'], 1), 'dim')]
        else:
            outcome = {'won': ('defeated', 'green'), 'lost': ('killed you', 'red')}.get(fight['result'], ('fled', 'dim'))
            parts += [('Last fight: ', 'dim'), (fight['monster'], None), (' - ' + outcome[0], outcome[1]),
                      ('  (%d round%s)\n' % (fight['round'], '' if fight['round'] == 1 else 's'), 'dim')]
        parts += [('%-21s' % fight['monster'][:20], 'dim'), (bar(fight['monster_hp'], fight['monster_max_hp']), 'red'),
                  (' %d/%d\n' % (fight['monster_hp'], fight['monster_max_hp']), 'dim'),
                  ('%-21s' % s['name'][:20], 'dim'), (bar(s['hp'], s['max_hp']), 'green'),
                  (' %d/%d   %s\n' % (s['hp'], s['max_hp'], s['weapon']), 'dim')]
        if not over:
            for line in fight['log'][-3:]:
                parts.append(('  ' + line + '\n', None))
        set_text(self.combat_text, parts)


def main(seed=None, autoplay=None, delay=0.4):
    root = tk.Tk()
    HauntedHouseApp(root, seed=seed, autoplay=autoplay, delay=delay)
    root.mainloop()
