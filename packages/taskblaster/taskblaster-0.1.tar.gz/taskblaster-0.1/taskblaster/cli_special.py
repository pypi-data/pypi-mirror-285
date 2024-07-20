import shutil
from pathlib import Path

import click

import taskblaster.cli as cli
from taskblaster.repository import Repository


@click.group()
def special():  # noqa: F811
    """More rare special commands."""


@special.command()
@click.argument('old')
@click.argument('new')
@cli.tree_argument()
@click.option(
    '--force',
    is_flag=True,
    type=str,
    default=False,
    help='Rename targets without prompting for confirmation.',
)
@cli.echo_mode()
@cli.with_repo
def rename_import_path(repo, old, new, tree, force, echo):
    """Rename import path for tasks.

    Replace OLD import paths with NEW ones.  OLD and NEW are function
    import paths as specified to tb.node().  The primary use of this
    command is to keep the repository up to date when a function has
    been moved or renamed during refactoring.

    No attempt is made to ensure that the new and old functions are
    equivalent or to otherwise invalidate tasks, so caution is advised."""

    paths, rename_fcn = repo.rename_import_path(tree, old, new)
    if len(paths) == 0:
        echo('No matches to rename.')
        return
    for path in paths:
        echo(f'Task {path} {old} -> {new}')

    prompt = (
        f'Are you sure you want to rename following {len(paths)} '
        'task import paths?'
    )
    if force:
        rename_fcn()
    elif echo.are_you_sure(prompt):
        rename_fcn()
    else:
        echo('Never mind.')


@special.command()
@click.argument('newrepopath')
@cli.tree_argument()
@cli.echo_mode()
@cli.with_repo
def clone_sub_tree(repo, newrepopath, tree, echo):
    """Clone TREE as new repository.

    Tasks in TREE and their ancestors are collected and copied as a
    new standalone repository."""
    newrepopath = Path(newrepopath).resolve()

    # Make sure the repository does not exist
    try:
        Repository.find(newrepopath)
    except Repository.RepositoryError as ex:
        echo(ex)
    else:
        raise click.ClickException(
            f'Target repository exists at {newrepopath}.'
        )

    pymodulefile = repo.root / repo._magic_dirname / repo._py_filename
    pymodulename = pymodulefile.read_text().strip()
    echo(f'module {pymodulename}')

    try:
        newrepo = Repository.create(newrepopath, modulename=pymodulename)
    except Repository.RepositoryError as ex:
        raise click.ClickException(ex)

    echo(f'Cloning {tree} to {newrepopath}')
    tree = repo.tree(tree)
    new_registry = newrepo.registry
    with newrepo:
        for node in tree.nodes_topological():
            new_node = repo.cache.entry(node.name).node(node.name)
            tags = repo.cache.registry.resources.get_tags(node.name)
            new_registry._add(new_node, tags, force_state=node.state)
            shutil.copytree(
                repo.tree_path / node.name, newrepo.tree_path / node.name
            )
