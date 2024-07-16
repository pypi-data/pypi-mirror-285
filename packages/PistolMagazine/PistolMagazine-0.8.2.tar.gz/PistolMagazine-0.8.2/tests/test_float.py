from pistol_magazine import Float

"""
left: The highest digit to the left of the decimal point, default 2 (1 ~ 2)
right: The highest digit to the right of the decimal point, default 2 (1 ~ 2)
unsigned: Whether to include a sign, default False
"""
float = Float(left=2, right=4, unsigned=True)


def test_float():
    print(float.mock())  # e.g. 51.782
    assert float.get_datatype() == 'Float'
