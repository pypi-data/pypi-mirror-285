import collections

import click
from conftest import check_states, tb_run_click

import taskblaster as tb
from taskblaster.testing import CompositeWorkflow


@tb.dynamical_workflow_generator_task
def thetask(inputs):
    for i, inp in enumerate(inputs):
        wf = CompositeWorkflow(msg=inp)
        name = 'muforloop' + str(i)
        yield name, wf


@tb.dynamical_workflow_generator_task
def dependingtask(inputs):
    inp = inputs
    for i in range(3):
        wf = CompositeWorkflow(msg=inp)
        name = 'loop' + str(i)
        yield name, wf
        inp = wf.hello


@tb.dynamical_workflow_generator_task
def nestedtask(inputs):
    for i, inp in enumerate(inputs):
        wf = GeneratedWorkflow(inputs=inp)
        name = 'mainloop' + str(i)
        yield name, wf


@tb.workflow
class GeneratedWorkflow:
    inputs = tb.var()  # list of input vars

    @tb.dynamical_workflow_generator({'results': '*/hello'})
    def generate_wfs_from_list(self):
        return tb.node('test_workflow_generator.thetask', inputs=self.inputs)

    @tb.task
    def depends_on_generate(self):
        return tb.node(
            'taskblaster.testing.post_process',
            tasks=self.generate_wfs_from_list.results,
        )


@tb.workflow
class NestedGeneratedWorkflow:
    inputs = tb.var()

    @tb.dynamical_workflow_generator({'results': '**'})
    def generate_nested_wfs_from_list(self):
        return tb.node(
            'test_workflow_generator.nestedtask', inputs=self.inputs
        )


@tb.workflow
class DependingGeneratedWorkflow:
    inputs = tb.var()

    @tb.dynamical_workflow_generator({'results': '**'})
    def generate_depending_wfs_from_list(self):
        return tb.node(
            'test_workflow_generator.dependingtask', inputs=self.inputs
        )


def test_depending_workflow_generator(tool):
    wf = DependingGeneratedWorkflow(inputs='A')
    # add the workflow to the tree
    repo = tool.repo
    rn = repo.runner()
    with repo:
        rn.run_workflow(wf)
    tb_run_click('run tree')
    check_states(22, 9, 10)


def test_nested_workflow_generator(tool):
    wf = NestedGeneratedWorkflow(inputs=[['A', 'B', 'C'], ['A', 'B', 'C']])
    # add the workflow to the tree
    repo = tool.repo
    rn = repo.runner()
    with repo:
        rn.run_workflow(wf)
    tb_run_click('run tree')
    check_states(50, 18, 18)


def test_workflow_generator(tool):
    wf = GeneratedWorkflow(inputs=['inputA', 'inputB', 'inputC'])

    # add the workflow to the tree
    repo = tool.repo
    rn = repo.runner()
    with repo:
        rn.run_workflow(wf)

    # submit the tasks added by the workflow
    tb_submit = 'submit tree/'
    result_submit = tb_run_click(tb_submit)

    # we check that generator tasks are added to the tree properly
    lines = output_by_lines(result_submit.output)

    assert lines[-1].strip() == 'Submitted 3 tasks'

    # run the tasks added by the workflow
    tb_run = 'run tree/'
    _ = tb_run_click(tb_run)
    print(_, _.output)

    # CHECK FAILURES: tb ls the tasks ran by the workflow
    tb_ls_f = 'ls -sF'
    result_f = tb_run_click(tb_ls_f)

    lines = output_by_lines(result_f.output)
    error_msg = [
        line.split('^^^^')[-1].strip()
        for line in lines
        if line.startswith('^^^^')
    ]
    counter = collections.Counter(error_msg)
    known_error_msg = [f'ValueError: input{ch}' for ch in ['A', 'B', 'C']]
    fail = len([line.split()[0] for line in lines if line.startswith('fail')])
    f_task = len(
        [
            line.split()[-1]
            for line in lines
            if line.startswith('fail') and line.endswith('fail')
        ]
    )
    print('\n'.join(lines))
    assert len(lines) - 2 == 18  # 9 failures, 9 failure strings, 2 header
    assert len(error_msg) == fail == f_task == 9  # we have 9 failed tasks
    assert all(i == 3 for i in counter.values())  # each failure occurs 3
    # times/input
    assert all(a == b for a, b in zip(counter.keys(), known_error_msg))

    # CHECK DONE
    tb_ls_d = 'ls -sd'
    result_d = tb_run_click(tb_ls_d)

    lines = output_by_lines(result_d.output)
    done = [line.split() for line in lines if line.startswith('done')]
    assert len(lines) == len(done) + 2 == 26  # done tasks + 2 lines of header

    # CHECK CANCELLED
    tb_ls_c = 'ls -sC'
    result_c = tb_run_click(tb_ls_c)

    lines = output_by_lines(result_c.output)
    cancel = [line.split() for line in lines if line.startswith('cancel')]
    assert len(lines) == len(cancel) + 2 == 11


def output_by_lines(output: str):
    return [
        line.strip()
        for line in click.unstyle(output).split('\n')
        if line.strip()
    ]
