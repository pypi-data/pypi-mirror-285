import pytest
from conftest import (
    check_conflict,
    check_states,
    return_cli_output_as_lines,
    tb_run_click,
)

from taskblaster.state import State

script = """\
from taskblaster.testing import {wf_name} as WF
def workflow(rn):
    msgs={msgs}
    for i, msg in enumerate(msgs):
        rn2 = rn.with_subdirectory(str(i))
        wf = WF(msg=msg, fail_cond1='{fail_cond1}', fail_cond2='{fail_cond2}')
        rn2.run_workflow(wf)
"""


def write_main_wfs(
    wf_name, msgs, wf_file='main_wf.py', fail_cond1='1', fail_cond2='2'
):
    txt = script.format(
        wf_name=wf_name,
        fail_cond1=fail_cond1,
        fail_cond2=fail_cond2,
        msgs=msgs,
    )
    with open(wf_file, 'w') as fd:
        fd.write(txt)


def test_run_all(simplerepo):
    with simplerepo:
        stats0 = simplerepo.tree().stat()

    ntasks = stats0.ntasks

    assert stats0.counts[State.new] == ntasks

    simplerepo.run_all_tasks()

    with simplerepo:
        stats = simplerepo.tree().stat()
    assert stats.ntasks == ntasks

    print(stats)

    end_states = [State.done, State.fail, State.cancel]

    for state in end_states:
        assert stats.counts[state] > 0

    assert sum(stats.counts[state] for state in end_states) == ntasks


def test_view(simplerepo):
    simplerepo.run_all_tasks()

    with simplerepo:
        simplerepo.view(['tree'])


def test_realistic_wf(unlockedrepo):
    write_main_wfs('ComplexWorkflow', ['hi0', 'hi1', 'hi2'])
    tb_run_click('workflow main_wf.py')
    tb_run_click('run tree')
    lines = return_cli_output_as_lines('ls --parents -cs')

    # Detailed verification of output
    def check_orig_output(lines, branches=(1, 2, 3)):
        # Remove extra lines for failed tasks
        for line in lines:
            if '^^^' in line:
                lines.remove(line)
        if 1 in branches:
            for line in lines[2:8]:
                assert line.strip() == 'done'
        if 2 in branches:
            s2 = 8
            assert lines[s2].strip() == 'done'
            assert lines[s2 + 1].strip() == 'fail'
            # assert 'ValueError' in lines[s2+2]
            for line in lines[s2 + 2 : s2 + 6]:
                assert line.strip() == 'cancel'
        if 3 in branches:
            s3 = 14
            for line in lines[s3 : s3 + 3]:
                assert line.strip() == 'done'
            assert lines[s3 + 3].strip() == 'fail'
            assert lines[s3 + 4].strip() == 'cancel'
            assert lines[s3 + 5].strip() == 'done'

    check_orig_output(lines)

    # Make conflict
    write_main_wfs(
        'ComplexWorkflow', ['hi0', 'hi3', 'hi2'], wf_file='main_wf2.py'
    )
    tb_run_click('workflow main_wf2.py')

    # Check so that states have not changed
    lines = return_cli_output_as_lines('ls --parents -cs')
    check_orig_output(lines)

    # Check so that conflict is correct
    lines = return_cli_output_as_lines('ls --parents -cc')
    for i, line in enumerate(lines[2:]):
        if i == 6:
            assert line.strip() == 'conflict'
        else:
            assert 'conflict' not in line.strip()

    # Check so that conflict can be resolved
    tb_run_click('resolve tree')
    lines = return_cli_output_as_lines('ls --parents -cc')
    assert lines[8].strip() == 'resolved'

    # Check so that conflict is removed if orig wf is run
    tb_run_click('workflow main_wf.py')
    lines = return_cli_output_as_lines('ls --parents -cc')
    for line in lines[2:]:
        assert 'conflict' not in line
        assert 'resolved' not in line

    # unrun failed task and check so that descendents
    # are updated correctly
    tb_run_click('unrun tree/1/cond_ok --force')
    lines = return_cli_output_as_lines('ls --parents -cs')
    for line in lines[6:13]:
        assert 'cancel' not in line

    # Check so that other branches are unchanged
    check_orig_output(lines, branches=[1, 3])

    # do tb workflow with new input that will not crash
    write_main_wfs(
        'ComplexWorkflow', ['hi0', 'hi0', 'hi0'], wf_file='main_wf3.py'
    )
    tb_run_click('workflow main_wf3.py')

    # unrun all conflicts
    lines = return_cli_output_as_lines('ls -ccf')
    num_conflicts = 0
    for line in lines[2:]:
        line = line.split()
        if len(line) == 0:
            continue
        if line[0] == 'conflict':
            num_conflicts += 1
            folder = line[1]
            return_cli_output_as_lines(f'unrun --force {folder}')
    assert num_conflicts == 2

    # check so that all conflicts and also failures have been removed
    lines = return_cli_output_as_lines('ls -cscf --parents')
    for line in lines[2:]:
        assert 'conflict' not in line
        assert 'fail' not in line

    tb_run_click('workflow main_wf3.py')  # update inputs
    tb_run_click('run tree')
    lines = return_cli_output_as_lines('ls -cs')
    for line in lines[2:]:
        if len(line) == 0:
            continue
        assert line.strip() == 'done'


@pytest.mark.parametrize(
    'wf', ['DynamicalGeneratedComplexWorkflow', 'GeneratedComplexWorkflow']
)
def test_realistic_wf_generator(unlockedrepo, wf):
    """Tests both dynamical and statically generated workflow
    A dynamical generated wf will have two extra tasks (thus 2)
    """

    # Different number of tasks in diffent wfs
    if 'Dynamical' in wf:
        dynamical = 1
    else:
        dynamical = 0

    write_main_wfs(wf, [['hi0', 'hi1']])
    tb_run_click('workflow main_wf.py')
    tb_run_click('run tree')
    # Check states
    check_states(14 + dynamical, 1, 6)
    write_main_wfs(wf, [['hi0', 'hi3']], wf_file='main_wf2.py', fail_cond1='5')
    tb_run_click('workflow main_wf2.py')

    # States should not have changed
    check_states(14 + dynamical, 1, 6)

    # Check conflict state
    # check_conflict(6, 0)
    # XXX I do not think this behavoiur is entirely correct
    # Currently the init task of the dynamical workflow is set to
    # conflict, but unrunning the init does not unrun the tasks that
    # actually had a conflict.
    # I have made a seperate test that fails for this and will update
    # this test once we have decided what should happen
    check_conflict(3 + dynamical, 0)
    tb_run_click('resolve tree')

    # Check conflict state updated to resolved
    # check_conflict(0, 6)
    # TEST
    check_conflict(0, 3 + dynamical)
    tb_run_click('unrun --force tree/0/generate_wfs_from_list/1/cond_ok')

    # Check so that states were properly unrun
    check_states(14 + dynamical, 0, 0, num_new=7)

    tb_run_click('run tree')

    # check so that there is still failures
    # due to resolved conflict
    check_states(14 + dynamical, 1, 6)

    # unrun tree and rerun
    tb_run_click('unrun tree --force')
    tb_run_click('workflow main_wf2.py')
    tb_run_click('run tree')

    # Check so that all tasks are done
    check_states(21 + dynamical, 0, 0)


def test_wf_generator_depend_on_nonexisting_task(unlockedrepo):
    write_main_wfs('GeneratedWrongWorkflow', [['hi0', 'hi1']])
    tb_run_click('workflow main_wf.py')
    tb_run_click('run tree')
    lines = return_cli_output_as_lines('ls -cs tree/0/depends_on_nonexisting')[
        2:
    ]
    assert lines[0] == 'done'


@pytest.fixture
def preparedrepo(unlockedrepo):
    """Test so that tb unrun tree marks all tasks of dynamical
    wf as new"""
    wf = 'DynamicalGeneratedComplexWorkflow'
    write_main_wfs(wf, [['hi0', 'hi1']])
    tb_run_click('workflow main_wf.py')
    tb_run_click('run tree')
    write_main_wfs(wf, [['hi0', 'hi3']], wf_file='main_wf2.py', fail_cond1='5')
    tb_run_click('workflow main_wf2.py')


def test_unrun_all(preparedrepo):
    tb_run_click('unrun tree --force')
    check_states(0, 0, 0, num_new=22)


def test_unrun_init(unlockedrepo):
    """Test so that tb unrun task that generates the input to
    dynamical workflow, unruns all task of the dynamical workflow
    and all tasks that depend on the dynamical wf"""
    wf = 'DynamicalGeneratedComplexWorkflow'
    write_main_wfs(wf, [['hi0', 'hi1']])
    tb_run_click('workflow main_wf.py')
    tb_run_click('run tree')

    # Unrun task that wf generator depends on
    tb_run_click('unrun tree/0/gen_input --force')
    check_states(2, 0, 0, num_new=20)

    # Unrun wf generator init task
    tb_run_click('run tree')
    tb_run_click('unrun tree/0/generate_wfs_from_list/init --force')
    check_states(3, 0, 0, num_new=19)
