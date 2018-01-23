from quilldelta.quilldelta.delta import Delta


class TestCompose:
    def test_insert_insert(self):
        a = Delta().insert('A')
        b = Delta().insert('B')
        expected = Delta().insert('B').insert('A')
        delta = a.compose(b)
        assert delta == expected, [delta.ops, expected.ops]

    def test_insert_retain(self):
        a = Delta().insert('A')
        b = Delta().retain(1, {'bold': True})
        expected = Delta().insert('A', {'bold': True})
        delta = a.compose(b)
        assert delta == expected, [delta.ops, expected.ops]

    def test_insert_delete(self):
        a = Delta().insert('A')
        b = Delta().delete(1)
        expected = Delta()
        delta = a.compose(b)
        assert delta == expected, [delta.ops, expected.ops]

    def test_delete_insert(self):
        a = Delta().delete(1)
        b = Delta().insert('B')
        expected = Delta().insert('B').delete(1)
        delta = a.compose(b)
        assert delta == expected, [delta.ops, expected.ops]

    def test_delete_retain(self):
        a = Delta().delete(1)
        b = Delta().retain(1, {'bold': True})
        expected = Delta().delete(1).retain(1, {'bold': True})
        delta = a.compose(b)
        assert delta == expected, [delta.ops, expected.ops]
