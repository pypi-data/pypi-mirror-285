import itertools

from pistol_magazine import DataMocker, provider


@provider
class CyclicParameterProvider(DataMocker):
    def __init__(self, parameter_list: list = None):
        """
        This class provides parameters in a cyclic manner from the given list.
        If no list is provided, it uses a default list of parameters.
        :param parameter_list: A list of parameters to cycle through. If None, a default list is used.
        """
        super().__init__()
        if parameter_list is None:
            parameter_list = ["default_param1", "default_param2", "default_param3"]
        self.parameters = itertools.cycle(parameter_list)

    def gen(self):
        return next(self.parameters)
