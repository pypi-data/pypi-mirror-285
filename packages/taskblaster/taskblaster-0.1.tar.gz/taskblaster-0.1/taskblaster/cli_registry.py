import click

from taskblaster.cli import echo_mode, with_repo
from taskblaster.state import State


@click.group()
def registry():  # noqa: F811
    """View or manipulate registry."""


@registry.command()
@with_repo
def build(repo):
    """Add all tasks in the tree to the registry."""
    import graphlib

    from taskblaster.entry import Entry

    registry = repo.cache.registry

    nodes = {}
    graph = {}

    for inputfile in repo.root.glob('tree/**/input.json'):
        entry = Entry(inputfile.parent, repo.cache.json_protocol)
        name = str(inputfile.parent.relative_to(repo.tree_path))
        node = entry.node(name)
        assert node.name == name

        nodes[name] = node
        graph[name] = set(node._parents)

    sorter = graphlib.TopologicalSorter(graph)

    for name in sorter.static_order():
        node = nodes[name]
        action, indexnode = registry.add_or_update(node=node)

        if repo.cache.entry(name).has_output():
            state = State.done
        else:
            state = State.new

        registry.update_state(name, state)
        print(action, indexnode.name, indexnode.state)


@registry.command()
@with_repo
def ancestors(repo):
    print(repo.cache.registry.ancestry.graph())


@registry.command()
@with_repo
def ls(repo):
    registry = repo.cache.registry
    for node in registry.index.nodes():
        print(node)


@registry.command()
@with_repo
@echo_mode()
@click.option(
    '--unapply',
    is_flag=True,
    help='Reverse operation: Remove inputs from registry (mostly for testing).'
    '  Does not prompt for confirmation.',
)
def patch_serialized_inputs(repo, echo, unapply):
    """Patch all tasks so inputs are stored in the registry.

    The purpose of this command is to migrate repositories where input
    lives only inside input.json such that the input will be inside
    the registry.  input.json will not be deleted.  The operation
    prompts for confirmation.

    This does not affect tasks that already have inputs stored in registry.
    """
    from taskblaster.inputs import MissingInput

    cache = repo.cache
    registry = cache.registry

    if unapply:
        to_be_patched = registry.inputs.names()

        for name in to_be_patched:
            echo(name)

        def patch_nodes():
            for name in to_be_patched:
                registry.inputs.remove(name)

    else:
        to_be_patched = []

        for node in registry.index.nodes():
            try:
                registry.inputs.get(node.name)
            except MissingInput:
                echo(node.name)
                actual_input = cache.entry(node.name).inputfile.read_text()
                to_be_patched.append((node, actual_input))

        def patch_nodes():
            for node, actual_input in to_be_patched:
                echo(f'Patching {node.name}')
                cache.registry.inputs.add(
                    node.name, serialized_input=actual_input
                )

    if not to_be_patched:
        echo('Nothing to do.')
        return

    action = 'Unmigrate' if unapply else 'Migrate'
    prompt = f'{action} the above {len(to_be_patched)} tasks?'

    if echo.are_you_sure(prompt):
        patch_nodes()
    else:
        echo('Never mind.')
