import importlib
import json

from taskblaster import TBUserError


def class_fullname(cls):
    return f'{cls.__module__}.{cls.__name__}'


def import_class(fullname):
    modname, classname = fullname.rsplit('.', 1)

    module = importlib.import_module(modname)
    cls = getattr(module, classname)

    if not hasattr(cls, 'tb_decode'):
        raise TypeError(f'Class {cls.__name__} does not implement tb_decode()')
    return cls


def encode_object(obj):
    if not hasattr(obj, 'tb_encode'):
        raise TypeError(
            f'Cannot encode object of type {obj.__class__} '
            'which does not implement tb_encode()'
        )

    fullname = class_fullname(type(obj))
    objdata = obj.tb_encode()
    return {'__tb_enc__': [fullname, objdata]}


def decode_object(dct):
    if '__tb_enc__' not in dct:
        return dct

    assert len(dct) == 1, list(dct)
    fullname, objdata = dct['__tb_enc__']

    if fullname.startswith('<'):
        raise TBUserError(
            'Cannot serializable classes defined in with temporary '
            f'package {fullname}. Define and import the class from a package.'
        )
    cls = import_class(fullname)
    obj = cls.tb_decode(objdata)
    # Should non-class factory functions be allowed in this role?
    # assert isinstance(obj, cls)
    return obj


def dumps(obj):
    return json.dumps(obj, default=encode_object)


def loads(string):
    return json.loads(string, object_hook=decode_object)
