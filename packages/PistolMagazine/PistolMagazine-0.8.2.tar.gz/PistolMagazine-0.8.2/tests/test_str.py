from pistol_magazine import Str, StrInt, StrFloat, StrTimestamp


def test_str():
    str = Str()
    print(str.mock())  # e.g. court
    print(str.match("123").mock())  # e.g.-6559854688025321017 <str type>
    print(str.match("information").mock())  # e.g. figure <str type>
    print(str.match("2.3").mock())  # e.g. 48.27 <str type>
    str_customize = Str(data_type="name")  # Support 'email', 'word'(Default), 'address', 'license_plate', 'name'
    print(str_customize.mock())  # e.g. Michelle Mendez


def test_str_int():
    str_int = StrInt(byte_nums=6, unsigned=True)
    print(str_int.mock())  # e.g. 123456 <str type>


def test_str_float():
    str_float = StrFloat(left=3, right=5, unsigned=True)
    print(str_float.mock())  # e.g. -466.40951 <str type>


def test_str_timestamp():
    # Unix Timestamp, len=10 <str type>
    str_timestamp1 = StrTimestamp(StrTimestamp.D_TIMEE10)
    # Millisecond Timestamp, len=13 <str type>
    str_timestamp2 = StrTimestamp(StrTimestamp.D_TIMEE13)
    # Unix Timestamp, len=10, random timestamp within the range from (NOW - 2 days) to (NOW + 2 days) <str type>
    str_timestamp3 = StrTimestamp(StrTimestamp.D_TIMEE10, days=2)

    print(str_timestamp1.mock())  # Now, len=10 <str type>
    print(str_timestamp2.mock())  # Now, len=13 <str type>
    print(str_timestamp3.mock())  # e.g. 1717598215 <str type>

    # Generate a timestamp with the same length as the given timestamp,
    # and within the range from (NOW - 1weeks) to (NOW + 1weeks), e.g. 1717759793 <str type>
    print(StrTimestamp(StrTimestamp.match('1717598215'), weeks=1).mock())

