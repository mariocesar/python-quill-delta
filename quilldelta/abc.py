import asyncio
from abc import ABC, abstractmethod
from collections import Sized


class SequenceReader(Sized, ABC):
    __slots__ = ('_data', '_index', 'eof')

    def __init__(self, data=None):
        if not data:
            data = []

        self.eof = False
        self._index = 0
        self._data = data

    def __len__(self):
        return len(self._data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        value = self.read()

        if value is None:
            self.eof = True
            raise StopIteration

        return value

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.__exit__(exc_type, exc_value, traceback)

    async def __aiter__(self):
        return self

    async def __anext__(self):
        value = await self.async_read()
        await asyncio.sleep(0)  # TODO: loop task switch

        if value is None:
            self.eof = True
            raise StopAsyncIteration

        return value

    @property
    def not_eof(self):
        return not self.eof

    def tell(self):
        return self._index

    def readable(self):
        return len(self._data) > 0

    def getvalue(self):
        return self._data

    def writable(self):
        return False

    def seek(self, index):
        assert index >= 0, f'Invalid index value: {index}'

        if index <= len(self):
            self._index = index
            if self.eof:
                self.eof = False
        else:
            self.eof = True
            self._index = len(self)

    def peek(self):
        try:
            return self._data[self._index]
        except IndexError:
            pass
        return

    def read(self):
        if self.eof:
            return None

        value = self.peek()

        if not value:
            self.eof = True
            value = None
        else:
            self._index += 1

            if self._index >= len(self):
                self.eof = True

        return value

    async def async_read(self):
        return self.read()

    @abstractmethod
    def readitem(self):
        pass
