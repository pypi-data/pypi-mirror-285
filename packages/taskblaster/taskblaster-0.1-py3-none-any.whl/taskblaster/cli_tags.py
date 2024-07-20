import click

import taskblaster.cli as cli


@click.command()
@cli.with_repo
@cli.tree_argument()
@click.option('--add', metavar='TAG', help='Add TAG to tasks.')
@click.option('--untag', metavar='TAG', help='Remove TAG from tasks.')
@cli.failure_option()
def tag(repo, tree, add, untag, failure):
    """List, tag, or untag tasks in TREE.

    Without options, list all tasks or selected tasks with their tags.

    With --add or --untag apply actions on selected tasks only.
    """

    if not any([add, untag]):
        # This is inclusive, i.e., tree defaults to everything
        tree = repo.tree(tree, failure=failure)
        tree.list_tags()
        return

    if not tree:
        print('No tasks selected')
        return

    tree = repo.tree(tree, failure=failure)
    if add:
        tree.add_tag(add)
    if untag:
        tree.untag(untag)
