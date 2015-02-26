from seth.core import _route_path, _resource_path
from seth.renderers import CsvRenderer, PdfRenderer


def includeme(config):
    config.add_directive('route_path', _route_path)
    config.add_directive('resource_path', _resource_path)
    config.add_renderer(name='pdf', factory=PdfRenderer)
    config.add_renderer(name='csv', factory=CsvRenderer)
