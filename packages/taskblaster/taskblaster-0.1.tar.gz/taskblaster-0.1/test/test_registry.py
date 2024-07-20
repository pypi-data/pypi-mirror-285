import sqlite3
from contextlib import contextmanager

import pytest

from taskblaster.registry import IndexNode, Registry
from taskblaster.state import State


def mknode(
    name,
    digest=None,
    state=State.new,
    awaitcount=0,
):
    # note: '' is not valid serialized input, it will only work so long as
    # nobody attempts to decode it.
    return IndexNode(
        name=name,
        state=state,
        awaitcount=awaitcount,
        workerclass='',
        argtext='dummy-text',
    )


@contextmanager
def mkregistry(directory, timeout=1):
    reg = Registry(directory / 'registry.dat', timeout)
    with reg.conn:
        yield reg


def test_index_add(index):
    assert index.count() == 0
    name = 'hello'
    index.add(mknode(name))

    assert index.contains(name)
    assert [node.name for node in index.nodes()] == [name]


def test_index_add_huge(index):
    assert index.count() == 0
    for i in range(200):
        name = str(hash('hello%d' % i))
        index.add(mknode(name))
    for i in range(199, 0, -1):
        name = str(hash('hello%d' % i))
        index.node(name)
    removed = []
    for i in range(199, 0, -1):
        name = str(hash('hello%d' % i))
        removed.append(name)
    index.remove_multiple(removed)


def test_index_delete(index):
    name = 'hello'

    index.add(mknode(name, 'arbitrary_dir'))
    index.add(mknode('hello2', 'other_dir'))

    assert index.count() == 2
    index.remove_multiple([name])
    assert index.count() == 1
    assert not index.contains(name)


@contextmanager
def fruit_db(tmp_path):
    with mkregistry(tmp_path) as registry:
        index = registry.index

        for name in ['apple', 'orange', 'lemon']:
            index.add(mknode(name, f'arbitrary_dir_{name}'))
        yield registry


@pytest.mark.skip
@pytest.mark.xfail(reason='wip locking system changes')
def test_locked(tmp_path):
    from taskblaster.registry import RegistryError

    with fruit_db(tmp_path):
        with pytest.raises(RegistryError):
            with mkregistry(tmp_path, timeout=0):
                pass


def test_readwrite(tmp_path):
    with fruit_db(tmp_path) as db:
        d1 = set(db.index.asdict())

    with mkregistry(tmp_path) as db2:
        d2 = set(db2.index.asdict())

    assert d1 == d2


# XXX Tests of new registry class below:


def test_index_empty(index):
    assert index.count() == 0


def test_add_contains(index):
    index.add(mknode('12345'))
    assert index.contains('12345')
    assert not index.contains('1234567890')
    assert index.count() == 1


def test_add_twice(index):
    index.add(mknode('123'))
    with pytest.raises(sqlite3.IntegrityError):
        index.add(mknode('123'))


def test_add_and_remove(index):
    name = '12345'
    node = mknode(name)
    index.add(node)
    assert index.contains(name)
    assert index.count() == 1

    index.remove_multiple([name])

    assert not index.contains(name)
    assert index.count() == 0


def test_index_multiple(index):
    for i in range(5):
        node = mknode(str(i))
        index.add(node)

    assert index.count() == 5
    index.remove_multiple(['1', '2'])
    names = {node.name for node in index.nodes()}
    assert names == {'0', '3', '4'}
    assert index.count() == 3
