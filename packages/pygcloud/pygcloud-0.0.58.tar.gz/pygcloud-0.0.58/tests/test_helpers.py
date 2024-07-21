"""@author: jldupont"""
import pytest
from pygcloud.helpers import validate_name, remove_parenthesis


@pytest.mark.parametrize("input,expected", [
    ("name777", True),
    ("9cannot_start_with_digit", False),
    ("name__666", True),
])
def test_validate_name(input, expected):
    assert validate_name(input) == expected


@pytest.mark.parametrize("input,expected", [
    ("(default)", "default"),
    ("no replace", "no replace"),
    ("(many) (replaces)", "many replaces")
])
def test_remove_parenthesis(input, expected):
    assert remove_parenthesis(input)
