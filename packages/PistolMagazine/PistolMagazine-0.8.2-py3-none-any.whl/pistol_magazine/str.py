from pistol_magazine.base import _BaseField
from datetime import datetime


class DataTypeDescriptor:
    def __init__(self, fake_instance):
        self._fake_instance = fake_instance
        self._valid_data_types = {name for name in dir(fake_instance) if not name.startswith('_')}
        self._invalid_data_types = {
            'weights', 'optional', 'get_formatter', 'provider', 'add_provider', 'set_formatter',
            'xml', 'parse', 'unique', 'format', 'cache_pattern', 'providers', 'seed_locale',
            'locales', 'get_arguments', 'enum', 'set_arguments', 'generator_attrs', 'factories',
            'seed', 'random', 'del_arguments'
        }

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get('data_type')

    def __set__(self, instance, value):
        if value not in self._valid_data_types or value in self._invalid_data_types:
            raise ValueError(f"Unsupported data type: {value}. Must be one of {self._valid_data_types.difference(self._invalid_data_types)}")
        instance.__dict__['data_type'] = value


class Str(_BaseField):
    data_type = DataTypeDescriptor(_BaseField.fake)

    def __init__(self, data_type="word"):
        self.data_type = data_type

    def mock(self):
        generator = getattr(self.fake, self.data_type, None)
        if generator is None:
            raise ValueError(f"No such generator for data type: {self.data_type}")
        return generator()

    @classmethod
    def match(cls, value: str):
        if value.isdigit():
            return StrInt()
        else:
            try:
                float(value)
                return StrFloat()
            except ValueError:
                return Str()


class StrInt(_BaseField):

    def __init__(self, byte_nums=64, unsigned=False):
        self.byte_nums = byte_nums
        self.unsigned = unsigned
        if unsigned:
            min_num = 0
            max_num = 2 ** byte_nums - 1
        else:
            min_num = -2 ** (byte_nums - 1)
            max_num = 2 ** (byte_nums - 1) - 1
        self.args = [min_num, max_num]

    def mock(self):
        from pistol_magazine.int import Int
        int_instance = Int(self.byte_nums, self.unsigned)
        return str(int_instance.mock())


class StrFloat(_BaseField):
    def __init__(self, left=2, right=2, unsigned=False):
        self.left = int(left)
        self.right = int(right)
        self.unsigned = unsigned

    def mock(self):
        from pistol_magazine.float import Float
        float_instance = Float(self.left, self.right, self.unsigned)
        return str(float_instance.mock())

    def get_datatype(self):
        return type(self).__name__


class StrTimestamp(_BaseField):
    D_TIMEE13 = 13
    D_TIMEE10 = 10

    def __init__(self, times: int or str = D_TIMEE13, **kwargs):
        self.current_time = datetime.now()
        self.times = int(times)
        self.kwargs = kwargs

    def mock(self):
        from pistol_magazine import Timestamp
        return str(Timestamp(self.times, **self.kwargs).mock())

    @classmethod
    def match(cls, value: str):
        if value.isdigit():
            from pistol_magazine import Timestamp
            result = Timestamp.match(int(value))
            return result
