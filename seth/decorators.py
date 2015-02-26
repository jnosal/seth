import venusian


class route_path(object):

    def __init__(self, path, attr=None):
        self.path = path
        self.attr = attr

    def register(self, scanner, name, wrapped):
        scanner.config.route_path(wrapped, self.path)

    def __call__(self, wrapped):
        venusian.attach(wrapped, self.register)
        return wrapped


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)