import json
from collections import namedtuple


def as_json(instance):
    return json.dumps(instance.as_data())


def sum_operation(instance, other):
    type_op = type(instance)
    type_other = type(other)

    if type(other) != type_op:
        raise ValueError(f'Operations are not from the same type {type_op.__name__} != {type_other}')

    if hasattr(instance, 'attributes'):
        if instance.attributes != other.attributes:
            raise ValueError('Can not add operations with different attributes')

        return type_op(instance.value + other.value, other.attributes)
    else:
        return type_op(instance.value + other.value)


def as_data(instance):
    name = type(instance).__name__.lower()
    data = instance._asdict()
    value = data.pop('value')
    return {name: value, **{k: v for k, v in data.items() if v}}


def fromdict(cls, data: dict):
    name = cls.__name__.lower()

    if name in data:
        value = data.pop(name)
        return cls(value, **data)


class Insert(namedtuple('Insert', 'value, attributes')):
    __slots__ = ()
    __str__ = as_json
    __add__ = sum_operation
    as_data = as_data
    as_json = as_json

    @classmethod
    def fromdict(cls, data):
        data.setdefault('attributes', None)
        return fromdict(cls, data)

    @property
    def length(self):
        if isinstance(self.value, str):
            return len(self.value)
        return 1


class Retain(namedtuple('Retain', 'value, attributes')):
    __slots__ = ()
    __str__ = as_json
    __add__ = sum_operation
    as_data = as_data
    as_json = as_json

    @classmethod
    def fromdict(cls, data: dict):
        data.setdefault('attributes', None)
        return fromdict(cls, data)

    @property
    def length(self):
        return self.value


class Delete(namedtuple('Delete', 'value')):
    __slots__ = ()
    __str__ = as_json
    __add__ = sum_operation
    as_data = as_data
    as_json = as_json

    @classmethod
    def fromdict(cls, data: dict):
        return fromdict(cls, data)

    @property
    def length(self):
        return self.value

    @length.setter
    def length(self, val):
        self.value = int(val)
