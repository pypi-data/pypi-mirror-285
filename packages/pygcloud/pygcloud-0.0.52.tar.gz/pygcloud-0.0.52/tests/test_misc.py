import pytest


def test_member_assignment():

    class X:
        def assign(self, param):
            """param was not assigned a value
            during initialization"""
            self.param = param

    x = X()

    with pytest.raises(AttributeError):
        assert x.param is None

    x.assign("value")

    assert x.param == "value"
