"""Test validation helpers."""

from pydid.validation import unwrap_if_list_of_one, single_to_list


def test_unwrap_if_list_of_one():
    assert 1 == unwrap_if_list_of_one([1])
    assert [1, 2] == unwrap_if_list_of_one([1, 2])


def test_single_to_list():
    assert [1] == single_to_list(1)
    assert [1, 2] == single_to_list([1, 2])
