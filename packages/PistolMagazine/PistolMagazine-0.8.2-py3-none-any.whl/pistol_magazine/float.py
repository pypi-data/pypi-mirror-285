from pistol_magazine.base import _BaseField


class Float(_BaseField):
    def __init__(self, left=2, right=2, unsigned=False):
        self.left = int(left)
        self.right = int(right)
        self.unsigned = unsigned

    def mock(self):
        result = self.fake.pyfloat(self.left, self.right)
        if not self.unsigned:
            result = abs(result)
        return result

    def get_datatype(self):
        return type(self).__name__
