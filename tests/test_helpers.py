from unittest import TestCase, mock

import pytest

from quilldelta import Delta, Insert


class TestConcat:
    def test_empty_delta(self):
        delta = Delta().insert('Test')
        concat = Delta()
        expected = Delta().insert('Test')
        assert delta.concat(concat).ops == expected.ops

        assert concat.concat(delta).ops == expected.ops

    def test_unmergeable(self):
        delta = Delta().insert('Test')
        original = Delta().insert('Test')
        concat = Delta().insert('!', {'bold': True})
        expected = Delta().insert('Test').insert('!', {'bold': True})

        assert delta.concat(concat).ops == expected.ops
        assert delta.ops == original.ops

    def test_mergeable(self):
        delta = Delta().insert('Test', {'bold': True})
        original = Delta().insert('Test', {'bold': True})

        concat = Delta().insert('!', {'bold': True}).insert('\n')
        expected = Delta().insert('Test!', {'bold': True}).insert('\n')

        assert delta.concat(concat) == expected
        assert delta.ops == original.ops


class TestChop:
    def test_chop_retain(self):
        delta = Delta().insert('Test').retain(4)
        expected = Delta().insert('Test')

        assert delta.chop().ops == expected.ops

    def test_chop_insert(self):
        delta = Delta().insert('Test')
        expected = Delta().insert('Test')

        assert delta.chop().ops == expected.ops

    def test_chop_formatted_retain(self):
        delta = Delta().insert('Test').retain(4, {'bold': True})
        expected = Delta().insert('Test').retain(4, {'bold': True})

        assert delta.chop().ops == expected.ops


class TestIteration(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delta = (Delta()
                     .insert('Hello')
                     .insert({'image': True})
                     .insert('World !'))

    def test_filter(self):
        ops = self.delta.ops.filter(lambda op: isinstance(op, Insert))

        assert len(ops) == 3

        ops = (ops.filter(lambda op: isinstance(op.value, str)))

        assert len(ops) == 2

    def test_foreach(self):
        spy_mock = mock.MagicMock()

        for op in self.delta.ops:
            spy_mock(op)

        assert spy_mock.call_count == 3

        assert spy_mock.call_args_list == [
            mock.call(Insert('Hello', None)),
            mock.call(Insert({'image': True}, None)),
            mock.call(Insert('World !', None))
        ]

    def test_map(self):
        def filterfunc(op):
            if isinstance(op, Insert):
                if isinstance(op.value, str):
                    return op.value
                return ''

        ops = list(map(filterfunc, self.delta.ops))

        assert ops == ['Hello', '', 'World !']

    def test_partition(self):
        def string_inserts(op):
            if isinstance(op, Insert):
                if isinstance(op.value, str):
                    return op.value
                return ''

        passed, failed = self.delta.partition(string_inserts)

        assert passed == [self.delta.ops[0], self.delta.ops[2]]
        assert failed == [self.delta.ops[1]]


class TestEachLine:
    @pytest.mark.skip
    def test_expected(self):
        delta = (Delta().insert('Hello\n\n')
                 .insert('World', {'bold': True})
                 .insert({'image': 'octocat.png'})
                 .insert('\n', {'align': 'right'})
                 .insert('!'))

        predicate = mock.Mock()
        delta.each_line(predicate)

        assert predicate.call_count == 4
        call_args = predicate.call_args_list

        assert call_args[0] == (Delta().insert('Hello'), {}, 0)
