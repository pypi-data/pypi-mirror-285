from pistol_magazine import *


def test_list():
    list = List()
    # Default [str, int, float], e.g. ['involve', 6642899413184882178, 65.23]
    print(list.mock())

    expect_format = [
        Datetime(Datetime.D_FORMAT_YMD, days=2),
        Timestamp(Timestamp.D_TIMEE10, days=2),
        Float(left=2, right=4, unsigned=True),
        Str(data_type="file_name"),
        Int(byte_nums=6, unsigned=True),
        ProviderField(
            RegexProvider(pattern=r"\d{3}-[a-z]{2}").get_value
        )
    ]
    print(List(expect_format).mock(to_json=True))  # e.g. '["2024-06-25 21:45:16", 1719483880, 76.4993, "coach.csv", 62]'
    print(List(expect_format).get_datatype())
