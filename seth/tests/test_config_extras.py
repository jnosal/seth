from decimal import Decimal
from datetime import datetime

from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound

from seth.classy.rest import generics
from seth.decorators import route_path, cached_property
from seth.tests import IntegrationTestBase, UnitTestBase


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
        self.assertRaises(TypeError, lambda: self.app.get('/decorated_cbv_spec').status_code)


class JsonAdapterTestCase(IntegrationTestBase):

    def make_localizer(self, *args, **kwargs):
        from pyramid.i18n import Localizer
        return Localizer(*args, **kwargs)

    def extend_app_configuration(self, config):
        config.include('seth')

        class GenericResource(generics.GenericApiView):

            def get(self, **kwargs):
                return {
                    'something': Decimal("3.0"),
                    'something_else': datetime.now()
                }

        config.register_resource(GenericResource, '/test')

    def test_decimal_and_datetme_are_serialized_properly(self):
        r = self.app.get('/test')
        self.assertEqual(r.status_int, 200)


class ExtraUtilsTestCase(UnitTestBase):

    def test_cached_property(self):
        import random

        class A(object):

            @property
            def not_cached(self):
                return random.random()

            @cached_property
            def cached(self):
                return random.random()

        inst = A()
        k1 = inst.cached
        k2 = inst.cached

        a1 = inst.not_cached
        a2 = inst.not_cached

        self.assertEqual(k1, k2)
        self.assertNotEqual(a1, a2)



