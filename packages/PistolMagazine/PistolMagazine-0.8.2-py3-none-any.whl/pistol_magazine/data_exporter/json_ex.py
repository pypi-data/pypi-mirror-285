import json
from .exporter import Exporter


class JSONExporter(Exporter):
    def export(self, data, filename):
        with open(filename, 'w') as output_file:
            json.dump(data, output_file, indent=4)
