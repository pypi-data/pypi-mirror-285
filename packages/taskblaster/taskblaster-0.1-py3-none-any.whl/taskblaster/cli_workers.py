import click

import taskblaster.cli as cli


@click.group()
def workers():  # noqa: F811
    """View or manipulate workers."""


@workers.command()
@cli.with_repo
@cli.echo_mode()
def ls(repo, echo):
    """List taskblaster workers."""
    registry = repo.cache.registry
    registry.workers.sync(repo, echo)
    registry.workers.ls(echo=echo)


@workers.command()
@cli.with_repo
@cli.echo_mode()
def config(repo, echo):
    """View worker configuration."""
    echo('Configured worker classes')
    echo(f'Path: {repo.resource_path}')
    echo()

    resources = repo.get_resources()
    for name in sorted(resources):
        workerinfo = resources[name]
        echo(workerinfo.description())
        echo()


def handle_workers_argument(ctx, param, value):
    return [parse_worker_arg(arg) for arg in value]


def parse_worker_arg(worker_arg: str):
    part1, *part2 = worker_arg.rsplit(':', 1)

    if part2:
        try:
            nworkers = int(part2[0])
        except ValueError:
            raise click.ClickException(
                f'{part2[0]!r} is not a valid number of workers'
            )
        return part1, nworkers

    if part1.isnumeric():
        return None, int(part1)

    return part1, 1


@workers.command()
@cli.with_repo
@cli.dryrun_option()
@click.option(
    '--subworker-count',
    default=None,
    metavar='COUNT',
    type=int,
    help='Number of MPI subworkers in run.',
)
@click.option(
    '--subworker-size',
    default=None,
    metavar='SIZE',
    type=int,
    help='Number of processes in each MPI subworker.',
)
@click.option(
    '-R', '--resources', help='Resource specification forwarded to myqueue.'
)
@cli.max_tasks_option()
@click.argument(
    'workers',
    nargs=-1,
    callback=handle_workers_argument,
    metavar='[WORKER[:NUM]...]',
)
@cli.supported_tags_option()
@cli.required_tags_option()
@cli.echo_mode()
def submit(
    repo,
    dry_run,
    resources,
    max_tasks,
    subworker_count,
    subworker_size,
    workers,
    tags,
    require,
    echo,
):
    """Submit workers as myqueue jobs.

    Without arguments, submit one generic worker.
    If WORKER is a number, submit that many generic workers.
    Else, WORKER must be the name of a configured worker in the resources file
    from which settings are taken (see tb workers config).
    Submit NUM workers of that type,
    or one worker if NUM is not specified.

    Examples:

      tb workers submit  # submit one generic worker\n
      tb workers submit 4  # submit 4 generic workers\n
      tb workers submit worker1  # submit one worker of type 'worker1'\n
      tb workers submit worker1:4  # submit 4 workers of type 'worker1'\n

    Options below override options taken from resources file.
    """
    registry = repo.cache.registry

    registry.workers.submit_workers(
        repo,
        dry_run,
        resource_config=repo.get_resources(),
        resources=resources,
        max_tasks=max_tasks,
        subworker_count=subworker_count,
        subworker_size=subworker_size,
        workers=workers,
        tags=tags,
        require=require,
        echo=echo,
    )
