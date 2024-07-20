import pytest

from taskblaster.repository import Repository


def test_init_module_does_not_exist(testdir):
    with pytest.raises(
        Repository.RepositoryError, match='Specified module .+? must exist'
    ):
        Repository.create(testdir, modulename='taskblaster.does_not_exist')


def test_init_module_missing_initializer(testdir):
    with pytest.raises(
        Repository.RepositoryError,
        match=r'.* does not implement a .+? function or class',
    ):
        Repository.create(testdir, modulename='taskblaster.registry')


def test_init(testdir):
    with Repository.create(testdir) as repo:
        assert len(repo.cache) == 0
        assert repo.cache.registry.index.count() == 0
        assert (testdir / 'tree').is_dir()
        assert (testdir / '.taskblaster/registry.db').is_file()


def test_info_no_repo(testdir):
    with pytest.raises(Repository.RepositoryError, match='No registry found'):
        Repository.find(testdir)


def test_init_twice_error(testdir):
    Repository.create(testdir)
    with pytest.raises(Repository.RepositoryError):
        Repository.create(testdir)


def test_info(repo):
    lines = repo.info()
    # (Can we actually test something meaningful about this?)
    assert lines[0].startswith('Module:')


def test_find_root_from_root(testdir):
    repo = Repository.create(testdir)
    repo1 = Repository.find(repo.root)
    assert repo1.root == repo.root


def test_find_root_from_inside_subdir(testdir):
    repo = Repository.create(testdir)
    subdir = testdir / 'subdir/othersubdir'
    subdir.mkdir(parents=True)
    repo1 = Repository.find(subdir)
    assert repo1.root == repo.root
