import sqlite3

import pytest

from taskblaster.resources import Resources


@pytest.fixture
def resources():
    conn = sqlite3.connect(':memory:')
    return Resources.initialize(conn)


@pytest.fixture
def tags():
    return [
        ('name1', 'tag1'),
        ('name1', 'tag2'),
        ('name2', 'tag2'),
        ('name2', 'tag3'),
    ]


def test_add(resources):
    nothing = resources.select_all()
    assert nothing == []

    assert not resources.has_tag('name', 'tag')
    resources.add_tag('name', 'tag')
    assert resources.has_tag('name', 'tag')

    assert resources.select_all() == [('name', 'tag')]
    assert resources.get_tags('name') == {'tag'}


def test_add_twice(resources):
    # Adding twice is same as adding once.
    resources.add_tag('name', 'tag')
    resources.add_tag('name', 'tag')

    assert resources.select_all() == [('name', 'tag')]


def test_many(resources, tags):
    resources.add_tags(tags)

    assert resources.get_tags('name1') == {'tag1', 'tag2'}
    assert resources.get_tags('name2') == {'tag2', 'tag3'}
    assert set(resources.select_all()) == set(tags)


def test_untag(resources, tags):
    tags = set(tags)
    resources.add_tags(tags)
    resources.untag('name1', 'tag1')

    assert set(resources.select_all()) == {
        ('name1', 'tag2'),
        ('name2', 'tag2'),
        ('name2', 'tag3'),
    }


def test_remove_name(resources, tags):
    resources.add_tags(tags)
    resources.remove('name1')
    assert set(resources.select_all()) == {
        ('name2', 'tag2'),
        ('name2', 'tag3'),
    }
