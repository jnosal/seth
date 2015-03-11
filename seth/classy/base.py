class View(object):
    dispatchable_methods = [
        'GET', 'POST', 'PUT', 'DELETE', 'PATCH',
        'CONNECT', 'TRACE', 'HEAD', 'OPTIONS'
    ]

    def __init__(self, request):
        self.request = request

    def perform_setup(self):
        pass

    @property
    def request_method(self):
        return self.request.method

    def dispatch(self, **kwargs):
        self.perform_setup()

        if self.request_method in self.dispatchable_methods:

            attr = self.request_method.lower()
            response_data = getattr(self, attr)(**kwargs)
            return response_data

        return self.not_allowed()

    def get(self, **kwargs):
        return self.not_allowed()

    def post(self, **kwargs):
        return self.not_allowed()

    def put(self, **kwargs):
        return self.not_allowed()

    def delete(self, **kwargs):
        return self.not_allowed()

    def patch(self, **kwargs):
        return self.not_allowed()

    def head(self, **kwargs):
        return self.not_allowed()

    def options(self, **kwargs):
        return self.not_allowed()

    def trace(self, **kwargs):
        return self.not_allowed()

    def connect(self, **kwargs):
        return self.not_allowed()