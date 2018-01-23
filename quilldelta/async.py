import asyncio
from functools import wraps

from quilldelta import delta


class AsyncMethod:
    def __init__(self, attr_name=None):
        self.attr_name = attr_name

    def create_attribute(self, cls, attr_name):
        name = self.attr_name or attr_name
        method = getattr(cls, name)

        assert callable(method), f'Attribute {name} is not callable'

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            loop = self.get_io_loop()
            callback = kwargs.pop('callback', None)
            future = loop.create_task(method(*args, **kwargs))
            future.add_done_callback(callback)
            return future

        return wrapper


class AsyncDelta(delta.Delta):
    push = AsyncMethod()
    insert = AsyncMethod()
    retain = AsyncMethod()
    delete = AsyncMethod()
    chop = AsyncMethod()
    filter = AsyncMethod()
    map = AsyncMethod()
    for_each = AsyncMethod()
    partition = AsyncMethod()
    reduce = AsyncMethod()
    change_length = AsyncMethod()
    length = AsyncMethod()
    compose = AsyncMethod()
    slice = AsyncMethod()
    concat = AsyncMethod()
    diff = AsyncMethod()
    each_line = AsyncMethod()
    transform = AsyncMethod()
    transform_position = AsyncMethod()

    def __init__(self, *args, **kwargs):
        io_loop = kwargs.pop('io_loop')

        if not io_loop:
            io_loop = asyncio.get_event_loop()

        super().__init__(*args, **kwargs)

        self.io_loop = io_loop

    def get_io_loop(self):
        return self.io_loop
