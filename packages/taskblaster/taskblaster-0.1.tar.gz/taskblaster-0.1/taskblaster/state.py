from enum import Enum

_unsuccessful = set('FCTMø')
_descendants_can_be_submitted = set('nqhrd')

# It is necessary to have q here for now, or otherwise the result task update
# done by Workflow.init task doesn't overwrite the task (displays conflict)
# if it is queued.
_pristine = set('nqC')

_bad_color = 'bright_red'


# XXX These are click color names
_colors = dict(
    ø='yellow',
    n='bright_blue',
    q='cyan',
    Q='cyan',
    h='yellow',
    r='bright_yellow',
    d='green',
    p='magenta',
    F=_bad_color,
    C='yellow',
    T=_bad_color,
    M=_bad_color,
)


class State(Enum):
    new = 'n'
    queue = 'q'
    # myqueue = 'Q'
    # hold = 'h'
    run = 'r'
    done = 'd'
    fail = 'F'
    # timeout = 'T'
    # memory = 'M'
    partial = 'p'
    cancel = 'C'
    # missing = 'ø'

    @classmethod
    def statecodes(cls):
        return ''.join(state.value for state in cls)

    @property
    def is_pristine(self):
        return self.value in _pristine

    @property
    def unsuccessful(self):
        return self.value in _unsuccessful

    @property
    def color(self):
        return _colors[self.value]

    @property
    def ansiname(self):
        import click

        return click.style(self.name, self.color)


class ConflictState(Enum):
    none = 'n'
    resolved = 'r'
    conflict = 'c'

    @property
    def color(self):
        conflictcolors = {'n': 'green', 'r': 'bright_blue', 'c': 'red'}
        return conflictcolors[self.value]
