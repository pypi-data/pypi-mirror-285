from random import choice

from pistol_magazine import DataMocker


class RandomChoiceFromListProvider(DataMocker):
    def __init__(self, value_list: list = None):
        """
        This class provides random values from the given list.
        If no list is provided, it uses a default list of values.

        Args:
        value_list (list): A list of values to choose from randomly. If None, a default list is used.
        """
        super().__init__()
        if value_list is None:
            value_list = ["default_random1", "default_random2", "default_random3"]
        self.values = value_list

    def gen(self):
        return choice(self.values)
