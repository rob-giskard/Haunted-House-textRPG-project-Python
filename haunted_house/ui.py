"""How the game talks to the player.

The game never calls print() or input() itself. It calls ui.show() to display text and
ui.ask() to get the player's answer. Any object with those two methods can run the game:
the window (GuiBridge in gui_state.py) and the tests (ScriptedUI below).
"""


class UI:
    """The interface every user interface implements."""

    def show(self, *parts):
        """Display text. Several parts are joined with spaces, like print()."""
        raise NotImplementedError

    def ask(self, prompt=''):
        """Show a prompt and return what the player typed."""
        raise NotImplementedError


class OutOfCommands(Exception):
    """Raised by ScriptedUI when the game asks for more input than it was given."""


class GameStuck(Exception):
    """Raised by ScriptedUI when the game keeps asking far longer than any real game would."""


class ScriptedUI(UI):
    """Plays a list of commands and records everything the game shows. Used by the tests.

    commands: the answers to give, in order.
    on_empty: what to do when the commands run out: 'raise' (default) raises OutOfCommands,
              any other string is returned as the answer (for example '' to just press Enter).
    max_answers: safety limit - if the game asks more often than this it is probably stuck in
              a loop, and GameStuck is raised instead of hanging forever.
    """

    def __init__(self, commands, on_empty='raise', max_answers=10000):
        self.commands = list(commands)
        self.on_empty = on_empty
        self.max_answers = max_answers
        self.transcript = []    # everything shown and asked, in order
        self.prompts = []       # just the prompts

    def show(self, *parts):
        self.transcript.append(' '.join(str(p) for p in parts))

    def ask(self, prompt=''):
        self.prompts.append(prompt)
        if len(self.prompts) > self.max_answers:
            raise GameStuck('the game asked for more than %d answers; last prompt: %r' % (self.max_answers, prompt))
        if self.commands:
            answer = self.commands.pop(0)
        elif self.on_empty == 'raise':
            raise OutOfCommands(prompt)
        else:
            answer = self.on_empty
        self.transcript.append(prompt + answer)
        return answer

    def text(self):
        return '\n'.join(self.transcript)
