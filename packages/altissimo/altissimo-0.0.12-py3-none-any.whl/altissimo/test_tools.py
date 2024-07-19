"""Altissimo Tools Tests file."""
import types

from .tools import chunks
from .tools import list_to_dict

fake_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

fake_dict_list = [
    {"id": 1, "name": "one", "key": "one", "value": 1},
    {"id": 2, "name": "two", "key": "two", "value": 1},
    {"id": 3, "name": "three", "key": "three", "value": 1},
    {"id": 4, "name": "four", "key": "four", "value": 1},
    {"id": 5, "name": "five", "key": "five", "value": 1},
    {"id": 6, "name": "six", "key": "six", "value": 2},
    {"id": 7, "name": "seven", "key": 0, "value": 2},
    {"id": 8, "name": "eight", "key": "", "value": 2},
    {"id": 9, "name": "nine", "key": None, "value": 2},
    {"id": 10, "name": "ten", "value": 2},
]


def test_chunks_generator():
    """Test that chunks returns a generator."""
    assert isinstance(chunks(fake_list, 4), types.GeneratorType)


def test_chunks_list_length():
    """Test that chunks returns the correct number of chunks."""
    assert len(list(chunks(fake_list, 4))) == 5


def test_chunks_list():
    """Test that chunks returns the correct chunks."""
    assert list(chunks(fake_list, 3)) == [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12],
        [13, 14, 15],
        [16, 17, 18],
        [19, 20]
    ]
    assert list(chunks(fake_list, 4)) == [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
        [17, 18, 19, 20]
    ]
    assert list(chunks(fake_list, 5)) == [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
        [11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20]
    ]


def test_list_to_dict_dict():
    """Test that list_to_dict returns a dictionary."""
    assert isinstance(list_to_dict(fake_dict_list), dict)


def test_list_to_dict_length():
    """Test that list_to_dict returns the correct number of items."""
    assert len(list_to_dict(fake_dict_list)) == len(fake_dict_list)


def test_list_to_dict_duplicate_keys():
    """Test that list_to_dict properly handles duplicate keys."""
    assert len(list_to_dict(fake_dict_list, key="value")) == 2


def test_list_to_dict_false_keys():
    """Test that list_to_dict properly handles keys that evaluate to false."""
    assert len(list_to_dict(fake_dict_list, key="key")) == 8
