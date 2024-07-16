from . import data_structures


def test_flatten_dict_works():
    data = {
        'a': {
            1: True,
            2: False
        },
        'b': {
            3: 'Hi',
            10: 'Bye',
        }
    }
    observed = data_structures.flatten_nested_dict(data)
    expected = {
        ('a', 1): True,
        ('a', 2): False,
        ('b', 3): 'Hi',
        ('b', 10): 'Bye',
    }
    assert observed == expected

def test_items():
    data = {'a': 1, 'b': 'hi'}
    observed = data_structures.items(data)
    expected = [('a', 1), ('b', 'hi')]
    assert observed == expected

def test_promote_key_list_of_dicts():
    data = [
        {'A': {'a': 1, 'b': [10, 20, 30]}},
        {'A': {'a': 10, 'b': [100, 200, 300]}}
    ]
    observed = data_structures.promote_key(data, key='newkey', attrs=['A', 'b', 1])
    expected = [
        {'A': {'a': 1, 'b': [10, 20, 30]}, 'newkey': 20},
        {'A': {'a': 10, 'b': [100, 200, 300]}, 'newkey': 200},
    ]
    assert observed == expected


def test_promote_key_dict_of_dicts():
    data = {
        'first': {'A': {'a': 1, 'b': [10, 20, 30]}},
        'second': {'A': {'a': 10, 'b': [100, 200, 300]}}
    }
    observed = data_structures.promote_key(data, key='newkey', attrs=['A', 'b', 1])
    expected = {
        'first': {'A': {'a': 1, 'b': [10, 20, 30]}, 'newkey': 20},
        'second': {'A': {'a': 10, 'b': [100, 200, 300]}, 'newkey': 200},
    }
    assert observed == expected


def test_multi_index():
    data = {'a': {'b': [10, 20, 30]}}
    observed = data_structures.multi_index(data, ['a', 'b', 1])
    expected = 20
    assert observed == expected


def test_sort_by():
    data = [
        (12, {'a': [4, {'A': 200, 'B': 200}]}),
        (65, {'a': [4, {'A': 50, 'B': 200}]}),
        (25, {'a': [4, {'A': 100, 'B': 200}]}),
    ]

    # A should be ascending
    observed = data_structures.sort_by(data, [1, 'a', 1, 'A'])
    expected = [
        (65, {'a': [4, {'A': 50, 'B': 200}]}),
        (25, {'a': [4, {'A': 100, 'B': 200}]}),
        (12, {'a': [4, {'A': 200, 'B': 200}]}),
    ]
    assert observed == expected

    # When reversed, A should be descending
    # A should be ascending
    observed = data_structures.sort_by(data, [1, 'a', 1, 'A'], reverse=True)
    expected = [
        (12, {'a': [4, {'A': 200, 'B': 200}]}),
        (25, {'a': [4, {'A': 100, 'B': 200}]}),
        (65, {'a': [4, {'A': 50, 'B': 200}]}),
    ]
    assert observed == expected
    
