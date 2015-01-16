from pyramid.response import Response
from seth.tests import IntegrationTestBase


class RouteDecoratorTests(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        def fbv(request):
            return Response('OK')

        class cbv(object):

            def __init__(self, request):
                self.request = request

            def __call__(self):
                return Response('OK')

        class cbv_spec(object):

            def __init__(self, request):
                self.request = request

            def spec(self):
                return Response('OK')

        config.route_path(fbv, '/fbv')
        config.route_path(cbv, '/cbv')
        config.route_path(cbv_spec, '/cbv_spec', attr='spec')

    def test_route_path_decorator_was_setup_correctly_for_fbv(self):
        self.assertEqual(200, self.app.get('/fbv').status_code)

    def test_route_path_decorator_was_setup_correctly_for_cbv(self):
        self.assertEqual(200, self.app.get('/cbv').status_code)

    def test_route_path_decorator_was_setup_correctly_for_cbv_spec(self):
        self.assertEqual(200, self.app.get('/cbv_spec').status_code)
