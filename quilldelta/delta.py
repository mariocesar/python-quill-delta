import json
from collections.abc import Sized
from functools import reduce
from typing import Dict, Iterable, List, TypeVar, Union

from . import utils as _
from .operations import OperationsList, OperationsReader
from .types import (Delete, Insert, OperationType, Retain,
                    is_delete, is_insert, is_retain,
                    it_insert_text, load_operation)

DeltaOperationsType = Union[List, Dict, TypeVar('Delta'), OperationsList]


class Delta(Sized, Iterable):
    __slots__ = ('ops',)

    def __init__(self, ops: DeltaOperationsType = None):
        if ops:
            assert isinstance(ops, (List, Dict, Delta, OperationsList)), \
                f'Wrong type {type(ops)} expected {DeltaOperationsType}'

        if isinstance(ops, Dict):
            assert 'ops' in ops, 'Unknown form, missing "ops" key.'
            ops = ops['ops']
        elif isinstance(ops, Delta):
            ops = ops.ops
        elif isinstance(ops, OperationsList):
            ops = ops
        elif isinstance(ops, List):
            ops = [load_operation(op) for op in ops]
        elif not ops:
            ops = []

        self.ops = OperationsList(ops)

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
        new_op = load_operation(value)
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
        this_reader = OperationsReader(self.ops)
        other_reader = OperationsReader(other.ops)

        while this_reader.not_eof or other_reader.not_eof:
            this_peek = this_reader.peek()
            other_peek = other_reader.peek()

            if is_insert(other_peek):
                delta.push(other_reader.readitem())
            elif is_delete(this_peek):
                delta.push(this_reader.readitem())
            else:
                length = min(this_reader.length() or 0,
                             other_reader.length() or 0)
                length = length if length > 0 else None

                a = this_reader.readitem(length)
                b = other_reader.readitem(length)

                if is_retain(b):
                    op = _.merge_dicts(a.attributes, b.attributes)

                    if is_retain(a):
                        op['retain'] = length or self.length()
                    else:
                        op['insert'] = a.value

                    delta.push(load_operation(op))

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

            self_op = reader.readitem()
            start = self_op.length - reader.length()

            if it_insert_text(self_op):
                try:
                    index = self_op.value.index(newline, start) - start
                except ValueError:
                    index = -1
            else:
                index = -1

            if index < 0:
                line.push(reader.readitem())
            elif index > 0:
                line.push(reader.readitem(index))
            else:
                if not func(line, reader.readitem(1).attributes, i):
                    return

                i += 1
                line = Delta()

        if line.length() > 0:
            func(line, {}, i)

    def transform(self, other, priority):
        raise NotImplementedError

    def transform_position(self, index, priority):
        raise NotImplementedError
