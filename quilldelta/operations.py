from collections import namedtuple
from typing import TypeVar, Union


def fromdict(cls, data: dict):
    name = cls.__name__.lower()
    if name in data:
        value = data.pop(name)
        return cls(value, **data)


class Insert(namedtuple('Insert', 'value, attributes')):
    __slots__ = ()

    @classmethod
    def fromdict(cls, data):
        data.setdefault('attributes', None)
        return fromdict(cls, data)

    def _asdict(self):
        return {'insert': self.value, 'attributes': self.attributes}

    @property
    def length(self):
        if isinstance(self.value, str):
            return len(self.value)
        return 1

    def __add__(self, other: TypeVar('Insert')):
        assert type(other) == Insert
        assert self.attributes == other.attributes, 'Can not sum insert operations with different attributes'

        return Insert(self.value + other.value, other.attributes)


class Retain(namedtuple('Retain', 'value, attributes')):
    __slots__ = ()

    @classmethod
    def fromdict(cls, data: dict):
        data.setdefault('attributes', None)
        return fromdict(cls, data)

    def _asdict(self):
        return {'retain': self.value, 'attributes': self.attributes}

    @property
    def length(self):
        return self.value

    def __add__(self, other: TypeVar('Retain')):
        assert type(other) == Retain
        assert self.attributes == other.attributes, 'Can not sum retain operations with different attributes'

        return Retain(self.value + other.value, other.attributes)


class Delete(namedtuple('Delete', 'length')):
    __slots__ = ()

    @classmethod
    def fromdict(cls, data: dict):
        return fromdict(cls, data)

    def _asdict(self):
        return {'delete': self.length}

    def __add__(self, other: TypeVar('Delete')):
        assert type(other) == Delete

        return Delete(self.length + other.length)


OperationType = Union[Insert, Retain, Delete, dict]
