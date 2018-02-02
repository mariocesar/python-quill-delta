import json
from collections import namedtuple

__all__ = ['Insert', 'Retain', 'Delete']


def _as_json(instance):
    return json.dumps(instance.as_data())


def _sum_operation(instance, other):
    type_op = type(instance)
    type_other = type(other)

    if type(other) != type_op:
        raise ValueError(f'Operations are not the same type '
                         f'{type_op.__name__} != {type_other}')

    if hasattr(instance, 'attributes'):
        instance_attr = instance.attributes if instance.attributes else None
        other_attr = other.attributes if other.attributes else None

        if instance_attr != other_attr:
            raise ValueError("Can't sum operations with different attributes")

        return type_op(instance.value + other.value, other_attr)
    else:
        return type_op(instance.value + other.value)


def _as_data(instance):
    name = type(instance).__name__.lower()
    data = instance._asdict()
    value = data.pop('value')
    return {name: value, **{k: v for k, v in data.items() if v}}


def _fromdict(cls, data: dict):
    name = cls.__name__.lower()

    if name in data:
        value = data.pop(name)
        return cls(value, **data)


class Insert(namedtuple('Insert', 'value, attributes')):
    __slots__ = ()
    __str__ = _as_json
    __add__ = _sum_operation

    as_data = _as_data
    as_json = _as_json

    @classmethod
    def fromdict(cls, data):
        data.setdefault('attributes', None)
        return _fromdict(cls, data)

    @property
    def length(self):
        if isinstance(self.value, str):
            return len(self.value)
        return 1


class Retain(namedtuple('Retain', 'value, attributes')):
    __slots__ = ()
    __str__ = _as_json
    __add__ = _sum_operation

    as_data = _as_data
    as_json = _as_json

    @classmethod
    def fromdict(cls, data: dict):
        data.setdefault('attributes', None)
        return _fromdict(cls, data)

    @property
    def length(self):
        return self.value


class Delete(namedtuple('Delete', 'value')):
    __slots__ = ()
    __str__ = _as_json
    __add__ = _sum_operation

    as_data = _as_data
    as_json = _as_json

    @classmethod
    def fromdict(cls, data: dict):
        return _fromdict(cls, data)

    @property
    def length(self):
        return self.value

    @length.setter
    def length(self, val):
        self.value = int(val)
