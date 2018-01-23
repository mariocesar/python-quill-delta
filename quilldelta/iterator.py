from math import inf

from .operations import Retain, Insert, Delete


class Iterator:
    def __init__(self, ops: list):
        self.ops = ops
        self.index = 0
        self.offset = 0

    def peek(self):
        if len(self.ops) >= self.index + 1:
            return self.ops[self.index]

    def peek_length(self):
        op = self.peek()
        return op.length - self.offset if op else inf

    def peek_type(self):
        op = self.peek()
        return type(op) if op else Retain

    def has_next(self):
        return self.peek_length() < inf

    def next(self, length=inf):
        next_op = self.peek()

        if next_op:
            offset = self.offset
            op_length = next_op.length

            if length >= op_length - offset:
                length = op_length - offset
                self.index += 1
                self.offset = 0
            else:
                self.offset += length

            if isinstance(next_op, Delete):
                return Delete(length)
            else:
                if isinstance(next_op, Retain):
                    return Retain(length, next_op.attributes)
                elif isinstance(next_op, Insert):
                    if isinstance(next_op.value, str):
                        value = next_op.value[self.offset:length]
                        return Insert(value, next_op.attributes)
                else:
                    return Insert(next_op.insert, next_op.attributes)
        else:
            return Retain(inf, None)
