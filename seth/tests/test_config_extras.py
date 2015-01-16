from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound

from seth.decorators import route_path
from seth.tests import IntegrationTestBase


@route_path('/decorated_fbv')
def decorated_fbv(request):
    return Response('OK')


@route_path('/decorated_cbv')
class decorated_cbv(object):

    def __init__(self, request):
        self.request = request

    def __call__(self):
        return Response('OK!')


class decorated_cbv_spec(object):

    def __init__(self, request):
        self.request = request

    @route_path('/decorated_cbv_spec', attr='spec')
    def spec(self):
        return Response('OK!')


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

    def test_route_path_decorator_was_setup_correctly_for_cbv_spe(self):
        self.assertEqual(200, self.app.get('/cbv_spec').status_code)

    def test_route_path_decorator_was_setup_correctly_for_decorated_fbv(self):
        self.assertRaises(HTTPNotFound, lambda: self.app.get('/decorated_fbv'))
        self.config.scan(__name__)
        self.assertEqual(200, self.app.get('/decorated_fbv').status_code)

    def test_route_path_decorator_was_setup_correctly_for_decorated_cbv(self):
        self.assertRaises(HTTPNotFound, lambda: self.app.get('/decorated_cbv'))
        self.config.scan(__name__)
        self.assertEqual(200, self.app.get('/decorated_cbv').status_code)

    def test_route_path_decorated_raises_typeerror_for_decorated_cbv_spec(self):
        self.assertRaises(HTTPNotFound, lambda: self.app.get('/decorated_cbv_spec'))
        self.config.scan(__name__)
        self.assertRaises(TypeError, lambda : self.app.get('/decorated_cbv_spec').status_code)