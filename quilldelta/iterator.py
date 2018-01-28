from collections import Sequence

from quilldelta.utils import is_delete, is_retain, it_insert_text
from .operations import Retain, Insert, Delete


class Iterator:
    def __init__(self, ops: Sequence):
        self.ops = ops
        self.index = 0
        self.offset = 0

    def peek(self):
        if len(self.ops) >= self.index + 1:
            return self.ops[self.index]

    def peek_length(self):
        op = self.peek()
        if op:
            return op.length - self.offset
        return 0

    def peek_type(self):
        op = self.peek()
        return type(op) if op else Retain

    def has_next(self):
        return self.peek_length() > 0

    def next(self, length=None):
        next_op = self.peek()
        print('length:', length, end=' ')

        if next_op:
            op_length = next_op.length - self.offset
            print('next_op.length:', next_op.length, end=' ')
            print('op_lenght:', op_length)

            if length:
                self.offset += length
            else:
                length = next_op.length - self.offset
                self.index += 1
                self.offset = 0

            print('offset:', self.offset, end=' '),
            print('self.index:', self.index, end=' ')
            print('self.offset:', self.offset, end=' ')

            if is_delete(next_op):
                return Delete(length)
            elif is_retain(next_op):
                return Retain(length, next_op.attributes)
            elif it_insert_text(next_op):
                value = next_op.value[:self.offset]
                print('value', next_op.value[:self.offset])
                return Insert(value, next_op.attributes)
            else:
                return Insert(next_op.insert, next_op.attributes)
        else:
            return Retain(0, None)
