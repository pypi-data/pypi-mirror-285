import os
import sys
from contextlib import contextmanager
from pathlib import Path


def color(string, fg=None, bg=None):
    import click

    return click.style(string, fg=fg, bg=bg)


def absolute(pth):
    if '..' in pth.parts:
        return pth.resolve()
    else:
        return pth.absolute()


def is_subpath(directory, fromdir):
    try:
        directory.relative_to(fromdir)
        return True
    except ValueError:
        return False


def relative_path_walkup(directory, fromdir):
    if sys.version_info >= (3, 12, 1):
        return directory.relative_to(fromdir, walk_up=True)
    else:
        common = Path(
            os.path.commonpath([absolute(directory), absolute(fromdir)])
        )
        to_common = Path('../' * len(fromdir.relative_to(common).parts))
        return to_common / directory.relative_to(common)


@contextmanager
def workdir(directory):
    cwd = Path.cwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(cwd)


def normalize(string):
    # The string must be a valid graphviz node name, so we replace some chars.
    # Also we put an x in front to ensure that the starting char
    # is alphabetic.
    string = string.replace('/', '__slash__').replace('-', '__dash__')
    return f'x{string}'


def pattern_match(pth, pattern):
    if isinstance(pattern, list):
        for ptrn in pattern:
            if pattern_match(pth, ptrn):
                return True
        return False
    # XXX if pattern absolute then ** glob patterns are ignored unless
    # leading with a /
    if pattern != '**':
        return Path('/' + pth).match('/' + pattern)
    return Path(pth).match(pattern)


def tree_to_graphviz_text(tree):
    tokens = ['digraph tasks {']

    graph = {}

    for node in tree.nodes_topological():
        ancestors = tree.registry.ancestry.ancestors(node.name)
        graph[node.name] = ancestors

    for name in graph:
        graphviz_name = normalize(name)
        tokens.append(f'  {graphviz_name} [label="{name}"]')

    for descendant, ancestors in graph.items():
        assert descendant in graph
        node2 = normalize(descendant)

        for ancestor in ancestors:
            assert ancestor in graph
            node1 = normalize(ancestor)
            tokens.append(f'  {node1} -> {node2}')

    tokens.append('}')
    return '\n'.join(tokens)


def format_duration(start_time, end_time):
    """
    If end_time is not given, duration is the current time running. If end_time
    is given, duration is the time the calculation took to run.

    :param start_time: Datetime start time string.
    :param end_time: Datetime end time string, if none is provided,
        datetime.now() is used.
    :return: duration = end_time - start_time
    """
    import datetime

    if start_time is None:
        return ''

    end_time = datetime.datetime.now() if end_time is None else end_time

    duration = end_time - start_time
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds %= 60
    if days > 0:
        duration = f'{days}d {hours:02}:{minutes:02}:{seconds:02}'
    else:
        duration = f'   {hours:02}:{minutes:02}:{seconds:02}'

    return duration
