from taskblaster.state import State


def parent_state_info(registry, name):
    regnode = registry.index.node(name)

    parent_states = registry.parent_states(name)
    nparents = len(parent_states)
    okcount = list(parent_states.values()).count(State.done)

    from taskblaster.registry import UNKNOWN_AWAITCOUNT

    if not (
        regnode.awaitcount == len(parent_states) - okcount
        or (regnode.awaitcount == UNKNOWN_AWAITCOUNT)
    ):
        raise RuntimeError('awaitcount mismatch.')

    if okcount == nparents:
        deps_color = State.done.color
    elif any(state.unsuccessful for state in parent_states.values()):
        deps_color = State.fail.color
    else:
        deps_color = State.new.color

    return okcount, nparents, deps_color


class Record:
    # XXX Either we need to reconcile this with ASR record objects,
    # or we need another name if it does not make sense to unify them.
    def __init__(self, node, inputs, directory, output):
        self.node = node
        self.inputs = inputs
        self.directory = directory
        self.output = output

    def __repr__(self):
        return f'<Record({self.node.name}, {self.directory})'


class Future:
    def __init__(self, node, cache):
        self.node = node
        self._cache = cache

    def _tb_pack(self):
        return {'__tb_type__': 'ref', 'name': self.node.name, 'index': None}

    @property
    def directory(self):
        return self._entry.directory

    @property
    def output(self):
        return Reference(self)

    @property
    def _actual_output(self):
        return self._entry.output()

    @property
    def _entry(self):
        return self._cache.entry(self.node.name)

    @property
    def _actual_inputs(self):
        target, namespace = self._cache.load_inputs_and_resolve_references(
            self.node
        )
        assert target == self.node.target
        return namespace

    def resolve_future_value(self):
        output = self._actual_output
        inputs = self._actual_inputs
        return Record(self.node, inputs, self.directory, output)

    @property
    def index(self):
        # Reference objects have indices that are tuples.
        # We distinguish ourselves by having an index which is None.
        return None

    def __repr__(self):
        return (
            f'<Future({self.node.target}, {self.node.name}, '
            f'{self.directory})>'
        )

    def _ancestors(self, seen):
        node = self.node

        for name in node.parents:
            ancestor = self._cache.get(name)
            yield from ancestor._ancestors(seen)

        if node not in seen:
            seen.add(node)
            yield self

    def ancestors(self):
        """Yield self and all ancestors in topological order."""
        # Document ordering.  Is current ordering the best?
        yield from self._ancestors(set())

    def has_output(self):
        return self._entry.has_output()

    def runall_blocking(self, repo):
        with repo:
            ancestors = [
                ancestor
                for ancestor in self.ancestors()
                if not ancestor.has_output()
            ]

        for ancestor in ancestors:
            ancestor.run_blocking(repo)

        if ancestors:
            # The final ancestor iterated over should be self,
            # unless all of them were done and we therefore did not
            # iterate over any
            assert ancestor is self

    def run_blocking(self, repo):
        from taskblaster.worker import Worker

        with repo:
            indexnode = self._cache.registry.index.node(self.node.name)
        worker = Worker(repo, selection=iter([indexnode]))
        loaded_task = worker.acquire_task()
        loaded_task.run(worker)
        # (Should this return the output?)

    @property
    def indexnode(self):
        return self._cache.registry.index.node(self.node.name)

    def describe(self):
        from taskblaster.listing import NodeInfo

        return NodeInfo(
            node=self.indexnode,
            registry=self._cache.registry,
            treedir=self._cache.directory,
            fromdir=self._cache.directory.parent,
            columns='sif',
        ).to_string()


class Reference:
    def __init__(self, future, index=tuple()):
        self.future = future
        self.index = index

    def __getitem__(self, index):
        return Reference(self.future, (*self.index, index))

    @property
    def node(self):
        return self.future.node

    def resolve_future_value(self):
        value = self.future._actual_output
        for i in self.index:
            value = value[i]
        return value

    def __repr__(self):
        node = self.future.node
        if not self.index:
            indexstr = '<returnval>'
        else:
            indexstr = ', '.join(repr(i) for i in self.index)
        return f'<Reference {node.name}-{node.shorthash}[{indexstr}]>'

    def _tb_pack(self):
        return {
            '__tb_type__': 'ref',
            'name': self.node.name,
            'index': list(self.index),
        }
