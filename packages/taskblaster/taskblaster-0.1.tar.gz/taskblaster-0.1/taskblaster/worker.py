import traceback
from datetime import datetime

from taskblaster import ENTRY_BRANCH, INITNAME, Reference, TBUserError
from taskblaster.namedtask import Task
from taskblaster.parallel import SerialCommunicator
from taskblaster.registry import Missing
from taskblaster.runner import Runner
from taskblaster.state import State
from taskblaster.util import workdir


class Panic(Exception):
    pass


def pop_special_kwargs(kwargs):
    special_kwargs = [
        '__tb_implicit__',
        '__tb_external__',
        '__tb_implicit_remove__',
    ]
    for kwarg in special_kwargs:
        kwargs.pop(kwarg, None)


def run_dynamical_init(rn, kwargs, function, init_ref):
    result_tasks = kwargs.pop('__tb_result_tasks__')
    from collections import defaultdict

    result_task_dct = defaultdict(dict)
    from taskblaster.util import pattern_match

    def filter_tasks(task):
        implicit_dep = Reference(init_ref.name)
        task.add_implicit_dependency(implicit_dep, remove=False)
        relname = rn.relative_to(task.name)
        for result_task, pattern in result_tasks.items():
            if not pattern_match(relname, pattern):
                continue
            result_task_dct[result_task][relname] = {
                '__tb_type__': 'ref',
                'name': task.name,
                'index': tuple(),
            }

    try:
        pop_special_kwargs(kwargs)
        generator = function(**kwargs)
    except TypeError:
        print(
            'Inconsistent call signature.'
            f'Task did not accept kwargs {kwargs.keys()}.'
        )
        raise
    for name, wf in generator:
        if hasattr(wf, '_is_tb_workflow') and wf._is_tb_workflow:
            subrn = rn.with_subdirectory(name)
            subrn.run_workflow(wf, callback=filter_tasks)
        else:
            taskname = rn.get_full_name(name)
            task = Task(taskname, wf.target, wf.kwargs, branch=ENTRY_BRANCH)
            rn._add_task(task)
            filter_tasks(task)

    for result_task in result_tasks:
        obj = result_task_dct[result_task]
        rn._add_task(
            Task(
                rn.get_full_name(result_task),
                'define',
                {'obj': obj},
                branch=ENTRY_BRANCH,
            )
        )


class TaskContext:
    """Object that allows tasks to access information about worker."""

    def __init__(self, comm, tb_comm, workername):
        self.comm = comm
        self.tb_comm = tb_comm
        self.workername = workername

    def parprint(self, *args, **kwargs):
        if self.tb_comm.rank == 0:
            print(*args, **kwargs)


ITERATE_WORKFLOW = 'taskblaster.worker.workflow_next'

# The run_workflow() code is actually a special case right now and does *not*
# call the target function.
INITIALIZE_WORKFLOW = 'taskblaster.runner.run_workflow'


def workflow_next():
    # There's a sanity check that the worker target functions exist.
    # We need to leave a placeholder function to satisfy the sanity check
    # even though the code special-cases the workflow_next() call.
    pass


class PartialTask(Exception):
    pass


class LoadedTask:
    def __init__(self, entry, name, target, kwargs):
        self.entry = entry
        self.directory = entry.directory
        self.name = name
        self.target = target
        self.kwargs = kwargs

    def _pack_ref(self):
        return {'__tb_type__': 'ref', 'name': self.name, 'index': tuple()}

    def run(self, worker):
        function = worker.repo.import_task_function(self.target)

        if not callable(function):
            raise TypeError(f'Expected callable but got {function}')

        with workdir(self.directory):
            kwargs = self.kwargs.copy()
            if getattr(function, '_tb_mpi', False):
                assert 'mpi' not in kwargs
                kwargs['mpi'] = TaskContext(
                    comm=worker.comm.usercomm(),
                    tb_comm=worker.comm,
                    workername=worker.name,
                )

            if self.target == ITERATE_WORKFLOW:
                rn = Runner(worker.repo, directory=self.directory.parent)

                workflow_obj, workflow_state = self.kwargs['obj']

                next_num = str(int(self.name.rsplit('/', 1)[1]) + 1)
                next_name = rn.get_full_name(next_num)
                value = workflow_obj.run(workflow_state)

                try:
                    next_state = workflow_obj.next_state(workflow_state, value)
                except StopIteration:  # maybe use StopWorkflow
                    next_state = None

                output = [workflow_obj, next_state]

                if next_state is not None:
                    task = Task(
                        next_name,
                        ITERATE_WORKFLOW,
                        kwargs=dict(obj=self._pack_ref()),
                        branch=ENTRY_BRANCH,
                    )

                    with rn._repo:
                        rn._add_task(task)

                    worker._affinity_tasks.append(task.name)

            elif self.target == INITIALIZE_WORKFLOW:
                # XXX Make sure this works in parallel

                rn = Runner(worker.repo, directory=self.directory.parent)
                workflow_obj = self.kwargs['workflow']
                initial_state = workflow_obj.init()
                nextname = rn.get_full_name('0')

                output = [workflow_obj, initial_state]

                assert self.name.endswith('/init')

                nexttask = Task(
                    nextname,
                    ITERATE_WORKFLOW,
                    kwargs=dict(obj=self._pack_ref()),
                    branch=ENTRY_BRANCH,
                )

                with rn._repo:
                    rn._add_task(nexttask)

                worker._affinity_tasks.append(nexttask.name)

            # XXX magical incantation to recognize workflow entry points (WIP):
            elif hasattr(function, '_tb_dynamical_workflow_generator_task'):
                if worker.comm.rank == 0:
                    rn = Runner(worker.repo, directory=self.directory.parent)
                    with worker.repo:
                        run_dynamical_init(rn, kwargs, function, self)
                output = None
            elif self.name.endswith(f'/{INITNAME}'):
                rn = Runner(worker.repo, directory=self.directory.parent)
                # Need to be careful about MPI and ranks.
                output = function(rn, **kwargs)
            else:
                pop_special_kwargs(kwargs)
                output = function(**kwargs)

            if worker.comm.rank == 0:
                self.entry.dump_output(output)


# XXX The inputdigest should be created from the actual digests
# of the inputs rather than just the encoded JSON, which contains
# the names.

# XXX here we need to save the hash of the inputs, where the
# namerefs are replaced by hashes.  That will work like before.
# But it's somewhat redundant since it only replaces the namerefs
# but otherwise is the same structure as the existing inputs.

# Then we hash the contents in that file, and that's the hash which
# we save to the registry.

# we need to dump a dictionary of {ref_id: hash}.
# Presumably we would save the digest to the registry,
# but then dump the actual

# Also: maybe some tasks are compared by return value,
# which is something that we can allow.  For example
# spacegroup might be 5, and remain 5 even if the inputs
# used to determine it change, and subsequent tasks should not
# be invalidated due to that.  Which means in the hashing
# it must be "5" that appears rather than a reference.


def exception_summary(exc):
    if exc is None:
        return None
    return f'{type(exc).__name__}: {exc}'


class Worker:
    MAX_TASKS_UNLIMITED = -1

    def __init__(
        self,
        repo,
        name='worker',
        selection=None,
        myqueue_id=None,
        comm=SerialCommunicator(),
        max_tasks=None,
        worker_class=None,  # (Are worker_class and name both necessary?)
        supported_tags=None,
        required_tags=None,
    ):
        self.name = name
        self.repo = repo
        self.comm = comm
        if supported_tags is None:
            supported_tags = set()
        if worker_class is not None:
            supported_tags.add(worker_class)
        self.supported_tags = supported_tags

        if required_tags is None:
            required_tags = set()
        self.required_tags = required_tags

        print('Starting worker rank=%03d size=%03d' % (comm.rank, comm.size))

        self.log(f'Worker class: {worker_class or "—"}')
        self.log(f'Required tags: {" ".join(sorted(required_tags)) or "—"}')
        self.log(f'Supported tags: {" ".join(sorted(supported_tags)) or "—"}')

        if selection is None:
            selection = self._select_any()

        self.selection = selection
        self.cache = repo.cache
        self.registry = repo.registry
        if max_tasks is None:
            max_tasks = self.MAX_TASKS_UNLIMITED
        self.max_tasks = max_tasks
        self.myqueue_id = myqueue_id

        # If a worker executes a workflow which generates tasks,
        # it often makes sense for that worker to immediately pick up
        # and run those tasks.  This is a stack of "prioritized" tasks
        # that will be executed before the worker returns to its normal
        # task selection method.
        #
        # If the worker never executes some prioritized tasks,
        # they will simply be left alone and another worker can pick them up.
        self._affinity_tasks = []

    def log(self, msg):
        # if self.comm.rank:
        #    return

        now = datetime.now()
        timestamp = str(now).rsplit('.', 1)[0]
        print(
            f'[rank={self.comm.rank:03d} {timestamp} {self.name}] {msg}',
            flush=True,
        )

    def _select_any(self):
        while True:
            yield self.cache.find_ready(
                supported_tags=self.supported_tags,
                required_tags=self.required_tags,
            )

    def acquire_task(self):
        while True:
            if self.comm.rank == 0:
                loaded_task = self._acquire_task()
            else:
                loaded_task = None

            loaded_task = self.comm.broadcast_object(loaded_task)

            if loaded_task is None:
                raise Missing
            if loaded_task == 'PANIC':
                raise Panic
            if loaded_task == 'CONTINUE':
                continue

            if not isinstance(loaded_task, LoadedTask):
                self.log(
                    f'Rank {self.comm.rank} expected to acquire a'
                    'LoadedTask from MPI broadcast_object, but got'
                    f'{loaded_task} instead of type {type(loaded_task)}.'
                )
                raise Panic

            break

        return loaded_task

    def _tags_compatible(self, tags):
        return self.required_tags <= tags <= self.supported_tags

    def _acquire_task(self):
        assert self.comm.rank == 0
        registry = self.cache.registry
        with registry.conn:
            try:
                if self._affinity_tasks:
                    name = self._affinity_tasks.pop()
                    indexnode = registry.index.node(name)
                    # XXX task may have been picked up by another
                    # worker in the meantime, must guard against this.
                else:
                    try:
                        indexnode = next(self.selection)
                        # task_tags = self.registry.resources.get_tags(
                        #     indexnode.name)
                        # if not self._tags_compatible(task_tags):
                        #     return 'CONTINUE'
                    except StopIteration:
                        raise Missing

                directory = self.cache.directory / indexnode.name
                directory.mkdir(parents=True, exist_ok=True)
                registry.update_task_running(
                    indexnode.name,
                    worker_name=self.name,
                    myqueue_id=self.myqueue_id,
                )

                entry = self.cache.entry(indexnode.name)

                serialized_input = self.cache.registry.inputs.get(
                    indexnode.name
                )

                target, kwargs = self.cache.load_inputs_and_resolve_references(
                    indexnode
                )

                entry.inputfile.write_text(serialized_input)
                return LoadedTask(entry, indexnode.name, target, kwargs)
            except Missing:
                return
            except TBUserError as ex:
                self.log(f'Error initializing task {indexnode.name}: {ex}')
                self._failed(indexnode, ex)
                return 'CONTINUE'
            except Exception as ex:
                self._failed(indexnode, ex)
                print('Worker panic! Stopping.')
                print('Exception occurred while trying to initialize ')
                print('queued task to be run at the worker')
                print(traceback.format_exc())
            return 'PANIC'

    def _failed(self, indexnode, exception):
        self.registry.update_task_failed(
            indexnode.name, error_msg=exception_summary(exception)
        )

    def main(self):
        self.log('Main loop')
        self.repo.worker_start_hook()
        try:
            ntasks = 0
            while True:
                if self.max_tasks is not None and ntasks == self.max_tasks:
                    self.log(
                        f'Max tasks {ntasks} reached, end worker main loop'
                    )
                    return

                ntasks += 1

                try:
                    self.process_one_task()
                except Missing:
                    self.log('No available tasks, end worker main loop')
                    return
                except Panic:
                    self.log(
                        'Worker terminating due to exception in task '
                        'initialization.'
                    )
                    return
        finally:
            self.repo.worker_finish_hook()

    def process_one_task(self):
        loaded_task = None
        prospective_state = State.fail
        try:
            try:
                loaded_task = self.acquire_task()
            except Missing:
                raise
            except Panic:
                raise
            except Exception as err:
                self.log(traceback.format_exc())
                self.log(f'Failed in initialization: {err}')
                # Log exception somehow.
                return

            starttime = datetime.now()
            print(f'Got task {loaded_task}')
            self.log(f'Running {loaded_task.name} ...')
            exception = None
            try:
                loaded_task.run(self)
            except (KeyboardInterrupt, Exception) as err:
                # Log the exception somehow
                stacktrace = traceback.format_exc()
                self.log(stacktrace)
                fname = f'stacktrace.rank{self.comm.rank:02d}.err'
                stacktracefile = loaded_task.entry.directory / fname
                stacktracefile.write_text(stacktrace)
                exception = err
                msg = exception_summary(exception)
                self.log(f'Task {loaded_task.name} failed: {msg}')
            else:
                prospective_state = State.done
                endtime = datetime.now()
                elapsed = endtime - starttime

                self.log(f'Task {loaded_task.name} finished in {elapsed}')

        finally:
            if loaded_task is not None and self.comm.rank == 0:
                name = loaded_task.name
                with self.registry.conn:
                    if prospective_state == State.done:
                        self.registry.update_task_done(name)
                    elif prospective_state == State.fail:
                        self.registry.update_task_failed(
                            loaded_task.name,
                            error_msg=exception_summary(exception),
                        )
                    else:
                        raise ValueError(
                            f'Unexpected state {prospective_state}'
                        )
