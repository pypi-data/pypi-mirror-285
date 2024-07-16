from pistol_magazine import Timestamp


def test_timestamp():
    # Unix Timestamp, len=10
    timestamp1 = Timestamp(Timestamp.D_TIMEE10)
    # Millisecond Timestamp, len=13
    timestamp2 = Timestamp(Timestamp.D_TIMEE13)
    # Unix Timestamp, len=10, random timestamp within the range from (NOW - 2 days) to (NOW + 2 days)
    timestamp3 = Timestamp(Timestamp.D_TIMEE10, days=2)

    print(timestamp1.mock())  # Now, len=10
    print(timestamp2.mock())  # Now, len=13
    print(timestamp3.mock())  # e.g. 1717598215

    # Generate a timestamp with the same length as the given timestamp,
    # and within the range from (NOW - 1weeks) to (NOW + 1weeks), e.g. 1717759793
    print(Timestamp(Timestamp.match(1717598215), weeks=1).mock())
