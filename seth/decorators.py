import venusian


class route_path(object):

    def __init__(self, path, *args, **kwargs):
        self.path = path

    def register(self, scanner, name, wrapped):
        scanner.config.route_path(wrapped, self.path)

    def __call__(self, wrapped):
        venusian.attach(wrapped, self.register)
        return wrapped