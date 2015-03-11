from seth.classy.web.base import WebResource
from seth.tests import IntegrationTestBase


class BasicWebResourceTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class SampleResource(WebResource):
            pass

        config.register_resource(SampleResource, '/test', web=True)

    def test_get_method_is_not_allowed(self):
        r = self.app.get('/test', expect_errors=True)
        self.assertEqual(r.status_int, 405)

    def test_post_method_is_not_allowed(self):
        r = self.app.post('/test', expect_errors=True)
        self.assertEqual(r.status_int, 405)

    def test_patch_method_is_not_allowed(self):
        r = self.app.patch('/test', expect_errors=True)
        self.assertEqual(r.status_int, 405)

    def test_put_method_is_not_allowed(self):
        r = self.app.put('/test', expect_errors=True)
        self.assertEqual(r.status_int, 405)

    def test_delete_method_is_not_allowed(self):
        r = self.app.delete('/test', expect_errors=True)
        self.assertEqual(r.status_int, 405)

    def test_head_method_is_not_allowed(self):
        r = self.app.head('/test', expect_errors=True)
        self.assertEqual(r.status_int, 405)

    def test_options_method_is_not_allowed(self):
        r = self.app.options('/test', expect_errors=True)
        self.assertEqual(r.status_int, 405)