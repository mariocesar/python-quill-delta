import json
from collections.abc import Sequence, Set, Sized
from functools import reduce
from typing import Dict, Iterable, List, TypeVar, Union

from .operations import Delete, Insert, Retain
from .reader import SequenceReader
from .utils import (chainable, clean_operation, is_delete, is_insert, is_retain, it_insert_text, op_from_dict,
                    truncate_repr)

OperationType = Union[Insert, Retain, Delete, Dict]


class OperationsReader(SequenceReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._offset = 0

    def length(self):
        try:
            self._data[self._index]
        except IndexError:
            return -1
        else:
            return self._data[self._index].length - self._offset

    def writable(self):
        return True

    def write(self, value):
        pass

    def read(self, length=None):
        peek = self.peek()

        if peek is None:
            return Retain(-1, None)

        op = super().read()  # type: Union[Insert, Retain, Delete]

        if op.length is not None:
            self._offset = 0
        else:
            self._offset = length

        if is_delete(op):
            return Delete(op.length)
        else:
            if is_retain(op):
                return Retain(length, op.attributes)
            if it_insert_text(op):
                return Insert(op.value[self._offset:], op.attributes)
            elif is_insert(op):
                return Insert(op.value, op.attributes)


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

    def __hash__(self):
        return Set._hash(self)

    def __repr__(self):
        return f'<Operations {truncate_repr(self._items)} at {id(self)}>'

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
        if self.last and is_retain(self.last) and not self.last.attributes:
            self._items.pop()


DeltaOperationsType = Union[List, Dict, TypeVar('Delta'), Operations]


class Delta(Sized, Iterable):
    __slots__ = ('ops',)

    def __init__(self, ops: DeltaOperationsType = None):
        if ops:
            assert isinstance(ops, (list, dict, Delta, Operations)), \
                f'Wrong type {type(ops)} expected {DeltaOperationsType}'

        if isinstance(ops, dict):
            assert 'ops' in ops, 'Unknown form, missing "ops" key.'
            ops = ops['ops']
        elif isinstance(ops, Delta):
            ops = ops.ops
        elif isinstance(ops, Operations):
            ops = ops
        elif isinstance(ops, list):
            ops = [clean_operation(op) for op in ops]
        elif not ops:
            ops = []

        self.ops = Operations(ops)

    def __repr__(self):
        return f'<Delta {self.ops} at 0x{id(self)}>'

    def __hash__(self):
        return hash(self.ops)

    def __eq__(self, other):
        if not isinstance(other, Delta):
            return False
        return self.ops == other.ops

    def __str__(self):
        return self.as_json()

    def __iter__(self):
        return iter(self.ops)

    def __len__(self):
        return len(self.ops)

    def copy(self):
        return Delta([op for op in self.ops])

    def length(self):
        return reduce(lambda length, op: op.length + length, self.ops, 0)

    def as_data(self):
        return [op.as_data() for op in self.ops]

    def as_text(self):
        return ''.join(self.ops.filter(it_insert_text))

    def as_json(self):
        return json.dumps(self.as_data())

    def as_markdown(self):
        raise NotImplementedError

    def as_html(self):
        raise NotImplementedError

    def insert(self, value: Union[str, Dict], attributes: dict = None):
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

    def concat(self, other):
        delta = Delta(self.ops)

        for op in other.ops:
            delta.push(op)

        return delta

    def change_length(self):
        def reducer(length, op):
            if is_insert(op):
                return length + op.length
            elif is_delete(op):
                return length - op.length
            else:
                return length

        return self.reduce(reducer, 0)

    def push(self, value: OperationType):

        # assert isinstance(value, OperationType)
        new_op = clean_operation(value)
        index = len(self.ops)
        last_op = self.ops.last

        if last_op:
            if is_delete(new_op) and is_delete(last_op):
                self.ops[index - 1] = last_op + new_op
                return self

            if is_insert(new_op) and is_delete(last_op):
                index -= 1
                previous_op = self.ops[index - 1]

                if it_insert_text(previous_op):
                    self.ops[index - 1] = previous_op + new_op
                    return self

            op_types = type(new_op), type(last_op)

            if Delete not in op_types:
                new_attr = new_op.attributes if new_op.attributes else None
                last_attr = last_op.attributes if last_op.attributes else None

                if new_attr == last_attr:

                    if it_insert_text(last_op) and it_insert_text(new_op):
                        self.ops[index - 1] = last_op + new_op
                        return self
                    if is_retain(last_op) and is_retain(new_op):
                        self.ops[index - 1] = last_op + new_op
                        return self

        if index == len(self.ops):
            self.ops.append(new_op)
        else:
            self.ops.insert(index, new_op)

        return self

    def compose(self, other: TypeVar('Delta')):
        delta = Delta()

        with OperationsReader(self.ops) as this_reader, \
                OperationsReader(other.ops) as other_reader:
            while this_reader.not_eof or other_reader.not_eof:
                this_peek = this_reader.peek()
                other_peek = other_reader.peek()

                if is_insert(other_peek):
                    delta.push(other_reader.read())
                elif is_delete(this_peek):
                    delta.push(this_reader.read())
                else:
                    length = min(this_reader.length(), other_reader.length())
                    length = length if length > 0 else None

                    a = this_reader.read(length)
                    b = other_reader.read(length)

                    if is_retain(b):
                        op = {'attributes': {
                            **(a.attributes or {}),
                            **(b.attributes or {})
                        }}

                        if is_retain(a):
                            op['retain'] = length or self.length()
                        else:
                            op['insert'] = a.value
                        delta.push(op_from_dict(op))

                    elif is_delete(b) and is_retain(a):
                        delta.push(b)

        delta.chop()

        return delta

    def slice(self, start=0, end=None):
        reader = OperationsReader(self.ops)
        return Delta([op for op in reader][start:end])

    def diff(self, other, index):
        raise NotImplementedError

    def each_line(self, func, newline='\n'):

        reader = OperationsReader(self.ops)
        line = Delta()
        i = 0

        while reader.not_eof:
            if not is_insert(reader.peek()):
                return

            self_op = reader.read()
            start = self_op.length - reader.length()

            if it_insert_text(self_op):
                try:
                    index = self_op.value.index(newline, start) - start
                except ValueError:
                    index = -1
            else:
                index = -1

            if index < 0:
                line.push(reader.read())
            elif index > 0:
                line.push(reader.read(index))
            else:
                if not func(line, reader.read(1).attributes, i):
                    return

                i += 1
                line = Delta()

        if line.length() > 0:
            func(line, {}, i)

    def transform(self, other, priority):
        raise NotImplementedError

    def transform_position(self, index, priority):
        raise NotImplementedError
