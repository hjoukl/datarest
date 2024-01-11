import pytest

from datarest.cli import _dict_from

def test__dict_from():
    # Test input with colon characters
    assert _dict_from([]) == {}
    assert _dict_from(['a : b']) == {'a': 'b'}
    assert _dict_from(['a : b ', 'c : d']) == {'a': 'b', 'c' : 'd'}





    

