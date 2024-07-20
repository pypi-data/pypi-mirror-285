import functools
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict
from warnings import warn


class TBUserError(Exception):
    """Errors in workflows or other components controlled by user."""


# Name for the default branch (i.e. branch name used for branches without
# @tb.branch decorator)
ENTRY_BRANCH = 'entry'

# Database name for unreachable reference
# Instance of UnreachableReference will be stored to db with this name
UNREACHABLE_REF = '__tb_unreachable__'

# Magical name of workflow initializer task:
INITNAME = 'init'


class Reference:
    """Simplest possible class to represent a dependency.

    It consisists of full name of the task and possible indexing of the
    tasks output. BoundTaskSpecification is a superclass, but internally
    the class is used by taskblaster to create relationships between
    tasks.
    """

    def __init__(self, name, index=None):
        self._name = name
        if index is None:
            index = tuple()
        self.index = index

    def _tb_pack(self):
        """_tb_pack attribute is to be set when packing kwargs of a task
        specification, and it will return a json-serializable dictionary.
        """
        return {'__tb_type__': 'ref', 'name': self._name, 'index': self.index}

    @property
    def name(self):
        return self._name

    @property
    def unreachable(self):
        return False


class UnreachableReference(Reference):
    """Reference which cannot ever be met.

    This is used for placeholder for a task which is not supposed to have its
    dependencies met, but we do not know its dependencies yet either.
    """

    def __init__(self):
        super().__init__(UNREACHABLE_REF)

    @property
    def unreachable(self):
        return True


class HashedExternalFile:
    def __init__(self, path, digest):
        self.path = path
        self.digest = digest

    def __repr__(self):
        return f'HashedExternalFile({self.path} [{self.digest}])'

    def tb_encode(self):
        return dict(path=str(self.path), digest=self.digest)

    @classmethod
    def tb_decode(cls, data):
        return cls(**data)


class ExternalFile:
    def __init__(self, path):
        from pathlib import Path

        # XXX should be resolved relative to root
        self.path = Path(path).resolve()

    def tb_encode(self):
        return str(self.path)

    @classmethod
    def tb_decode(cls, data):
        return cls(data)

    def _filehash(self):
        from hashlib import sha256

        chunksize = 2**16
        hashobj = sha256()
        with self.path.open('rb') as fd:
            while True:
                chunk = fd.read(chunksize)
                if not chunk:
                    break
                hashobj.update(chunk)
        return hashobj.hexdigest()

    def hashed(self):
        digest = self._filehash()
        return HashedExternalFile(self.path, digest)

    def __repr__(self):
        return f'ExternalFile({self.path!r})'


class InputVariable:
    """Declaration of a workflow input variable."""

    def __init__(self, default):
        self._default = default


_no_default = object()


def var(default=_no_default) -> InputVariable:
    """Define an input variable for a workflow.

    If ``default`` is specified, the input variable becomes optional.

    Example::

      @tb.workflow
      class MyWorklow:
          x = tb.var()
          y = tb.var(default=42)

      wf = MyWorkflow(x=17)
    """
    return InputVariable(default)


class TBProperty(property):
    """Superclass for all workflow properties

    Currently, this includes
      * task
      * subworkflow
      * dynamical_workflow_genarator
    decorators.

    XXX To be extended further.
    """

    def __init__(self, *, fget):
        super().__init__(fget=fget)
        self.branch = ENTRY_BRANCH
        self.jump = None
        self._if = None
        self.external = False
        self.loop = False


class StopWorkflow(Exception):
    """Error signaling workflow execution to stop due to unresolved output."""


class TaskBlasterInterrupt(Exception):
    pass


class TaskView:
    def __init__(self, node, future):
        self._future = future
        self.node = node

    @property
    def input(self):
        return self._future._entry.read_inputfile()

    @property
    def output(self):
        return (
            self._future._entry.output()
            if self._future._entry.has_output()
            else None
        )

    @property
    def realized_input(self):
        return self._future._actual_inputs


def actions(**actions):
    """Return decorator for task function to provide custom actions."""

    def deco(func):
        func._tb_actions = actions
        return func

    return deco


class subworkflow(TBProperty):
    def __init__(self, meth):
        self.meth = meth
        self._tb_subworkflow = True

        @functools.wraps(meth)
        def wrapper(self, **kwargs):
            workflow = meth(self, **kwargs)
            workflow._rn = self._rn.with_subdirectory(meth.__name__)
            return workflow

        super().__init__(fget=wrapper)


# XXX To be removed, by flagging the task to by a dynamical workflow
# task by some other way
def dynamical_workflow_generator_task(f):
    f._tb_dynamical_workflow_generator_task = True
    return f


def dynamical_workflow_generator(result_tasks=None):
    # XXX To be refactored
    class dynamical_workflow_generator_property(TBProperty):
        def __init__(self, meth):
            self.meth = meth
            self._tb_result_tasks = result_tasks
            self._tb_dynamical_workflow_generator = True
            self.generated_wf = None

            def wrapper(self_noshadow, **kwargs):
                return self.generated_wf

            super().__init__(fget=wrapper)

        def __call__(self, *args, **kwargs):
            return self.meth(*args, **kwargs)

    return dynamical_workflow_generator_property


class TaskSpecificationProperty(TBProperty):
    def __init__(self, unbound_meth, *, is_workflow=False, tags=None):
        self.unbound_meth = unbound_meth
        self.is_workflow = is_workflow
        self.tags = tags
        super().__init__(fget=self._fget)

    @property
    def methname(self):
        return self.unbound_meth.__name__

    def _fget(self, workflow):
        name = workflow._rn.get_full_name(self.methname)
        if self.loop:
            name += '-%03d' % workflow._rn._seen_branches[self.branch]

        return BoundTaskSpecification(name, self, workflow)

    @classmethod
    def decorator(cls, **kwargs):
        return lambda method: cls(method, **kwargs)

    def __repr__(self):
        # XXX Display special attributes only if they are set
        return (
            f'TaskSpecificationProperty({self.unbound_meth.__name__!r}, '
            f"is_workflow={self.is_workflow}, branch='{self.branch}', "
            f'_if={self._if}, loop={self.loop}, '
            f'jump={self.jump}, branch={self.branch})'
        )


class UserWorkflowError(Exception):
    pass


GETITEM = '['
GETATTR = '.'


class BoundTaskSpecification(Reference):
    def __init__(self, name, declaration, workflow, index=tuple()):
        assert index is not None
        super().__init__(name, index)
        self.declaration = declaration
        self.workflow = workflow

    def previous_loop(self):
        name, iteration = self._name.split('-')
        name = f'{name}-{int(iteration)-1:03d}'
        return BoundTaskSpecification(
            name, self.declaration, self.workflow, index=self.index
        )

    @property
    def jump(self):
        return self.declaration.jump

    @property
    def _if(self):
        return self.declaration._if

    @property
    def external(self):
        return self.declaration.external

    @property
    def branch(self):
        return self.declaration.branch

    @property
    def name(self):
        # Confusingly we rename the specification with /init at the end
        # if it is a workflow.  Maybe this can be avoided or hidden more.
        if self.declaration.is_workflow:
            return f'{self._name}/{INITNAME}'
        else:
            return self._name

    def __call__(self):
        """At workflow level, call wrapped unbound method to produce node."""
        try:
            return self.declaration.unbound_meth(self.workflow)
        except Exception as ex:
            raise UserWorkflowError from ex

    def task(self):
        from taskblaster.namedtask import Task, new_workflowtask

        taskspec = self()

        if self.external:
            taskspec.kwargs.update({'__tb_external__': True})

        if getattr(taskspec, '_is_tb_workflow', False):
            # Old-style class workflows are not TaskSpecs at all,
            # but we want to treat workflows more like tasks so
            # here we pretend and normalize it into a Task.
            #
            # This approach use some cleanup.
            return new_workflowtask(taskspec, self.name)

        return Task(
            self.name,
            taskspec.target,
            taskspec.kwargs,
            is_workflow=self.declaration.is_workflow,
            bts=self,
            verify=taskspec.verify,
            tags=self.declaration.tags,
        )

    def __repr__(self):
        return (
            f'{type(self).__name__}({self.name!r}, {self.declaration}, '
            f'{self.workflow}, {self.index})'
        )

    def __getitem__(self, index):
        """Reference of index into output of this task specification.

        Return new reference which is an index into the return value of
        another task.

        For example a workflow can do tb.node(x=self.othertask['hello']).

        """
        return self._accessor(GETITEM, index)

    def __getattr__(self, name):
        """Reference via attributes into output of this task specification.

        Return new reference which is an index into the return value of
        another task.

        For example a workflow can do tb.node(x=self.othertask.hello).

        """
        return self._accessor(GETATTR, name)

    def _accessor(self, code, index):
        newindex = (*self.index, (code, index))
        return BoundTaskSpecification(
            self.name, self.declaration, self.workflow, newindex
        )


def fixedpoint(_property):
    """Specifies that this is an OUTPUT of a workflow, to which other
    workflows can depend on.
    """
    if not isinstance(_property, TaskSpecificationProperty):
        raise TBUserError(
            '@taskblaster.fixedpoint decorator should be above'
            ' @taskblaster.task'
        )
    _property.external = True
    return _property


def jump(branch_name=None, on_success=None):
    """Specifies that there is an jump to another branch from this branch.

    If branch_name is specified, the jump will be UNCONDITIONAL.
    If on_success is given, the jump will only be done if the task
    is succesful
    """
    if (branch_name is None) == (on_success is None):
        raise TBUserError(
            'Exactly one of the arguments branch_name or on_success'
            ' must be specified.'
        )

    def wrapper(_property):
        if not isinstance(_property, TBProperty):
            raise TBUserError(
                '@taskblaster.jump decorator should be above'
                ' @taskblaster.task/subworkflow decorators'
            )
        _property.jump = {'branch': branch_name, 'on_success': on_success}
        return _property

    return wrapper


def _if(dct=None, *, true=None, false=None):
    """Specifies that there is a CONDITIONAL jump to another branch.

    If the result returned by the task decorated evaluated to True,
    true branch is selected, and otherwise false branch is selected.
    """

    def wrapper(_property):
        if not isinstance(_property, TaskSpecificationProperty):
            raise TBUserError(
                '@taskblaster._if decorator should be above @taskblaster.task'
            )

        if dct is not None:
            if true is not None or false is not None:
                raise TBUserError(
                    '@taskblaster._if decorator should be used either '
                    'by passing a switch dictionary or true, false keywords, '
                    'not both.'
                )
            _property._if = dct
        else:
            _property._if = {True: true, False: false}

        return _property

    return wrapper


class Phi:
    """Phi operator, as is commonly used in intermet"""

    UNRESOLVED = '<unresolved Phi operator>'

    def __init__(self, index=tuple(), **kwargs):
        self.index = index
        self.kwargs = kwargs
        self.resolved = Phi.UNRESOLVED

    def resolve(self, runner):
        try:
            resolved = self.kwargs[runner._from_branch]
        except KeyError:
            # XXX Implicitly allowing to jump here from another
            # branches as well. Is this good or not?
            # Alternate is to require all branches to be specified
            # at jump, for example Phi(a=None, b=None, c=self.x).
            resolved = None

        if (
            resolved is not None
            and runner._from_branch == runner._current_branch
        ):
            resolved = resolved.previous_loop()

        assert self.resolved is Phi.UNRESOLVED
        for _type, name in self.index:
            resolved = resolved._accessor(_type, name)

        self.resolved = resolved
        return self.resolved

    def _tb_pack(self):
        assert self.resolved is not Phi.UNRESOLVED
        return self.resolved

    def __getitem__(self, index):
        return self._accessor(GETITEM, index)

    def __getattr__(self, name):
        return self._accessor(GETATTR, name)

    def _accessor(self, code, index):
        newindex = (*self.index, (code, index))
        return Phi(index=newindex, **self.kwargs)


def branch(name, loop=False):
    """Specifies that a task or a subworkflow is to belong to a particular
    branch.
    """

    def wrapper(_property):
        if not isinstance(_property, TBProperty):
            if callable(_property):
                add = ' Missing @taskblaster.task?'
            else:
                add = ''
            raise UserWorkflowError(
                '@taskblaster.branch decorator not allowed'
                f'for {_property}.{add}'
            )
        _property.branch = name
        _property.loop = loop
        return _property

    return wrapper


class VerificationFailed(Exception):
    pass


def verify_external_file_task(inputs, output):
    external_path = inputs['path']
    # print('Verifying external file', external_path)
    external_digest = ExternalFile(external_path).hashed().digest
    # print('external digest', external_digest)
    stored_digest = output.digest
    # print('stored digest', stored_digest)
    if stored_digest != external_digest:
        raise VerificationFailed(
            f'Warning: External file {external_path}'
            f'({external_digest[:8]}...) does not match '
            f'stored hash ({stored_digest[:8]}...)'
        )


def external_file(meth):
    @functools.wraps(meth)
    def task_fun(self):
        # Calls the method at Workflow class level to get the
        # BoundTaskSpecification reference to the file
        argument = meth(self)
        assert isinstance(argument, (Input, BoundTaskSpecification, str, Path))
        return node(
            'taskblaster.external_file_task',
            path=argument,
            __tb_verify__='taskblaster.verify_external_file_task',
        )

    return task(task_fun)


def task(_meth=None, **kwargs):
    """Decorator to specify tasks within the workflow class.

    Returns a property of type TaskSpecificationProperty.
    """
    deco = TaskSpecificationProperty.decorator(is_workflow=False, **kwargs)

    if _meth is None:
        return deco
    else:
        assert not kwargs
        return deco(_meth)


class TaskSpec:
    def __init__(self, target, kwargs, verify=None):
        self.target = target
        self.kwargs = kwargs
        self.verify = verify

    def __repr__(self):
        return (
            f'<TaskSpec({self.target}, '
            f'{self.kwargs}, verify={self.verify})'
        )


def node(target, **kwargs):
    verify = kwargs.pop('__tb_verify__', None)
    return TaskSpec(target, kwargs, verify=verify)


def define(meth):
    @functools.wraps(meth)
    def wrapper(self):
        obj = meth(self)
        return node('define', obj=obj)

    return task(wrapper)


class Input:
    def __init__(self, value, *, _index=tuple()):
        # If the input variable has no default, it actually defaults to
        # the unique _no_default object which means we don't allow it.
        assert value is not _no_default
        self._value = value
        self.index = _index

    def __repr__(self):
        indextext = ''.join(f'[{part!r}]' for part in self.index)
        return f'<Input({self._value!r}){indextext}>'

    def _tb_pack(self):
        return self.getvalue()

    def getvalue(self):
        # XXX This indexing pattern exists in approximately two places.
        obj = self._value
        for _type_and_index in self.index:
            if isinstance(_type_and_index, (list, tuple)):
                _type, index = _type_and_index
                if _type == GETITEM:
                    obj = obj[index]
                elif _type == GETATTR:
                    obj = getattr(obj, index)
                else:
                    assert 0
            else:
                # Old style defaults to getitem
                obj = obj[_type_and_index]

        return obj

    def __getitem__(self, item):
        return Input(self._value, _index=(*self.index, (GETITEM, item)))

    def __getattr__(self, item):
        return Input(self._value, _index=(*self.index, (GETATTR, item)))


def totree(definitions, name, root=None):
    def workflow(rn):
        if root is not None:
            rn = rn.with_subdirectory(root)

        for key in definitions:
            obj = definitions[key]
            rn1 = rn.with_subdirectory(key)
            fullname = f'{key}/{name}'
            rn1.define(obj, fullname)

    return workflow


class DummyUnboundTask:
    """XXX To be removed and replaced with reference"""

    def __init__(self, future, *, _index=tuple()):
        self.future = future
        self.name = str(future.directory.relative_to(future._cache.directory))

        self.index = _index

    def _refhook(self):
        return self

    def _tb_pack(self):
        return {
            '__tb_type__': 'ref',
            'name': self.future.node.name,
            'index': self.index,
        }

    def __getitem__(self, index):
        return DummyUnboundTask(
            self.future, _index=(*self.index, (GETITEM, index))
        )

    def __getattr__(self, index):
        return DummyUnboundTask(
            self.future, _index=(*self.index, (GETATTR, index))
        )

    @property
    def unreachable(self):
        return False


def _oldglob(cache, pattern):
    for future in cache.values():
        # TODO: Efficient lookup for matching patterns.
        # Maybe we cannot do general globs then?  But that's okay.
        path = future.directory
        relpath = path.relative_to(cache.directory)

        if relpath.match(pattern):
            yield future, relpath


def _newglob(cache, pattern):
    for indexnode in cache.registry.index.glob_simple(pattern):
        future = cache[indexnode.name]
        path = future.directory
        relpath = path.relative_to(cache.directory)
        yield future, relpath


def parametrize_glob(pattern, *, globmethod='old'):
    if globmethod == 'old':
        globfunction = _oldglob
    elif globmethod == 'new':
        globfunction = _newglob
    else:
        raise ValueError(globmethod)

    def wrap(workflow_cls):
        def workflow(rn):
            cache = rn._cache

            assert rn.directory.samefile(cache.directory)

            # XXX This should be a kind of query instead of
            # looping over all the values.

            for future, relpath in globfunction(cache, pattern):
                unbound_task = DummyUnboundTask(future)

                actual_workflow = workflow_cls(unbound_task)
                rn1 = rn.with_subdirectory(relpath.parent)
                rn1.run_workflow(actual_workflow)

        return workflow

    return wrap


class BranchSpecification:
    def __init__(
        self, unbound_tasks, subworkflows, dynamical_workflow_generators
    ):
        self.unbound_tasks = unbound_tasks
        self.subworkflows = subworkflows
        self.dynamical_workflow_generators = dynamical_workflow_generators

        branching_tasks = []
        loop = None
        for unbound_task in unbound_tasks.values():
            if unbound_task.loop is not None:
                if loop is not None:
                    if unbound_task.loop != loop:
                        raise TBUserError(
                            'All branch definitions with equal name must'
                            ' have same loop=True/False condition.'
                        )
                loop = unbound_task.loop
            if unbound_task.jump is not None:
                branching_tasks.append(unbound_task)
            # Deliberately not elif here to catch _if and jump both defined
            # error!
            if unbound_task._if is not None:
                branching_tasks.append(unbound_task)

        self.loop = loop

        if len(branching_tasks) > 1:
            raise TBUserError(
                'Only one branching decorator per branch allowed.'
            )

        # Figure out which task branches,
        # and to which branches this task can branch to
        self.jumps = []
        self.if_task = None
        if len(branching_tasks) == 1:
            task = branching_tasks[0]
            if task.jump is not None:
                self.jumps = [task.jump]
            if task._if is not None:
                self.jumps = [
                    target for target in task._if if target is not None
                ]
                self.if_task = task

    @classmethod
    def from_workflow_class(cls, workflow_cls):
        branch_names = []
        for name, value in vars(workflow_cls).items():
            if isinstance(value, TBProperty):
                branch_names.append(value.branch)

        # Make sure the is a dictionary corresponding to entry branch
        if ENTRY_BRANCH not in branch_names:
            branch_names.append(ENTRY_BRANCH)
            warning_str = (
                f'Workflow has no {ENTRY_BRANCH} branch. Not doing anything.'
            )
            warn(warning_str)

        # Add properties from all branches
        branches = {
            branch_name: cls.by_name(workflow_cls, branch_name)
            for branch_name in branch_names
        }
        return branches

    @classmethod
    def by_name(cls, workflow_cls, branch_name):
        unbound_tasks = {}
        subworkflows = {}
        dynamical_workflow_generators = {}

        def correct_branch(_property):
            return branch_name == _property.branch

        for name, value in vars(workflow_cls).items():
            if isinstance(value, TaskSpecificationProperty):
                if not correct_branch(value):
                    continue
                unbound_tasks[name] = value
            elif isinstance(value, subworkflow):
                if not correct_branch(value):
                    continue
                subworkflows[name] = value
            elif hasattr(value, '_tb_dynamical_workflow_generator'):
                if not correct_branch(value):
                    continue
                dynamical_workflow_generators[name] = value

        return cls(unbound_tasks, subworkflows, dynamical_workflow_generators)


def workflow(cls):
    """Class decorator for workflows.

    Example::

      @workflow
      class MyClass:
          a = tb.var()

          ...
    """
    # Gather all of the input variables to one dictionary
    inputvars = {}
    for name, value in vars(cls).items():
        if isinstance(value, InputVariable):
            inputvars[name] = value

    cls._inputvars = inputvars

    # Define constructor for the Workflow class
    def constructor(self, **kwargs):
        self.inputs = kwargs

        self._rn = None

        names = set(inputvars)

        for name in names:
            if name in kwargs:
                value = kwargs[name]
            else:
                value = inputvars[name]._default
                if value is _no_default:
                    raise TypeError(
                        f'Workflow missing required keyword argument: {name}'
                    )

            if not getattr(value, '_is_tb_workflow', None):
                # We want all workflow inputs to be "future"-ish.
                # Therefore:
                #  * Given a "future"-ish value, we do nothing in particular.
                #  * Given a concrete value, we store Input(value).
                value = Input(value)

            setattr(self, name, value)

        keys = set(kwargs.keys())
        extra_variables = keys.difference(names)
        if extra_variables:
            raise TBUserError(
                f'Unrecognized variables to workflow {extra_variables}'
            )

    cls._is_tb_workflow = True
    cls.__init__ = constructor

    # Create the default branch
    cls._branches = BranchSpecification.from_workflow_class(cls)

    def get_branch(self):
        branch = self._rn._current_branch
        if branch not in self._branches:
            raise TBUserError(f"Branch {branch} doesn't exist.")
        return self._branches[branch]

    # Define a wrapper for dynamical workflow generators
    def get_dynamical_workflow_generators(self):
        branch = get_branch(self)
        return branch.dynamical_workflow_generators

    cls._dynamical_workflow_generators = property(
        get_dynamical_workflow_generators
    )

    # Define a wrapper for subworkflows
    def get_subworkflows(self):
        branch = get_branch(self)
        return branch.subworkflows

    cls._subworkflows = property(get_subworkflows)

    # Define a wrapper for unbound tasks
    def get_unbound_tasks(self):
        branch = get_branch(self)
        return branch.unbound_tasks

    cls._unbound_tasks = property(get_unbound_tasks)

    # Define a wrapper for unbound tasks
    def get_external_tasks(self):
        externals = {}
        for branch in self._branches.values():
            for task_name, task in branch.unbound_tasks.items():
                if task.external:
                    externals[task_name] = task
        return externals

    cls._external = property(get_external_tasks)

    def __repr__(self):
        clsname = type(self).__name__
        vartext = ', '.join(
            '{}={}'.format(varname, getattr(self, varname))
            for varname in sorted(self._inputvars)
        )
        return f'<{clsname}({vartext})>'

    cls.__repr__ = __repr__

    def tb_encode(self):
        return {name: getattr(self, name) for name in self._inputvars}

    @classmethod
    def tb_decode(cls, data):
        assert set(data) == set(inputvars)
        return cls(**data)

    cls.tb_encode = tb_encode
    cls.tb_decode = tb_decode

    return cls


class JSONCodec(ABC):
    """Encoder/decoder for custom types.

    Taskblaster can encode and decode only specific types.
    A plugin can provide a custom implementation of this class
    to support additional types.
    """

    @abstractmethod
    def decode(self, dct: Dict[str, Any]) -> Any:
        """Decode dictionary generated by encode into object."""

    @abstractmethod
    def encode(self, obj: Any) -> Dict[str, Any]:
        """Encode object as dictionary.

        This should raise TypeError for types that cannot be encoded."""


def mpi(_meth=None, min_cores=None, max_cores=None):
    """Decorator for tasks that require MPI.

    With multiple MPI subworkers, tasks cannot use MPI world
    as that would cause deadlocks among subworkers.

    Those tasks should instead bear this decorator,
    which causes the taskblaster worker to pass an MPI context
    to the task::

        @mpi
        def mytask(mpi, a):
             print(mpi.comm.rank)

    Tasks that need to use a communicator which is not MPI world
    world communicator may need to access a taskblaster worker's
    communicator.
    """
    # Allow the decorator to be used either with or without
    # parameters
    if _meth is not None:
        # @tb.mpi is used without parenthesis, core specifications are None
        return _mpi(_meth)
    else:
        return functools.partial(
            _mpi, min_cores=min_cores, max_cores=max_cores
        )


def _mpi(func, min_cores=None, max_cores=None):
    func._tb_mpi = True
    func._tb_min_cores = min_cores
    func._tb_max_cores = max_cores

    @functools.wraps(func)
    def wrapper(*args, mpi=None, **kwargs):
        """Initialize MPI communicators and call the decorated function."""
        # (We should probably use a shortcut for building the task context.)
        from taskblaster.repository import Repository
        from taskblaster.worker import TaskContext

        repo = Repository.find()
        mpi_world = repo.mpi_world()
        if mpi is None:
            usercomm = mpi_world.usercomm()
            mpi = TaskContext(usercomm, mpi_world, 'main')
        if func._tb_min_cores and mpi.comm.size < func._tb_min_cores:
            raise TBUserError(
                'Trying to run a job with too few MPI cores.'
                f'Have {mpi.comm.size}, needed {func._tb_min_cores}.'
            )
        if func._tb_max_cores and mpi.comm.size > func._tb_max_cores:
            raise TBUserError(
                'Trying to run a job with too many MPI cores.'
                f'Have {mpi.comm.size}, max {func._tb_max_cores}.'
            )
        return func(*args, mpi=mpi, **kwargs)

    return wrapper


@mpi(max_cores=1)
def external_file_task(path, mpi):
    """..."""
    print('Setting up external file', path)
    path = Path(path)  # XXX taskblaster does not support jsonin Path objects
    target = Path(path.name)
    print('Copying file', path, 'to', target)
    shutil.copy(path, target)
    return ExternalFile(target).hashed()


__all__ = [
    '_if',
    'actions',
    'branch',
    'define',
    'dynamical_workflow_generator',
    'external_file_task',
    'fixedpoint',
    'InputVariable',
    'JSONCodec',
    'jump',
    'mpi',
    'node',
    'parametrize_glob',
    'Phi',
    'StopWorkflow',
    'subworkflow',
    'TBUserError',
    'TaskView',
    'task',
    'totree',
    'UserWorkflowError',
    'VerificationFailed',
    'var',
    'workflow',
]
