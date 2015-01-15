from pyramid.response import Response
from seth.tests import IntegrationTestBase


class RouteDecoratorTests(IntegrationTestBase):

    def extend_app_configuration(self, config):

        def dummy(request):
            return Response('OK')

        config.add_route('index', '/')
        config.add_view(dummy, route_name='index')
