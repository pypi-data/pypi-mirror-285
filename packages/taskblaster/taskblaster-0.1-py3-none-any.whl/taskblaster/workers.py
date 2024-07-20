import click

from taskblaster.mqintegration import MissingMyqueue, myqueue
from taskblaster.util import color

"""
   Lifespan

   tb worker submit

      Will register a worker to workers table with status 'queued'

   tb worker ls

      Will query myqueue and update states of each worker

      Will list status of all workers, their subworkers, and their tasks.
      For each worker, it will list also all tasks from runinfo.
      Will register a worker to workers table with status queue

   tb worker ls

      Will query myqueue to

      Will list status of all workers, their subworkers, and their tasks

"""

CREATE_TABLE_workers = """
CREATE TABLE IF NOT EXISTS workers (
    myqueue_id VARCHAR(12) PRIMARY KEY,
    wall_time INT,
    physical_queue VARCHAR(50),
    cores INT,
    subworker_size INT,
    subworker_count INT,
    state CHAR(1),
    submit_time timestamp NULL,
    start_time timestamp NULL,
    end_time timestamp NULL)"""

CREATE_TABLE_runinfo = """
CREATE TABLE IF NOT EXISTS runinfo (
    task_name VARCHAR(512) PRIMARY KEY,
    myqueue_id VARCHAR(12),
    subworker_id VARCHAR(512),
    exception VARCHAR(512) NULL,
    state CHAR(1),
    start_time timestamp NULL,
    end_time timestamp NULL)
    """


def rename_runlog_to_runinfo_if_possible(conn):
    import sqlite3

    try:
        conn.execute("""ALTER TABLE runlog RENAME TO runinfo""")
    except sqlite3.OperationalError:
        pass


class WorkerRow:
    def __init__(self, row):
        (
            self.myqueue_id,
            self.wall_time,
            self.physical_queue,
            self.cores,
            self.subworker_size,
            self.subworker_count,
            self.state,
            self.submit_time,
            self.start_time,
            self.end_time,
        ) = row


class Workers:
    def __init__(self, conn):
        self.conn = conn

    @classmethod
    def initialize(cls, conn):
        """Table manages synchronization between taskblaster and myqueue.

        myqueue_id has an unique identified, which links a task to a
        particular myqueue job.

        subworker_id is a unique name for the taskblaster worker,
        which is running the task.
        """
        conn.execute(CREATE_TABLE_workers)
        rename_runlog_to_runinfo_if_possible(conn)
        conn.execute(CREATE_TABLE_runinfo)

        indices = {
            'runlog_index': 'runinfo(task_name)',
            'runlog_index2': 'runinfo(myqueue_id)',
            'runlog_index3': 'runinfo(subworker_id)',
            'worker_myqueue_id': 'workers(myqueue_id)',
        }

        for indexname, target in indices.items():
            statement = f'CREATE INDEX IF NOT EXISTS {indexname} ON {target}'
            conn.execute(statement)

        return cls(conn)

    def get_active_workers(self):
        query = "SELECT * FROM workers WHERE state in ('q','h','r')"
        # qhr is definition of active per myqueue
        return [WorkerRow(row) for row in self.conn.execute(query)]

    def sync(self, repo, echo):
        """Synchronize worker information with myqueue.

        If worker is active in task blaster (myqueue state 'queued', 'hold'
        or running'), query myqueue for its status:
          * If myqueue doesn't find task (user has removed it from
            myqueue manually), mark tb worker to failed state,
            and mark all of subworker *running* tasks as *Failed*.
          * If myqueue returns multiple tasks for one id,
            display a warning and utilize the last one on the list
            (should not happen).
          * If myqueue state is_bad() returns True, update all *running*
            subworker tasks to *Failed*.
          * In any case, update worker state with myqueue state.
        """

        try:
            with myqueue() as queue:
                for worker in self.get_active_workers():
                    self.sync_one_worker(repo, queue, worker, echo)
        except MissingMyqueue:
            # Presumably there is nothing to synchronize.
            #
            # We could be better though: What determines whether we actually
            # need to synchronize is whether any of our workers are in fact
            # myqueue workers — not whether myqueue is installed or
            # can be loaded.
            pass

    def worker_failed(self, repo, myqueue_id, error_msg):
        for name in self.get_running_tasks_by_myqueue_id(myqueue_id):
            repo.registry.update_task_failed(name, error_msg)

        query = 'UPDATE workers SET state=(?) WHERE myqueue_id=(?)'
        self.conn.execute(query, ('F', myqueue_id))

    def sync_one_worker(self, repo, queue, worker, echo):
        from myqueue.selection import Selection

        mqtasks = queue.select(Selection(ids=set([worker.myqueue_id])))
        if len(mqtasks) == 0:
            echo(
                'Warning: Cannot retrieve information from myqueue '
                f'about task {worker.myqueue_id}. Marking tasks by '
                'each subworker as failed, and worker as failed.'
            )

            self.worker_failed(
                repo,
                worker.myqueue_id,
                'Failed due to worker manually removed from myqueue.',
            )

            return

        if len(mqtasks) > 1:
            job = worker.myqueue_id
            echo(f'Warning: myqueue returned multiple tasks for id {job}.')

        mqtask = mqtasks.pop()
        if mqtask.state.is_bad():
            self.worker_failed(
                repo,
                worker.myqueue_id,
                f'Failed due to worker condition: {str(mqtask.state)}.',
            )

        if mqtask.state.value != worker.state:
            query = 'UPDATE workers SET state=(?) WHERE myqueue_id=(?)'
            self.conn.execute(query, (mqtask.state.value, worker.myqueue_id))

    def submit_workers(
        self,
        repo,
        dry_run,
        resource_config,
        resources,
        max_tasks,
        workers,
        subworker_count,
        subworker_size,
        tags,
        require,
        echo,
    ):
        from taskblaster.mqintegration import mq_worker_task, submit_manytasks
        from taskblaster.registry import Missing
        from taskblaster.repository import WorkerSpecification

        resource_dct = repo.get_resources()
        workerdir = repo.root / 'runlogs'
        workerdir.mkdir(exist_ok=True)

        nworkers_submitted = 0

        if not workers:
            workers = [(None, 1)]

        for worker_class, nworkers in workers:
            if worker_class is None:
                worker_spec = WorkerSpecification()
            else:
                try:
                    worker_spec0 = resource_dct[worker_class]
                except KeyError:
                    raise click.ClickException(
                        f'Worker class {worker_class!r} not defined in '
                        f'{repo.resource_path}',
                    )

                import copy

                worker_spec = copy.deepcopy(worker_spec0)

            if resources is not None:
                worker_spec.resources = resources

            if tags is not None:
                worker_spec.tags |= tags

            if require is not None:
                worker_spec.required_tags |= require

            mqtasks = [
                mq_worker_task(
                    directory=workerdir,
                    resources=resources,
                    worker_module=repo.run_module,
                    max_tasks=max_tasks,
                    worker_class=worker_class,
                    subworker_size=subworker_size,
                    subworker_count=subworker_count,
                    tags=tags,
                    require=require,
                )
                for _ in range(nworkers)
            ]

            try:
                repo.cache.find_ready(
                    required_tags=require, supported_tags=tags
                )
            except Missing:
                echo(
                    f'No {worker_class or "generic"} workers submitted '
                    'as no compatible task is ready'
                )
                continue

            submit_manytasks(mqtasks, dry_run=dry_run)
            nworkers_submitted += len(mqtasks)

            if dry_run:
                continue

            for task in mqtasks:
                self.register_worker(task, subworker_size, subworker_count)

        if nworkers_submitted:
            action = 'Would submit' if dry_run else 'Submitted'
            workers = 'worker' if nworkers_submitted == 1 else 'workers'
            echo(f'{action} {nworkers_submitted} {workers} in total')
        else:
            echo()
            lines = [
                'No compatible task is ready -- no workers submitted.',
                '',
                'Conditions for a worker to pick up a task:',
                ' * Task must be queued',
                ' * All task dependencies must be done',
                ' * Worker tags must include all task tags',
                ' * Task tags must include all "required" tags of worker',
                '',
                f'Worker tags are: {tags or "(no tags)"}',
                f'Worker required tags are: {require or "(no tags)"}',
            ]

            echo('\n'.join(lines))

    def register_worker(self, mqtask, subworker_size, subworker_count):
        query = """
INSERT INTO workers (myqueue_id, wall_time, physical_queue,
cores, subworker_size, subworker_count,
state, submit_time) VALUES
(?, ?, ?, ?, ?, ?, ?,
DATETIME(CURRENT_TIMESTAMP, 'localtime'))"""

        resources = mqtask.resources
        self.conn.execute(
            query,
            (
                mqtask.id,
                resources.tmax,
                resources.nodename,
                resources.cores,
                subworker_size,
                subworker_count,
                'q',
            ),
        )

    def ls(self, cols='isW', *, echo):
        def status(state):
            return {
                'q': ('queued', 'yellow'),
                'd': ('done', 'green'),
                'r': ('running', 'bright_yellow'),
                'u': ('undefined', 'bright_red'),
                'h': ('hold', 'yellow'),
                'F': ('FAILED', 'bright_red'),
                'T': ('TIMEOUT', 'bright_red'),
                'M': ('MEMORY', 'bright_red'),
                'C': ('CANCELLED', 'bright_red'),
            }[state]

        query = 'SELECT * FROM workers'
        columns = {
            'i': ('myqueue id', 12, lambda x: x[0]),
            's': ('status', 10, lambda x: status(x[6])),
            'W': ('wall time', 10, lambda x: str(x[1])),
        }

        def adjust_cell(s, length):
            col = None
            if isinstance(s, tuple):
                s, col = s
            if len(s) > length:
                s = s[: length - 1] + '…'
            return color(s.ljust(length), col)

        # Header row
        for col in cols:
            name, length, _ = columns[col]
            echo(color(adjust_cell(name, length), 'yellow'), nl=False)
        echo()

        # Header line
        for col in cols:
            _, length, _ = columns[col]
            echo(color('─' * (length - 1) + ' ', 'bright_yellow'), nl=False)
        echo()

        # Rows
        for row in self.conn.execute(query):
            for col in cols:
                _, length, func = columns[col]
                echo(adjust_cell(func(row), length), nl=False)

            echo()

            # This prints all the tasks of a worker but we should probably
            # not do that:
            # myqueue_id = row[0]
            # for task in self.get_tasks_by_myqueue_id(myqueue_id):
            #    echo(task)

    def get_runinfo(self, name):
        query = (
            'SELECT subworker_id, start_time, end_time, exception'
            ' FROM runinfo WHERE task_name=(?)'
        )
        rows = self.conn.execute(query, (name,))
        for row in rows:
            return row
        return '', None, None, None

    def remove_runinfo(self, name):
        query = 'DELETE FROM runinfo WHERE task_name=(?)'
        self.conn.execute(query, (name,))

    def get_tasks_by_myqueue_id(self, myqueue_id):
        query = (
            'SELECT task_name '
            'FROM runinfo, registry'
            ' WHERE runinfo.myqueue_id=(?)'
            ' AND registry.name = runinfo.task_name'
        )
        return [row for (row,) in self.conn.execute(query, (myqueue_id,))]

    def get_running_tasks_by_myqueue_id(self, myqueue_id):
        query = (
            'SELECT task_name '
            'FROM runinfo, registry'
            ' WHERE runinfo.myqueue_id=(?)'
            ' AND registry.name = runinfo.task_name'
            " AND registry.state='r'"
        )
        return [row for (row,) in self.conn.execute(query, (myqueue_id,))]

    def register_task_running(self, name, myqueue_id, subworker_id):
        query = (
            'INSERT INTO runinfo '
            '(task_name, myqueue_id, subworker_id, start_time)'
            ' VALUES (?, ?, ?,'
            " DATETIME(CURRENT_TIMESTAMP,'localtime'))"
            ' ON CONFLICT(task_name)'
            ' DO UPDATE SET myqueue_id=(?), subworker_id=(?), '
            " start_time=DATETIME(CURRENT_TIMESTAMP, 'localtime')"
        )
        self.conn.execute(
            query, (name, myqueue_id, subworker_id, myqueue_id, subworker_id)
        )

    def register_task_failed(self, name, exception):
        assert exception is not None
        self._register_task_finished(name, exception)

    def register_task_done(self, name):
        self._register_task_finished(name, None)

    def _register_task_finished(self, name, exception):
        query = (
            'UPDATE runinfo'
            ' SET exception=(?), '
            " end_time=DATETIME(CURRENT_TIMESTAMP, 'localtime')"
            ' WHERE task_name=(?)'
        )
        self.conn.execute(query, (exception, name))

    def update_worker_state(
        self, name, myqueue_id, subworker_id, state, exception=None
    ):
        """
        state='r', add the record and update start time
        state='d', update the end time
        state='F', update the end time
        """
        query = (
            'UPDATE runinfo'
            ' SET exception=(?), '
            " end_time=DATETIME(CURRENT_TIMESTAMP, 'localtime')"
            ' WHERE task_name=(?)'
        )
        self.conn.execute(query, (exception, name))

    def find_running_myqueue_jobs(self):
        query = (
            'SELECT DISTINCT runinfo.myqueue_id'
            ' FROM registry'
            ' LEFT JOIN runinfo ON registry.name = runinfo.task_name'
        )
        return [row[0] for row in self.conn.execute(query)]
