from unittest import mock

from quilldelta import Delta


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

        assert delta.concat(concat).ops == expected.ops
        assert delta.ops == original.ops


class TestChop:
    def test_retain(self):
        delta = Delta().insert('Test').retain(4)
        expected = Delta().insert('Test')

        assert delta.chop().ops == expected.ops

    def test_insert(self):
        delta = Delta().insert('Test')
        expected = Delta().insert('Test')

        assert delta.chop().ops == expected.ops

    def test_formatted_retain(self):
        delta = Delta().insert('Test').retain(4, {'bold': True})
        expected = Delta().insert('Test').retain(4, {'bold': True})

        assert delta.chop().ops == expected.ops


class TestEachLine:
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
