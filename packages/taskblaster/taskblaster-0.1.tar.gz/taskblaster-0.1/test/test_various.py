import pytest

from taskblaster.state import State
from taskblaster.testing import CompositeWorkflow

NTASKS = 13


@pytest.fixture
def bigrepo(repo):
    wf = CompositeWorkflow(msg='hello')
    repo.runner().run_workflow(wf)
    return repo


def test_workflow(bigrepo):
    # (The fixture already runs the workflow)
    assert bigrepo.registry.index.count() == NTASKS


def test_ls_empty(repo):
    assert repo.registry.index.count() == 0
    lines = [*repo.tree().ls()]
    assert set(lines[0].split()) >= {'deps', 'state', 'folder'}
    assert set(lines[1]) == {'─'}
    assert len(lines) == 2


def test_ls_nonempty(bigrepo):
    lines = [*bigrepo.tree().ls()]
    assert len(lines) == 2 + NTASKS
    assert 'tree/' in lines[-1]


def test_stat(bigrepo):
    stats = bigrepo.tree().stat()
    txt = stats.tostring()
    assert str(NTASKS) in txt
    assert 'new' in txt

    counts = stats.counts
    assert counts.pop(State.new) == NTASKS
    assert not any(counts.values())
