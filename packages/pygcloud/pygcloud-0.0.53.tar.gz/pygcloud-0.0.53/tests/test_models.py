"""@author: jldupont"""
import pytest
from dataclasses import dataclass

from pygcloud.models import Param, EnvParam, Result, EnvValue, \
    ServiceGroup, service_groups, LazyEnvValue, LazyAttrValue


def test_env_can_be_modified():
    import os
    os.environ["$$__$$"] = "test"
    assert os.environ["$$__$$"] == "test"


def test_lazy_env_value():
    import os

    lv = None

    with pytest.raises(ValueError):
        lv = LazyEnvValue("$$_$$")
        # need to do something with 'lv' or else
        # it gets compiled-out
        print(lv)

    assert isinstance(lv, LazyEnvValue)

    os.environ["$$_$$"] = "test"

    # __eq__ operator
    assert lv == 'test', print(lv)

    # __ne__ operator
    assert (lv != "test") == False, print(lv)  # NOQA


def test_lazy_env_value2():

    ll = [LazyEnvValue("$??"), "abc"]

    # use repr in order to bypass element wise comparison
    # which would have used LazyEnvValue.__eq__ and thus
    # triggered attempt to get from os.environ
    assert repr(ll) == "[LazyEnvValue($??) = None, 'abc']"

    l2 = list(ll)
    first = l2[0]

    # should not raise
    print(repr(first))


@dataclass
class X:
    NAME = "X"
    PARAM = "X"


@dataclass
class Y(X):
    NAME = "Y"


def test_param():
    p = Param("key", "value")
    assert p.key == "key"


def test_unpack_tuple():

    t = ("key", "value")
    key, value = t

    assert key == "key"
    assert value == "value"


def test_param_as_tuple():
    p = Param("key", "value")
    assert p[0] == "key"
    assert p[1] == "value"

    assert len(p) == 2

    key, value = p
    assert key == "key"
    assert value == "value"


def test_dataclass():
    y = Y()
    assert y.NAME == "Y"
    assert y.PARAM == "X"


def test_sys_env(env_first_key, env_first_value):

    p = EnvParam("--key", env_first_key)

    assert p[0] == "--key"
    assert p[1] == env_first_value


def test_env_value(env_first_key, env_first_value):

    v = EnvValue(env_first_key)

    assert v == env_first_value, \
        print(f"key={env_first_key} , value={env_first_value}")


def test_result_repr():

    r = Result(success=True, message="msg", code=0)
    expected = """Result(success=True, message='msg', code=0)"""

    assert repr(r) == expected, \
        print(r)

    assert str(r) == expected, \
        print(str(r))


def test_service_group_1(env_first_key, env_first_value, mock_service):

    sg = ServiceGroup(EnvValue(env_first_key))

    assert len(sg) == 0

    sg.append(mock_service)

    assert len(sg) == 1

    with pytest.raises(AssertionError):
        sg.append(...)

    assert sg.name == env_first_value


def test_service_groups():

    service_groups.clear()

    sg1 = service_groups.create("sg1")
    sg2 = service_groups.create("sg2")

    # idempotence
    assert sg2 == service_groups.create("sg2"), \
        print(service_groups.all)

    # behaves like a list
    assert len(service_groups) == 2
    assert isinstance(service_groups, list)

    assert sg1.name == "sg1"
    assert sg2.name == "sg2"


@dataclass
class Data:
    d: dict
    e: str
    f: int


data = Data(d={"k": "v", "k2": {"k3": "v3"}}, e="666", f=666)


@pytest.mark.parametrize("obj, path, expected", [
    (data, "d.k",  "v"),
    (data, "e",    "666"),
    (data, "f",    666),
    (data, "d.k2", {"k3": "v3"})
])
def test_lazy_attr_value(obj, path, expected):

    lv = LazyAttrValue(obj, path)

    assert lv == expected, print(lv)
    assert str(lv) == str(expected), print(lv)
