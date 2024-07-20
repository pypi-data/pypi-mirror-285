def test_ls(simplerepo):
    with simplerepo:
        lines = [*simplerepo.tree().ls()]
    print(lines)


def test_ls_outside_tree(simplerepo):
    """Test that ls does not crash if there are tasks outside cwd."""
    # (The repo fixture restores cwd)
    path = simplerepo.tree_path / 'arbitrary_dir'
    path.mkdir()
    with simplerepo:
        print([*simplerepo.tree().ls(fromdir=path)])


def test_ls_across_subdirs(simplerepo):
    import click

    path = simplerepo.tree_path / 'subworkflow'

    with simplerepo:
        lines = [*simplerepo.tree().ls(parents=True, fromdir=path)]

    found = False
    for line in lines:
        tokens = click.unstyle(line).split()
        if '../ok' in tokens:
            found = True
            break

    assert found
