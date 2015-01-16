def _route_path(config, view, path, *args, **kwargs):

    def callback():
        route_name = getattr(view, '__qualname__', view.__name__)
        config.add_route(route_name, path)
        config.add_view(view, route_name=route_name, *args, **kwargs)

    discriminator = ('route_path', path)
    config.action(discriminator, callback)