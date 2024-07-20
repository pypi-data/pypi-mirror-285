import traceback
from collections import defaultdict
from pathlib import Path

import click

import taskblaster as tb
from taskblaster import (
    ENTRY_BRANCH,
    Phi,
    Reference,
    TBUserError,
    UnreachableReference,
    UserWorkflowError,
    VerificationFailed,
)
from taskblaster.future import Future
from taskblaster.hashednode import Node
from taskblaster.namedtask import Task, new_workflowtask
from taskblaster.state import State
from taskblaster.util import color


def define(obj):
    return obj


def run_workflow(rn, workflow):
    assert workflow._rn is None
    workflow._rn = rn

    with rn._repo:
        for name in workflow._unbound_tasks:
            unbound_task = getattr(workflow, name)
            task = unbound_task.task()
            rn._add_task(task)


def print_traceback(ex):
    print('--- Error in workflow ----------------')
    print(''.join(traceback.format_exception(ex)))
    print('--------------------------------------')


class GeneratedWorkflow:
    def __init__(
        self, fullname, name, init=None, result_tasks=None, branch=None
    ):
        # XXX: To be refactored, fullname, and name redundant
        self.name = name
        self.fullname = fullname
        self.init = init
        self.result_tasks = result_tasks
        self.branch = branch

    def __getattr__(self, attr):
        if attr not in self.result_tasks:
            raise RuntimeError('xxx')
        return Reference(f'{self.fullname}/{attr}')

    def generate_fixed_points(self, rn):
        rn = rn.with_subdirectory(self.name)

        full_name = rn.get_full_name('init')
        kwargs = self.init.kwargs.copy()
        kwargs.update({'__tb_result_tasks__': self.result_tasks})
        task = Task(
            full_name, self.init.target, kwargs, branch=ENTRY_BRANCH
        )  # XXX Hard coded to entry
        init_ref = Reference(full_name)
        yield task

        for name, glob in self.result_tasks.items():
            full_name = rn.get_full_name(name)
            # The idea of this line is to set a placeholder tasks for other
            # static tasks to depend on. The dependence will be set to point
            # to init task of this workflow temporarily. After the worker
            # runs the init task, it will then reassign both the target,
            # and kwargs of this task.
            # XXX Force overwrite, so that queued tasks, even they are or are
            # not in pristine state set will not result into conflict, and
            # then the this task will be updated.
            task = Task(
                full_name,
                '<to be updated>',
                {'obj': init_ref},
                branch=self.branch,
            )
            yield task


class Runner:
    def __init__(
        self,
        repo,
        *,
        directory=Path(),
        dry_run=False,
        silent=False,
        clobber_existing=False,
        max_tasks=None,
    ):
        self._repo = repo
        self._directory = Path(directory)
        self._dry_run = dry_run
        self._silent = silent
        self._current_workflow = None
        self._current_branch = None
        self._from_branch = None
        self._seen_branches = defaultdict(int)
        self._pre_print = ''
        self._post_print = ''

        self._clobber_existing = clobber_existing

    def relative_to(self, pth):
        return str(
            Path(pth).relative_to(
                self._directory.relative_to(self._cache.directory)
            )
        )

    @property
    def prefix(self):
        return str(self._directory)

    @property
    def _cache(self):
        return self._repo.cache

    @property
    def directory(self):
        return self._repo.tree_path / self._directory

    def with_subdirectory(self, directory):
        return self._new(directory=self._directory / directory)

    def get_full_name(self, name):
        fullpath = self.directory / name
        relpath = fullpath.relative_to(self._cache.directory)
        return str(relpath)

    def _new(self, **kwargs):
        kwargs = {
            'repo': self._repo,
            'dry_run': self._dry_run,
            'silent': self._silent,
            'directory': self._directory,
            'clobber_existing': self._clobber_existing,
            **kwargs,
        }

        return Runner(**kwargs)

    def _find_refs(self, task):
        import json

        from taskblaster import Input

        runner_self = self

        class ReferenceFinder:
            def __init__(self, codec):
                self._refs = []
                self.codec = codec

            def default(self, obj):
                if isinstance(obj, Path):
                    return None
                if isinstance(obj, Input):
                    return obj.getvalue()
                if isinstance(obj, Reference):
                    self._refs.append(obj)
                    return None
                if isinstance(obj, Future):
                    # XXX also there's Reference
                    raise RuntimeError('should not receive Future here?')
                if isinstance(obj, Phi):
                    resolved = obj.resolve(runner_self)
                    return resolved
                if hasattr(obj, '_refhook'):
                    ref = obj._refhook()
                    self._refs.append(ref)
                    return None

                return self.codec.encode(obj)

            def find_refs(self, task):
                # (The encoder extracts the references as a side
                # effect of encoding.)
                json.dumps(task.kwargs, default=self.default)
                return self._refs

        reffinder = ReferenceFinder(codec=self._cache.json_protocol.codec)
        refs = reffinder.find_refs(task)
        return refs

    def add_workflow(self, name, workflow):
        task = new_workflowtask(workflow, f'{name}/{tb.INITNAME}')
        self._add_task(task)

    def run_workflow(self, workflow, callback=lambda x: None):
        seen = set()

        for task in self._iterate_tasks(workflow, callback=callback):
            for required_task in self._topological_order(task, seen):
                callback(required_task)
                # XXX This works out very badly with branches
                # XXX All of this need to be restrutured
                # assert required_task.name in seen
                branch_name = required_task.branch
                if (
                    required_task.bts is not None
                    and required_task.bts.workflow == self._current_workflow
                    and branch_name not in self._seen_branches
                ):
                    raise TBUserError(
                        f'Task {required_task} depending on branch not'
                        f' yet visited ({branch_name}). Visited branches'
                        f' {set(self._seen_branches)}.'
                    )

                self._add_task(required_task)

    def _topological_order(self, task, seen):
        if task.name in seen:
            return

        refs = self._find_refs(task)
        for ref in refs:
            if ref.name in seen:
                continue

            if ref.unreachable:
                continue

            if ref.name in self._cache:
                # Ignore task which already exists -- we don't need
                # to generate that task.
                #
                # Although somewhere we should check, or be able to check,
                # that it isn't outdated.
                continue

            # The task is not in cache, and we are referencing to an object
            # with a same branch, within a loop...
            branches = self._current_workflow._branches
            is_loop = branches[self._current_branch].loop
            if is_loop and ref.branch == self._current_branch:
                # ...therefore, we must mean one from previous iteration
                if ref.name not in self._cache:
                    ref = ref.previous_loop()
                    assert ref.name in self._cache

            try:
                ref_task = ref.task()

            except UserWorkflowError:
                # We have this exception check in two places,
                # maybe it can be better?
                print(
                    f'{task.name} unreachable due to dependency '
                    f'{ref.name!r}'
                )
                return

            # Should use iterative rather than recursive
            yield from self._topological_order(ref_task, seen)

        if task.target != 'fixedpoint':
            seen.add(task.name)
        yield task

    def _create_dynamical_workflow(self, master_workflow, name, node_fun):
        # XXX To be refactored
        result_tasks = node_fun._tb_result_tasks
        node = node_fun(master_workflow)
        full_name = master_workflow._rn.get_full_name(name)
        generated_wf = GeneratedWorkflow(
            full_name,
            name,
            init=node,
            result_tasks=result_tasks,
            branch=self._current_branch,
        )
        yield from generated_wf.generate_fixed_points(master_workflow._rn)
        node_fun.generated_wf = generated_wf

        rn = master_workflow._rn.with_subdirectory(name)
        bound_init_task_name = rn.get_full_name('init')
        entry = self._cache.entry(bound_init_task_name)
        if entry.has_output():
            from taskblaster.worker import run_dynamical_init

            node = self._cache.name2node(bound_init_task_name)

            generator_fun = self._repo.import_task_function(node.target)
            target, kwargs = self._cache.load_inputs_and_resolve_references(
                node
            )
            implicit_dep = Reference(bound_init_task_name)
            run_dynamical_init(rn, kwargs, generator_fun, implicit_dep)

    def _new_branch(self, branch_name):
        self._from_branch = self._current_branch
        self._current_branch = branch_name

        if not self._current_workflow._branches[branch_name].loop:
            if branch_name in self._seen_branches:
                raise TBUserError(
                    f'Revisiting a non-loop branch {branch_name}'
                )
        self._seen_branches[self._current_branch] += 1

    def pre_print(self, s):
        self._pre_print += s
        self._pre_print = self._pre_print.rstrip()
        self._pre_print += ' ' * (10 - len(click.unstyle(self._pre_print)))

    def post_print(self, s):
        self._post_print += s

    def print(self, s):
        self.pre_print('')
        print(self._pre_print, end='')
        print(s, end=' ')
        print(self._post_print)
        self._pre_print = ''
        self._post_print = ''

    def print_new_if(self, bound_task):
        self.pre_print(color('if:', fg='bright_blue'))
        for key, value in bound_task._if.items():
            if key is True:
                key = 'T'
            if key is False:
                key = 'F'
            self.post_print(color(f'{key}=', fg='bright_cyan'))
            self.post_print(color(value, fg=State.new.color))
            self.post_print(' ')

    def print_realized_if(self, bound_task, output, jump_to):
        self.pre_print(color('if:', fg='bright_blue'))
        for key, value in bound_task._if.items():
            cl = State.done.color if output == key else State.fail.color
            if key is True:
                key = 'T'
            if key is False:
                key = 'F'
            self.post_print(color(f'{key}=', fg='bright_cyan'))
            self.post_print(color(value, fg=cl))
            self.post_print(' ')

        self.post_print(
            color('jump: ', fg='bright_magenta')
            + color(jump_to, fg='bright_cyan')
        )

    def _iterate_tasks(self, workflow, no_assert=False, callback=None):
        # XXX We need a WorkflowRunner which takes just one workflow
        # and a Runner. Now Runner is mutable with two states:
        # either it is assigned to a workflow or not
        # self._current_workflow and the asserts are there to disable problems
        # arising from this mutability
        # assert self._current_workflow is None
        self._current_workflow = workflow
        if self._current_branch is None:
            self._new_branch('entry')

        self.pre_print(color(f'{self._current_branch}:', fg='bright_cyan'))
        if not no_assert:
            assert workflow._rn is None
        workflow._rn = self

        jump_to = None
        _if_task = None

        # Create fixedpoint tasks
        for task_name, task in workflow._external.items():
            full_name = self.get_full_name(task_name)
            if full_name not in self._cache:
                unmet_ref = UnreachableReference()
                task = Task(
                    full_name, 'fixedpoint', {'obj': unmet_ref}, branch='entry'
                )
                yield task

        for key, value in workflow._dynamical_workflow_generators.items():
            yield from self._create_dynamical_workflow(workflow, key, value)

        for name, subwfprop in workflow._subworkflows.items():
            self.print('')
            subworkflow = getattr(workflow, name)
            # Clean up hacky management of _rn attribute

            # There cannot be both _ifs in subworkflows
            assert subwfprop._if is None

            sub_rn = subworkflow._rn
            subworkflow._rn = None
            sub_rn.run_workflow(subworkflow, callback=callback)

            if subwfprop.jump:
                # There can be only one jump in a branch
                # XXX Remove replication
                assert jump_to is None

                jump_to = subwfprop.jump
                if jump_to['branch'] is not None:
                    # Just a direct jump to another branch
                    assert jump_to['on_success'] is None
                    jump_to = jump_to['branch']
                    self.post_print(
                        color('jump: ', fg='bright_magenta')
                        + color(jump_to, fg='bright_cyan')
                    )
                else:
                    assert 0  # No on_success for subworkflows

        for name in workflow._unbound_tasks:
            bound_task = getattr(workflow, name)
            try:
                bt = bound_task.task()
                if bound_task.jump:
                    # There can be only one jump in a branch
                    assert jump_to is None

                    # There cannot be both _if and jump in a single task
                    assert bound_task._if is None

                    jump_to = bound_task.jump
                    if jump_to['branch'] is not None:
                        # Just a direct jump to another branch
                        assert jump_to['on_success'] is None
                        jump_to = jump_to['branch']
                        self.post_print(
                            color('jump: ', fg='bright_magenta')
                            + color(jump_to, fg='bright_cyan')
                        )
                    else:
                        # We are dealing with only on_success jump
                        # XXX Make into a function
                        has_output = False
                        try:
                            entry = self._cache.entry(bound_task.name)
                        except KeyError:
                            pass
                        else:
                            if entry.has_output():
                                has_output = True
                        if has_output:
                            self.post_print(
                                color('jump: ', fg='bright_green')
                                + color(
                                    jump_to['on_success'], fg='bright_cyan'
                                )
                            )
                            jump_to = jump_to['on_success']
                        else:
                            self.post_print(
                                color('jump: ', fg='bright_blue')
                                + color(
                                    jump_to['on_success'], fg='bright_cyan'
                                )
                            )
                            jump_to = None

                if bound_task._if is not None:
                    assert _if_task is None
                    _if_task = bound_task
                    assert jump_to is None
                    try:
                        entry = self._cache.entry(bound_task.name)
                    except KeyError:
                        self.print_new_if(bound_task)
                    else:
                        if entry.has_output():
                            output = entry.output()
                            # jump_to = true if output else false
                            jump_to = bound_task._if[output]
                            self.print_realized_if(bound_task, output, jump_to)
                        else:
                            self.print_new_if(bound_task)

                yield bt
            except UserWorkflowError as err:
                print_traceback(err.__cause__)
                break
            # taskdir = self.directory / name
            # name = str(taskdir.relative_to(self._cache.directory))
            # task = unbound_task.task()

            # 1) encode to JSON and find dependencies
            # 2) make sure all dependencies exist (or recurse until they do)
            #
            # name = f'{self.prefix}/{name}'
            # task = unbound_task.bind(name, workflow)

            # Here we can also write down how to instantiate this workflow
            # object.  If that info is included in the task, then we can rerun
            # task generation upon request without the user needing to know
            # which workflow file generated it.

            # What do we actually need to do?
            # if task exists:
            #  - Task exists?
            #    - target or kwargs changed?
            #      - invalidate
            #      -
            #    - Invalidate if cha
            #  - If target or kwargs changed, invalidate
            #  - If task does not exist, add task.

            # (We probably need to yield and recurse dependencies.)

        if jump_to is not None:
            self._new_branch(jump_to)
            workflow._rn = None
            # XXX: tail recursion, do not recurse here, but nove to outer
            # method
            for task in self._iterate_tasks(workflow, callback=callback):
                if _if_task is not None:
                    task.add_implicit_dependency(_if_task, remove=True)
                yield task

        # XXX See above XXX
        assert self._current_workflow is workflow

    def run_verification_task(self, verify, node):
        # XXX Allow verification to fail gracefully if this fails for some
        # other reason
        if node._name not in self._cache:
            return
        entry = self._cache.entry(node._name)
        if not entry.has_output():
            return

        target, kwargs = self._cache.load_inputs_and_resolve_references(node)

        verify_fun = self._repo.import_task_function(verify)

        try:
            verify_fun(inputs=kwargs, output=entry.output())
        except VerificationFailed as ex:
            print(color(*ex.args, fg='bright_red'))

    def _add_task(self, task, dynamic_parent=None, force_overwrite=False):
        import click

        node = task._node(self._cache)

        if task.verify:
            self.run_verification_task(task.verify, node)

        action_str, indexnode = self._cache.add_or_update(
            node,
            force_overwrite=force_overwrite,
            tags=task.tags,
            clobber_existing=self._clobber_existing,
        )

        future = Future(node, self._cache)

        colors = {
            'have': 'yellow',
            'update': 'bright_yellow',
            'add': 'bright_blue',
            'conflict': 'bright_red',
            'resolved': 'bright_blue',
        }

        self.print(
            '{}{} {}'.format(
                ' ' * (8 - len(action_str)),
                click.style(action_str, colors[action_str]),
                future.describe(),
            )
        )

        return future

    def _node(self, taskname, kwargs, name, dynamic_parent=None):
        # Raise an error if task cannot be imported:
        self._repo.import_task_function(taskname)
        return Node.new(
            self._cache.json_protocol,
            taskname,
            kwargs,
            name,
            dynamic_parent=dynamic_parent,
        )

    def task(self, target, name, **kwargs):
        node = self._node(target, kwargs, name)
        return self._task(node)

    def _task(self, node):
        assert not Path(node.name).is_absolute()
        # TODO remove this (old) implementation
        action, indexnode = self._cache.add_or_update(node)
        future = Future(node, self._cache)

        # XXX fromdir=pwd
        if not self._silent:
            print('{:>9s}: {}'.format(action, future.describe()))
        return future

    def define(self, obj, name):
        # XXX duplicates stuff from currently in __init__
        node = self._node('define', {'obj': obj}, name=name)
        return self._task(node)
