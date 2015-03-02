def _route_path(config, view, path, *args, **kwargs):
    route_name = getattr(view, '__qualname__', view.__name__)
    config.add_route(route_name, path)
    config.add_view(view, route_name=route_name, *args, **kwargs)


def _resource_path(config, view, path, *args, **kwargs):
    route_name = getattr(view, '__qualname__', view.__name__)

    attr = 'dispatch'
    renderer = kwargs.pop('renderer', 'json')

    config.add_route(route_name, path)
    config.add_view(
        view, route_name=route_name,
        attr=attr, *args, renderer=renderer,
        **kwargs
    )