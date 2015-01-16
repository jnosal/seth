from seth.core import _route_path


def includeme(config):
    config.add_directive('route_path', _route_path)