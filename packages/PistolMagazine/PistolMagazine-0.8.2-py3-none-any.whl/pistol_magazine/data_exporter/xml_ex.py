import dicttoxml
from .exporter import Exporter


class XMLExporter(Exporter):
    def export(self, data, filename):
        xml_data = dicttoxml.dicttoxml(data)
        with open(filename, 'wb') as output_file:
            output_file.write(xml_data)
