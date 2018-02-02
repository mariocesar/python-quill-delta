from itertools import chain

import pytest

from quilldelta.reader import SequenceReader


def test_empty_reader_constructor():
    reader = SequenceReader()

    assert reader.tell() == 0
    assert len(reader) == 0
    assert reader.getvalue() == []

    assert not reader.readable()
    assert not reader.writable()

    reader.seek(0)
    assert reader.tell() == 0

    reader.seek(10)
    assert reader.tell() == 0


def test_reader_constructor():
    reader = SequenceReader([1, 2, 3, 4])

    assert reader.tell() == 0
    assert len(reader) == 4
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
    reader = SequenceReader([1, 2, 3, 4])
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
    with SequenceReader([1, 2, 3, 4]) as reader:
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

    async with SequenceReader([1, 2, 3, 4]) as async_reader:
        assert async_reader.tell() == 0
        assert async_reader.read() == 1
        assert async_reader.read() == 2
        assert async_reader.read() == 3
        assert async_reader.read() == 4

        assert async_reader.read() is None
        assert async_reader.read() is None

        assert async_reader.tell() == 4

    assert async_reader.tell() == 0

    chained = []

    with SequenceReader([1, 2, 3, 4]) as reader1:
        with SequenceReader([5, 6, 7, 8]) as reader2:
            for op in chain(reader1, reader2):
                chained.append(op)

    assert chained == [1, 2, 3, 4, 5, 6, 7, 8]

    chained = []

    async with SequenceReader([1, 2, 3, 4]) as reader1:
        async with SequenceReader([5, 6, 7, 8]) as reader2:
            while not reader1.eof:
                chained.append(await reader1.async_read())

            while not reader2.eof:
                chained.append(await reader2.async_read())

    assert chained == [1, 2, 3, 4, 5, 6, 7, 8]


@pytest.mark.asyncio
async def test_reader_iterator():
    with SequenceReader([1, 2, 3, 4]) as reader:
        data = []

        for op in reader:
            data.append(op)

        assert data == [1, 2, 3, 4]

    async with SequenceReader([1, 2, 3, 4]) as reader:
        data = []

        async for op in reader:
            data.append(op)

        assert data == [1, 2, 3, 4]

    assert reader.read() is None
