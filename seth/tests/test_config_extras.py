from decimal import Decimal
from datetime import datetime

from seth.classy.rest import generics
from seth.decorators import cached_property
from seth.tests import IntegrationTestBase, UnitTestBase


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



