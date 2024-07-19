"""
@author: jldupont
"""
import re

REGEX_VALIDATE_NAME = re.compile(r"^[a-zA-Z][0-9a-zA-Z\_\-]{0,62}$")


def validate_name(name: str) -> bool:
    if not isinstance(name, str):
        return False

    return REGEX_VALIDATE_NAME.match(name) is not None


def remove_parenthesis(name: str) -> str:
    assert isinstance(name, str)

    return name.replace("(", "").replace(")", "")
