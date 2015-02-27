def _route_path(config, view, path, *args, **kwargs):

    def callback():
        route_name = getattr(view, '__qualname__', view.__name__)
        config.add_route(route_name, path)
        config.add_view(view, route_name=route_name, *args, **kwargs)

    discriminator = ('route_path', path)
    config.action(discriminator, callback)


def _resource_path(config, view, path, *args, **kwargs):

    def callback():
        route_name = getattr(view, '__qualname__', view.__name__)
        config.add_route(route_name, path)
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        renderer = kwargs.pop('renderer', 'json')

        for method in methods:
            config.add_view(
                view, route_name=route_name,
                request_method=method,
                attr=method.lower(), *args, renderer=renderer,
                **kwargs
            )

    discriminator = ('resource_path', path)
    config.action(discriminator, callback)