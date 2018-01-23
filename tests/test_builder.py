import pytest

from quilldelta import Delta, Insert, Retain, Delete


class TestConstructor:
    @pytest.fixture
    def dict_ops(self):
        return [
            {'insert': 'abc'},
            {'retain': 1, 'attributes': {'color': 'red'}},
            {'delete': 4},
            {'insert': 'def', 'attributes': {'bold': True}},
            {'retain': 6}
        ]

    @pytest.fixture
    def inst_ops(self):
        return [
            Insert('abc', None),
            Retain(1, {'color': 'red'}),
            Delete(4),
            Insert('def', {'bold': True}),
            Retain(6, None)
        ]

    def test_empty(self):
        delta = Delta()

        assert len(delta.ops) == 0

    def test_empty_ops(self):
        delta = Delta()
        delta.insert('').delete(0).retain(0)

        assert len(delta.ops) == 0

    def test_array_of_ops(self, dict_ops, inst_ops):
        delta = Delta(dict_ops)
        assert delta.ops == inst_ops

    def test_delta_in_object_form(self, dict_ops, inst_ops):
        delta = Delta({'ops': dict_ops})
        assert delta.ops == inst_ops

    def test_delta(self, dict_ops, inst_ops):
        original = Delta(inst_ops)
        delta = Delta(original)

        assert delta.ops == original.ops


class TestInsert:
    def test_insert_text(self):
        delta = Delta().insert('test')

        assert len(delta.ops) == 1
        assert delta.ops == [Insert('test', None)]

    def test_insert_text_none(self):
        delta = Delta().insert('test', None)

        assert len(delta.ops) == 1
        assert delta.ops == [Insert('test', None)]

    def test_insert_embed(self):
        delta = Delta().insert(1)

        assert len(delta.ops) == 1
        assert delta.ops == [Insert(1, None)]

    def test_insert_embed_attributes(self):
        obj = {'url': 'https://quilljs.com', 'alt': 'Quill'}
        delta = Delta().insert(1, obj)

        assert len(delta.ops) == 1
        assert delta.ops == [Insert(1, obj)]

    def test_insert_embed_non_integer(self):
        value = {'url': 'https://quilljs.com'}
        attrs = {'alt': 'Quill'}
        delta = Delta().insert(value, attrs)

        assert len(delta.ops) == 1
        assert delta.ops == [Insert(value, attrs)]

    def test_insert_text_attributes(self):
        delta = Delta().insert('test', {'bold': True})

        assert len(delta.ops) == 1
        assert delta.ops == [Insert('test', {'bold': True})]

    def test_insert_text_after_delete(self):
        delta = Delta().delete(1).insert('a')
        expected = Delta().insert('a').delete(1)

        assert delta == expected, [delta.ops, expected.ops]

    def test_insert_text_after_delete_with_merge(self):
        delta = Delta().insert('a').delete(1).insert('b')
        expected = Delta().insert('ab').delete(1)

        assert delta == expected, [delta.ops, expected.ops]

    def test_insert_text_after_delete_no_merge(self):
        delta = Delta().insert(1).delete(1).insert('a')
        expected = Delta().insert(1).insert('a').delete(1)

        assert delta == expected, [delta.ops, expected.ops]

    def test_insert_text_empty_attributes(self):
        delta = Delta().insert('a', {})
        expected = Delta().insert('a')

        assert delta == expected, [delta.ops, expected.ops]

    def test_delta_insert_text(self):
        delta = Delta()

        assert delta.ops == []

        delta = (delta
                 .insert('Hello', None)
                 .insert(' ', None)
                 .insert('World!', None))

        assert len(delta.ops) == 1, delta.ops
        assert delta.ops == [Insert('Hello World!', None)]

        delta.insert('\n', None)
        delta.insert('Hello World', None)
        delta.insert('!', None)

        assert len(delta.ops) == 1, delta.ops
        assert delta.ops == [Insert('Hello World!\nHello World!', None)]


class TestDelete:
    def test_delete_0(self):
        delta = Delta().delete(0)
        assert delta.ops == []

    def test_delete_positive(self):
        delta = Delta().delete(1)
        assert len(delta.ops) == 1
        assert delta.ops == [Delete(1)]

    def test_delta_delete_text(self):
        delta = (Delta()
                 .insert('foo')
                 .insert(' ')
                 .insert('bar'))

        assert delta.ops == [Insert('foo bar', None)]

        delta.delete(2).delete(2)

        delta.insert(' ')
        delta.insert('baz')

        assert delta.ops == [Insert('foo bar baz', None), Delete(4)]


class TestRetain:
    def test_retain_0(self):
        delta = Delta().retain(0)
        assert delta.ops == []

    def test_retain_length(self):
        delta = Delta().retain(2)
        assert len(delta.ops) == 1
        assert delta.ops == [Retain(2, None)]

    def test_retain_length_none(self):
        delta = Delta().retain(2, None)
        assert len(delta.ops) == 1
        assert delta.ops == [Retain(2, None)]

    def test_retain_length_attributes(self):
        delta = Delta().retain(1, {'bold': True})
        assert len(delta.ops) == 1
        assert delta.ops == [Retain(1, {'bold': True})]

    def test_retain_length_empty_attributes(self):
        delta = Delta().retain(1, {})
        assert len(delta.ops) == 1
        assert delta.ops == [Retain(1, None)]


class TestPush:
    def test_push_into_empty(self):
        delta = Delta()
        delta.push({'insert': 'test'})
        assert len(delta.ops) == 1

    def test_push_consecutive_delete(self):
        delta = Delta().delete(2)
        delta.push({'delete': 3})

        assert len(delta.ops) == 1
        assert delta.ops == [Delete(5)]

    def test_push_consecutive_text(self):
        delta = Delta().insert('a')
        delta.push({'insert': 'b'})

        assert len(delta.ops) == 1
        assert delta.ops == [Insert('ab', None)]

    def test_push_consecutive_text_with_matching_attributes(self):
        delta = Delta().insert('a', {'bold': True})
        delta.push({'insert': 'b', 'attributes': {'bold': True}})

        assert len(delta.ops) == 1
        assert delta.ops == [Insert('ab', {'bold': True})]

    def test_push_consecutive_retain_with_matching_attributes(self):
        delta = Delta().retain(1, {'bold': True})
        delta.push({'retain': 3, 'attributes': {'bold': True}})

        assert len(delta.ops) == 1
        assert delta.ops == [Retain(4, {'bold': True})]

    def test_push_consecutive_text_with_not_matching_attributes(self):
        delta = Delta().insert('a', {'bold': True})
        delta.push({'insert': 'b'})

        assert len(delta.ops) == 2
        assert delta.ops == [
            Insert('a', {'bold': True}),
            Insert('b', None)
        ]

    def test_push_consecutive_retain_with_not_matching_attributes(self):
        delta = Delta().retain(1, {'bold': True})
        delta.push({'retain': 3})

        assert len(delta.ops) == 2
        assert delta.ops == [
            Retain(1, {'bold': True}),
            Retain(3, None)
        ]

    def test_push_consecutive_embeds_with_matching_attributes(self):
        delta = Delta().insert(1, {'alt': 'Description'})
        delta.push({'insert': {'url': 'http://quilljs.com'}, 'attributes': {'alt': 'Description'}})

        assert len(delta.ops) == 2
        assert delta.ops == [
            Insert(1, {'alt': 'Description'}),
            Insert({'url': 'http://quilljs.com'}, {'alt': 'Description'})
        ]
