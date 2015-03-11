from pyramid.response import Response
from pyramid.httpexceptions import HTTPMethodNotAllowed

from seth.classy.base import View


class WebResource(View):

    def perform_setup(self):
        pass

    def not_allowed(self):
        return Response("Method {0} is not allowed".format(
            self.request_method), status=HTTPMethodNotAllowed.code
        )

    def get_context_data(self):
        pass