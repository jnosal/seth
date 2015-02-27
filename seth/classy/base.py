from pyramid.httpexceptions import HTTPNotFound, HTTPMethodNotAllowed,\
    HTTPBadRequest, HTTPUnauthorized


class RestResource(object):

    authenticators = ()
    allowed_methods = []

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

    def get(self):
        return self.not_allowed()

    def post(self):
        return self.not_allowed()

    def put(self):
        return self.not_allowed()

    def delete(self):
        return self.not_allowed()

    def patch(self):
        return self.not_allowed()

    def head(self):
        return self.not_allowed()

    def options(self):
        return self.not_allowed()

    def trace(self):
        return self.not_allowed()

    def connect(self):
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