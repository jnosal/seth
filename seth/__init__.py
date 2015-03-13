from seth.core import _register_resource, _register_export,\
    get_adapted_json_renderer, register_query_listener
from seth.renderers import CsvRenderer, PdfRenderer


def includeme(config):
    config.add_directive('register_resource', _register_resource)
    config.add_directive('register_export_resource', _register_export)
    config.add_directive('register_query_listener', register_query_listener)

    config.add_renderer(name='pdf', factory=PdfRenderer)
    config.add_renderer(name='csv', factory=CsvRenderer)

    adapted_json_renderer = get_adapted_json_renderer()
    config.add_renderer('json', adapted_json_renderer)