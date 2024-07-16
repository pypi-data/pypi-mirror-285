import pytest
from pistol_magazine.bool import Bool


def test_bool_1():
    bool = Bool().mock()
    print(bool)


@pytest.mark.parametrize("test_input,expected", [(True, True), (False, True), ("?", False)], ids=["bool1", "bool2", "str"])
def test_bool_2(test_input, expected):
    assert Bool().match(test_input) is expected
