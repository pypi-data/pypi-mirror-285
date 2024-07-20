import pytest

from taskblaster.cache import FileCache
from taskblaster.hashednode import Node
from taskblaster.registry import Missing
from taskblaster.state import State
from taskblaster.storage import JSONProtocol


@pytest.fixture
def cache(tmp_path, registry):
    cache = FileCache(
        directory=tmp_path / 'tree',
        registry=registry,
        json_protocol=JSONProtocol(tmp_path),
    )
    with cache.registry.conn:
        yield cache


def mknode(target, dct, name):
    from pathlib import Path

    return Node.new(JSONProtocol(Path('/tmp/nonexistent')), target, dct, name)


@pytest.fixture
def nodes():
    return [
        mknode('hello', {}, 'a'),
        mknode('hello2', {}, 'b'),
        mknode('hello', {'a': 42}, 'c'),
    ]


def test_empty_cache(cache):
    assert len(cache) == 0
    assert '12345' not in cache
    assert len(list(cache)) == 0
    with pytest.raises(KeyError):
        cache['12345']


def test_cache_add(cache):
    """Test behaviour when adding a single node."""
    node = mknode('hello', {'a': 3, 'b': 4}, 'id')
    print(node.name)

    assert len(cache) == 0
    assert node.name not in cache
    action, indexnode = cache.add_or_update(node)
    assert action == 'add'
    assert len(cache) == 1

    assert indexnode.name in cache
    future1 = cache[node.name]
    assert future1.node.name == indexnode.name


def test_has_already(cache):
    node = mknode('hello', {}, 'id')
    cache.add_or_update(node)
    assert node.name in cache
    action, indexnode = cache.add_or_update(node)
    assert action == 'have'


def test_remove(cache, nodes):
    # We make 3 nodes.  Then we delete nodes[1] and verify that.

    for node in nodes:
        cache.add_or_update(node)

    n_initial = 3
    assert len(cache) == n_initial
    cache.delete_nodes([nodes[1]])
    n_remains = len(cache)
    assert n_remains == 2

    for i in range(3):
        exists = i != 1
        name = nodes[i].name
        assert (name in cache) == exists

        if exists:
            indexnode = cache.registry.index.node(name)
            assert indexnode.name == nodes[i].name
            assert cache.registry.inputs.get(name) == nodes[i].serialized_input


def test_repr(cache):
    print(str(cache))
    print(repr(cache))


def test_finished(cache):
    node = mknode('func', {'x': 1}, 'n1')
    cache.add_or_update(node)
    future = cache[node.name]  # Future(node, cache)
    node2 = mknode('func', {'x': future}, 'n2')
    cache.add_or_update(node2)

    def node2_awaitcount():
        return cache.registry.index.node(node2.name).awaitcount

    assert node2_awaitcount() == 1
    cache.registry._update_state(future.node.name, State.done)
    assert node2_awaitcount() == 0
    cache.registry._update_state(future.node.name, State.fail)
    assert node2_awaitcount() == 1


def test_find_ready(cache):
    node = mknode('func', {}, 'nodename')
    cache.add_or_update(node)
    with pytest.raises(Missing):
        cache.find_ready()
    cache.registry._update_state(node.name, State.queue)
    indexnode = cache.find_ready()
    assert indexnode.name == node.name


def test_none_ready(cache):
    with pytest.raises(Missing):
        cache.find_ready()


def add_and_submit_multiple(cache, ntasks):
    for n in range(ntasks):
        name = f'hello{n}'
        node = mknode('hello', {}, name)
        cache.add_or_update(node)
        cache.registry._update_state(node.name, State.queue)


def test_find_ready_tag(cache):
    add_and_submit_multiple(cache, ntasks=3)

    with pytest.raises(Missing):
        cache.find_ready(required_tags={'sometag'})

    cache.registry.resources.add_tag('hello2', 'sometag')

    task = cache.find_ready(required_tags={'sometag'})
    assert task.name == 'hello2'


def find_all_ready(cache, **kwargs):
    add_and_submit_multiple(cache, ntasks=5)

    resources = cache.registry.resources
    # (hello0 is left untagged)
    tagdata = [
        ('hello1', 'tag1'),
        ('hello2', 'tag1'),
        ('hello2', 'tag2'),
        ('hello3', 'tag2'),
        ('hello4', 'tag3'),
    ]

    resources.add_tags(tagdata)
    nodes = cache.registry.find_all_ready(**kwargs)
    return {node.name for node in nodes}


@pytest.mark.parametrize(
    'supported, required, expected_result',
    [
        (['tag1'], [], ['hello0', 'hello1']),
        (['tag2', 'tag3'], [], ['hello0', 'hello3', 'hello4']),
        ([], ['tag1'], ['hello1']),
        (['tag1'], ['tag2'], ['hello2', 'hello3']),
    ],
)
def test_find_by_tag_multi(cache, supported, required, expected_result):
    # The find_all_ready() function has a number of variously tagged tasks.
    #
    # This test issues some selections on that, then verifies the result.
    print(supported, required, expected_result)
    tasknames = find_all_ready(
        cache,
        supported_tags=set(supported),
        required_tags=set(required),
    )
    assert tasknames == set(expected_result)
