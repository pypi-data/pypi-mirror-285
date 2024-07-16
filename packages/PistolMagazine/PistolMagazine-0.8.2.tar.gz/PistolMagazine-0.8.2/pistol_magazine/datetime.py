from datetime import datetime, timedelta
from random import random

from pistol_magazine.base import _BaseField


class TimeDeltaDescriptor:
    valid_keys = {'days', 'seconds', 'microseconds', 'milliseconds', 'minutes', 'hours', 'weeks'}

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name, {})

    def __set__(self, obj, value):
        if not isinstance(value, dict):
            raise TypeError(f"{self.name} must be a dictionary")
        for key in value:
            if key not in self.valid_keys:
                valid_keys_str = ', '.join(self.valid_keys)
                raise ValueError(f"Invalid key '{key}' for timedelta. Valid keys are: {valid_keys_str}")
        obj.__dict__[self.name] = value


class Datetime(_BaseField):
    D_FORMAT_YMD = "%Y-%m-%d %H:%M:%S"
    D_FORMAT_YMD_T = "%Y-%m-%dT%H:%M:%S"

    kwargs = TimeDeltaDescriptor()

    def __init__(self, date_format=D_FORMAT_YMD, **kwargs):
        self.date_format = date_format
        self.kwargs = kwargs

    def mock(self):
        current_time = datetime.now()
        if not self.kwargs:
            return current_time.strftime(self.date_format)
        else:
            delta = timedelta(**self.kwargs)
            start_time = current_time - delta
            end_time = current_time + delta
            random_time = start_time + (end_time - start_time) * random()
            return random_time.strftime(self.date_format)

    @classmethod
    def match(cls, value):
        for date_format in cls.defined_list:
            try:
                datetime.strptime(value, date_format)
                return date_format
            except ValueError:
                continue

    def get_datatype(self):
        return "_".join([type(self).__name__, str(self.date_format)])
