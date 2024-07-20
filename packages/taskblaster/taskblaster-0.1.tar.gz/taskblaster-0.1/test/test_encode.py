class Encodeable:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def tb_encode(self):
        return self.kwargs

    @classmethod
    def tb_decode(cls, dct):
        return cls(**dct)

    def __repr__(self):
        return f'Encodeable({self.kwargs})'


def test_encode_path(repo, tmp_path):
    cache = repo.cache

    protocol = cache.json_protocol

    path = repo.tree_path / 'somepath'
    nodeinput = ['dummytarget', {'obj': Encodeable(path=path)}]

    json_text = protocol.serialize_inputs(nodeinput, 'somename')

    loaded_input = protocol._actually_load(
        cache, json_text, directory=repo.root / 'xxx'
    )

    assert loaded_input[0] == 'dummytarget'
    assert loaded_input[1]['obj'].kwargs['path'] == path
