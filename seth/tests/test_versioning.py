from seth import versioning
from seth.tests import IntegrationTestBase
from seth.classy.rest import generics


class DefaultVersioningResource(generics.GenericApiView):

    def get(self, **kwargs):
        return {}


class NotShowVersionResource(generics.GenericApiView):
    display_version = False

    def get(self, **kwargs):
        return {}


class BaseVersioningTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')
        config.register_resource(DefaultVersioningResource, '/test_basic')
        config.register_resource(NotShowVersionResource, '/test_do_not_display_version')

    def test_default_setup(self):
        r = self.app.get('/test_basic')
        self.assertEqual(r.status_int, 200)
        self.assertIn('API-Version', r.headers.keys())
        self.assertEqual(r.headers['API-Version'], '1.0')

    def test_do_not_display_version(self):
        r = self.app.get('/test_do_not_display_version')
        self.assertEqual(r.status_int, 200)
        self.assertNotIn('API-Version', r.headers.keys())


class CustomVersioningPoliciesTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class NoGetVersionInfoPolicy(versioning.BaseVersioningPolicy):
            default_version = '2.0'

        class NoGetVersionInfonResource(generics.GenericApiView):
            versioning_policy = NoGetVersionInfoPolicy

            def get(self, **kwargs):
                return {}

        config.register_resource(NoGetVersionInfonResource, '/test_no_get_version_info')

        class AnotherVersionPolicy(versioning.BaseVersioningPolicy):
            default_version = '2.0'

            def get_version_info(self, request, *args, **kwargs):
                return '2.0'

        class AnotherVersionResource(generics.GenericApiView):
            versioning_policy = AnotherVersionPolicy

            def get(self, **kwargs):
                return {}

        config.register_resource(AnotherVersionResource, '/test_another_version')

        class PredefineVersionPolicy(versioning.BaseVersioningPolicy):
            default_version = None

            def get_default_version(self, request):
                return '666'

            def get_version_info(self, request, *args, **kwargs):
                return '666'

        class PredefineVersionResource(generics.GenericApiView):
            versioning_policy = PredefineVersionPolicy

            def get(self, **kwargs):
                return {}

        config.register_resource(PredefineVersionResource, '/test_predefine')

    def test_raises_NotImplementedError_if_get_version_info_is_not_provided(self):
        self.assertRaises(NotImplementedError, lambda: self.app.get('/test_no_get_version_info'))

    def test_another_version_set(self):
        r = self.app.get('/test_another_version')
        self.assertEqual(r.status_int, 200)
        self.assertIn('API-Version', r.headers.keys())
        self.assertEqual(r.headers['API-Version'], '2.0')

    def test_predefine_version(self):
        r = self.app.get('/test_predefine')
        self.assertEqual(r.status_int, 200)
        self.assertIn('API-Version', r.headers.keys())
        self.assertEqual(r.headers['API-Version'], '666')


class CheckParamsVersionPolicy(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class CheckQueryParamsResource(generics.GenericApiView):
            versioning_policy = versioning.CheckQueryParamsVersioningPolicy

            def get(self, **kwargs):
                return {}

        config.register_resource(CheckQueryParamsResource, '/test_query_params')

        class AllowVersionOnePolicy(versioning.CheckQueryParamsVersioningPolicy):
            default_version = '22.0'

            def get_allowed_version(self):
                return ['5.0']

        class CheckQueryParamsResourceSecond(generics.GenericApiView):
            versioning_policy = AllowVersionOnePolicy

            def get(self, **kwargs):
                return {}

        config.register_resource(CheckQueryParamsResourceSecond, '/test_allow_version')

    def test_no_version_in_query_params_all_versions_allowed(self):
        r = self.app.get('/test_query_params')
        self.assertEqual(r.status_int, 200)

    def test_wrong_version_in_query_params_all_versions_allowed(self):
        r = self.app.get('/test_query_params?version=2.0')
        self.assertEqual(r.status_int, 200)

    def test_correct_version_in_query_params_all_versions_allowed(self):
        r = self.app.get('/test_query_params?version=1.0')
        self.assertEqual(r.status_int, 200)

    def test_allow_default_version(self):
        r = self.app.get('/test_allow_version?version=22.0')
        self.assertEqual(r.status_int, 200)

    def test_allowed_versions(self):
        r = self.app.get('/test_allow_version?version=5.0')
        self.assertEqual(r.status_int, 200)

    def test_wrong_version_in_query_params_allowed_are_set(self):
        r = self.app.get('/test_allow_version?version=1.0', expect_errors=True)
        self.assertEqual(r.status_int, 404)

    def test_no_version_in_query_params_allowed_are_set(self):
        r = self.app.get('/test_allow_version', expect_errors=True)
        self.assertEqual(r.status_int, 404)


class CheckHeaderVersionPolicy(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class AllowVersionOnePolicy(versioning.CheckHeaderVersioningPolicy):
            default_version = '22.0'

            def get_allowed_version(self):
                return ['5.0']

        class CheckQueryParamsResourceSecond(generics.GenericApiView):
            versioning_policy = AllowVersionOnePolicy

            def get(self, **kwargs):
                return {}

        config.register_resource(CheckQueryParamsResourceSecond, '/test_allow_header')

    def test_allow_default_version(self):
        r = self.app.get('/test_allow_header', headers={'Api-Version': '22.0'})
        self.assertEqual(r.status_int, 200)

    def test_allowed_versions(self):
        r = self.app.get('/test_allow_header', headers={'Api-Version': '5.0'})
        self.assertEqual(r.status_int, 200)

    def test_wrong_version_in_headers(self):
        r = self.app.get('/test_allow_header', headers={'Api-Version': '666.0'}, expect_errors=True)
        self.assertEqual(r.status_int, 404)

    def test_no_header_in_request(self):
        r = self.app.get('/test_allow_header', expect_errors=True)
        self.assertEqual(r.status_int, 404)

    def test_wrong_header_set(self):
        r = self.app.get('/test_allow_header', headers={'Api-WRONG': '22.0'}, expect_errors=True)
        self.assertEqual(r.status_int, 404)