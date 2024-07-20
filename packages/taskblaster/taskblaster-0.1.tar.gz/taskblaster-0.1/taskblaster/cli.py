import os
import sys
import warnings
from functools import wraps
from pathlib import Path

import click

from taskblaster import TaskBlasterInterrupt
from taskblaster.repository import Repository
from taskblaster.state import State

# Translate --color options to click.echo() inputs:
TB_COLOR_MODES = {
    'auto': None,
    'always': True,
    'never': False,
}


class Echo:
    def __init__(self, mode):
        self.mode = mode

    def __call__(self, *args, **kwargs):
        """Echo string in correct color mode."""
        return click.echo(*args, color=self.mode, **kwargs)

    def restyle(self, string):
        """Uncolor or leave the string unchanged depending on mode.

        Functions like click.confirm() do not take a color flag,
        so we need to send strings through this when we want another
        behaviour than click's default behaviour."""
        if self.mode is False:
            string = click.unstyle(string)

        return string

    def are_you_sure(self, prompt):
        # Click confirm() does not support the color option.
        # It will always remove colors if we are not a tty.
        # Of course this is a fringe case since interactive prompts
        # make little sense in the non-tty case.
        if self.mode is not False:
            prompt = click.style(prompt, 'bright_red')
        return click.confirm(prompt)


def colormode(mode):
    if mode is None:
        mode = os.environ.get('TB_COLORS', 'auto')
        if mode not in TB_COLOR_MODES:
            warnings.warn(f'Ignoring bad TB_COLORS mode: {mode}')
            mode = 'auto'

    return Echo(TB_COLOR_MODES[mode])


def echo_mode():
    return click.option(
        '--color',
        'echo',
        metavar='WHEN',
        type=click.Choice([*TB_COLOR_MODES]),
        callback=lambda ctx, param, value: colormode(value),
        help=(
            'Colorize output; use "always" for colors, "never" for no '
            'colors, or "auto" (default).  '
            'Default can be overridden by the TB_COLORS '
            'environment variable.'
        ),
    )


def silent_option():
    return click.option(
        '-s', '--silent', is_flag=True, help='Do not print to screen.'
    )


def dryrun_option():
    return click.option(
        '-z',
        '--dry-run',
        is_flag=True,
        help='Simulate what would happen, but do nothing.',
    )


def max_tasks_option():
    return click.option(
        '--max-tasks',
        type=int,
        default=-1,
        metavar='NUM',
        help='Maximum number of tasks for worker to run.',
    )


def tree_argument():
    return click.argument('tree', nargs=-1)


def format_node_short(node):
    from taskblaster.util import color

    state = node.state
    to_be_removed = hasattr(node, 'to_be_removed') and node.to_be_removed
    return ' '.join(
        [
            color('remove:', fg='bright_red') if to_be_removed else 'unrun: ',
            color(state.name, state.color).ljust(17),
            color(node.name),
        ]
    )


def _repository(directory=None):
    if directory is None:
        directory = Path.cwd()

    try:
        return Repository.find(directory)
    except Repository.RepositoryError as ex:
        raise click.ClickException(f'{ex}')


def with_repo(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with _repository() as repo:
            return func(*args, **kwargs, repo=repo)

    return wrapper


@click.group()
def tb():
    """Taskblaster, a high-throughput workflow utility.

    Utility to define and run vast quantities of computational tasks,
    organizing inputs and outputs in a directory tree.

    Use the init subcommand to initialize an empty repository.  Then
    write a workflow function and run it to create a directory tree of
    tasks.  Then submit tasks using your favourite high-performance
    computing batch system.
    """


@tb.command()
@click.argument('script', type=click.Path(exists=True))
@dryrun_option()
@silent_option()
@with_repo
@click.option(
    '--clobber-existing',
    is_flag=True,
    help='Overwrite leftover unregistered tasks in tree where necessary.  '
    'Such tasks may appear if workflow generation crashes, but they are not '
    'ordinarily supposed to appear and will otherwise trigger an error.',
)
def workflow(repo, script, dry_run, silent, clobber_existing):
    """Run workflow creating folders for tasks inside tree."""
    repo.run_workflow_script(
        script,
        dry_run,
        silent,
        clobber_existing=clobber_existing,
    )


@tb.command()
@click.argument(
    'pymodule', default='taskblaster.repository', metavar='[MODULE]'
)
@click.argument('directory', default='.')
def init(pymodule, directory):
    """Initialize repository inside directory.

    The optional MODULE argument can be used to specify a plugin.  A
    plugin is a Python module defining a subclass of the taskblaster
    Repository class.  This can be used to provide a custom JSON
    encoder to store objects not known to taskblaster, and to enable
    parallel workers and subworkers using MPI."""
    root = Path(directory).resolve()
    try:
        Repository.create(root, modulename=pymodule)
    except Repository.RepositoryError as ex:
        raise click.ClickException(ex)
    print(f'Created repository using module "{pymodule}" in "{root}".')


@tb.command()
@with_repo
def info(repo):
    """Print information about repository.

    This prints a brief overview of special files and directories
    associated with the current project."""
    info = repo.info()
    print('\n'.join(info))


def choose_states(ctx, param, value: str):
    # (None means any state)
    if value is None:
        return None

    choice = set(value)
    statecodes = State.statecodes()

    bad_states = choice - set(statecodes)

    if bad_states:
        raise click.BadParameter(
            'States must be among {}; got {}'.format(
                statecodes, ''.join(bad_states)
            )
        )

    return {State(value) for value in choice}


def state_option():
    return click.option(
        '--state',
        '-s',
        type=click.UNPROCESSED,
        callback=choose_states,
        help=(
            'Select only tasks with this state.  State be any of: {}.'.format(
                repr(State.statecodes())
            )
        ),
    )


def failure_option():
    return click.option(
        '--failure',
        '-F',
        type=click.UNPROCESSED,
        help='Select only tasks with failure string matching the string',
    )


_default_ls_columns = 'sirITf'


@tb.command()
@tree_argument()
@click.option(
    '--parents',
    is_flag=True,
    help='List ancestors of selected tasks outside selection.  '
    'Implies topological sort (default: False).',
    default=False,
)
@click.option(
    '--columns',
    '-c',
    is_flag=False,
    help='Columns to display: '
    'd: digest, '
    's: state, '
    'i: dependencies, '
    'f: folder, '
    'I: myqueue id and subworker, '
    'r: tags, '
    't: time info, '
    'T: time duration, '
    'c: conflict, '
    'C: conflict info, '
    f'(default: {_default_ls_columns})',
    default=_default_ls_columns,
)
@state_option()
@click.option(
    '--sort',
    type=click.Choice(['name', 'topo']),
    help="Sort tasks alphabetically ('name') or topologically ('topo').",
)
@echo_mode()
@failure_option()
@with_repo
def ls(repo, tree, columns, state, parents, sort, failure, echo):
    """List tasks under directory TREEs.

    Find tasks inside specified TREEs and collect their dependencies
    whether inside TREE or not.  Then perform the specified actions
    on those tasks and their dependencies."""

    if sort is None:
        sort = 'name'

    repo.registry.workers.sync(repo, echo)
    for line in repo.tree(tree, states=state, sort=sort, failure=failure).ls(
        parents=parents, columns=columns
    ):
        echo(line)


@tb.command()
@tree_argument()
@with_repo
@echo_mode()
def stat(repo, tree, echo):
    """Print statistics about selected tasks."""

    # If patterns point to directories, we must recurse into
    # those directories, i.e. <pattern>/*.
    #
    # But we can't just append /* because then we don't match the
    # directory itself.
    #
    # We also can't append * because then we match more things
    # than the user wanted.

    # Here we're doing O(N) work which is not necessary
    # when we're only counting.
    echo(repo.tree(tree).stat().tostring())


@tb.command()
@tree_argument()
@with_repo
@echo_mode()
def submit(repo, tree, echo):
    """Mark tasks in TREE and dependencies for execution.

    Only affects new tasks.  To submit a failed task,
    unrun it first."""

    listing = repo.listing(columns='sirf', fromdir=Path.cwd())

    nodes = [*repo.tree(tree).submit()]
    for line in listing.to_string([]):
        echo(line)  # Header

    all_tags = set()
    for node in nodes:
        nodeinfo = listing.nodeinfo(node)
        all_tags |= nodeinfo.tags
        echo(nodeinfo.to_string())

    echo()
    echo(f'Submitted {len(nodes)} tasks')
    if all_tags:
        echo(f'Tags included: {",".join(all_tags)}')


def setup_kill_signal_handlers():
    import signal

    def raise_signal(sig, frame):
        raise TaskBlasterInterrupt(f'Interrupted by signal {sig}.')

    for sig in [signal.SIGCONT, signal.SIGTERM]:
        signal.signal(sig, raise_signal)


def _split_tags(ctx, params, tags):
    return set(tags.split(',')) if tags else set()


def required_tags_option():
    return click.option(
        '--require',
        type=str,
        metavar='TAGS',
        callback=_split_tags,
        help='Require worker to pick up only tasks with all the TAGS '
        'specified as comma-separated list.',
    )


def supported_tags_option():
    return click.option(
        '--tags',
        metavar='TAGS',
        type=str,
        callback=_split_tags,
        help='Allow worker to pick up tasks with any of TAGS specified as '
        'comma-separated list.',
    )


def worker_class_option():
    return click.option(
        '--worker-class',
        type=str,
        metavar='WORKER',
        help='Worker class for this worker.  The name must exist in the '
        'resource configuration, see tb workers config.',
    )


@tb.command()
@tree_argument()
@click.option(
    '--subworker-count', type=int, help='Number of MPI subworkers in run.'
)
@click.option(
    '--subworker-size',
    type=int,
    help='Number of processes in each MPI subworker.',
)
@click.option(
    '--greedy',
    is_flag=True,
    help='Run also tasks created while running specified selection.',
)
@worker_class_option()
@supported_tags_option()
@required_tags_option()
@max_tasks_option()
@dryrun_option()
@echo_mode()
def run(
    tree,
    subworker_count,
    subworker_size,
    max_tasks,
    greedy,
    worker_class,
    tags,
    require,
    dry_run,
    echo,
):
    """Launch worker to execute tasks.

    The worker runs tasks in TREE and any dependencies with matching
    tags.  TREE defaults to all queued tasks."""
    repo = _repository()

    tags |= require  # if a worker "requires" a tag, tag is also "supported"

    worker_classes = repo.get_resources()
    if worker_class is not None:
        workerspec = worker_classes[worker_class]
        tags |= workerspec.tags
        require |= workerspec.required_tags

    if dry_run:
        with repo:
            repo.tree(tree).dry_run(
                worker_class,
                supported_tags=tags,
                required_tags=require,
                echo=echo,
            )
        return

    # Should we queue any selected tasks or only the queued subset?
    # Maybe queue them unless given an option.
    #
    # So: We take tree as an input.  If user used glob patterns,
    # the shell will have expanded them already.  Thus,
    # we take some paths as an input.  They may be tasks
    # or they may have subfolders that are tasks.
    #
    # What we need is to select all subfolders.  It would appear that
    # we can use sqlite's glob functionality for this.
    #
    # Then we need to "submit" those, and then launch a worker selecting
    # only those.
    #
    # So actually, if we received 1000 dirs, we can't just hog them
    # right away.  We could submit them immediately, but then the
    # worker just needs to be able to not return anything *except*
    # something matching one of those 1000 dirs.

    # Workers can be killed in exotic ways; keyboardinterrupt,
    # SIGCONT, SIGTERM, SIGKILL, who knows.  We try to catch
    # the signals and finalize/unlock/etc. gracefully.
    setup_kill_signal_handlers()

    # TODO: Replace with MYQUEUE_ID when we have one:
    myqueue_id = os.getenv('SLURM_JOB_ID', 'N/A')

    repo.run_worker(
        tree,
        name=myqueue_id,
        subworker_count=subworker_count,
        subworker_size=subworker_size,
        greedy=greedy,
        worker_class=worker_class,
        supported_tags=tags,
        required_tags=require,
    )


@tb.command()
@tree_argument()
@with_repo
@state_option()
@failure_option()
@click.option(
    '--force',
    default=False,
    is_flag=True,
    help='Unrun tasks without prompting for confirmation.',
)
@echo_mode()
def unrun(tree, repo, state, force, failure, echo):
    """Delete output files from TREE and reset task state to new.

    Unrunning a task also unruns its descendants."""
    # Might be wise to concentrate actual outputs inside a subdir
    # and then rmtree that subdir, except we hate using rmtree because
    # it is kind of dangerous.
    if not tree:
        return

    nodes, unrun = repo.tree(
        tree, states=state, failure=failure
    ).select_unrun()

    unrun_cnt = 0
    del_cnt = 0
    for node in nodes:
        if hasattr(node, 'to_be_removed'):
            del_cnt += 1
        else:
            unrun_cnt += 1
        echo(format_node_short(node))

    ntasks = len(nodes)
    if not ntasks:
        echo('No tasks selected.')
        return

    prompt = ''
    if unrun_cnt > 0:
        prompt += (
            f"Unrun the above {unrun_cnt}" f" task{'s' if unrun_cnt>1 else ''}"
        )
    if del_cnt > 0:
        if unrun_cnt > 0:
            prompt += ' and '
        prompt += f"REMOVE the above {del_cnt} task{'s' if del_cnt>1 else ''}?"

    if force or echo.are_you_sure(prompt):
        unrun()

        prompt = ''
        if unrun_cnt > 0:
            prompt += (
                f"{unrun_cnt} task" f"{'s' if unrun_cnt>1 else ''} were unrun"
            )
        if del_cnt > 0:
            if unrun_cnt > 0:
                prompt += ' and '
            prompt += f"{del_cnt} task{'s' if del_cnt>1 else ''} were removed"
        prompt += '.'
        echo(prompt)
    else:
        echo('Never mind.')


@tb.command()
@tree_argument()
@with_repo
@state_option()
def resolve(tree, repo, state):
    """Mark conflicts as resolved in TREE.

    Change the conflict state to "resolved" for selected tasks with
    conflict state "conflict"."""

    if not tree:
        return

    repo.tree(tree, states=state).resolve_conflict()


@tb.command()
@tree_argument()
@with_repo
@state_option()
def unresolve(tree, repo, state):
    """Mark resolved tasks as in conflict.

    Change the conflict state to "conflict" for selected tasks
    with conlict state "resolved"."""
    if not tree:
        return

    repo.tree(tree, states=state).unresolve_conflict()


@tb.command()
def completion():
    """Print bash command-line completion incantation.

    To enable command-line completion, include the
    script the shell rc file, e.g., ~/.bashrc.

    For shells other than bash, see the documentation of click
    for how to set up command-line completion."""
    import subprocess

    progname = Path(sys.argv[0]).name
    name = progname.replace('-', '_').upper()
    command = 'echo "$(_{}_COMPLETE=bash_source {})"'.format(name, progname)

    subprocess.run(command, shell=True, check=True)


@tb.command()
@tree_argument()
@dryrun_option()
@with_repo
@state_option()
@echo_mode()
def remove(tree, dry_run, repo, state, echo):
    """Delete tasks in TREE entirely.  Caution is advised."""

    if not tree:
        return

    nodes, delete = repo.tree(tree, states=state).remove()

    msg = 'would delete:' if dry_run else 'deleting:'
    for node in nodes:
        echo(f'{msg} {node.name}')

    ntasks = len(nodes)
    if not ntasks:
        echo('No tasks selected')
        return

    prompt = (
        f'WARNING: This permanently removes the above task(s).\nAre '
        f'you certain about deleting the above {ntasks} task(s)?'
    )
    if not dry_run and echo.are_you_sure(prompt):
        delete()
    elif not dry_run:
        echo('Never mind.')


@tb.command()
@with_repo
@click.option(
    '--action',
    type=str,
    help='Perform specified action for the selected tasks.  '
    'To associate tasks with actions, see the documentation'
    'for the @tb.actions decorator.',
)
@tree_argument()
def view(repo, action, tree):
    """View detailed information or execute task-specific actions."""
    repo.view(tree, action=action)


@tb.command()
@tree_argument()
@with_repo
def graph(repo, tree):
    """Generate dependency graph.

    This computes the dependency graph of the specified tasks and prints
    it in machine-friendly graphviz format for further processing.
    Examples:

      $ tb graph | dot -T svg > graph.svg  # convert to svg using graphviz\n
      $ tb graph | dot -T pdf > graph.pdf\n
      $ tb graph | display  # open window using imagemagick display command\n
    """
    repo.graph(tree)


def conflict_error(err):
    msg = """\
A task already exists in this directory with different inputs.
You may wish to assign a different name for the task in the workflow,
or delete the old task."""

    # We need also some error handling options, e.g., skip conflicts,
    # or always override, or choosing interactively.
    # Even better, we could generate multiple conflicts and list them
    # at the end.
    return click.ClickException(f'{err}\n{msg}')


def define_subgroups():
    from taskblaster.cli_registry import registry
    from taskblaster.cli_special import special
    from taskblaster.cli_tags import tag
    from taskblaster.cli_workers import workers

    tb.add_command(registry)
    tb.add_command(workers)
    tb.add_command(tag)
    tb.add_command(special)


define_subgroups()


cli = tb  # Old alias referenced by pip installations


if __name__ == '__main__':
    tb.main()
