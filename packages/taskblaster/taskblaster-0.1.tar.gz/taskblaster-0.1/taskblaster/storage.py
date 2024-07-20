import json
import typing
from abc import ABC, abstractmethod
from pathlib import Path

from taskblaster import GETATTR, GETITEM, JSONCodec, TBUserError
from taskblaster.encoding import decode_object, encode_object
from taskblaster.hashednode import PackedReference


class NullCodec(JSONCodec):
    def decode(self, dct):
        return dct

    def encode(self, obj):
        clsname = type(obj).__name__
        raise TypeError(f'No encoding rule for type {clsname}: {obj}')


class ExtensibleCodec(JSONCodec):
    def __init__(self, usercodec):
        self.usercodec = usercodec

    def encode(self, obj):
        if hasattr(obj, 'tb_encode'):
            return encode_object(obj)
        return self.usercodec.encode(obj)

    def decode(self, dct):
        if '__tb_enc__' in dct:
            return decode_object(dct)
        return self.usercodec.decode(dct)


class JSONProtocol:
    def __init__(self, root, usercodec=None):
        if usercodec is None:
            usercodec = NullCodec()

        self.root = root
        self.codec = ExtensibleCodec(usercodec)

    def serialize_inputs(self, obj: typing.Any, name) -> bytes:
        # The taskblaster caching mechanism uses hashes of serialized objects.
        # This is the function which serializes those things.  We should be
        # quite careful that this doesn't change behaviour.
        #
        # Note that keys are sorted so equal dictionaries will hash equally.

        outputencoder = self.outputencoder(self.root / name)

        return json.dumps(
            obj,
            default=outputencoder.encode_and_pack_references,
            sort_keys=True,
        )

    def load_inputs_without_resolving_references(self, buf, name):
        directory = self.root / name
        outputencoder = self.outputencoder(directory)
        decoder = NodeDecoder(outputencoder.decode)
        name, kwargs = json.loads(buf, object_hook=decoder.decode)
        references = decoder.references
        return name, kwargs, references

    def _actually_load(self, cache, jsontext, directory):
        outputencoder = self.outputencoder(directory)
        unpacker = ReferenceDecoder(outputencoder.decode, cache)
        name, namespace = json.loads(jsontext, object_hook=unpacker.decode)

        # The commented code below decides how we hash an input.
        #  * First we hash the text of the inputfile.
        #
        #  * Then we decode the references inside the inputfile.  When doing
        #    so, the ReferenceDecoder remembers the hashes of all the refs
        #    it sees.  This gives us a {name: digest} mapping for all the refs,
        #
        #  * Then we hash the {name: digest} mapping
        #
        #  * Finally we combine the inputfile hash and the refmap hash,
        #    which is then the full inputhash which will change if any
        #    names or dependency digests should change.
        #
        # This logic is relatively essential so it should probably not
        # be nearly as "buried" as is the case here.

        # digestmap = {
        #    name: digest.long for name, digest in unpacker.name2digest.items()
        # }
        # digestmap_text = json.dumps(digestmap, sort_keys=True)
        # digestmap_digest = mkhash(digestmap_text.encode('ascii'))
        # final_digest = mkhash(
        #    (json_digest + digestmap_digest).encode('ascii'))

        # XXXX refactor
        namespace.pop('__tb_dynamic_parent__', None)
        return name, namespace

    def outputencoder(self, directory):
        return OutputEncoding(self.codec, self.root, directory)


class BaseNodeDecoder(ABC):
    """Helper class to determine dependencies while reading JSON.

    Since dependencies (input "kwargs") can be arbitrarily nested,
    determining the dependencies requires complicated looping and
    type checking.

    This class implements a JSON hook which, whenever it reads a
    dependency, stores it.  That way, the JSON read loop
    takes care of the complicated looping, and we build the
    dependencies as a side effect when loading.

    That is what this class implements.
    """

    def __init__(self, decode):
        self._decode = decode
        self.references = []

    def decode(self, dct):
        if dct.get('__tb_type__') == 'ref':
            name = dct['name']
            index = dct['index']
            ref = self.decode_reference(name, index)
            self.references.append(ref)
            return ref

        return self._decode(dct)

    @abstractmethod
    def decode_reference(self, name, index): ...


class NodeDecoder(BaseNodeDecoder):
    def decode_reference(self, name, index):
        return PackedReference(name, index)


class ReferenceDecoder(BaseNodeDecoder):
    def __init__(self, decode, cache):
        super().__init__(decode)
        self.cache = cache

    def decode_reference(self, name, index):
        entry = self.cache.entry(name)
        if index is None:
            raise RuntimeError('Index is None!')

        value = entry.output()
        assert isinstance(index, list)
        for _type_and_subindex in index:
            if isinstance(_type_and_subindex, (list, tuple)):
                _type, subindex = _type_and_subindex
                if _type == GETITEM:
                    try:
                        value = value[subindex]
                    except Exception as e:
                        raise TBUserError(
                            f'Cannot index {value} with {subindex}: {e}.'
                        ) from None
                elif _type == GETATTR:
                    try:
                        value = getattr(value, subindex)
                    except Exception as e:
                        raise TBUserError(
                            f'{value} does not have an attribute '
                            f'{subindex}: {e}.'
                        ) from None
                else:
                    assert 0
            else:
                try:
                    value = value[_type_and_subindex]
                except Exception as e:
                    raise TBUserError(
                        f'Cannot index {value} with {_type_and_subindex}: {e}.'
                    ) from None

        return value


class OutputEncoding:
    """Helper for passing files between tasks via JSON encoding/decoding.

    We don't want to persistently save absolute paths because they
    become wrong if anything is moved.  But we are okay with saving
    a reference such as "myfile.dat".  When loading the file (and
    for passing result objects to other tasks), the file should then
    be resoved relative to the location of the original task.

    For example suppose we have cachedir/mytask-12345/myfile.dat .

    The task returns Path('myfile.dat') which we serialize as myfile.dat.
    That way if we rename/move cachedir or mytask-12345, the information
    which we stored does not become wrong.

    Only at runtime when we load the resultfile do we evaluate myfile
    inside whatever cachedir it was loaded from – at that point it becomes
    an absolute path.

    Note also how the value of that path will not be used for any hashes
    or equality checks, since we track identity through the dependency graph.
    """

    def __init__(self, codec, root, directory):
        self.codec = codec
        self.root = root
        # XXX get rid of .absolute()
        self.directory = directory.absolute()

    def decode(self, dct):
        tbtype = dct.get('__tb_type__')
        if tbtype is None:
            return self.codec.decode(dct)
        elif tbtype == 'Path':
            return self._decode_path(dct)

        raise RuntimeError(f'bad tbtype={tbtype!r}')

    def encode(self, obj):
        if isinstance(obj, Path):
            return self._encode_path(obj)
        return self.codec.encode(obj)

    def loads(self, jsontext):
        return json.loads(jsontext, object_hook=self.decode)

    def dumps(self, obj):
        # sort keys or not?  For consistency with hashable inputs,
        # we could sort the keys.  But we don't need to, because this
        # is for storing outputs.  We'll sort them.
        return json.dumps(obj, default=self.encode, sort_keys=True)

    def encode_and_pack_references(self, obj, _recursions=[0]):
        # If the encoder also ends up encoding its dependencies'
        # dependencies, then that's bad and we have a problem.
        # This is a little check that'll fail if this is called
        # recursively:
        assert _recursions[0] == 0
        _recursions[0] += 1

        try:
            if hasattr(obj, '_tb_pack'):
                return obj._tb_pack()
        finally:
            _recursions[0] -= 1
        return self.encode(obj)

    def _encode_path(self, path):
        if '..' in path.parts:
            # (Should this be user error?  Let's be nasty about it though)
            raise RuntimeError('Refusing to encode path with ".." in it')

        if path.is_absolute():
            # We only want to encode the part after TB root:
            relpath = path.relative_to(self.root)

            # Use magic string '//' for "absolute" TB paths here:
            path_string = f'//{relpath}'
        else:
            path_string = str(path)
        return {'__tb_type__': 'Path', 'path': path_string}

    def _decode_path(self, dct):
        assert set(dct) == {'__tb_type__', 'path'}
        # Should we require that the path is relative?
        path_string = dct['path']
        if path_string.startswith('//'):
            path = self.root / path_string[2:]
        else:
            path = self.directory / dct['path']

        if '..' in path.parts:
            raise RuntimeError('Refusing to decode dangerous ".." path')

        return path
