from dataclasses import dataclass
from pathlib import Path

from taskblaster.registry import Registry
from taskblaster.state import State
from taskblaster.util import color, format_duration, relative_path_walkup


@dataclass
class Column:
    key: str
    title: str
    width: int

    def padded_title(self):
        return self.title.ljust(self.width)


def _all_columns():
    columns = {}

    def add(key, *args):
        columns[key] = Column(key, *args)

    add('s', 'state', 8)
    add('i', 'deps', 5)
    add('f', 'folder', 29)
    add('I', 'worker', 10)
    add('r', 'tags', 11)
    add('t', 'start time'.ljust(15) + 'end time', 15 + 16)
    add('T', '   time', 11)  # padded so title aligns with hours
    add('c', 'conflict', 11)
    add('C', 'conflict info', 15)
    return columns


all_columns = _all_columns()


@dataclass
class Listing:
    # We should refactor so column information is defined in a single place.
    # Here we define the headers but the formatting is done elsewhere.
    # nodes: list[nodes]
    columns: str
    registry: Registry
    treedir: Path
    fromdir: Path

    def nodeinfo(self, node):
        return NodeInfo(
            node=node,
            registry=self.registry,
            treedir=self.treedir,
            fromdir=self.fromdir,
            columns=self.columns,
        )

    def to_string(self, nodes):
        headerline = ' '.join(
            all_columns[key].padded_title() for key in self.columns
        )
        yield headerline.rstrip()
        yield '─' * len(headerline)

        for node in nodes:
            node_info = self.nodeinfo(node)
            yield node_info.to_string()


class NodeInfo:
    def __init__(self, node, registry, treedir, fromdir, columns):
        from taskblaster.future import parent_state_info

        self.node = node
        self.name = node.name
        self.state = State(node.state)
        self.relpath = relative_path_walkup(treedir / node.name, fromdir)
        self.columns = columns

        self._get_runinfo(registry=registry)
        self.conflict_info = self.get_conflict_info(registry=registry)
        self.parent_state_info = parent_state_info(
            registry=registry, name=self.name
        )

        self.tags = registry.resources.get_tags(self.name)

    def _get_runinfo(self, registry):
        (
            subworker_id,
            start_time,
            end_time,
            exception,
        ) = registry.workers.get_runinfo(self.name)
        duration = format_duration(start_time=start_time, end_time=end_time)
        my_dict = dict(
            worker_name=subworker_id,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            exception=exception,
        )

        for k, v in my_dict.items():
            setattr(self, k, v)

    def get_conflict_info(self, registry):
        from taskblaster.state import ConflictState

        conflict, conflictinfo, conflictinp = registry.get_conflict_info(
            self.name
        )
        conflictinfo = str(conflictinfo)[1:]
        if conflict:
            conflict = ConflictState(conflict)
        else:
            conflict = ConflictState.none

        return conflict, conflictinfo, conflictinp

    def to_string(self):
        import click

        from taskblaster.registry import UNKNOWN_AWAITCOUNT

        node = self.node
        state = self.state
        okcount, nparents, deps_color = self.parent_state_info

        if node.awaitcount == UNKNOWN_AWAITCOUNT:
            nparents = '?'

        conflict, conflictinfo, conflictinp = self.conflict_info

        start_time = self.format_timestamp(self.start_time)
        end_time = self.format_timestamp(self.end_time)

        folder_name = str(self.relpath)
        info_dct = {
            's': color(state.name, state.color),
            'i': color(f'{okcount}/{nparents}', deps_color),
            'f': folder_name,
            'I': color(self.worker_name, state.color),
            't': (
                f'{start_time} {end_time}' if self.worker_name != '' else ''
            ),
            'r': ','.join(self.tags),
            'T': color(str(self.duration), state.color),
            'c': color(conflict.name, conflict.color),
            'C': conflictinfo,
        }

        output = []

        spacing_deficit = 0

        for key in self.columns:
            column = all_columns[key]

            token = info_dct[key]

            printed_width = len(click.unstyle(token))
            target_width = column.width - spacing_deficit
            padding_length = max(target_width - printed_width, 0)
            token += ' ' * padding_length
            spacing_deficit += printed_width + padding_length - column.width
            output.append(token)

        line = ' '.join(output).rstrip()

        if self.exception is not None:
            exception = (
                self.exception[:120] + '…'
                if len(self.exception) > 120
                else self.exception
            )
            line += '\n^^^^  ' + color(exception, 'bright_red')
        return line

    @staticmethod
    def format_timestamp(timestamp) -> str:
        if timestamp is None:
            return ''
        return timestamp.strftime('%y-%m-%d %H:%M')
