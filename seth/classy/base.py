from pyramid.httpexceptions import HTTPNotFound, HTTPMethodNotAllowed,\
    HTTPCreated, HTTPBadRequest


class RestResource(object):

    def __init__(self, request):
        self.request = request

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

    def created(self):
        self.request.response.status_int = HTTPCreated.code
        return {
            'success': True
        }

    def bad_request(self, errors=None):
        errors = errors if errors else []
        self.request.response.status_int = HTTPBadRequest.code
        return {
            'errors': errors
        }


class BaseSchemaMixin(object):
    schema = None

    def get_schema_class(self, *args, **kwargs):
        raise NotImplementedError

    def _get_schema(self, many):
        if self.schema:
            return self.schema(many=many)
        else:
            return self.get_schema_class()(many=many)

    def dump_schema(self, schema_class, data):
        # override if schema is handled differently
        results = schema_class.dump(data)
        return results.data

    def load_schema(self, schema_class, data):
        return schema_class.load(data)