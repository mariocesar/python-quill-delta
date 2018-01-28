from collections import Sized


class OperationsReader(Sized):
    __slots__ = ('_data', '_index', '_is_async', 'eof')

    def __init__(self, data=None):
        if not data:
            data = []

        self.eof = False
        self._is_async = False
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
            if self._is_async:
                raise StopAsyncIteration
            else:
                raise StopIteration

        return value

    async def __aiter__(self):
        return self.__iter__()

    async def __anext__(self):
        return self.__next__()

    async def __aenter__(self):
        self._is_async = True
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._is_async = False
        self.__exit__(exc_type, exc_value, traceback)

    def length(self):
        return len(self)

    def seek(self, index):
        if index <= self.length():
            self._index = index
            if self.eof:
                self.eof = False
        elif index >= self.length():
            self.eof = True
            self._index = self.length()

    def tell(self):
        return self._index

    def read(self, length=None):
        if self.eof:
            return None

        try:
            value = self._data[self._index]
        except IndexError:
            self.eof = True
            value = None
        else:
            self._index += 1

        return value

    async def async_read(self, length=None):
        return self.read(length)

    def readable(self):
        return len(self._data) > 0

    def getvalue(self):
        return self._data

    def writable(self):
        return False
