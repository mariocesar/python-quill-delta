from functools import reduce

import pytest

from quilldelta import Delete, Insert, Retain


class TestInsert:
    def test_insert_constructor(self):
        op = Insert('foo', None)

        assert op.value == 'foo'
        assert op.attributes is None
        assert op.length == 3

        op = Insert(1, None)

        assert op.value == 1
        assert op.attributes is None

    def test_insert_attributes(self):
        op = Insert('foo', {'bold': True})

        assert op.attributes == {'bold': True}

    def test_parse(self):
        op = Insert.fromdict({'insert': 'foo'})

        assert op.value == 'foo'
        assert op.attributes is None

    def test_insert_embed(self):
        op = Insert({'image': 'photo.jpg'}, None)

        assert op.value == {'image': 'photo.jpg'}
        assert op.attributes is None

        assert op.length == 1

    def test_as_data(self):
        op = Insert('foo', {'bold': True})

        assert op.as_data() == {'insert': 'foo', 'attributes': {'bold': True}}

    def test_as_json(self):
        op = Insert('foo', {'bold': True})

        assert op.as_json() == '{"insert": "foo", "attributes": {"bold": true}}'

    def test_sum_operation(self):
        op = Insert('foo', None) + Insert(' bar', None)
        assert op == Insert('foo bar', None)

        op = reduce(lambda o, other: o + other, [
            Insert('foo', None),
            Insert(' ', None),
            Insert('bar', None)])

        assert op == Insert('foo bar', None)

        op = Insert('foo', {'bold': True}) + Insert(' bar', {'bold': True})
        assert op == Insert('foo bar', {'bold': True})

        with pytest.raises(ValueError) as err:
            Insert('foo', None) + 'bar'

        assert err.match('Operations are not from the same type')

        with pytest.raises(ValueError) as err:
            Insert('foo', {'bold': True}) + Insert(' bar', {'bold': False})

        assert err.match('operations with different attributes')


class TestRetain:
    def test_retain_constructor(self):
        op = Retain(1, None)

        assert op.value == 1
        assert op.length == 1
        assert op.attributes is None

    def test_retain_attributes(self):
        op = Retain(1, {'bold': True})

        assert op.attributes == {'bold': True}

    def test_parse(self):
        op = Retain.fromdict({'retain': 1})

        assert op.value == 1
        assert op.length == 1
        assert op.attributes is None

    def test_as_data(self):
        op = Retain(1, {'bold': True})

        assert op.as_data() == {'retain': 1, 'attributes': {'bold': True}}

    def test_as_json(self):
        op = Retain(1, {'bold': True})

        assert op.as_json() == '{"retain": 1, "attributes": {"bold": true}}'

    def test_sum_operation(self):
        op = Retain(1, None) + Retain(2, None)
        assert op == Retain(3, None)

        op = reduce(lambda o, other: o + other, [
            Retain(1, None),
            Retain(2, None),
            Retain(3, None)])

        assert op == Retain(6, None)

        op = Retain(1, {'bold': True}) + Retain(2, {'bold': True})
        assert op == Retain(3, {'bold': True})

        with pytest.raises(ValueError) as err:
            Retain(1, None) + Insert('foo', None)

        assert err.match('Operations are not from the same type')

        with pytest.raises(ValueError) as err:
            Retain(1, {'bold': True}) + Retain(1, {'bold': False})

        assert err.match('operations with different attributes')


class TestDelete:
    def test_retain_constructor(self):
        op = Delete(1)

        assert op.value == 1
        assert op.length == 1

    def test_parse(self):
        op = Delete.fromdict({'delete': 1})

        assert isinstance(op, Delete)
        assert op.value == 1
        assert op.length == 1

    def test_as_data(self):
        op = Delete(1)

        assert op.as_data() == {'delete': 1}

    def test_as_json(self):
        op = Delete(1)

        assert op.as_json() == '{"delete": 1}'

    def test_sum_operation(self):
        op = Delete(1) + Delete(2)
        assert op == Delete(3)

        op = reduce(lambda o, other: o + other, [
            Delete(1),
            Delete(2),
            Delete(3)])

        assert op == Delete(6)

        with pytest.raises(ValueError) as err:
            Delete(1) + Insert('foo', None)

        assert err.match('Operations are not from the same type')
