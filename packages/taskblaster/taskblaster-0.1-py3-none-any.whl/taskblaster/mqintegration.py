class MissingMyqueue(Exception):
    pass


def myqueue(dry_run=False):
    try:
        import myqueue  # noqa: F401
    except ModuleNotFoundError:
        raise MissingMyqueue()

    from myqueue.config import Configuration
    from myqueue.queue import Queue

    # XXX depends on pwd does it not?  Should probably depend on workflow
    # location.
    try:
        config = Configuration.read()
    except ValueError:
        raise MissingMyqueue()

    return Queue(config=config, dry_run=dry_run)


def submit_manytasks(tasks, dry_run, max_mq_tasks=None):
    from myqueue.submitting import submit

    with myqueue(dry_run=dry_run) as queue:
        submit(queue, tasks, max_tasks=max_mq_tasks)


def mq_worker_task(
    directory,
    resources,
    worker_module,
    max_tasks=None,
    subworker_size=None,
    subworker_count=None,
    worker_class=None,
    tags=None,
    require=None,
):
    from myqueue.task import create_task

    args = ['run']

    if max_tasks is not None:
        args.append(f'--max-tasks={max_tasks:d}')
    if subworker_size is not None:
        args.append(f'--subworker-size={subworker_size:d}')
    if subworker_count is not None:
        args.append(f'--subworker-count={subworker_count:d}')

    if worker_class:
        args.append(f'--worker-class={worker_class}')

    if tags:
        txt = ','.join(tags)
        args.append(f'--tags={txt}')

    if require:
        txt = ','.join(require)
        args.append(f'--require={txt}')

    return create_task(
        cmd='taskblaster',
        name='worker',
        args=args,
        deps=[],
        resources=resources,
        folder=directory,
    )
