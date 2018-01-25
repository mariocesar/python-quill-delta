import unittest

from quilldelta import Delta, Retain, Insert, Delete


class TestData(unittest.TestCase):
    def test_insert_as_data(self):
        assert Insert('foo', None).asdata() == {'insert': 'foo'}
        assert Insert('foo', {}).asdata() == {'insert': 'foo'}
        assert Insert('foo', {'bold': True}).asdata() == {
            'insert': 'foo',
            'attributes': {'bold': True}
        }
        assert Insert(1, {'img': 'image.jpg'}).asdata() == {
            'insert': 1,
            'attributes': {'img': 'image.jpg'}
        }

    def test_retain_as_data(self):
        assert Retain(1, None).asdata() == {'retain': 1}
        assert Retain(1, {}).asdata() == {'retain': 1}
        assert Retain(1, {'bold': True}).asdata() == {
            'retain': 1,
            'attributes': {'bold': True}
        }

    def test_delete_as_data(self):
        assert Delete(1).asdata() == {'delete': 1}
        assert Delete(2).asdata() == {'delete': 2}

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

        self.assertListEqual(delta.asdata(), expected)


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

        self.assertListEqual(delta.asdata(), expected)

    def test_delta_as_string(self):
        delta = Delta(ops=[
            Insert('abc', None),
            Retain(1, {'color': 'red'}),
            Delete(3),
        ])

        assert str(delta) == ('[{"insert": "abc"}, '
                              '{"retain": 1, "attributes": {"color": "red"}}, '
                              '{"delete": 3}]')
