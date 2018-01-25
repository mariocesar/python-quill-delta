import json
from functools import reduce
from math import inf
from typing import List, TypeVar, Union, Dict, Any

from .iterator import Iterator
from .operations import OperationType, Insert, Retain, Delete


def op_from_dict(data: dict):
    if 'insert' in data:
        return Insert.fromdict(data)
    elif 'retain' in data:
        return Retain.fromdict(data)
    elif 'delete' in data:
        return Delete.fromdict(data)

    raise ValueError('Unknown operation for %s' % data)


class Delta:
    def __init__(self, ops: Union[List[OperationType], Dict, TypeVar('Delta')] = None):
        self.ops = []

        if isinstance(ops, dict):
            assert 'ops' in ops, 'Unknown form of ops {}'.format(ops)
            ops = ops['ops']
        elif isinstance(ops, Delta):
            ops = ops.ops
        elif ops is not None:
            if not isinstance(ops, (tuple, list)):
                assert 'Unknown form of ops {}'.format(ops)

        if not ops:
            ops = []

        for op in ops:
            if isinstance(op, dict):
                self.ops.append(op_from_dict(op))
            else:
                self.ops.append(op)

    def __repr__(self):
        return f'<Delta {self.ops}>'

    def __eq__(self, other):
        return self.ops == other.ops

    def __iter__(self):
        return iter(self.ops)

    def __str__(self):
        return json.dumps(self.asdata())

    def asdata(self):
        return [op.asdata() for op in self.ops]

    def push(self, new_op: OperationType):
        if isinstance(new_op, dict):
            new_op = op_from_dict(new_op)

        index = len(self.ops)

        if index > 0:
            last_op = self.ops[-1]
        else:
            last_op = None

        if last_op:
            if isinstance(new_op, Delete) and isinstance(last_op, Delete):
                self.ops[index - 1] = last_op + new_op
                return self

            if isinstance(new_op, Insert) and isinstance(last_op, Delete):
                index -= 1

                try:
                    last_op = self.ops[index - 1]
                except IndexError:
                    self.ops.insert(0, new_op)
                    return self

            if all(map(lambda op: isinstance(op, (Insert, Retain)), [new_op, last_op])):
                if isinstance(new_op, type(last_op)):
                    if new_op.attributes == last_op.attributes:
                        if type(new_op.value) == type(last_op.value):
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
        if len(self.ops) > 0:
            last_op = self.ops[-1]

            if isinstance(last_op, Retain) and not last_op.attributes:
                self.ops.pop()

        return self

    def filter(self, func):
        return filter(func, self.ops)

    def map(self, func):
        return map(func, self.ops)

    def for_each(self, func):
        for op in self.ops:
            func(op)

    def partition(self, func):
        passed, failed = [], []
        ok = passed.append
        fail = failed.append

        self.for_each(lambda op: ok(op) if func(op) else fail(op))

        return passed, failed

    def reduce(self, func, initial=0):
        return reduce(func, self.ops, initial=initial)

    def change_length(self):
        def reducer(length, op):
            if isinstance(op, Insert):
                return length + op.length
            elif isinstance(op, Delete):
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

                if isinstance(other_op, Retain):
                    attrs = {}
                    if other_op.attributes:
                        attrs.update(other_op.attributes)

                    if self_op.attributes:
                        attrs.update(self_op.attributes)

                    if isinstance(self_op, Retain):
                        new_op = Retain(length, attrs or None)
                    else:
                        new_op = Insert(self_op.value, attrs or None)

                    delta.push(new_op)
                elif isinstance(other_op, Delete) and isinstance(self_op, Retain):
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
        delta = Delta(self.ops.copy())

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

            if isinstance(self_op, Insert) and isinstance(self_op.value, str):
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
