from pathlib import Path

import pytest

from taskblaster.encoding import dumps, loads
from taskblaster.storage import JSONProtocol


def test_object_not_serializable():
    with pytest.raises(TypeError, match='Cannot encode object'):
        dumps(object())


class MyEncodable:
    def __init__(self, thing):
        self.thing = thing

    def tb_encode(self):
        return self.thing

    @classmethod
    def tb_decode(cls, objdata):
        return cls(objdata)


def test_json_roundtrip():
    obj = MyEncodable([1, 2, 'hello', {'x1': True, 'x2': None}])

    txt = dumps(obj)
    newobj = loads(txt)

    assert newobj.thing == obj.thing


@pytest.mark.parametrize(
    'obj',
    [None, 'hello', 123, [1, 2, 4], {}, {'a': 'b', 'c': 'd'}, True, 1.2345],
)
def test_json_different_builtins(obj):
    assert loads(dumps(obj)) == obj


@pytest.fixture
def outputencoder():
    # (We do not need the path to actually exist.)
    root = Path('/tmp/fictitious_path')
    return JSONProtocol(root).outputencoder(root / 'a/b/c')


def test_encode_samedir(outputencoder):
    assert (
        outputencoder.decode(outputencoder.encode(Path('.')))
        == outputencoder.directory
    )


def test_encode_abspath(outputencoder):
    # Path is inside root but outside encoder's directory.
    path = outputencoder.root / 'somepath'
    assert path.is_absolute()
    assert outputencoder.decode(outputencoder.encode(path)) == path


def test_encode_relpath(outputencoder):
    path = Path('somepath')
    newpath = outputencoder.decode(outputencoder.encode(path))
    assert newpath.is_absolute()
    assert outputencoder.directory / path == newpath


def test_no_doubledot(outputencoder):
    with pytest.raises(RuntimeError):
        outputencoder.encode(Path('hello/..'))
