from dataclasses import asdict as dataclass_asdict
from dataclasses import dataclass

from taskblaster.state import State


def iterate_collatz(n):
    i = 0
    while n != 1:
        n = collatz_function(n)
        i += 1
    return i


def collatz_function(n):
    return 3 * n + 1 if n % 2 else n // 2


@dataclass
class CollatzState:
    i: int
    n: int

    def tb_encode(self):
        return dataclass_asdict(self)

    @classmethod
    def tb_decode(cls, dct):
        return cls(**dct)


class TBCollatz:
    def __init__(self, n0):
        self.n0 = n0

    def init(self):
        return CollatzState(0, n=self.n0)

    def next_state(self, state, output):
        if output == 1:
            raise StopIteration

        return CollatzState(state.n + 1, output)

    def run(self, state):
        return collatz_function(n=state.n)
        # return tb.node('collatz_function', n=state.n)

    def tb_encode(self):
        return {'n0': self.n0}

    @classmethod
    def tb_decode(cls, dct):
        return cls(**dct)


def test_collatz(testdir):
    from taskblaster.repository import Repository

    repo = Repository.create(testdir)
    repo._tasks['collatz_function'] = collatz_function

    rn = repo.runner()

    n0 = 42
    workflow = TBCollatz(n0)

    with repo:
        rn.add_workflow(str(n0), workflow)

        print([*repo.tree().ls()])

    def ls(names=None):
        with repo:
            for line in repo.tree(names).ls():
                print(line)

    def runtask(name):
        repo.run_worker([name])
        ls([name])

    niter = iterate_collatz(n0)

    runtask(f'tree/{n0}')
    ls()

    with repo:
        nodes = [*repo.tree([f'tree/{n0}']).nodes_topological()]

        assert nodes[0].name.endswith('init')
        assert len(nodes) == niter + 1
        for i, node in enumerate(nodes[1:], start=1):
            assert node.state == State.done
            ancestors = repo.registry.ancestry.ancestors(node.name)
            assert ancestors == {nodes[i - 1].name}
