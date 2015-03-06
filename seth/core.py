import decimal
import datetime

from pyramid.renderers import JSON


def _register_resource(config, view, path, *args, **kwargs):
    route_name = getattr(view, '__qualname__', view.__name__)

    attr = 'dispatch'
    renderer = kwargs.pop('renderer', 'json')

    config.add_route(route_name, path)
    config.add_view(
        view, route_name=route_name,
        attr=attr, *args, renderer=renderer,
        **kwargs
    )


def get_adapted_json_renderer():
    json_renderer = JSON()

    def datetime_adapter(obj, request):
        return obj.isoformat()

    def decimal_adapter(obj, request):
        return str(obj)

    json_renderer.add_adapter(datetime.datetime, datetime_adapter)
    json_renderer.add_adapter(datetime.date, datetime_adapter)
    json_renderer.add_adapter(datetime.time, datetime_adapter)
    json_renderer.add_adapter(decimal.Decimal, decimal_adapter)

    return json_renderer