import pytest

from taskblaster.parallel import ParallelizationError, choose_subworkers


@pytest.mark.parametrize(
    'size, subsize, subcount, refsize',
    [
        [6, 2, 3, 2],
        [6, 2, None, 2],
        [6, None, 2, 3],
        [6, None, None, 6],
    ],
)
def test_choose_subworkers(size, subsize, subcount, refsize):
    subsize, subcount = choose_subworkers(size, subsize, subcount)
    assert subsize * subcount == size
    assert refsize == subsize


@pytest.mark.parametrize(
    'size, subsize, subcount',
    [
        [6, 3, 3],
        [6, 4, None],
        [6, None, 4],
        [6, 1, 1],
    ],
)
def test_bad_parallelization(size, subsize, subcount):
    with pytest.raises(ParallelizationError):
        choose_subworkers(size, subsize, subcount)
