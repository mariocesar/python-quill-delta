import json
from functools import reduce
from collections.abc import Sequence
from math import inf
from typing import Any, Union, List, Iterable, TypeVar, Dict

from .iterator import Iterator
from .operations import Insert, Retain, Delete
from .utils import clean_operation, truncate_repr, chainable, is_insert, is_delete, is_retain, it_insert_text

OperationType = Union[Insert, Retain, Delete, Dict]


class Operations(Sequence):
    def __init__(self, items: Union[List, Iterable] = None):
        if items:
            assert isinstance(items, (List, Iterable)), f'Wrong type {type(items)} for items'

        self._items = []
        self.last = None

        if not items:
            items = []

        for item in items:
            self.append.inner(self, item)

    def __repr__(self):
        return f'<Operations {truncate_repr(self._items)}>'

    def __len__(self):
        return len(self._items)

    def __getitem__(self, item):
        return self._items[item]

    def __setitem__(self, key: int, value: OperationType):
        value = clean_operation(value)
        self._items[key] = value
        self.last = self._items[-1]

    def __eq__(self, other: Union[TypeVar('Operations'), List]):
        assert isinstance(other, (Operations, list)), f'Wrong type {type(other)}'

        if isinstance(other, Operations):
            return self._items == other._items
        elif isinstance(other, list):
            return self._items == other

    def __add__(self, other: Union[TypeVar('Operations'), List]):
        assert isinstance(other, (Operations, list)), f'Wrong type {type(other)}'

        if isinstance(other, Operations):
            return Operations(self._items + other._items)
        elif isinstance(other, list):
            return Operations(self._items + other)

    @chainable
    def append(self, value: OperationType):
        value = clean_operation(value)
        self._items.append(value)
        self.last = value

    @chainable
    def insert(self, index: int, value: OperationType):
        value = clean_operation(value)
        self._items.insert(index, value)
        self.last = self._items[-1]

    @chainable
    def filter(self, func):
        return Operations(filter(func, self))

    @chainable
    def map(self, func):
        return Operations(map(func, self))

    @chainable
    def chop(self):
        if self.last and is_retain(self.last) and self.last.attributes:
            self._items.pop()


DeltaOperationsType = Union[List, Dict, TypeVar('Delta'), Operations]


class Delta:
    def __init__(self, ops: DeltaOperationsType = None):
        if ops:
            assert isinstance(ops, (list, dict, Delta, Operations)), \
                f'Wrong type {type(ops)} expected {DeltaOperationsType}'

        if isinstance(ops, dict):
            assert 'ops' in ops, 'Unknown form, missing "ops" key.'
            ops = Operations(ops['ops'])
        elif isinstance(ops, Delta):
            ops = ops.ops
        elif isinstance(ops, Operations):
            ops = ops
        elif isinstance(ops, list):
            ops = [clean_operation(op) for op in ops]
        elif not ops:
            ops = Operations()

        self.ops = ops

    def __repr__(self):
        return f'<Delta {truncate_repr(self.ops)}>'

    def __eq__(self, other):
        return self.ops == other.ops

    def __str__(self):
        return json.dumps(self.asdata())

    def asdata(self):
        return [op.asdata() for op in self.ops]

    def push(self, new_op: OperationType):
        new_op = clean_operation(new_op)
        index = len(self.ops)
        last_op = self.ops.last

        if last_op:
            if is_delete(new_op) and is_delete(last_op):
                self.ops[index - 1] = last_op + new_op
                return self

            if is_insert(new_op) and is_delete(last_op):
                index -= 1

                if not self.ops.last:
                    self.ops.insert(0, new_op)
                    return self

            op_types = type(new_op), type(last_op)

            if Delete not in op_types:
                if new_op.attributes == last_op.attributes:
                    if op_types[0] == op_types[1]:
                        self.ops[index - 1] = last_op + new_op
                        return self

        if index == len(self.ops):
            self.ops.append(new_op)
        else:
            self.ops.insert(index, new_op)

        return self

    def insert(self, value: Any, attributes: dict = None):
        if not attributes:
            attributes = None

        if isinstance(value, str):
            if len(value) > 0:
                self.push(Insert(value, attributes))
        else:
            self.push(Insert(value, attributes))

        return self

    def retain(self, length: int, attributes: dict = None):
        if not attributes:
            attributes = None

        if length > 0:
            self.push(Retain(length, attributes))

        return self

    def delete(self, length: int):
        if length > 0:
            self.push(Delete(length))
        return self

    def chop(self):
        return Delta(self.ops.chop())

    def partition(self, func):
        passed, failed = [], []

        for op in self.ops:
            if func(op):
                passed.append(op)
            else:
                failed.append(op)

        return passed, failed

    def reduce(self, func, initial=0):
        return reduce(func, self.ops, initial=initial)

    def change_length(self):
        def reducer(length, op):
            if is_insert(op):
                return length + op.length
            elif is_delete(op):
                return length - op.length
            else:
                return length

        return self.reduce(reducer, 0)

    def length(self):
        return reduce(lambda length, op: op.length + length, self.ops, 0)

    def compose(self, other: TypeVar('Delta')):
        self_iter = Iterator(self.ops)
        other_iter = Iterator(other.ops)
        delta = Delta()

        while self_iter.has_next() or other_iter.has_next():
            if other_iter.peek_type() == Insert:
                delta.push(other_iter.next())
            elif self_iter.peek_type() == Delete:
                delta.push(self_iter.next())
            else:
                length = min(self_iter.peek_length(), other_iter.peek_length())
                self_op = self_iter.next(length)
                other_op = other_iter.next(length)

                if is_retain(other_op):
                    attrs = {}
                    if other_op.attributes:
                        attrs.update(other_op.attributes)

                    if self_op.attributes:
                        attrs.update(self_op.attributes)

                    if is_retain(self_op):
                        new_op = Retain(length, attrs or None)
                    else:
                        new_op = Insert(self_op.value, attrs or None)

                    delta.push(new_op)
                elif is_delete(other_op) and is_retain(self_op):
                    delta.push(other_op)

        delta.chop()

        return delta

    def slice(self, start=0, end=inf):
        ops = []
        cursor = Iterator(ops)
        index = 0

        while index < inf and cursor.has_next():
            if index < start:
                next_op = cursor.next(start - index)
            else:
                next_op = cursor.next(end - index)
                ops.append(next_op)

            index += next_op.length

        return Delta(ops)

    def concat(self, other):
        delta = Delta(self.ops)

        if len(other.ops) > 0:
            delta.push(other.ops[0])
            delta.ops = delta.ops + other.ops[1:]

        return delta

    def diff(self, other, index):
        raise NotImplementedError

    def each_line(self, func, newline='\n'):
        cursor = Iterator(self.ops)
        line = Delta()
        i = 0

        while cursor.has_next():
            if cursor.peek_type() != Insert:
                return

            self_op = cursor.peek()
            start = self_op.length - cursor.peek_length()

            if it_insert_text(self_op):
                try:
                    index = self_op.value.index(newline, start) - start
                except ValueError:
                    index = -1
            else:
                index = -1

            if index < 0:
                line.push(cursor.next())
            elif index > 0:
                line.push(cursor.next(index))
            else:
                if not func(line, cursor.next(1).attributes, i):
                    return
                i += 1
                line = Delta()

        if line.length() > 0:
            func(line, {}, i)

    def transform(self, other, priority):
        raise NotImplementedError

    def transform_position(self, index, priority):
        raise NotImplementedError
