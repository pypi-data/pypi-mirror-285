from pistol_magazine import DataMocker


class IncrementalValueProvider(DataMocker):
    def __init__(self, start=0, step=1):
        """
        This class provides incrementing values starting from a given value.

        Args:
        start (int): The starting value. Defaults to 0.
        step (int): The step value for each increment. Defaults to 1.
        """
        super().__init__()
        self.current = start
        self.step = step

    def gen(self):
        value = self.current
        self.current += self.step
        return value
