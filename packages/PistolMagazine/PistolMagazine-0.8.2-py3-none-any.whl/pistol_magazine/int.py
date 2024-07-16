import random

from pistol_magazine.base import _BaseField


class Int(_BaseField):

    def __init__(self, byte_nums=64, unsigned=False):
        if unsigned:
            min_num = 0
            max_num = 2 ** byte_nums - 1
        else:
            min_num = -2 ** (byte_nums - 1)
            max_num = 2 ** (byte_nums - 1) - 1
        self.args = [min_num, max_num]

    def mock(self):
        return random.randint(*self.args)


class UInt(Int):

    def __init__(self):
        super().__init__(64, True)


class UInt8(Int):
    def __init__(self):
        super().__init__(8, True)


class Int8(Int):
    def __init__(self):
        super().__init__(8, False)


class UInt16(Int):
    def __init__(self):
        super().__init__(16, True)


class Int16(Int):
    def __init__(self):
        super().__init__(16, False)


class UInt32(Int):
    def __init__(self):
        super().__init__(32, True)


class Int32(Int):
    def __init__(self):
        super().__init__(32, False)
