import taskblaster as tb


def relax(atoms):
    atoms, _ = atoms
    return atoms - 1, 'original relax'


def check_magnetic_state(atoms):
    atoms, msg = atoms
    return atoms > 3


def relax_non_magnetic(atoms):
    atoms, msg = atoms
    return atoms - 2, 'non_magnetic'


def post_process(tasks):
    print(tasks)
    return tasks


def check_converged(atoms):
    atoms, msg = atoms
    return atoms <= 0


def post_process_atoms(atoms):
    return atoms


def fail(msg):
    raise ValueError(msg)


def ok(msg):
    return msg


def collect(tasks):
    print(tasks)
    return tasks


def conditional_ok(msg, fail_cond='1'):
    if fail_cond in msg:
        raise ValueError(f'{fail_cond} in msg')
    return msg


def mysum(msg1, msg2):
    return msg1 + msg2


def check_value(value, expected_value):
    assert value == expected_value
    return value


def is_true(inp):
    return True


@tb.workflow
class Workflow:
    msg = tb.var()

    @tb.task
    def ok(self):
        return tb.node('taskblaster.testing.ok', msg=self.msg)

    @tb.task
    def dependsonok(self):
        return tb.node('taskblaster.testing.ok', msg=self.ok)

    @tb.task
    def fail(self):
        return tb.node('taskblaster.testing.fail', msg=self.msg)

    @tb.task
    def dependsonfail(self):
        return tb.node('sleep', msg=self.fail)


@tb.workflow
class CompositeWorkflow:
    msg = tb.var()

    @tb.task
    def hello(self):
        return tb.node('taskblaster.testing.ok', msg=self.msg)

    @tb.subworkflow
    def subworkflow(self):
        return Workflow(msg=self.msg)

    @tb.subworkflow
    def subworkflow2(self):
        return Workflow(msg=self.hello)

    @tb.subworkflow
    def subworkflow3(self):
        return Workflow(msg=self.subworkflow.ok)


@tb.dynamical_workflow_generator_task
def generate_wfs_from_list(inputs):
    for i, inp in enumerate(inputs):
        wf = CompositeWorkflow(msg=inp)
        name = str(i)
        yield name, wf


@tb.dynamical_workflow_generator_task
def generate_wfs_from_list_complex(msg, fail_cond1, fail_cond2):
    for i, inp in enumerate(msg):
        wf = ComplexWorkflow(
            msg=inp, fail_cond1=fail_cond1, fail_cond2=fail_cond2
        )
        name = str(i)
        yield name, wf


@tb.workflow
class GeneratedWorkflow:
    inputs = tb.var()  # list of input vars

    @tb.dynamical_workflow_generator({'results': '*/hello'})
    def generate_wfs_from_list(self):
        return tb.node(
            'taskblaster.testing.generate_wfs_from_list', inputs=self.inputs
        )

    @tb.task
    def depends_on_generate(self):
        return tb.node('collect', tasks=self.generate_wfs_from_list.results)


@tb.workflow
class WorkflowB:
    msg = tb.var()
    fail_cond = tb.var()

    @tb.task
    def ok(self):
        return tb.node('taskblaster.testing.ok', msg=self.msg)

    @tb.task
    def cond_ok(self):
        return tb.node(
            'taskblaster.testing.conditional_ok',
            msg=self.ok,
            fail_cond=self.fail_cond,
        )


@tb.workflow
class ComplexWorkflow:
    msg = tb.var()
    fail_cond1 = tb.var()
    fail_cond2 = tb.var()

    @tb.task
    def ok(self):
        return tb.node('taskblaster.testing.ok', msg=self.msg)

    @tb.task
    def cond_ok(self):
        return tb.node(
            'taskblaster.testing.conditional_ok',
            msg=self.ok,
            fail_cond=self.fail_cond1,
        )

    @tb.subworkflow
    def subworkflowA(self):
        return WorkflowB(msg=self.cond_ok, fail_cond=self.fail_cond2)

    @tb.task
    def depend_on_A(self):
        return tb.node(
            'taskblaster.testing.mysum',
            msg1=self.subworkflowA.ok,
            msg2=self.subworkflowA.cond_ok,
        )

    @tb.task
    def depend_on_A_ok(self):
        return tb.node('taskblaster.testing.ok', msg=self.subworkflowA.ok)


@tb.workflow
class GeneratedComplexWorkflow:
    msg = tb.var()  # list of input vars
    fail_cond1 = tb.var()
    fail_cond2 = tb.var()

    @tb.task
    def ok(self):
        return tb.node('taskblaster.testing.ok', msg=self.fail_cond1)

    @tb.task
    def cond_ok(self):
        return tb.node(
            'taskblaster.testing.conditional_ok',
            msg=self.fail_cond2,
            fail_cond=self.fail_cond1,
        )

    @tb.dynamical_workflow_generator(
        {'ok': '*/ok', 'result0': '0/depend_on_A_ok', 'all': '**'}
    )
    def generate_wfs_from_list(self):
        return tb.node(
            'taskblaster.testing.generate_wfs_from_list_complex',
            msg=self.msg,
            fail_cond1=self.ok,
            fail_cond2=self.cond_ok,
        )

    @tb.task
    def depends_on_all(self):
        return tb.node(
            'taskblaster.testing.collect',
            tasks=self.generate_wfs_from_list.all,
        )

    @tb.task
    def depends_on_result0(self):
        return tb.node(
            'taskblaster.testing.collect',
            tasks=self.generate_wfs_from_list.result0,
        )

    @tb.task
    def depends_on_ok(self):
        return tb.node(
            'taskblaster.testing.collect', tasks=self.generate_wfs_from_list.ok
        )


@tb.workflow
class GeneratedWrongWorkflow:
    msg = tb.var()  # list of input vars
    fail_cond1 = tb.var()
    fail_cond2 = tb.var()

    @tb.dynamical_workflow_generator({'nonexisting': '*/doesnotexist'})
    def generate_wfs_from_list(self):
        return tb.node(
            'taskblaster.testing.generate_wfs_from_list_complex',
            msg=self.msg,
            fail_cond1='1',
            fail_cond2='2',
        )

    @tb.task
    def depends_on_nonexisting(self):
        return tb.node(
            'taskblaster.testing.check_value',
            value=self.generate_wfs_from_list.nonexisting,
            expected_value={},
        )


@tb.dynamical_workflow_generator_task
def generate_wfs_task(msg, fail_cond1, fail_cond2):
    for i, inp in enumerate(msg):
        wf = ComplexWorkflow(
            msg=inp, fail_cond1=fail_cond1, fail_cond2=fail_cond2
        )
        name = str(i)
        yield name, wf


@tb.workflow
class DynamicalGeneratedComplexWorkflow:
    msg = tb.var()  # list of input vars
    fail_cond1 = tb.var()
    fail_cond2 = tb.var()

    @tb.task
    def gen_input(self):
        return tb.node('taskblaster.testing.ok', msg=self.msg)

    @tb.task
    def ok(self):
        return tb.node('taskblaster.testing.ok', msg=self.fail_cond1)

    @tb.task
    def cond_ok(self):
        return tb.node(
            'taskblaster.testing.conditional_ok',
            msg=self.fail_cond2,
            fail_cond=self.fail_cond1,
        )

    @tb.dynamical_workflow_generator(
        {'ok': '*/ok', 'result0': '0/depend_on_A_ok', 'all': '**'}
    )
    def generate_wfs_from_list(self):
        return tb.node(
            'taskblaster.testing.generate_wfs_task',
            msg=self.gen_input,
            fail_cond1=self.fail_cond1,
            fail_cond2=self.fail_cond2,
        )

    @tb.task
    def depends_on_all(self):
        return tb.node(
            'taskblaster.testing.collect',
            tasks=self.generate_wfs_from_list.all,
        )

    @tb.task
    def depends_on_result0(self):
        return tb.node(
            'taskblaster.testing.collect',
            tasks=self.generate_wfs_from_list.result0,
        )

    @tb.task
    def depends_on_ok(self):
        return tb.node(
            'taskblaster.testing.collect', tasks=self.generate_wfs_from_list.ok
        )


def workflow(rn):
    for i in range(2):
        msg = f'hello {i}'
        rn.with_subdirectory(str(i)).run_workflow(Workflow(msg=msg))


@tb.workflow
class RelaxWorkflow:
    atoms = tb.var()

    @tb.task
    def relax(self):
        return tb.node('taskblaster.testing.relax', atoms=self.atoms)

    @tb._if(true='final', false='non_mag')
    @tb.task
    def check_magnetic_state(self):
        return tb.node(
            'taskblaster.testing.check_magnetic_state', atoms=self.relax
        )

    @tb.branch('non_mag')
    @tb.jump('final')
    @tb.task
    def relax_non_magnetic(self):
        return tb.node(
            'taskblaster.testing.relax_non_magnetic', atoms=self.relax
        )

    @tb.branch('final')
    # @tb.jump('entry')
    @tb.task
    def finalizer(self):
        return tb.node(
            'taskblaster.testing.post_process_atoms',
            atoms=tb.Phi(non_mag=self.relax_non_magnetic, entry=self.relax),
        )


@tb.workflow
class RelaxWorkflowLoop:
    atoms = tb.var()

    @tb.branch('entry')
    @tb.jump('relax')
    @tb.task
    def prepare_atoms(self):
        return tb.node('define', obj=self.atoms)

    @tb.branch('relax', loop=True)
    @tb.task
    def relax(self):
        return tb.node(
            'taskblaster.testing.relax',
            atoms=tb.Phi(entry=self.prepare_atoms, relax=self.relax),
        )

    @tb.branch('relax', loop=True)
    @tb._if(true='final', false='relax')
    @tb.task
    def check_converged(self):
        return tb.node('taskblaster.testing.check_converged', atoms=self.relax)

    @tb.branch('final')
    @tb.task
    def finalize(self):
        return tb.node(
            'taskblaster.testing.post_process_atoms', atoms=self.relax
        )


@tb.workflow
class RelaxWorkflowExternal:
    atoms = tb.var()

    @tb.branch('entry')
    @tb.jump('relax')
    @tb.task
    def prepare_atoms(self):
        return tb.node('define', obj=self.atoms)

    @tb.branch('relax', loop=True)
    @tb.task
    def relax(self):
        return tb.node(
            'taskblaster.testing.relax',
            atoms=tb.Phi(entry=self.prepare_atoms, relax=self.relax),
        )

    @tb.branch('relax', loop=True)
    @tb._if(true='final', false='relax')
    @tb.task
    def check_converged(self):
        return tb.node('taskblaster.testing.check_converged', atoms=self.relax)

    @tb.branch('final')
    @tb.fixedpoint  # External tasks can depend on this
    @tb.task
    def converged(self):
        return tb.node(
            'taskblaster.testing.post_process_atoms', atoms=self.relax
        )


@tb.workflow
class PassPaths:
    @tb.define
    def a(self):
        from pathlib import Path

        return Path('a.b')

    @tb.define
    def b(self):
        return self.a


@tb.workflow
class CombinedWorkflow:
    atoms = tb.var()

    @tb.subworkflow
    def relax(self):
        return RelaxWorkflowExternal(atoms=self.atoms)

    @tb._if(true='final', false='non_mag')
    @tb.task
    def check_magnetic_state(self):
        return tb.node(
            'taskblaster.testing.check_magnetic_state',
            atoms=self.relax.converged,
        )

    @tb.branch('non_mag')
    @tb.jump('final')
    @tb.task
    def relax_non_magnetic(self):
        return tb.node(
            'taskblaster.testing.relax_non_magnetic',
            atoms=self.relax.converged,
        )

    @tb.branch('final')
    # @tb.jump('entry')
    @tb.task
    def postprocess(self):
        return tb.node(
            'taskblaster.testing.post_process_atoms',
            atoms=tb.Phi(
                non_mag=self.relax_non_magnetic, entry=self.relax.converged
            ),
        )


@tb.workflow
class SubWorkflow:
    inp = tb.var()
    inp2 = tb.var()

    @tb.branch('entry')
    @tb._if(true='b1', false='b2')
    @tb.task
    def is_true(self):
        return tb.node('taskblaster.testing.is_true', inp=self.inp2)

    @tb.branch('b1')
    @tb.jump('external')
    @tb.task
    def one(self):
        return tb.node('taskblaster.testing.ok', msg=self.inp)

    @tb.branch('b2')
    @tb.jump('external')
    @tb.task
    def two(self):
        return tb.node('taskblaster.testing.ok', msg=self.inp)

    @tb.fixedpoint
    @tb.branch('external')
    @tb.task
    def results(self):
        return tb.node(
            'taskblaster.testing.ok', msg=tb.Phi(b1=self.one, b2=self.two)
        )


@tb.workflow
class TestWfCancel:
    atoms = tb.var()

    @tb.task
    def fail(self):
        return tb.node('taskblaster.testing.fail', msg=self.atoms)

    @tb.task
    def passed(self):
        return tb.node('taskblaster.testing.ok', msg=self.atoms)

    @tb.subworkflow
    def sw1(self):
        return SubWorkflow(inp=self.fail, inp2=self.passed)
