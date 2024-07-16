from pistol_magazine import Datetime


def test_datetime():
    # "%Y-%m-%d %H:%M:%S"
    datetime1 = Datetime(Datetime.D_FORMAT_YMD)
    # "%Y-%m-%dT%H:%M:%S"
    datetime2 = Datetime(Datetime.D_FORMAT_YMD_T)
    # Random datetime within the range from (NOW - 2 days) to (NOW + 2 days), format "%Y-%m-%d %H:%M:%S"
    datetime3 = Datetime(Datetime.D_FORMAT_YMD, days=2)

    print(datetime1.mock())  # Now, e.g. 2024-06-05 16:24:16
    print(datetime2.mock())  # Now, e.g. 2024-06-05T16:24:16
    print(datetime3.mock())  # e.g. 2024-06-04 11:48:41

    # Generate a datetime with the same format as the given datetime,
    # and within the range from (NOW - 1weeks) to (NOW + 1weeks), e.g. 2024-06-10 16:38:17
    print(Datetime(Datetime.match('2024-06-05 16:24:16'), weeks=1).mock())
