import decimal
import datetime

from pyramid.renderers import JSON


def _register_resource(config, view, path, *args, **kwargs):
    route_name = getattr(view, '__qualname__', view.__name__)

    attr = 'dispatch'
    renderer = kwargs.pop('renderer', 'json')
    web = kwargs.pop('web', False)

    config.add_route(route_name, path)

    if not web:
        config.add_view(
            view, route_name=route_name,
            attr=attr, *args, renderer=renderer, **kwargs
        )

    else:
        # if this is a web resource we optionally register json renderer
        # which renders context as json object
        if not renderer == 'json':
            config.add_view(
                view, route_name=route_name,
                attr=attr, *args, renderer=renderer,
                accept="text/html", **kwargs
            )
        config.add_view(
            view, route_name=route_name,
            attr=attr, *args, renderer='json',
            accept="application/json", **kwargs
        )


def _register_export(config, view, path, *args, **kwargs):
    route_name = getattr(view, '__qualname__', view.__name__)

    config.add_route(route_name, path)
    config.add_view(
        view, route_name=route_name,
        attr='get', *args, renderer='json',
        **kwargs
    )

    for renderer in ['pdf', 'csv']:

        if path.endswith('/'):
            path_ = '{0}{1}/'.format(path, renderer)
        else:
            path_ = '{0}/{1}/'.format(path, renderer)

        route_name_ = "{0}_{1}".format(route_name, renderer)

        config.add_route(route_name_, path_)
        config.add_view(
            view, route_name=route_name_,
            attr=renderer, *args, renderer=renderer,
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


def register_query_listener(config, engine, threshold=10):
    from seth.helpers.ext.sa import setup_query_listener
    setup_query_listener(engine, threshold)
