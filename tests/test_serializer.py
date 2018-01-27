import unittest

import pytest

from quilldelta import Delta, Retain, Insert, Delete
from quilldelta.utils import op_from_dict


class TestParser:
    def test_insert_from_dict(self):
        assert op_from_dict({'insert': 1}) == Insert(1, None)
        assert op_from_dict({'insert': 'foo'}) == Insert('foo', None)
        assert op_from_dict({'insert': 'foo', 'attributes': {'bold': True}}) == Insert('foo', {'bold': True})

    def test_retain_from_dict(self):
        assert op_from_dict({'retain': 1}) == Retain(1, None)
        assert op_from_dict({'retain': 1, 'attributes': {'bold': True}}) == Insert(1, {'bold': True})

    def test_delete_from_dict(self):
        assert op_from_dict({'delete': 1}) == Delete(1)

    def test_unknown_operation(self):
        with pytest.raises(ValueError) as error:
            assert op_from_dict({'emotion': 1})

        assert error.match('Unknown operation')


class TestData(unittest.TestCase):
    def test_insert_as_data(self):
        assert Insert('foo', None).as_data() == {'insert': 'foo'}
        assert Insert('foo', {}).as_data() == {'insert': 'foo'}
        assert Insert('foo', {'bold': True}).as_data() == {
            'insert': 'foo',
            'attributes': {'bold': True}
        }
        assert Insert(1, {'img': 'image.jpg'}).as_data() == {
            'insert': 1,
            'attributes': {'img': 'image.jpg'}
        }

    def test_retain_as_data(self):
        assert Retain(1, None).as_data() == {'retain': 1}
        assert Retain(1, {}).as_data() == {'retain': 1}
        assert Retain(1, {'bold': True}).as_data() == {
            'retain': 1,
            'attributes': {'bold': True}
        }

    def test_delete_as_data(self):
        assert Delete(1).as_data() == {'delete': 1}
        assert Delete(2).as_data() == {'delete': 2}

    def test_delta_as_data(self):
        delta = Delta(ops=[
            Insert('abc', None),
            Retain(1, {'color': 'red'}),
            Delete(4),
            Insert('def', {'bold': True}),
            Retain(6, None)
        ])

        expected = [
            {'insert': 'abc'},
            {'retain': 1, 'attributes': {'color': 'red'}},
            {'delete': 4},
            {'insert': 'def', 'attributes': {'bold': True}},
            {'retain': 6}
        ]

        self.assertListEqual(delta.as_data(), expected)


class TestAsStringJson(unittest.TestCase):
    def test_insert_str_json(self):
        assert str(Insert('foo', None)) == '{"insert": "foo"}'
        assert str(Insert('foo', {})) == '{"insert": "foo"}'
        assert str(Insert('foo', {'bold': True})) == '{"insert": "foo", "attributes": {"bold": true}}'

    def test_retain_str_json(self):
        assert str(Retain('foo', None)) == '{"retain": "foo"}'
        assert str(Retain('foo', {})) == '{"retain": "foo"}'
        assert str(Retain('foo', {'bold': True})) == '{"retain": "foo", "attributes": {"bold": true}}'

    def test_delete_str_json(self):
        assert str(Delete(1)) == '{"delete": 1}'

    def test_delta_as_data(self):
        delta = Delta(ops=[
            Insert('abc', None),
            Retain(1, {'color': 'red'}),
            Delete(4),
            Insert('def', {'bold': True}),
            Retain(6, None)
        ])

        expected = [
            {'insert': 'abc'},
            {'retain': 1, 'attributes': {'color': 'red'}},
            {'delete': 4},
            {'insert': 'def', 'attributes': {'bold': True}},
            {'retain': 6}
        ]

        self.assertListEqual(delta.as_data(), expected)

    def test_delta_as_string(self):
        delta = Delta(ops=[
            Insert('abc', None),
            Retain(1, {'color': 'red'}),
            Delete(3),
        ])

        assert str(delta) == ('[{"insert": "abc"}, '
                              '{"retain": 1, "attributes": {"color": "red"}}, '
                              '{"delete": 3}]')
