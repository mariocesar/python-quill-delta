import copy
import json
from functools import wraps
from typing import Any, Dict, List


def truncate_repr(items: list, length=10):
    if len(items) > 0:
        items = items[:length]
        items = str(items).strip('[]')
        return f'[{items}{", ..." if len(items) < 10 else ""}]'
    else:
        return '[]'


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


def dict_to_class(cls, attrs: Dict):
    name = cls.__name__.lower()

    if name in attrs:
        value = attrs.pop(name)
        return cls(value, **attrs)


def instance_as_dict(instance: Any):
    name = type(instance).__name__.lower()
    data = instance._asdict()
    value = data.pop('value')
    return {name: value, **{k: v for k, v in data.items() if v}}


def instance_as_json(instance: Any):
    if hasattr(instance, 'as_data'):
        return json.dumps(instance.as_data())
    elif hasattr(instance, '_asdict'):
        return json.dumps(instance._asdict())

    raise ValueError("Instance can't be output as JSON")


def merge_dicts(*args: List):
    result = {}

    for source in args:
        if source is not None:
            source = copy.deepcopy(source)  # type: dict
            result.update(source)

    return result
