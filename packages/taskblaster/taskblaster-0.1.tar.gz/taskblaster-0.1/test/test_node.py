import pytest

from taskblaster.hashednode import Node
from taskblaster.storage import JSONProtocol


class FakeReference:
    def __init__(self, node):
        self.node = node

    def _tb_pack(self):
        return {'__tb_type__': 'ref', 'name': self.node.name, 'index': None}


def ref(node):
    # Utility function for building trees of nodes.
    return FakeReference(node)


def mknode(target, dct, name):
    from pathlib import Path

    return Node.new(JSONProtocol(Path('/tmp/nonexistent')), target, dct, name)


@pytest.mark.xfail
def test_node_equals():
    n1 = mknode('hello', {}, 'n1')
    n2 = mknode('hello', {}, 'n1')  # XXX this needs updating
    # when node identity checks are properly implemented
    assert 0
    assert n1 == n1
    assert n1 == n2


@pytest.mark.xfail
def test_node_equals_ordered():
    n1 = mknode('a', {'x': 1, 'y': 2}, 'n1')
    n2 = mknode('a', {'y': 2, 'x': 1}, 'n1')
    assert 0
    assert n1 == n2


@pytest.fixture
def nodes():
    a = mknode('a', {}, 'a')
    b = mknode('b', {'x': ref(a)}, 'b')
    c = mknode('c', {'x': ref(a), 'y': ref(b)}, 'c')
    d = mknode('d', {'args': [ref(n) for n in [a, b, c]]}, 'd')
    return (a, b, c, d)


def test_node_parents(nodes):
    (a, b, c, d) = nodes
    assert a.parents == tuple()
    assert b.parents == (a.name,)
    assert set(c.parents) == {a.name, b.name}
    assert set(d.parents) == {a.name, b.name, c.name}


def test_describe(nodes):
    for node in nodes:
        print(node.describe())
