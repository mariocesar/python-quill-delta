from collections.abc import Sequence, Set
from typing import Iterable, List, TypeVar, Union

from .abc import SequenceReader
from .types import (Delete, Insert, OperationType, Retain, is_delete, is_insert,
                    is_retain, it_insert_text, load_operation)
from .utils import (chainable, truncate_repr)


class OperationsReader(SequenceReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._offset = 0

    def length(self):
        if self.eof:
            return None

        return self.peek().length - self._offset

    def writable(self):
        return True

    def write(self, value):
        pass

    def readitem(self, length=None):
        peek = self.peek()

        if peek is None:
            return Retain(-1, None)

        op = self.read()  # type: Union[Insert, Retain, Delete]

        if length is None:
            self._offset = 0
        else:
            self.seek(self._index - 1)
            self._offset += length

        if is_delete(op):
            return Delete(op.length)
        else:
            if is_retain(op):
                return Retain(length, op.attributes)
            if it_insert_text(op):
                return Insert(op.value[:self._offset], op.attributes)
            elif is_insert(op):
                return Insert(op.value, op.attributes)


class OperationsList(Sequence):
    def __init__(self, items: Union[List, Iterable] = None):
        if items:
            assert isinstance(items, (
                List, Iterable)), f'Wrong type {type(items)} for items'

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
        value = load_operation(value)
        self._items[key] = value
        self.last = self._items[-1]

    def __eq__(self, other: Union[TypeVar('OperationsList'), List]):
        assert isinstance(other,
                          (OperationsList, list)), f'Wrong type {type(other)}'

        if isinstance(other, OperationsList):
            return self._items == other._items
        elif isinstance(other, list):
            return self._items == other

    def __add__(self, other: Union[TypeVar('OperationsList'), List]):
        assert isinstance(other,
                          (OperationsList, list)), f'Wrong type {type(other)}'

        if isinstance(other, OperationsList):
            return OperationsList(self._items + other._items)
        elif isinstance(other, list):
            return OperationsList(self._items + other)

    @chainable
    def append(self, value: OperationType):
        value = load_operation(value)
        self._items.append(value)
        self.last = value

    @chainable
    def insert(self, index: int, value: OperationType):
        value = load_operation(value)
        self._items.insert(index, value)
        self.last = self._items[-1]

    @chainable
    def filter(self, func):
        return OperationsList(filter(func, self))

    @chainable
    def map(self, func):
        return OperationsList(map(func, self))

    @chainable
    def chop(self):
        if self.last and is_retain(self.last) and not self.last.attributes:
            self._items.pop()
