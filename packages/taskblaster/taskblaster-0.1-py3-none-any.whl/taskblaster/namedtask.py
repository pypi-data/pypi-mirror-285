import taskblaster as tb


class Task:
    def __init__(
        self,
        name,
        target,
        kwargs,
        dynamical=False,
        is_workflow=False,
        source=None,
        bts=None,
        branch=None,
        verify=None,
        tags=None,
    ):
        # XXX make the source mandatory
        self.name = name
        self.target = target
        self.kwargs = kwargs
        self.dynamical = dynamical  # XXX unused I think
        self.is_workflow = is_workflow
        self.source = source
        self.verify = verify
        # XXX Clean up, just take branch as input
        self.bts = bts
        if bts is not None:
            self.branch = bts.branch
            assert branch is None
        else:
            assert bts is None
            self.branch = branch
        assert self.branch is not None
        self.tags = tags

    def signature(self):
        tokens = ', '.join(
            f'{name}={value!r}' for name, value in self.kwargs.items()
        )
        return f'{self.target}({tokens})'

    def add_implicit_dependency(self, dependency, *, remove):
        """Add implicit dependency to Task

        We store the dependencies in kwargs in a list of 2-tuples in a variable
        called either __tb_implicit__ or __tb_implicit_remove__ with the
        full name of the dependency, and the dependency itself in the tuple.

        In case of __tb_implicit__, unrun will unrun this task, if the
        implicit dependency is unrun.

        In case of __tb_implicit_remove__, unrun will remove this task,
        if the 'implicit remove' dependency is unrun.
        """
        if not hasattr(dependency, 'name'):
            raise AttributeError('No attribute called name in dependency.')
        argname = f"__tb_implicit{'_remove' if remove else ''}__"
        if argname not in self.kwargs:
            self.kwargs[argname] = []
        self.kwargs[argname].append((dependency.name, dependency))

    def __repr__(self):
        sig = self.signature()
        return f'Task({self.name}, {sig})'

    def _node(self, cache):
        from taskblaster.hashednode import Node

        return Node.new(
            cache.json_protocol,
            self.target,
            dct=self.kwargs,
            name=self.name,
            dynamic_parent=self.source,
        )


# stage 1: task generation
#  save tasks with namerefs (unhashed).
#  we save/maintain the awaitcount using the namerefs.
#  when awaitcount is 0, a task can run

# stage 2: task execution
#  resolve dependencies: we can hash inputs/outputs of dependencies
#  as we want, and store that.  This allows checking/invalidating
#  if anything changes.
#  hash needs to be saved somewhere; it could be part of the output
#  ("record") since next task won't start until current task is done
#  anyway,


def new_workflowtask(workflow, name):
    # XXX This will be <run_path>.ActualClassName.  We need a mechanism
    # to have the actual file written down and (safely) get stuff from there.
    target = 'taskblaster.runner.run_workflow'
    kwargs = {'workflow': workflow}
    # target = f'{wfclass.__module__}.{wfclass.__name__}'
    # kwargs = {name: getattr(workflow, name) for name in workflow._inputvars}
    assert name.endswith(f'/{tb.INITNAME}')
    task = Task(
        name, target, kwargs, False, is_workflow=True, branch=tb.ENTRY_BRANCH
    )
    return task
