import copy
from abc import abstractmethod
from faker import Faker


class _MetaField(type):
    name_map = {}
    fake = Faker()

    def __new__(mcs, clsname, bases, clsdict):
        clsdict["name_map"] = mcs.name_map
        clsdict["fake"] = mcs.fake
        if bases:
            defined_list = copy.copy(bases[0].defined_list)
        else:
            defined_list = []
        for key, value in clsdict.items():
            if key.startswith('D_'):
                defined_list.append(value)
        clsdict["defined_list"] = defined_list
        new_cls = type.__new__(mcs, clsname, bases, clsdict)
        mcs.name_map[clsname] = new_cls
        return new_cls


class _BaseField(metaclass=_MetaField):
    name_map: dict
    fake: Faker
    defined_list: list

    @abstractmethod
    def mock(self):
        return "base"

    def get_datatype(self):
        return type(self).__name__
