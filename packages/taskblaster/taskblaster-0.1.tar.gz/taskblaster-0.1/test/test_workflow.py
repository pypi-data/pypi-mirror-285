import pytest

from taskblaster.repository import Repository
from taskblaster.testing import GeneratedWorkflow, PassPaths


class MyTasks:
    @staticmethod
    def hello(whom):
        return f'hello, {whom}!'

    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def multiply(a, b):
        return a * b


def workflow(rn):
    rn.task('hello')


@pytest.fixture
def newrepo(testdir):
    # Unlocked repository
    return Repository.create(testdir)


@pytest.fixture
def bigrepo(newrepo):
    inputs = ['hi1', 'hi2', 'hi3']
    wf = GeneratedWorkflow(inputs=inputs)
    with newrepo:
        newrepo.runner().run_workflow(wf)
    newrepo.run_worker(
        tree=['tree/generate_wfs_from_list/init'], name='test_worker'
    )
    return newrepo


@pytest.fixture
def pathpassrepo(newrepo):
    wf = PassPaths()
    with newrepo:
        newrepo.runner().run_workflow(wf)
    newrepo.run_worker(tree=['tree'], name='test_worker')
    return newrepo


def test_workflow_hello(newrepo):
    newrepo._tasks['hello'] = MyTasks.hello

    rn = newrepo.runner()

    whom = 'world'

    with newrepo:
        hello = rn.task('hello', whom=whom, name='xxx')

    hello.run_blocking(newrepo)

    with newrepo:
        assert hello.has_output()
        record = hello.resolve_future_value()
    assert record.output == f'hello, {whom}!'


def test_workflow(newrepo):
    newrepo._tasks['add'] = MyTasks.add
    newrepo._tasks['multiply'] = MyTasks.multiply

    rn = newrepo.runner()

    with newrepo:
        five = rn.task('add', a=2, b=3, name='add')
        twenty = rn.task('multiply', a=five.output, b=4, name='mul')

    twenty.runall_blocking(newrepo)
    with newrepo:
        assert twenty.resolve_future_value().output == 20


def test_generate_wf(bigrepo):
    with bigrepo:
        lines = [*bigrepo.tree().ls()]
    assert len(lines) == 44


def test_pass_paths(pathpassrepo):
    with pathpassrepo:
        lines = [*pathpassrepo.tree().ls()]
    assert len(lines) == 4


def test_create_cancelled(tool):  # simplerepo, workflow_classes):
    from taskblaster.state import State

    repo = tool.repo
    wf = tool.simpleworkflow(msg='hello')
    rn = repo.runner()

    with repo:
        rn.run_workflow(wf)

    repo.run_all_tasks()

    with repo:
        nodename = 'dependsondependsonfail'
        print(repo.tree().stat())
        node = repo.registry.index.node(nodename)
        assert node.state == State.cancel

        _, confirm = repo.tree([f'tree/{nodename}']).remove()
        confirm()
        assert not repo.registry.contains(nodename)

    wf = tool.simpleworkflow(msg='hello')
    with repo:
        rn.run_workflow(wf)

        node = repo.registry.index.node(nodename)
        assert node.state == State.cancel
