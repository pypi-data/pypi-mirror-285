import hashlib
from copy import deepcopy
from typing import Any, Dict, Optional, Sequence


def mkhash(buf: bytes) -> str:
    return hashlib.sha256(buf).hexdigest()


class PackedReference:
    def __init__(self, name: str, index: Any):
        assert isinstance(name, str)
        self.name = name
        if index is not None:
            index = list(index)
        self.index = index

    def _tb_pack(self):
        return {'__tb_type__': 'ref', 'name': self.name, 'index': self.index}

    def __repr__(self):
        index = self.index

        indextext = None
        if index is None:
            indextext = ' (record)'
        else:
            indextext = ''.join([f'[{i!r}]' for i in index])
        return f'‹{self.name}›{indextext}'


class Node:
    def __init__(
        self,
        target: str,
        dct: Dict[str, Any],
        buf,
        name,
        refs,
        dynamic_parent: Optional[str] = None,
        dynamic_deps_parent: Optional[str] = None,
    ):
        self._target = target
        self._dct = dict(dct)
        self._buf = buf
        self._name = name
        self._refs = refs
        parent_names = set(ref.name for ref in self._refs)
        if dynamic_parent is not None:
            parent_names.add(dynamic_parent)
        self._parents = tuple(sorted(parent_names))

        self._dynamic_parent = dynamic_parent

    def keywords(self) -> Dict[str, Any]:
        return deepcopy(self._dct)

    @property
    def serialized_input(self):
        return self._buf

    @classmethod
    def new(cls, json_protocol, target, dct, name, dynamic_parent=None):
        # The input dictionary contains Futures, References etc., which
        # have a reference to the cache and hence cannot be directly
        # serialized.
        #
        # We want to obtain those as "packed" quantities that can
        # be serialized.  We serialize them using a hook which packs them
        # (thus delegating to JSON the responsibility of object tree
        #  traversal) and then we load them again, at which point
        # the inter-task dependencies are "packed" as data.
        inputs = [target, dct]
        if dynamic_parent is not None:
            dct['__tb_dynamic_parent__'] = dynamic_parent
        buf = json_protocol.serialize_inputs(inputs, name)
        return cls.fromdata(json_protocol, buf, name)

    @property
    def parents(self) -> Sequence[str]:
        return self._parents

    @classmethod
    def fromdata(cls, json_protocol, buf, name, dynamic_parent=None) -> 'Node':
        (
            target,
            kwargs,
            refs,
        ) = json_protocol.load_inputs_without_resolving_references(buf, name)
        dynamic_parent = kwargs.pop('__tb_dynamic_parent__', None)  # XXXX
        node = Node(
            target=target,
            dct=kwargs,
            buf=buf,
            name=name,
            refs=refs,
            dynamic_parent=dynamic_parent,
        )
        assert node._buf == buf
        return node

    @property
    def target(self) -> str:
        return self._target

    @property
    def name(self) -> str:
        return self._name

    def describe(self) -> str:
        lines = [
            f'{self.target}',
            f'{set(self._dct)}',
        ]

        return '\n'.join(lines)

    def __repr__(self) -> str:
        parts = [self.target, f'{self._dct}']
        content = ', '.join(parts)
        return f'Node({content})'

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, obj) -> bool:
        return self._buf == getattr(obj, '_buf', None)

    def __neq__(self, obj) -> bool:
        return not (self == obj)

    def input_repr(self, maxlen=8):
        nodevars = []
        for name, value in self._dct.items():
            valuetext = f'{value!r}'
            if maxlen is not None and len(valuetext) > maxlen:
                valuetext = '…'
            vartext = f'{name}={valuetext}'
            nodevars.append(vartext)

        input_text = '{target}({args})'.format(
            target=self.target, args=', '.join(nodevars)
        )

        return input_text
