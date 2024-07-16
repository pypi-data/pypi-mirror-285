from pistol_magazine import Int, Int8, Int16, Int32, UInt, UInt8, UInt16, UInt32

"""
Signed integer: The range is from -2^(n-1) to 2^(n-1) - 1 (n is the number of bits). Default n = 64.
"""
int = Int()  # n=64

int8 = Int8()  # n=8

int16 = Int16()  # n=16

int32 = Int32()  # n=32

"""
Unsigned integer: The range is from 0 to 2^n - 1 (n is the number of bits).Default n = 64.
"""
uint = UInt()  # n=64

uint8 = UInt8()  # n=8

uint16 = UInt16()  # n=16

uint32 = UInt32()  # n=32

int_cus1 = Int(byte_nums=4, unsigned=False)  # [-8, 7]

int_cus2 = Int(byte_nums=4, unsigned=True)  # [0, 15]


def test_int():
    print(int.mock())  # e.g.-6369700457507597669
    print(uint8.mock())  # e.g.217
    print(int_cus1.mock())  # e.g. 5
    print(int_cus2.mock())  # e.g. 14
