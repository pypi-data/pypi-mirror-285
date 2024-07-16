from random import uniform

from pistol_magazine import DataMocker


class RandomFloatInRangeProvider(DataMocker):
    def __init__(self, start=0.0, end=1.0, precision=2):
        """
        This class provides random float values within a specified range and precision.

        Args:
        start (float): The starting range. Defaults to 0.0.
        end (float): The ending range. Defaults to 1.0.
        precision (int): The number of decimal places to round to. Defaults to 2.
        """
        super().__init__()
        self.start = start
        self.end = end
        self.precision = precision

    def gen(self):
        """
        Returns a random float value within the specified range rounded to the specified precision.

        Returns:
        A random float value between start and end, rounded to the specified number of decimal places.
        """
        value = uniform(self.start, self.end)
        return round(value, self.precision)
