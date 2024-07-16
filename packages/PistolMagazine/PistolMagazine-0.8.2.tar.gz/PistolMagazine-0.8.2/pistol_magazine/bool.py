from random import getrandbits
from pistol_magazine.base import _BaseField


class Bool(_BaseField):
    def mock(self):
        return bool(getrandbits(1))

    @classmethod
    def match(cls, value):
        return isinstance(value, bool)
