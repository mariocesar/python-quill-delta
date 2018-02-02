from functools import partial, wraps
from typing import Dict, Union

from .operations import Delete, Insert, Retain

is_insert = lambda op: isinstance(op, Insert)
is_retain = lambda op: isinstance(op, Retain)
is_delete = lambda op: isinstance(op, Delete)
it_insert_text = lambda op: is_insert(op) and isinstance(op.value, str)

CleanValueType = Union[Insert, Retain, Delete, Dict]


def clean_operation(value: CleanValueType):
    assert isinstance(value, (Insert, Retain, Delete, dict)), \
        f'Wrong type {type(value)} expected {CleanValueType}'

    if isinstance(value, dict):
        value = op_from_dict(value)
    return value


def truncate_repr(items: list, length=10):
    items = items[:length]
    items = str(items).strip('[]')
    return f'[{items}{", ..." if len(items) < 10 else ""}]'


def op_from_dict(data: dict):
    if 'insert' in data:
        return Insert.fromdict(data)
    elif 'retain' in data:
        return Retain.fromdict(data)
    elif 'delete' in data:
        return Delete.fromdict(data)

    raise ValueError('Unknown operation for %s' % data)


def chainable(func):
    @wraps(func)
    def wrapper(instance, *args, **kwargs):
        instance_class = type(instance)
        items = func(instance, *args, **kwargs)

        if items:
            assert isinstance(items, (list, instance_class)), \
                'Invalid return value expected list or Operations'

        if isinstance(items, instance_class):
            return items
        elif isinstance(items, list):
            return instance_class(items)
        elif not items:
            return instance_class(instance._items)

    wrapper.inner = func
    return wrapper
