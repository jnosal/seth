from pyramid.httpexceptions import HTTPNotFound

from seth.tests import PostgresqlDatabaseMixin, UnitTestBase,\
    IntegrationTestBase
from seth.tenancy import get_domain_url_from_request
from seth.tests.models import Tenant


class DiscoverTenantSchemaTestCase(UnitTestBase):

    def test_discover_schema(self):
        request = self.get_csrf_request()

        request.domain = 'www.google.com'
        self.assertEqual(get_domain_url_from_request(request), 'google.com')

        request = self.get_csrf_request()
        request.domain = 'google.com'
        self.assertEqual(get_domain_url_from_request(request), 'google.com')


class SqliteTenantTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')
        self.assertRaises(RuntimeError, lambda: config.register_tenancy(TenantModel=None))

    def test_bulk(self):
        pass


class PostgresqlTenantTestCase(PostgresqlDatabaseMixin, IntegrationTestBase):

    def extend_app_configuration(self, config):
        def index(request):
            from pyramid.response import Response
            return Response('OK')

        config.include('seth')
        config.register_tenancy(TenantModel=Tenant)
        config.add_route('index', '/')
        config.add_view(view=index, route_name='index')

    def test_get_request_no_public_tenant_exists(self):
        self.assertRaises(HTTPNotFound, lambda: self.app.get('/', expect_errors=True))

    def test_get_request_public_tenant_exists(self):
        Tenant.manager.create(schema_name='public', domain_url='localhost')
        r = self.app.get('/', expect_errors=True)
        self.assertEqual(r.status_int, 200)