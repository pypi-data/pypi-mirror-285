from __future__ import annotations

import importlib
import runpy
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import taskblaster as tb
from taskblaster.cache import FileCache
from taskblaster.future import Future
from taskblaster.registry import Registry
from taskblaster.runner import Runner
from taskblaster.state import State
from taskblaster.storage import JSONProtocol
from taskblaster.tree import Tree

# XXX remove duplicate definition from worker.py
MAX_TASKS_UNLIMITED = -1


@dataclass
class WorkerSpecification:
    name: str | None = None
    tags: set[str] = field(default_factory=set)
    required_tags: set[str] = field(default_factory=set)
    resources: str | None = None
    max_tasks: int = MAX_TASKS_UNLIMITED
    subworker_size: int | None = None
    subworker_count: int | None = None

    @classmethod
    def from_workerconfig(cls, config_dct):
        worker_specs = {}
        for name, dct in config_dct.items():
            worker_specs[name] = cls(
                name=name,
                tags=set(dct.get('tags', [])),
                required_tags=set(dct.get('required_tags', [])),
                resources=dct.get('resources'),
            )

        return worker_specs

    def description(self):
        dct = asdict(self).copy()

        def jointags(tags):
            return ' '.join(tags) if tags else '—'

        # Slightly nicer strings for printing:
        dct['tags'] = jointags(self.tags)
        dct['required_tags'] = jointags(self.required_tags)
        dct['resources'] = repr(dct['resources'])

        return '\n    '.join(
            [f'{name}: {value}' for name, value in dct.items()]
        )


def read_resource_file(path):
    if not path.exists():
        return {}

    try:
        namespace = runpy.run_path(str(path))
    except Exception as err:
        # This is a user error, but in this particular case the user
        # will definitely want to see the stack trace.
        raise tb.TBUserError(f'Could not load resources from {path}') from err

    try:
        resources_dict = namespace['resources']
    except KeyError:
        # Error message should be made more informative once syntax is stable
        example = 'resources = {}'
        raise tb.TBUserError(
            f'Resource file {path} exists but does not contain at least '
            f'"{example}"'
        )

    return resources_dict


class Repository:
    _tasks_module_name = 'tasks.py'
    _tree_name = 'tree'
    _registry_name = 'registry.db'
    _magic_dirname = '.taskblaster'
    _py_filename = 'pymodule'
    _resource_filename = 'resources.py'

    class RepositoryError(Exception):
        pass

    # Other files:
    #  * lib/ -- task library directory (TODO)
    #  * tbconfig.ini -- configuration file or files (TODO)
    #  * ASR database specification file or files -- belongs in ASR though
    #
    # Also:
    #  * registry could be hidden if we have a tool for working with it.

    def __init__(self, root, usercodec=None, run_module='taskblaster.worker'):
        self.root = root.resolve()
        self.registry = Registry(self.registry_path)
        self.cache = FileCache(
            directory=self.tree_path,
            registry=self.registry,
            json_protocol=JSONProtocol(self.tree_path, usercodec),
        )
        self.run_module = run_module

        # When testing within a single process, it is useful to have a
        # namespace of ready-made tasks without having to import from files.
        self._tasks = {}

        from taskblaster.runner import define

        self._tasks['define'] = define

        self.usermodules = {}  # self.import_userscripts()

    def worker_start_hook(self):
        pass

    def worker_finish_hook(self):
        pass

    def get_resources(self):
        dct = read_resource_file(self.resource_path)
        return WorkerSpecification.from_workerconfig(dct)

    def import_userscripts(self):
        """Import all the .py files under self.root.

        Python will then see them as modules, which means classes
        can be serialized/deserialized using module names with JSON/pickle."""
        import pkgutil

        usermodules = {}
        for module_info in pkgutil.walk_packages([str(self.root)]):
            scriptname, module = self.import_userscript(module_info)
            usermodules[scriptname] = module
        return usermodules

    def import_userscript(self, module_info):
        import importlib.util
        import sys

        # We consider ad-hoc modules to live inside this fake package:
        userpath = 'taskblaster.userpath'

        scriptname = f'{module_info.name}.py'
        file_path = Path(module_info.module_finder.path) / scriptname

        # XXX If any of this goes wrong, we should simply skip the
        # file.  Some files may be edited by user and we wouldn't want
        # a syntax error in one of those files to prevent workers
        # from running.
        module_name = f'{userpath}.{module_info.name}'

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return scriptname, module

    def mpi_world(self):
        from taskblaster.parallel import SerialCommunicator

        return SerialCommunicator()

    @property
    def magicdir(self):
        return self.root / self._magic_dirname

    @property
    def registry_path(self):
        return self.magicdir / self._registry_name

    @property
    def tree_path(self):
        return self.root / self._tree_name

    @property
    def resource_path(self):
        return self.root / self._resource_filename

    def __enter__(self):
        # A process (e.g. this process) is allowed to hold the lock more
        # than once.  This is useful because we can perform actions
        # that require locking without needing to check whether we are
        # already holding the lock.
        #
        # Thus, we keep a count of the number of times we have acquired
        # the lock.
        #
        # The lock is not thread safe, but it is safe wrt. other (external)
        # processes.
        self.registry.conn.__enter__()
        return self

    def __exit__(self, *args):
        self.registry.conn.__exit__(*args)

    def __repr__(self):
        return f'<Repository(root={self.root})>'

    def tree(self, directories=None, **kwargs):
        return Tree(self, directories=directories, **kwargs)

    def import_task_function(self, taskname):
        tokens = taskname.rsplit('.', 1)

        if taskname in self._tasks:
            return self._tasks[taskname]

        if len(tokens) == 2:
            module, funcname = tokens
            module = importlib.import_module(module)
            func = getattr(module, funcname)
        else:
            namespace = self.import_tasks()
            try:
                func = namespace[taskname]
            except KeyError:
                raise tb.TBUserError(
                    f'Could import task with target: {taskname}'
                )

        return func

    def import_tasks(self) -> Dict[str, Any]:
        # Should allow whole package in <root>/lib/ from which to import
        #
        # We need some way of guaranteeing that tasks cannot invoke
        # malicious functions.
        #
        # Right now we allow loading from any function named via
        # import path, so that can execute anything.
        #
        # Maybe ASR can have a way to point to 'valid' things.
        try:
            # we do str() for mypy
            target = str(self.tasks_module)
            return runpy.run_path(target, run_name=target)
        except FileNotFoundError:
            return {}
        #    raise self.RepositoryError('No tasks defined.  Define tasks in '
        #                               f'{self.tasks_module}')

    @property
    def tasks_module(self) -> Path:
        return self.root / self._tasks_module_name

    @classmethod
    def create(
        cls, root, modulename='taskblaster.repository', exists_ok=False
    ) -> 'Repository':
        root = root.resolve()

        def trouble(msg):
            raise cls.RepositoryError(msg)

        try:
            module = importlib.import_module(modulename)
        except ModuleNotFoundError:
            trouble(f'Specified module "{modulename}" must exist')

        try:
            tb_init_repo = module.tb_init_repo
        except AttributeError:
            trouble(
                f'Specified module "{modulename}" '
                'does not implement a tb_init_repo(root) '
                'function or class'
            )

        magic_dir = root / cls._magic_dirname
        magic_dir.mkdir(parents=True, exist_ok=True)

        modulefile = magic_dir / cls._py_filename
        modulefile.write_text(f'{modulename}\n')

        registry = magic_dir / cls._registry_name

        if not exists_ok and registry.exists():
            trouble(f'Already exists: {registry}')
        registry.touch()

        tree_path = root / cls._tree_name
        tree_path.mkdir(exist_ok=True)
        repo = tb_init_repo(root)
        return repo

    @classmethod
    def find_root_directory(cls, directory='.'):
        directory = Path(directory).resolve()
        for root in (directory, *directory.parents):
            registry_location = root / cls._magic_dirname / cls._registry_name
            if registry_location.exists():
                return root

        raise cls.RepositoryError(
            f'No registry found in {directory} or parents. '
            'Run tb init MODULE to initialize empty repository here.'
        )

    @classmethod
    def find(cls, directory='.') -> 'Repository':
        root = cls.find_root_directory(directory)
        pymodulefile = root / cls._magic_dirname / cls._py_filename
        pymodulename = pymodulefile.read_text().strip()
        pymodule = importlib.import_module(pymodulename)
        tb_init_repo = pymodule.tb_init_repo
        repo = tb_init_repo(root)
        if not isinstance(repo, cls):
            raise cls.RepositoryError(
                f'{pymodulename}.tb_init_repo did not return'
                ' a repository object.'
            )
        return repo

    def plugin_pymodule(self):
        return (self.magicdir / self._py_filename).read_text().strip()

    def info(self) -> List[str]:
        have_tasks = self.tasks_module.is_file()
        taskfile = str(self.tasks_module)

        if not have_tasks:
            taskfile += ' (not created)'

        index = self.cache.registry.index

        lenstring = 'entry' if index.count() == 1 else 'entries'

        pymodulename = self.plugin_pymodule()
        pymodule = importlib.import_module(pymodulename)

        resources = self.get_resources()
        resource_string = str(self.resource_path)

        if not self.resource_path.is_file():
            resource_string += ' (not created)'
        else:
            resource_string += f' ({len(resources)} worker classes)'

        return [
            f'Module:     {pymodulename}',
            f'Code:       {pymodule.__file__}',
            f'Root:       {self.root}',
            f'Tree:       {self.cache.directory}',
            f'Registry:   {self.registry_path}'
            f' ({index.count()} {lenstring})',
            f'Tasks:      {taskfile}',
            f'Resources:  {resource_string}',
        ]

    def runner(self, **kwargs):
        return Runner(self, directory=self.cache.directory, **kwargs)

    def listing(self, columns, fromdir):
        from taskblaster.listing import Listing

        return Listing(
            columns=columns,
            registry=self.registry,
            fromdir=fromdir,
            treedir=self.tree_path,
        )

    def graph(self, tree):
        from taskblaster.util import tree_to_graphviz_text

        tree = self.tree(tree)
        txt = tree_to_graphviz_text(tree)
        print(txt)

    def _view(self, tree):
        from taskblaster.view import view_node

        for node in self.tree(tree).nodes():
            view_node(self, node)

    def rename_import_path(self, tree, old, new):
        from taskblaster.hashednode import Node

        to_be_patched = []

        for node in self.tree(tree).nodes():
            hashednode = self.cache.name2node(node.name)

            if hashednode.target == old:
                to_be_patched.append(hashednode)

        def rename_fcn():
            for hashednode in to_be_patched:
                name = hashednode.name
                newnode = Node.new(
                    json_protocol=self.cache.json_protocol,
                    target=new,
                    dct=hashednode._dct,
                    name=name,
                    dynamic_parent=hashednode._dynamic_parent,
                )
                inputs = self.cache.registry.inputs
                inputs.remove(name)

                # We re-serializes the kwargs, and it should get the same
                # string afterwards except for the one changed path.
                # Let's do a sanity check:
                assert (
                    hashednode.serialized_input.replace(old, new, 1)
                    == newnode.serialized_input
                )

                inputs.add(name, newnode.serialized_input)
                print(f'Renamed import path for {name}.')
            print(f'Renamed {len(to_be_patched)} task import paths.')

        return [node.name for node in to_be_patched], rename_fcn

    def view(self, tree, action=None, relative_to=None):
        if action is None:
            return self._view(tree)
        else:
            return self._run_action(
                tree, action=action, relative_to=relative_to
            )

    def _run_action(self, tree, action, relative_to):
        results = []
        for node in self.tree(tree, relative_to=relative_to).nodes():
            hashednode = self.cache.name2node(node.name)

            function = self.import_task_function(hashednode.target)
            actions = getattr(function, '_tb_actions', {})

            if action not in actions:
                print(f'<node "{node.name}" does not have action "{action}">')
                continue

            actionfunc = actions[action]
            future = Future(hashednode, self.cache)
            record = tb.TaskView(node=node, future=future)
            results.append(actionfunc(record))

        return results

    def run_all_tasks(self):
        # (We use this for testing.)
        self.run_worker(tree=[self.tree_path], name='testworker')

    def run_worker(
        self,
        tree=None,
        name='worker',
        subworker_count=None,
        subworker_size=None,
        max_tasks=None,
        greedy=False,
        **kwargs,
        # worker_class=None,
        # tags=None,
    ):
        from taskblaster.parallel import choose_subworkers
        from taskblaster.worker import Worker

        world = self.mpi_world()
        subworker_size, subworker_count = choose_subworkers(
            size=world.size,
            subworker_count=subworker_count,
            subworker_size=subworker_size,
        )

        comm = world.split(subworker_size)

        subworker_group = world.rank // subworker_size

        subworker_id = f'{name}-{subworker_group}/{subworker_count}'

        if tree:
            tree = self.tree(tree, states={State.queue, State.new})

            def find_tasks():
                # XXX We need to base this on a query instead of this hack
                # Here we try to discard tasks that do not have the right
                # tags.

                runnable = {State.queue, State.new}
                while True:
                    found = False
                    if greedy:
                        search_fun = tree.nodes
                    else:
                        search_fun = tree.nodes_topological
                    for indexnode in search_fun():
                        # The nodes_topological() iterator may have outdated
                        # information, so we need to refresh everything we see:
                        indexnode = self.registry.index.node(indexnode.name)

                        if indexnode.state not in runnable:
                            continue

                        if indexnode.awaitcount != 0:
                            continue

                        tags = self.registry.resources.get_tags(indexnode.name)
                        if not worker._tags_compatible(tags):
                            # XXX beware of repeated looping over the same
                            # tasks!  This should probably be changed
                            # to a database query of some kind.
                            continue

                        found = True
                        yield indexnode
                    if not found:
                        break

            selection = find_tasks()
        else:
            selection = None

        # Names are a bit illogical, meaning of "worker name" differs below
        if max_tasks is None:
            max_tasks = Worker.MAX_TASKS_UNLIMITED
        worker = Worker(
            repo=self,
            name=subworker_id,
            myqueue_id=name,
            comm=comm,
            selection=selection,
            max_tasks=max_tasks,
            **kwargs,
        )
        worker.main()

    def run_workflow_script(
        self,
        script,
        dry_run,
        silent,
        script_name='workflow',
        **kwargs,
    ):
        import runpy

        namespace = runpy.run_path(script)
        if script_name not in namespace:
            raise self.RepositoryError(
                f'When running `tb workflow {script}`, the {script} must '
                'contain `def workflow(rn)`.'
            )
        workflow = namespace[script_name]
        # workflow_module = self.usermodules[script]
        # workflow = workflow_module.workflow

        # def run_workflow(self, workflow, dry_run=False):
        # Should we use introspection for mapping arguments to parametrized
        # workflows?  I think not, since it leaves us unable to define
        # whether we want Record, output, or indexed output.
        #
        # Nevertheless here we go, until we define a better way.
        # Probably we should instead decorate.  Whatever we do, we will
        # likely want this statically defined (i.e. in the workflow code
        # somehow) and not do it "ephemerally" at CLI level.

        rn = self.runner(dry_run=dry_run, silent=silent, **kwargs)
        # try:
        # with self.registry.conn:
        workflow(rn)
        # except DirectoryConflict as err:
        # Task exists with same name but different hash, i.e.,
        # inputs have changed.
        # We should properly visualize the differences between
        # inputs.
        # raise conflict_error(err)
        # XXX re-enable proper errmsg
        # raise err


def tb_init_repo(root):
    return Repository(root)
