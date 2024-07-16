import json

from pistol_magazine.base import _BaseField


class List(_BaseField):
    def __init__(self, list_fields: list = None):
        from pistol_magazine.float import Float
        from pistol_magazine.int import Int
        from pistol_magazine.str import Str
        if list_fields is None:
            self.list_fields = [Str(), Int(), Float()]
        else:
            self.list_fields = list_fields
        # self.mock()

    def mock(self, to_json: bool = False):
        data = [i.mock() for i in self.list_fields]
        if to_json:
            if not isinstance(data, list):
                raise TypeError("Expected a list for JSON serialization.")
            return json.dumps(data)
        else:
            return data

    def get_datatype(self):
        return [value.get_datatype() for value in self.list_fields]
