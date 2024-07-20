from taskblaster.state import State


def printlines_indented(string, *, indent):
    for line in string.split('\n'):
        spaces = ' ' * indent
        print(f'{spaces}{line}')


def view_node(repo, node):
    cache = repo.cache
    name = node.name
    entry = cache.entry(name)
    hashednode = cache.name2node(name)
    depth = cache.registry.get_depth(name)

    state = State(node.state)

    print(f'name: {name}')
    print(f'  location: {entry.directory}')
    print(f'  state:    {state.name}')
    print(f'  target:   {hashednode.target}(…)')
    print(f'  wait for: {node.awaitcount} dependencies')
    print(f'  depth:    {depth}')
    print()

    print_parents(hashednode)
    print_input(hashednode, node)
    print_output(state, entry)
    print_runinfo(*cache.registry.workers.get_runinfo(name))
    target = hashednode.target
    if target != 'fixedpoint':
        print_custom_actions(repo.import_task_function(hashednode.target))


def print_parents(hashednode):
    print('  parents:')
    if hashednode.parents:
        for parent in hashednode.parents:
            print(f'    {parent}')
    else:
        print('    <task has no dependencies>')
    print()


def print_input(hashednode, indexnode):
    # inputstring = hashednode.input_repr(maxlen=None)
    print('  input:')
    # printlines_indented(inputstring, indent=4)
    printlines_indented(hashednode.serialized_input, indent=4)
    print()


def print_output(state, entry):
    print('  output:')
    if state == State.done:
        outputstring = repr(entry.output())
        printlines_indented(outputstring, indent=4)
    else:
        print('    <task not finished yet>')
    print()


def print_custom_actions(function):
    actions = getattr(function, '_tb_actions', {})
    if actions:
        print('  actions:')
        for action, function in actions.items():
            origin = f'{function.__name__}() ' f'from [{function.__module__}]'
            print(f'    {action}: {origin}')
            if function.__doc__ is not None:
                line = function.__doc__.strip().split('\n')[0]
                print(f'      {line}')
    else:
        print('No custom actions defined for this task.')
    print()


def print_runinfo(worker_name, starttime, endtime, err):
    if starttime is None:
        assert not worker_name
        assert not endtime
        assert not err
        print('Task has no run information')
    else:
        print('Run information:')
        print(f'    Worker name: {worker_name}')
        print(f'    Start time: {starttime}')
        print(f'    End time: {endtime}')
        if endtime is not None and starttime is not None:
            duration = endtime - starttime
        else:
            duration = None
        print(f'    Duration: {duration}')
        print(f'    Error: {err}')
        print()
