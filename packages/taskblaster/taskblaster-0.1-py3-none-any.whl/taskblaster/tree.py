from pathlib import Path
from typing import Union

from taskblaster import UNREACHABLE_REF
from taskblaster.listing import Listing
from taskblaster.state import State
from taskblaster.util import absolute, color, is_subpath


def normalize_patterns(repo, directories, relative_to=None):
    if relative_to is None:
        cwd = Path.cwd()
    else:
        cwd = relative_to
    if not directories:
        directories = ['.']

        if not is_subpath(cwd, repo.cache.directory):
            cwd = repo.root

    def patternize(pattern):
        path = absolute(cwd / pattern)
        if path == repo.root:
            path = repo.cache.directory

        relpath = path.relative_to(repo.cache.directory)
        pattern = str(relpath)
        if pattern == '.':
            pattern = '*'  # XXX not very logical
        return pattern

    return [patternize(directory) for directory in directories]


class Tree:
    def __init__(
        self,
        repo,
        directories: Union[list, str],
        states=None,
        relative_to=None,
        failure=None,
        sort='name',
    ):
        self.repo = repo

        if isinstance(directories, str):
            directories = [directories]

        # Some of these are actually patterns that we use to glob
        # inside the registry, which is a bit misleading.
        self.directories = normalize_patterns(
            repo, directories, relative_to=relative_to
        )

        self.registry = repo.registry
        self.cache = repo.cache

        if failure is not None and states is None:
            states = {State.fail}

        self.states = states
        self.failure = failure
        self.sort = sort

    def nodes(self):
        return self._nodes(False, set())

    def nodes_topological(self, reverse=False):
        return self._nodes(topological_order=True, seen=set(), reverse=reverse)

    def _recurse_kin(self, node, seen, reverse=False):
        if node.name in seen:
            return

        ancestry = self.registry.ancestry
        if reverse:
            kin_names = ancestry.descendants(node.name)
        else:
            kin_names = ancestry.ancestors(node.name)

        for kin_name in kin_names:
            if kin_name in seen:
                continue
            if kin_name == UNREACHABLE_REF:
                continue
            kin = self.registry.index.node(kin_name)
            yield from self._recurse_kin(kin, seen, reverse=reverse)

        seen.add(node.name)
        yield node

    def submit(self):
        # XXX We need only loop recursively over nodes that are new.
        nodes = [
            node
            for node in self.nodes_topological()
            if node.state == State.new
        ]
        self.registry.index.update_states(
            [node.name for node in nodes], State.queue.value
        )
        return [node.replace(state=State.queue) for node in nodes]

    def _update_conflict(self, oldstate, newstate):
        nodes = [node for node in self.nodes() if node.state != State.new]
        for node in nodes:
            task_name = node.name
            conflict, info, inp = self.registry.get_conflict_info(task_name)
            if conflict == oldstate:
                self.registry.update_conflicts(
                    task_name, conflict=newstate, reason=info, buf=inp
                )

    def resolve_conflict(self):
        self._update_conflict('c', 'r')

    def unresolve_conflict(self):
        self._update_conflict('r', 'c')

    def select_unrun(self):
        nodes = [node for node in self.nodes_topological(reverse=True)]

        nodes_dct = {node.name: node for node in nodes}

        affected_nodes = []
        for indexnode in nodes:
            node = self.cache.name2node(indexnode.name)
            kwargs = node._dct
            implicit_remove = kwargs.pop('__tb_implicit_remove__', [])

            # XXX "implicit" was assigned in local namespace but unused?
            # Now we just pop it from kwargs:
            # implicit = kwargs.pop('__tb_implicit__', [])
            kwargs.pop('__tb_implicit__', None)

            external = kwargs.pop('__tb_external__', None)
            indexnode.external = external
            indexnode.reset_external = False
            if external:
                for name, _ in implicit_remove:
                    if name in nodes_dct:
                        indexnode.reset_external = True

            if len(implicit_remove) > 0 and not external:
                for name, _ in implicit_remove:
                    if name in nodes_dct:
                        indexnode.to_be_removed = True

            if not indexnode.external and indexnode.state in {
                State.new,
                State.cancel,
            }:
                continue

            affected_nodes.append(indexnode)

        def unrun():
            for node in affected_nodes:
                to_be_removed = (
                    hasattr(node, 'to_be_removed') and node.to_be_removed
                )
                entry = self.cache.entry(node.name)
                if not node.external and to_be_removed:
                    self.cache.delete_nodes([node])
                    continue

                self.registry.unrun(node.name)

                if node.reset_external:
                    from taskblaster.hashednode import Node

                    UNREACHABLE_KWARGS = {
                        'obj': {
                            '__tb_type__': 'ref',
                            'name': UNREACHABLE_REF,
                            'index': tuple(),
                        }
                    }
                    external_node = Node.new(
                        self.cache.json_protocol,
                        'fixedpoint',
                        UNREACHABLE_KWARGS,
                        node.name,
                    )
                    self.cache.add_or_update(
                        external_node, force_overwrite=True
                    )

                # (If we are strict about state <--> files,
                # then we don't always need to talk to the FS.)
                entry.inputfile.unlink(missing_ok=True)
                if node.state == State.done:
                    outputfile = entry.outputfile
                    outputfile.unlink(missing_ok=True)
                    # Should nuke the whole directory

                try:
                    entry.directory.rmdir()
                except OSError:
                    pass  # (Directory not empty)

            return len(nodes)

        return affected_nodes, unrun

    def remove(self):
        nodes = list(self.nodes_topological(reverse=True))

        def delete():
            self.cache.delete_nodes(nodes)
            print(f'{len(nodes)} task(s) were deleted.')

        return nodes, delete

    def _nodes(self, topological_order, seen, reverse=False):
        for directory in self.directories:
            nodes = self.registry.index.glob(
                [directory],
                states=self.states,
                sort=self.sort,
                failure=self.failure,
            )

            for node in nodes:
                if node.name in seen:
                    continue

                if topological_order:
                    yield from self._recurse_kin(node, seen, reverse=reverse)
                else:
                    seen.add(node.name)
                    yield node

    def ls(self, parents=False, columns='sifIt', *, fromdir=None):
        # each element is either a task or a subdirectory to recurse.
        if fromdir is None:
            fromdir = Path.cwd()

        if parents:
            iternodes = self.nodes_topological()
        else:
            iternodes = self.nodes()

        ls_info = Listing(
            registry=self.registry,
            treedir=self.cache.directory,
            fromdir=fromdir,
            columns=columns,
        )

        return ls_info.to_string(iternodes)

    def stat(self) -> 'Stats':
        return Stats(self.nodes())

    def add_tag(self, tag):
        resources = self.registry.resources
        for node in self.nodes():
            if resources.has_tag(node.name, tag):
                print(f'{node.name} already tagged as {tag!r}')
            else:
                resources.add_tag(node.name, tag)
                print(f'{node.name} tagged as {tag!r}')

    def list_tag(self, tag):
        names = self.registry.resources.select_tag(tag)
        for name in names:
            print(name)

    def untag(self, tag):
        resources = self.registry.resources
        for node in self.nodes():
            if resources.has_tag(node.name, tag):
                resources.untag(node.name, tag)
                print(f'{node.name} untagged as {tag!r}')
            else:
                print(f'{node.name} already not tagged as {tag!r}')

    def list_tags(self):
        alltags = {
            node.name: self.registry.resources.get_tags(node.name)
            for node in self.nodes()
        }

        if not alltags:
            print('There are no tagged tasks.')

        fmt = '{:<24s} {}'
        print(fmt.format('Name', 'Tags'))
        print('─' * 79)
        for name, tags in alltags.items():
            print(fmt.format(name, ' '.join(sorted(tags))))

    def dry_run(self, worker_class, supported_tags, required_tags, echo):
        # Not so efficient because we do not perform a combined
        # query for names.

        # Here we are deciding whether we can run a task or not, but it is
        # actually the query in registry which implements the decision in
        # reality.  So it would be wise for all that code to live e.g.
        # in resources.py.

        for node in self.nodes_topological():
            tags = self.registry.resources.get_tags(node.name)

            unsupported_tags = tags - supported_tags
            missing_req = required_tags - tags

            if node.awaitcount:
                awaitstate = color(
                    f'awaits:{node.awaitcount}', 'bright_yellow'
                )
            else:
                awaitstate = color('awaits:0', 'bright_green')

            if missing_req:
                tagstring = ' '.join(missing_req)
                conclusion = color(f'Task missing tag: {tagstring}', 'red')
            elif unsupported_tags:
                tagstring = ' '.join(unsupported_tags)
                conclusion = color(f'Worker missing tag: {tagstring}', 'red')
            elif node.state not in {State.new, State.queue}:
                conclusion = color('Task not new or queued', 'bright_yellow')
            elif node.awaitcount > 0:
                conclusion = color('Dependencies not done', 'bright_yellow')
            else:
                conclusion = color('Ready', 'bright_green')

            echo(
                f'{node.name:30} {node.state.ansiname:16} {awaitstate:18} '
                f'{conclusion}'
            )


class Stats:
    def __init__(self, nodes):
        counts = {state: 0 for state in State}

        for node in nodes:
            counts[node.state] += 1

        self.counts = counts
        self.ntasks = sum(counts.values())

    def tostring(self):
        lines = []
        for state in State:
            num = self.counts[state]
            # The strings are long because of the ANSI codes.
            # Could/should we be able to get the printed string length
            # somehow?
            lines.append(f'{state.ansiname:18s} {num}')
        return '\n'.join(lines)
