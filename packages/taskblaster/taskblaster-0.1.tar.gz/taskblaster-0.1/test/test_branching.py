from conftest import check_conflict, check_states, tb_run_click

script = """\
from taskblaster.testing import {wf_name} as WF
def workflow(rn):
    for name, atoms in {inputs}:
        rn2 = rn.with_subdirectory(name)
        wf = WF(atoms=(atoms, {msg}))
        rn2.run_workflow(wf)
"""


def write_main_wfs(wf_name, inputs, wf_file='main_wf.py', msg="'input msg'"):
    txt = script.format(wf_name=wf_name, inputs=inputs, msg=msg)
    with open(wf_file, 'w') as fd:
        fd.write(txt)


def test_simple_branching(tool):
    write_main_wfs(
        'RelaxWorkflow', "[('mag_example', 6), ('nonmag_example', 1)]"
    )

    # test basics
    def test_basics():
        tb_run_click('workflow main_wf.py')
        check_states(0, 0, 0, num_new=4)
        tb_run_click('run tree')
        check_states(4, 0, 0)
        tb_run_click('workflow main_wf.py')
        check_states(4, 0, 0, num_new=3)
        tb_run_click('run tree')
        check_states(7, 0, 0)

    test_basics()
    # test unrun all
    tb_run_click('unrun tree --force')
    # Now everything should work as the first time
    test_basics()

    # test unrun
    tb_run_click('unrun tree/nonmag_example/check_magnetic_state --force')
    check_states(4, 0, 0, num_new=1)
    tb_run_click('run tree')
    check_states(5, 0, 0)
    tb_run_click('workflow main_wf.py')
    check_states(5, 0, 0, num_new=2)
    tb_run_click('run tree')
    check_states(7, 0, 0)

    # test conflict
    write_main_wfs(
        'RelaxWorkflow',
        "[('mag_example', 8), ('nonmag_example', 1)]",
        wf_file='main_wf2.py',
    )
    tb_run_click('workflow main_wf2.py')
    check_conflict(1, 0)
    tb_run_click('resolve tree')
    check_conflict(0, 1)
    tb_run_click('unrun tree/mag_example/relax --force')
    check_conflict(0, 0)
    check_states(4, 0, 0, num_new=2)
    tb_run_click('run tree')
    check_states(6, 0, 0)
    tb_run_click('workflow main_wf2.py')
    check_states(6, 0, 0, num_new=1)
    tb_run_click('run tree')
    check_states(7, 0, 0)


def test_loop(tool):
    write_main_wfs('RelaxWorkflowLoop', "[('test3', 3)]")

    # Test a simple loop
    tb_run_click('workflow main_wf.py')
    check_states(0, 0, 0, num_new=3)
    nn = 2
    # Do tb run, tb workflow until no more tasks are generated.
    # I suppose this should be done automatically in the future
    for i in range(3):
        tb_run_click('run tree')
        check_states(3 + 2 * i, 0, 0)
        tb_run_click('workflow main_wf.py')
        if i == 2:
            nn = 1
        check_states(3 + 2 * i, 0, 0, num_new=nn)
    tb_run_click('run tree')
    check_states(8, 0, 0)

    # Test conflict
    write_main_wfs(
        'RelaxWorkflowLoop', "[('test3', 2)]", wf_file='main_wf2.py'
    )
    tb_run_click('workflow main_wf2.py')
    check_conflict(1, 0)
    check_states(8, 0, 0)
    tb_run_click('unrun tree/test3/prepare_atoms --force')

    # Now tasks that were genersated in the loop should have been removed
    # and we should be back at the beginning
    tb_run_click('workflow main_wf2.py')
    check_states(0, 0, 0, num_new=3)

    # Now loop converged after two steps
    tb_run_click('run tree')
    check_states(3, 0, 0)
    tb_run_click('workflow main_wf2.py')
    check_states(3, 0, 0, num_new=2)
    tb_run_click('run tree')
    check_states(5, 0, 0)
    tb_run_click('workflow main_wf2.py')
    check_states(5, 0, 0, num_new=1)
    tb_run_click('run tree')
    check_states(6, 0, 0)


def test_combined(tool):
    """Simple test of combined wf. Should test to unrun etc once
    simple loop passes
    """
    write_main_wfs('CombinedWorkflow', "[('nonmag_example', 6)]")
    # Tasks for first iteration in loop are created
    tb_run_click('workflow main_wf.py')
    check_states(0, 0, 0, num_new=5)
    tb_run_click('run tree --greedy')

    # run tb workflow and tb run until all tasks have been generated
    for i in range(5):
        # Check so that tasks are done
        check_states(3 + 2 * i, 0, 0, num_new=2)

        # Upon running tb workflow again new tasks are generated
        tb_run_click('workflow main_wf.py')
        check_states(3 + 2 * i, 0, 0, num_new=4)
        tb_run_click('run tree --greedy')

    # Check so that tasks are done
    check_states(13, 0, 0, num_new=2)
    # generate new tasks
    tb_run_click('workflow main_wf.py')
    check_states(13, 0, 0, num_new=2)

    tb_run_click('run tree --greedy')
    # Check so that tasks are done
    check_states(15, 0, 0)


def test_cancel_dynamic(tool):
    write_main_wfs('TestWfCancel', "[('test_cancel', 'hi')]")
    tb_run_click('workflow main_wf.py')
    tb_run_click('run tree --greedy')
    tb_run_click('workflow main_wf.py')
    tb_run_click('run tree --greedy')
    check_states(2, 1, 2)
