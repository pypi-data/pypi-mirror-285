import rstr
from pistol_magazine import DataMocker


class RegexProvider(DataMocker):
    def __init__(self, pattern):
        """
        This class generates values that match a given regular expression pattern.

        Args:
        pattern: The regular expression pattern to generate matching values for.
        """
        super().__init__()
        self.pattern = pattern

    def gen(self):
        """
        Returns a value generated to match the regular expression pattern.

        Returns:
        A string value that matches the regular expression pattern.
        """
        return rstr.xeger(self.pattern)
