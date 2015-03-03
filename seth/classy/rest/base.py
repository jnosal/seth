from pyramid.httpexceptions import HTTPNotFound, HTTPMethodNotAllowed,\
    HTTPBadRequest, HTTPUnauthorized


class RestResource(object):

    authenticators = ()
    allowed_methods = []
    dispatchable_methods = [
        'GET', 'POST', 'PUT', 'DELETE', 'PATCH',
        'CONNECT', 'TRACE', 'HEAD', 'OPTIONS'
    ]

    def __init__(self, request):
        self.request = request

    def get_authenticators(self):
        return ()

    def get_view_name(self):
        return self.__class__.__name__

    def get_view_description(self):
        return u""

    def get_allowed_methods(self):
        return self.allowed_methods

    @property
    def request_method(self):
        return self.request.method

    @property
    def default_response_headers(self):
        headers = [
            ('Allow', ', '.join(self.allowed_methods)),
        ]
        return headers

    def dispatch(self, **kwargs):
        if self.request_method in self.dispatchable_methods:

            attr = self.request_method.lower()
            response_data = getattr(self, attr)(**kwargs)
            headers = self.default_response_headers
            self.request.response.headerlist.extend(headers)
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

    def not_allowed(self):
        self.request.response.status_int = HTTPMethodNotAllowed.code
        return {
            'error': 'This method is not allowed.',
            'method': self.request.method
        }

    def not_found(self):
        self.request.response.status_int = HTTPNotFound.code
        return {
            'error': 'Not found.'
        }

    def not_authorized(self):
        self.request.response.status_int = HTTPUnauthorized.code
        return {
            'error': 'Not authorized.'
        }

    def bad_request(self, errors=None):
        errors = errors if errors else []
        self.request.response.status_int = HTTPBadRequest.code
        return {
            'errors': errors
        }