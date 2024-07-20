def test_read_empty_resources(repo):
    resources = repo.get_resources()
    assert resources == {}


sample_resources = {
    'worker0': {
        'tags': ['potato', 'onion'],
        'required_tags': {'eggs'},
        'resources': '42:helloworld:1h',
    },
}


def test_read_resources(repo):
    path = repo.root / repo._resource_filename
    path.write_text(f'resources = {sample_resources!r}\n')
    resources = repo.get_resources()
    worker = resources['worker0']
    assert worker.name == 'worker0'
    assert worker.tags == {'potato', 'onion'}
    assert worker.required_tags == {'eggs'}
    assert worker.resources == '42:helloworld:1h'
