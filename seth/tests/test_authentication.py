from seth import auth
from seth.tests import IntegrationTestBase
from seth.classy.rest import generics


class DefaultAuthenticatedResource(generics.GenericApiView):
    authentication_policy = None

    def get(self, **kwargs):
        return {}


class BaseAuthenticatedTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')
        config.register_resource(DefaultAuthenticatedResource, '/test_basic')

    def test_default_setup(self):
        r = self.app.get('/test_basic')
        self.assertEqual(r.status_int, 200)


class TokenAuthenticationPolicy(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class CheckQueryParamsResource(generics.GenericApiView):
            authentication_policy = auth.SecretTokenAuthenticationPolicy

            def get(self, **kwargs):
                return {}

        config.register_resource(CheckQueryParamsResource, '/test_token')

    def test_no_token_in_params(self):
        r = self.app.get('/test_token', expect_errors=True)
        self.assertEqual(r.status_int, 401)

    def test_wrong_token_in_params(self):
        r = self.app.get('/test_token?token=wrong_token', expect_errors=True)
        self.assertEqual(r.status_int, 401)

    def test_correct_token_in_params_wrong_param_name(self):
        r = self.app.get('/test_token?tokennamewrong=secret', expect_errors=True)
        self.assertEqual(r.status_int, 401)

    def test_correct_token_param_name_and_value(self):
        r = self.app.get('/test_token?token=secret')
        self.assertEqual(r.status_int, 200)


class CheckHeaderAuthenticatioPolicy(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class AllowHeaderAuthPolicy(auth.HeaderAuthenticationPolicy):
            header_name = 'My-Header'
            header_secret = 'My-Value'

        class CheckQueryParamsResourceSecond(generics.GenericApiView):
            authentication_policy = AllowHeaderAuthPolicy

            def get(self, **kwargs):
                return {}

        config.register_resource(CheckQueryParamsResourceSecond, '/test_header')

    def test_no_header_in_request(self):
        r = self.app.get('/test_header', headers={}, expect_errors=True)
        self.assertEqual(r.status_int, 401)

    def test_header_in_request_but_incorrect_value(self):
        r = self.app.get('/test_header', headers={'My-Header': '123'}, expect_errors=True)
        self.assertEqual(r.status_int, 401)

    def test_value_in_header_but_wrong_header_name(self):
        r = self.app.get('/test_header', headers={'Wrong': 'My-Value'}, expect_errors=True)
        self.assertEqual(r.status_int, 401)

    def test_correct_header_name_and_value(self):
        r = self.app.get('/test_header', headers={'My-Header': 'My-Value'}, expect_errors=True)
        self.assertEqual(r.status_int, 200)