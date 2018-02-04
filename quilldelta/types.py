from collections import namedtuple
from functools import partial
from typing import Any, Dict, Union

from quilldelta import utils as _

__all__ = ['Insert', 'Retain', 'Delete', 'OperationType',
           'is_retain', 'is_insert', 'is_delete',
           'it_insert_text', 'load_operation']


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


class Insert(namedtuple('Insert', 'value, attributes')):
    __slots__ = ()
    __str__ = _.instance_as_json
    __add__ = _sum_operation

    as_data = _.instance_as_dict
    as_json = _.instance_as_json

    @classmethod
    def fromdict(cls, data):
        data.setdefault('attributes', None)
        return _.dict_to_class(cls, data)

    @property
    def length(self):
        if isinstance(self.value, str):
            return len(self.value)
        return 1


class Retain(namedtuple('Retain', 'value, attributes')):
    __slots__ = ()
    __str__ = _.instance_as_json
    __add__ = _sum_operation

    as_data = _.instance_as_dict
    as_json = _.instance_as_json

    @classmethod
    def fromdict(cls, data: dict):
        data.setdefault('attributes', None)
        return _.dict_to_class(cls, data)

    @property
    def length(self):
        return self.value

    @length.setter
    def length(self, val: int):
        assert isinstance(val, int)
        self.value = val


class Delete(namedtuple('Delete', 'value')):
    __slots__ = ()
    __str__ = _.instance_as_json
    __add__ = _sum_operation

    as_data = _.instance_as_dict
    as_json = _.instance_as_json

    @classmethod
    def fromdict(cls, data: dict):
        return _.dict_to_class(cls, data)

    @property
    def length(self):
        return self.value

    @length.setter
    def length(self, val: int):
        assert isinstance(val, int)
        self.value = val


OperationType = Union[Insert, Retain, Delete, Dict]


def load_operation(data: OperationType):
    if isinstance(data, (Insert, Retain, Delete)):
        return data
    elif isinstance(data, Dict):
        if 'insert' in data:
            return Insert.fromdict(data)
        elif 'retain' in data:
            return Retain.fromdict(data)
        elif 'delete' in data:
            return Delete.fromdict(data)

    raise ValueError('Unknown operation for %s' % data)


def _isinstance(op: Any, class_or_tuple):
    return isinstance(op, class_or_tuple)


is_insert = partial(_isinstance, class_or_tuple=Insert)
is_retain = partial(_isinstance, class_or_tuple=Retain)
is_delete = partial(_isinstance, class_or_tuple=Delete)


def it_insert_text(op: Any):
    return is_insert(op) and isinstance(op.value, str)
