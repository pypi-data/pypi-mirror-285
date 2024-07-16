from datetime import datetime, timedelta
from random import random

from pistol_magazine.base import _BaseField


class TimeDeltaDescriptor:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        if not isinstance(value, dict):
            raise TypeError(f"{self.name} must be a dictionary")
        valid_keys = {'days', 'seconds', 'microseconds', 'milliseconds', 'minutes', 'hours', 'weeks'}
        for key in value:
            if key not in valid_keys:
                valid_keys_str = ', '.join(valid_keys)
                raise ValueError(f"Invalid key '{key}' for timedelta. Valid keys are: {valid_keys_str}")
        obj.__dict__[self.name] = value


class Timestamp(_BaseField):
    D_TIMEE13 = 13
    D_TIMEE10 = 10

    kwargs = TimeDeltaDescriptor()

    def __init__(self, times: int or str = D_TIMEE13, **kwargs):
        self.current_time = datetime.now()
        self.times = int(times)
        self.kwargs = kwargs

    def mock(self):
        if not self.kwargs:
            return int(self.current_time.timestamp() * (10 ** (self.times-10)))
        else:
            delta = timedelta(**self.kwargs)
            start_time = self.current_time - delta
            end_time = self.current_time + delta
            random_time = start_time + (end_time - start_time) * random()
            return int(random_time.timestamp() * (10 ** (self.times-10)))

    @classmethod
    def match(cls, value):
        now = datetime.now()
        start = now - timedelta(weeks=100)
        end = now + timedelta(weeks=100)
        for times in cls.defined_list:
            try:
                timestamp = value / (10 ** (times - 10))
                if timestamp > 1:
                    date = datetime.fromtimestamp(timestamp)
                    if start < date < end:
                        return times

            except (ValueError, OSError):
                pass

    def get_datatype(self):
        return "_".join([type(self).__name__, str(self.times)])
