def test_rename_import_path(tool):
    tool.run_simple_workflow()
    tasks = tool.select('*')

    def get_target_functions(names):
        with tool.repo:
            return {
                name: tool.repo.cache.name2node(name).target for name in names
            }

    old_targets = get_target_functions(task.name for task in tasks)

    old_targetfunc = 'ok'
    new_targetfunc = 'new.target.function'

    tool.command(
        'special rename-import-path '
        f'--force {old_targetfunc} {new_targetfunc}'
    )

    new_targets = get_target_functions(task.name for task in tasks)

    assert old_targetfunc in old_targets.values()
    assert old_targetfunc not in new_targets.values()
    assert new_targetfunc not in old_targets.values()
    assert new_targetfunc in new_targets.values()

    for task in tasks:
        assert (old_targets[task.name] == old_targetfunc) == (
            new_targets[task.name] == new_targetfunc
        )
