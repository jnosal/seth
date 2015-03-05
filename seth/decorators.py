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


class cached_property(object):

    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res