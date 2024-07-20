import sqlite3
from dataclasses import dataclass
from dataclasses import replace as _dataclass_replace
from pathlib import Path
from random import random
from time import sleep
from typing import Set

from taskblaster import UNREACHABLE_REF
from taskblaster.inputs import SerializedInputTable
from taskblaster.resources import Resources
from taskblaster.state import State
from taskblaster.workers import Workers

UNKNOWN_DEPTH = 9999


@dataclass
class IndexNode:
    name: str  # task name (i.e., normalized path)
    state: State  # one-letter representation of state
    awaitcount: int  # how many direct ancestors are not done?
    workerclass: str
    argtext: str  # possibly ellipsized description text (for viewing)
    # (-1 if unknown.)

    @classmethod
    def fromrow(cls, row):
        # Defines how registry rows are converted into IndexNode objects.

        return cls(
            name=row[0],
            state=State(row[1]),
            awaitcount=row[2],
            workerclass=row[3],
            argtext=row[4],
        )

    def replace(self, **kwargs):
        return _dataclass_replace(self, **kwargs)

    def torow(self):
        return (
            self.name,
            self.state.value,
            self.awaitcount,
            self.workerclass,
            self.argtext,
            '',  # "digest"
        )


class Index:
    def __init__(self, conn):
        self.conn = conn

    @classmethod
    def initialize(cls, conn):
        conn.execute(
            """
CREATE TABLE IF NOT EXISTS registry (
    name VARCHAR(512) PRIMARY KEY,
    state CHAR(1),
    awaitcount INTEGER,
    workerclass VARCHAR(512),
    argtext VARCHAR(80),
    digest CHAR(64)
)"""
        )

        # Stores the depth inside the directed acyclic graph of each task.
        #
        # The depth is longest distance to root task, i.e., the depths
        # are a partial topological ordering of states.
        conn.execute(
            """
CREATE TABLE IF NOT EXISTS topological_depth (
    name VARCHAR(512) PRIMARY KEY,
    depth INTEGER
)"""
        )

        indices = {
            'state_index': 'registry(state)',
            'name_index': 'registry(name)',
            'awaitcount_index': 'registry(awaitcount)',
            'workerclass_index': 'registry(workerclass)',
            'ready_index': 'registry(state, awaitcount, workerclass)',
            'digest_index': 'registry(digest)',
        }

        for indexname, target in indices.items():
            statement = f'CREATE INDEX IF NOT EXISTS {indexname} ON {target}'
            conn.execute(statement)

        """conflicts table keeps track of tasks with conflicts. I.e. tasks
           that are marked as done but which were excecuted with different
           input paramaters than in the current workflow.
        """
        conn.execute(
            """
CREATE TABLE IF NOT EXISTS conflicts (
    task_name VARCHAR(512) PRIMARY KEY,
    conflict CHAR(1),
    reason BLOB,
    buf BLOB)
    """
        )

        return cls(conn)

    def add(self, indexnode: IndexNode) -> None:
        row = indexnode.torow()
        questionmarks = ', '.join('?' * len(row))
        query = f'INSERT INTO registry VALUES ({questionmarks})'
        self.conn.execute(query, row)

    def update_states(self, names, state):
        query = 'UPDATE registry SET state=(?) WHERE name=(?)'
        self.conn.executemany(query, [(state, name) for name in names])

    def update_state(self, name, state):
        self.update_states([name], state)

    def update_awaitcount(self, name, awaitcount):
        query = 'UPDATE registry SET awaitcount=(?) WHERE name=(?)'
        self.conn.execute(query, (awaitcount, name))

    def count(self) -> int:
        cursor = self.conn.execute('SELECT COUNT(*) FROM registry')
        return cursor.fetchone()[0]

    def glob_simple(self, pattern: str):
        query = 'SELECT * FROM registry WHERE name GLOB (?)'
        cursor = self.conn.execute(query, (pattern,))
        return [IndexNode.fromrow(row) for row in cursor.fetchall()]

    def glob(self, patterns, states=None, sort='name', failure=None):
        # matching a/b should include itself (obviously)
        # matching a/b should also include a/b/c and other subdirectories.
        #
        # To get both, we pass pattern as well as pattern/*, matching either.
        query_args = list(patterns)
        query_args += [pattern + '/*' for pattern in patterns]

        # Is there a way to execute multiple globs or must we build
        # this potentially very long string?
        glob_where = ' OR '.join(['registry.name GLOB (?)'] * len(query_args))

        if states:
            statechars = [state.value for state in states]
            questionmarks = ', '.join('?' * len(statechars))
            where = f'({glob_where}) AND registry.state IN ({questionmarks})'
            query_args += list(statechars)
        else:
            where = glob_where

        tables = ['registry']

        if failure is not None:
            tables.append('runinfo')
            where += (
                ' AND registry.name = runinfo.task_name'
                f" AND instr(runinfo.exception, '{failure}')>0 "
            )

        tables = ', '.join(tables)
        if sort == 'name':
            query = f'SELECT * FROM {tables} WHERE {where} ORDER BY name'
        elif sort == 'topo':
            query = (
                f'SELECT registry.* FROM {tables} JOIN topological_depth '
                f'on registry.name = topological_depth.name '
                f'WHERE {where} order by topological_depth.depth, name'
            )
        else:
            raise ValueError(f'Invalid sort: {sort!r}')
        cursor = self.conn.execute(query, query_args)
        return [IndexNode.fromrow(row) for row in cursor.fetchall()]

        # We should re-enable more globbing/name filtering options:
        # Selecting tasks with given name or folders that contain pattern
        # XXX Could be done more efficient
        # output = []
        # for row in cursor.fetchall():
        #    indxnode = IndexNode.fromrow(row)
        #    if name == indxnode.name.split('/')[-1]:
        #        output.append(indxnode)
        #    elif pattern:
        #        if pattern in indxnode.name:
        #            output.append(indxnode)
        # return output

    def nodes(self):
        cursor = self.conn.execute('SELECT * FROM registry ORDER BY name')
        for row in cursor:
            yield IndexNode.fromrow(row)

    def _getnode(self, name):
        query = 'SELECT * FROM registry WHERE name=(?)'
        cursor = self.conn.execute(query, (name,))
        rows = cursor.fetchall()
        return rows

    def node(self, name: str) -> IndexNode:
        rows = self._getnode(name)
        if len(rows) != 1:
            raise Missing(name)
        return IndexNode.fromrow(rows[0])

    def contains(self, name: str) -> bool:
        rows = self._getnode(name)
        return bool(rows)

    def remove_multiple(self, names):
        query = 'DELETE FROM registry WHERE name=(?)'
        self.conn.executemany(query, [(name,) for name in names])
        for name in names:
            self.conn.execute(
                'DELETE FROM topological_depth WHERE name=(?)', (name,)
            )

    def asdict(self):
        return {node.name: node for node in self.nodes()}


class Missing(LookupError):
    pass


class Ancestry:
    """Storage of vertices in dependency graph as node --> parent map."""

    tablename = 'dependencies'

    def __init__(self, conn):
        self.conn = conn

    @classmethod
    def initialize(cls, conn) -> None:
        table = cls.tablename
        conn.execute(
            f"""\
CREATE TABLE IF NOT EXISTS {table} (
    ancestor CHAR(64),
    descendant CHAR(64),
    PRIMARY KEY (ancestor, descendant)
)"""
        )
        conn.execute(
            'CREATE INDEX IF NOT EXISTS ancestor_index '
            f'ON {table}(ancestor)'
        )
        conn.execute(
            'CREATE INDEX IF NOT EXISTS descendant_index '
            f'ON {table}(descendant)'
        )
        conn.execute(
            'CREATE INDEX IF NOT EXISTS combined_index '
            f'ON {table}(ancestor, descendant)'
        )
        return cls(conn)

    def _all(self):
        query = f'SELECT * FROM {self.tablename}'
        return self.conn.execute(query).fetchall()

    def graph(self):
        tokens = ['digraph ancestors {']

        for ancestor, descendant in self._all():
            for node in [ancestor, descendant]:
                tokens.append(f'  "{node}" [label="{node[:6]}"]')

            tokens.append(f'  "{ancestor}" -> "{descendant}"')

        tokens.append('}')
        return '\n'.join(tokens)

    def add(self, parent_name: str, name: str) -> None:
        query = f'INSERT INTO {self.tablename} VALUES (?, ?)'
        self.conn.execute(query, (parent_name, name))

    def contains(self, parent_name: str, name: str) -> None:
        query = (
            f'SELECT ancestor, descendant FROM {self.tablename} '
            'WHERE ancestor=(?) AND descendant=(?)'
        )
        cursor = self.conn.execute(query, (parent_name, name))
        count = len(cursor.fetchall())
        assert count <= 1
        return bool(count)

    def remove(self, parent_name: str, name: str) -> None:
        if not self.contains(parent_name, name):
            raise KeyError(parent_name, name)
        query = (
            f'DELETE FROM {self.tablename} '
            'WHERE ancestor=(?) AND descendant=(?)'
        )
        self.conn.execute(query, (parent_name, name))

    def _get_any(self, which: str, other: str, name: str) -> Set[str]:
        query = f'SELECT {which} FROM {self.tablename} WHERE {other}=(?)'
        cursor = self.conn.execute(query, (name,))
        return {obj[0] for obj in cursor.fetchall()}

    def ancestors(self, name: str) -> Set[str]:
        return self._get_any('ancestor', 'descendant', name)

    def descendants(self, name: str) -> Set[str]:
        return self._get_any('descendant', 'ancestor', name)

    # High-level functions -- they don't quite belong here.
    # Move to registry or something
    def add_node(self, node):
        for parent_name in node.parents:
            self.add(parent_name, node.name)

    def remove_node(self, node):
        for parent_name in self.ancestors(node.name):
            self.remove(parent_name, node.name)


UNKNOWN_AWAITCOUNT = -1


class Registry:
    """Collection of tasks providing efficient access.

    The registry is a mapping from task IDs (hashes) to task locations
    (directories inside cache)."""

    def __init__(self, regfile: Path, timeout=60):
        self.regfile = regfile
        self.conn = Connection(regfile, timeout)

        with self.conn:
            Index.initialize(self.conn)
            Ancestry.initialize(self.conn)
            Workers.initialize(self.conn)
            Resources.initialize(self.conn)
            SerializedInputTable.initialize(self.conn)

    def unrun(self, name):
        self.workers.remove_runinfo(name)
        self._update_state(name, State.new)
        self.clear_conflict(name)
        self._recursive_update_descendant_state(
            name, State.new, until_state=State.new, clear_conflict=True
        )

    def _recursive_update_descendant_state(
        self, nodename, state, until_state, clear_conflict=False
    ):
        for descendant in self._recurse_descendants(nodename, until_state):
            self._update_state(descendant, state)
            if clear_conflict:
                self.clear_conflict(descendant)

    def cancel_descendants(self, nodename):
        self._recursive_update_descendant_state(
            nodename, State.cancel, State.cancel
        )

    def _recurse_descendants(self, nodename, until_state):
        for descendant in self.ancestry.descendants(nodename):
            node = self.index.node(descendant)
            if node.state == until_state:
                continue

            yield from self._recurse_descendants(descendant, until_state)
            yield descendant

    def _new_indexnode(self, node, awaitcount):
        return IndexNode(
            name=node.name,
            state=State.new,
            awaitcount=awaitcount,
            workerclass=None,
            argtext=node.input_repr(),
        )

    def _awaitcount(self, name):
        parent_names = self.ancestry.ancestors(name)
        parent_states = []
        for parent_name in parent_names:
            if parent_name == UNREACHABLE_REF:
                return UNKNOWN_AWAITCOUNT
                # parent_states.append(State.new)
            else:
                parent_states.append(State(self.index.node(parent_name).state))

        # XXX crashes on orphans.
        return len([state for state in parent_states if state != State.done])

    def get_depth(self, name: str) -> int:
        cursor = self.conn.execute(
            'SELECT depth FROM topological_depth WHERE name=(?)', (name,)
        )
        row = cursor.fetchone()
        if row is None:
            return UNKNOWN_DEPTH
        else:
            return row[0]

    def _compute_depth(self, name):
        ancestors = self.ancestry.ancestors(name)
        # (Should do this in a single query, not a loop)
        depths = sorted(self.get_depth(ancestor) for ancestor in ancestors)
        if not depths:
            return 0
        if depths[0] == UNKNOWN_DEPTH:
            return UNKNOWN_DEPTH
        return depths[-1] + 1

    def _add(self, node, tags, force_state=None):
        self.ancestry.add_node(node)
        awaitcount = self._awaitcount(node.name)
        indexnode = self._new_indexnode(node, awaitcount)
        self.index.add(indexnode)

        for tag in tags:
            self.resources.add_tag(node.name, tag)

        self.inputs.add(node.name, node.serialized_input)

        if force_state:
            self._update_state(node.name, force_state)
        else:
            parent_states = set(self.parent_states(node.name).values())
            if State.cancel in parent_states or State.fail in parent_states:
                self._update_state(node.name, State.cancel)
                indexnode.state = State.cancel

        depth = self._compute_depth(indexnode.name)
        self.conn.execute(
            'INSERT INTO topological_depth VALUES (?, ?)',
            (indexnode.name, depth),
        )

        return indexnode

    def add_or_update(self, node, force_overwrite=False, tags=None):
        if tags is None:
            tags = set()

        try:
            indexnode = self.index.node(node.name)
        except Missing:
            return 'add', self._add(node, tags=tags)
        else:
            depth = self.get_depth(indexnode.name)
            old_tags = self.resources.get_tags(indexnode.name)
            old_input = self.inputs.get(indexnode.name)
            add_tags = tags - old_tags

            force_overwrite |= node.serialized_input != old_input

            if (
                force_overwrite
                or depth == UNKNOWN_DEPTH
                and indexnode.state.is_pristine
            ):
                # XXX unduplicate
                self.ancestry.remove_node(indexnode)
                self.index.remove_multiple([node.name])
                self.workers.remove_runinfo(node.name)
                self.inputs.remove(node.name)
                return 'update', self._add(node, tags=tags)
            elif add_tags:
                # Should we have a way to remove tags at this level?
                for tag in add_tags:
                    self.resources.add_tag(node.name, tag)
                indexnode = self.index.node(node.name)
                return 'update', indexnode
            else:
                return 'have', indexnode

    def find_ready(self, *args, **kwargs):
        """Find one task that is ready to run."""
        cursor = self._find_ready(*args, **kwargs)
        result = cursor.fetchone()
        if result is None:
            raise Missing()

        return IndexNode.fromrow(result)

    def find_all_ready(self, *args, **kwargs):
        # We use this for testing, but it will be useful for workers
        # to pick up some number of small tasks simultaneously.
        cursor = self._find_ready(*args, **kwargs)
        return [IndexNode.fromrow(result) for result in cursor.fetchall()]

    def _find_ready(self, required_tags=None, supported_tags=None, names=None):
        if required_tags is None:
            required_tags = set()

        if supported_tags is None:
            supported_tags = set()

        supported_tags |= required_tags

        def questionmarks(seq):
            txt = ', '.join('?' * len(seq))
            return f'({txt})'

        required_tags_query = f"""\
SELECT name FROM resources
WHERE tag IN {questionmarks(required_tags)}
"""
        bad_tags_query = f"""\
SELECT DISTINCT(name) FROM resources
WHERE tag NOT IN {questionmarks(supported_tags)}
"""

        query_params = []
        requirements = ["registry.state='q'", 'registry.awaitcount=0']

        requirements.append(f'registry.name NOT IN ({bad_tags_query})')
        query_params += supported_tags

        if required_tags:
            requirements.append(f'registry.name IN ({required_tags_query})')
            query_params += required_tags

        where = '\n AND '.join(requirements)
        query = f'SELECT registry.* FROM registry WHERE\n {where}'
        return self.conn.execute(query, query_params)

    def _fetchall(self, query, *args):
        return self.conn.execute(query, *args).fetchall()

    def parent_states(self, name):
        states = {}

        done_count = 0
        for parent_name in self.ancestry.ancestors(name):
            if parent_name == UNREACHABLE_REF:
                states[parent_name] = State.new
                continue
            try:
                state = State(self.index.node(parent_name).state)
            except Missing:
                print('Cannot find', parent_name, 'a parent of', name)
                raise
            states[parent_name] = state
            if state == State.done:
                done_count += 1

        node = self.index.node(name)
        awaitcount = node.awaitcount
        if not (
            awaitcount == len(states) - done_count
            or (awaitcount == UNKNOWN_AWAITCOUNT)
        ):
            raise RuntimeError('Await count mismatch')
        return states

    def update_task_done(self, name):
        self._update_state(name, State.done)
        self.workers.register_task_done(name)

    def update_task_running(self, name, worker_name, myqueue_id):
        self._update_state(name, State.run)
        self.workers.register_task_running(name, myqueue_id, worker_name)

    def update_task_failed(self, name, error_msg):
        self._update_state(name, State.fail)
        self.cancel_descendants(name)
        self.workers.register_task_failed(name, error_msg)

    def clear_conflict(self, name):
        query = 'DELETE FROM conflicts WHERE task_name=(?)'
        self.conn.execute(query, (name,))

    def update_conflicts(self, name, conflict, reason='', buf=0):
        """Updates the coflictlog. If row does not exist it adds it"""
        query = (
            'INSERT INTO conflicts '
            '(task_name, conflict, reason, buf) VALUES (?, ?, ?, ?) '
            'ON CONFLICT(task_name) '
            'DO UPDATE SET conflict=?, reason=?, buf=?'
        )
        self.conn.execute(
            query, (name, conflict, reason, buf, conflict, reason, buf)
        )

    def get_conflict_info(self, name):
        query = (
            'SELECT conflict, reason, buf from conflicts WHERE task_name=(?)'
        )
        rows = self.conn.execute(query, (name,))
        for row in rows:
            return row
        return 'n', '', 0

    def _update_state(self, name, state):
        descendants = self.ancestry.descendants(name)
        indexnode = self.index.node(name)

        oldstate = State(indexnode.state)
        delta_readiness = (state == State.done) - (oldstate == State.done)

        self.index.update_state(indexnode.name, state.value)
        if state == State.new:
            self.workers.remove_runinfo(indexnode.name)
        for descendant in descendants:
            descendant_indexnode = self.index.node(descendant)
            if descendant_indexnode.awaitcount == UNKNOWN_AWAITCOUNT:
                continue

            if delta_readiness != 0:
                self.index.update_awaitcount(
                    descendant_indexnode.name,
                    descendant_indexnode.awaitcount - delta_readiness,
                )

    def remove_nodes(self, nodes):
        for node in nodes:
            self.ancestry.remove_node(node)
            self.clear_conflict(node.name)
            self.workers.remove_runinfo(node.name)
            self.resources.remove(node.name)
            self.inputs.remove(node.name)
        self.index.remove_multiple([node.name for node in nodes])

    def contains(self, name):
        return self.index.contains(name)

    @property
    def index(self):
        # XXX we need to hide the database tables
        # so we can keep them in sync
        # assert self.conn is not None
        return Index(self.conn)

    @property
    def workers(self):
        return Workers(self.conn)

    @property
    def ancestry(self):
        assert self.conn is not None
        return Ancestry(self.conn)

    @property
    def resources(self):
        return Resources(self.conn)

    @property
    def inputs(self):
        return SerializedInputTable(self.conn)


class Connection:
    def __init__(self, filename, timeout):
        self.filename = filename
        self._conn = None
        self.timeout = timeout

    @property
    def execute(self):
        return self._conn.execute

    @property
    def executemany(self):
        return self._conn.executemany

    def __enter__(self):
        assert self._conn is None
        self._conn = self._connect()
        return self._conn

    def __exit__(self, type, value, tb):
        if type is None:
            action = 'COMMIT'
        else:
            action = 'ROLLBACK'
        self._conn.execute(action)
        self._conn = None

    def _connect(self, max_retries=20):
        import time

        total_timeout = self.timeout
        pre_delay = 0.1
        warning_displayed = False
        while True:
            start = time.time()
            timeout = pre_delay + random() * 5
            total_timeout -= timeout
            pre_delay += 1.5
            try:
                connection = sqlite3.connect(
                    self.filename,
                    timeout=timeout,
                    detect_types=sqlite3.PARSE_DECLTYPES
                    | sqlite3.PARSE_COLNAMES,
                    isolation_level='EXCLUSIVE',
                )
                connection.execute('BEGIN EXCLUSIVE')

                # If warning was displayed, also then display that we
                # got the lock
                if warning_displayed:
                    print('Obtained lock in', time.time() - start)

            except sqlite3.OperationalError as err:
                max_retries -= 1
                if total_timeout > 0 and max_retries > 0:
                    print(
                        'Warning: Failed to obtain lock in',
                        time.time() - start,
                    )
                    warning_displayed = True
                    sleep(timeout / 3)
                    continue
                msg = 'Failed to open sqlite3-connection to' f'{self.filename}'
                raise RegistryError(msg) from err
            break
        return connection


class RegistryError(Exception):
    pass
