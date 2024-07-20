import sqlite3

import pytest

from taskblaster.registry import Ancestry


@pytest.fixture
def ancestry(tmp_path):
    dbfile = tmp_path / 'ancestry.db'
    with sqlite3.connect(dbfile) as conn:
        Ancestry.initialize(conn)
        yield Ancestry(conn)


@pytest.fixture
def familytree(ancestry):
    ancestry.add('wotan', 'siegmund')
    ancestry.add('wotan', 'sieglinde')

    ancestry.add('wotan', 'brünnhilde')
    ancestry.add('erda', 'brünnhilde')

    ancestry.add('siegmund', 'siegfried')
    ancestry.add('sieglinde', 'siegfried')
    return ancestry


def test_ancestry(familytree):
    assert familytree.ancestors('siegfried') == {'siegmund', 'sieglinde'}
    assert familytree.ancestors('brünnhilde') == {'wotan', 'erda'}
    assert familytree.ancestors('wotan') == set()
    assert familytree.descendants('wotan') == {
        'siegmund',
        'sieglinde',
        'brünnhilde',
    }
    assert familytree.descendants('siegmund') == {'siegfried'}
    assert familytree.descendants('siegfried') == set()


def test_contains(familytree):
    assert familytree.contains('wotan', 'siegmund')


def test_containsnot(familytree):
    assert not familytree.contains('wotan', 'fafner')


def test_add_twice(ancestry):
    ancestry.add('hello', 'world')
    with pytest.raises(sqlite3.IntegrityError):
        ancestry.add('hello', 'world')


def test_remove(familytree):
    parents = familytree.ancestors('brünnhilde')
    descendants = familytree.descendants('erda')
    assert 'erda' in parents
    assert 'brünnhilde' in descendants

    familytree.remove('erda', 'brünnhilde')

    assert familytree.ancestors('brünnhilde') == parents - {'erda'}
    assert familytree.descendants('erda') == descendants - {'brünnhilde'}


def test_cannot_remove(ancestry):
    assert not ancestry.contains('hello', 'world')
    with pytest.raises(KeyError):
        ancestry.remove('hello', 'world')
