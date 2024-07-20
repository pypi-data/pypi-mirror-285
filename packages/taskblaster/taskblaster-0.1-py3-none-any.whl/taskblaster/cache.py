from collections.abc import Mapping
from pathlib import Path

from taskblaster.entry import Entry
from taskblaster.future import Future
from taskblaster.state import ConflictState


class FileCache(Mapping):
    def __init__(self, *, directory, registry, json_protocol):
        self.directory = Path(directory)
        self._absdir = self.directory.absolute()

        self.registry = registry
        self.json_protocol = json_protocol

    def entry(self, name) -> Entry:
        if not self.registry.contains(name):
            raise KeyError(name)
        directory = self.directory / name
        return Entry(directory, self.json_protocol)

    def __len__(self):
        return self.registry.index.count()

    def __iter__(self):
        return (regnode.name for regnode in self.registry.index.nodes())

    def name2node(self, name):
        from taskblaster.hashednode import Node

        # XXX Fixme: This has the purpose of raising Missing
        # instead of the input being missing ....
        self.registry.index.node(name)
        serialized_input = self.registry.inputs.get(name)
        assert serialized_input is not None
        return Node.fromdata(self.json_protocol, serialized_input, name)

    def __getitem__(self, name) -> Future:
        from taskblaster.registry import Missing

        try:
            node = self.name2node(name)
        except Missing:
            raise KeyError(name)
        return Future(node, self)

    def __repr__(self):
        return (
            f'{type(self).__name__}({self.directory}, '
            f'[{self.registry.index.count()} entries])'
        )

    def add_or_update(
        self,
        node,
        *,
        force_overwrite=False,
        tags=None,
        clobber_existing=False,
    ):
        name = node.name

        if self.registry.contains(name):
            previous_node = self.name2node(name)

            import warnings

            if clobber_existing:
                warnings.warn('clobber_existing currently ignored')

            previous_indexnode = self.registry.index.node(name)

            if node.serialized_input != previous_node.serialized_input:
                if not previous_indexnode.state.is_pristine:
                    # We could punt the state back to new and overwrite,
                    # but for now the user will have to unrun manually.

                    con, info, buf = self.registry.get_conflict_info(
                        previous_indexnode.name
                    )

                    new_buf = node._buf
                    if buf != new_buf:
                        self.registry.update_conflicts(
                            previous_indexnode.name,
                            conflict='c',
                            reason=previous_node._buf,
                            buf=new_buf,
                        )

                        return 'conflict', previous_indexnode
                    return ConflictState(con).name, previous_indexnode

                # Maybe we should only overwrite if previous node is 'new'
                #  - if it's failed, we probably shouldn't delete errmsg etc.
                #  - what if it's queued?
                force_overwrite = True

            # check if conflict has been resolved and update conflicts
            self.registry.clear_conflict(previous_indexnode.name)

        action, indexnode = self.registry.add_or_update(
            node,
            force_overwrite=force_overwrite,
            tags=tags,
        )

        assert action in {'add', 'update', 'have'}
        return action, indexnode

    def load_inputs_and_resolve_references(self, node):
        serialized_input = self.registry.inputs.get(node.name)
        return self.json_protocol._actually_load(
            self, serialized_input, self.directory / node.name
        )

    def find_ready(self, required_tags=None, supported_tags=None):
        """Return a task which is ready to run right now.

        Returns None if no such task is found.
        """

        # TODO: Change to raise NoSuchTask() if there is no task.
        # Also: We need to find things only with the right kind of worker.
        # What if we depend on things in other directories?  We need to
        # be able to run those, too.
        #
        # Probably we should also be able to limit searching to a particular
        # directory, but that doesn't always work well since dependencies
        # often reside in different directories
        return self.registry.find_ready(required_tags, supported_tags)

    def delete_nodes(self, nodes):
        # XXX must work if registry/tree are inconsistent.
        import shutil

        entries = [self.entry(node.name) for node in nodes]
        cachedir = self._absdir.resolve()

        for entry in entries:
            assert cachedir in entry.directory.parents

        for entry in entries:
            entry.delete()

            directory = entry.directory.resolve()
            # Let's be a little bit paranoid before rmtreeing:
            assert 'tree' in directory.parent.parts
            assert self.directory.is_absolute()
            assert self.directory in directory.parents
            if directory.exists():
                shutil.rmtree(directory)
            remove_empty_dirs(cachedir, entry.directory)

        self.registry.remove_nodes(nodes)


def remove_empty_dirs(root, directory):
    """Remove directory and all empty parent directories up to root."""
    if root not in directory.parents:
        raise RuntimeError(f'Refusing to delete dirs outside {root}!')

    for parent in directory.parents:
        if parent == root:
            break
        try:
            parent.rmdir()
        except OSError:  # directory not empty
            break


class DirectoryConflict(OSError):
    pass
