import pymysql
from .exporter import Exporter


class DataValidator:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        validated_data = self._validate_data_structure(value)
        instance.__dict__[self.name] = validated_data

    def _validate_data_structure(self, data):
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError("Data must be a dictionary or a list of dictionaries")

        for entry in data:
            if not isinstance(entry, dict):
                raise ValueError("Each entry in the list must be a dictionary")
            for key, value in entry.items():
                if isinstance(value, (dict, list)):
                    raise ValueError("Nested dictionaries or lists are not allowed")

        return data


class DBExporter(Exporter):
    data = DataValidator()

    def __init__(self, table_name, db_config):
        self.table_name = table_name
        self.db_config = db_config
        self._data = None

    def export(self, data, filename=None):
        self.data = data  # Trigger validation through descriptor

        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor()

        for entry in self.data:
            keys = ", ".join(entry.keys())
            values = ", ".join(['%s'] * len(entry))
            sql = f"INSERT INTO {self.table_name} ({keys}) VALUES ({values})"
            cursor.execute(sql, tuple(entry.values()))

        conn.commit()
        cursor.close()
        conn.close()
