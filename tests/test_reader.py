import pytest

from quilldelta.reader import OperationsReader


def test_empty_reader_constructor():
    reader = OperationsReader()

    assert reader.tell() == 0
    assert reader.length() == 0
    assert reader.getvalue() == []

    assert not reader.readable()
    assert not reader.writable()

    reader.seek(0)
    assert reader.tell() == 0

    reader.seek(10)
    assert reader.tell() == 0


def test_reader_constructor():
    reader = OperationsReader([1, 2, 3, 4])

    assert reader.tell() == 0
    assert reader.length() == 4
    assert reader.getvalue() == [1, 2, 3, 4]

    assert reader.readable()
    assert not reader.writable()

    reader.seek(0)
    assert reader.tell() == 0

    reader.seek(2)
    assert reader.tell() == 2

    reader.seek(10)
    assert reader.tell() == 4


def test_reader_seek():
    reader = OperationsReader([1, 2, 3, 4])
    assert reader.tell() == 0

    assert reader.read() == 1
    assert reader.read() == 2

    assert reader.tell() == 2

    reader.seek(0)

    assert reader.read() == 1
    assert reader.read() == 2

    reader.seek(10)

    assert reader.read() is None


@pytest.mark.asyncio
async def test_reader_contextmanager():
    with OperationsReader([1, 2, 3, 4]) as reader:
        assert reader.tell() == 0
        assert reader.read() == 1

        assert reader.read() == 2
        assert reader.tell() == 2

        reader.read(), reader.read(), reader.read()
        reader.read(), reader.read(), reader.read()

        assert reader.read() is None
        assert reader.read() is None

        assert reader.tell() == 4

    assert reader.tell() == 0

    async with OperationsReader([1, 2, 3, 4]) as async_reader:
        assert async_reader.tell() == 0
        assert async_reader.read() == 1
        assert async_reader.read() == 2
        assert async_reader.read() == 3
        assert async_reader.read() == 4

        assert async_reader.read() is None
        assert async_reader.read() is None

        assert async_reader.tell() == 4

    assert async_reader.tell() == 0


@pytest.mark.asyncio
async def test_reader_iterator():
    with OperationsReader([1, 2, 3, 4]) as reader:
        data = []

        for op in reader:
            data.append(op)

        assert data == [1, 2, 3, 4]

    async with OperationsReader([1, 2, 3, 4]) as reader:
        data = []

        async for op in reader:
            data.append(op)

        assert data == [1, 2, 3, 4]

    assert reader.read() is None
