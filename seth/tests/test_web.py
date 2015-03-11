import json

import wtforms
from pyramid.response import Response

from seth.classy.web.base import WebResource
from seth.classy.web import generics
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


class TestForm(wtforms.Form):
    field = wtforms.TextAreaField('a')
    required_field = wtforms.TextAreaField('b', [wtforms.validators.InputRequired()])

    def __json__(self, request):
        is_valid = self.validate()
        return {
            'data': self.data,
            'errors': self.errors,
            'is_valid': is_valid
        }


class ProcessFormViewTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')
        config.include('pyramid_jinja2')
        config.add_jinja2_search_path('seth.tests:templates/')

        class SampleNoForm(generics.ProcessFormView):
            pass

        config.register_resource(SampleNoForm, '/test1/', web=True)

        class SampleProcess(generics.ProcessFormView):
            form = TestForm

            def form_is_valid(self, form):
                return Response("OK")

        config.register_resource(SampleProcess, '/test/', renderer='test_form.jinja2', web=True)

    def test_get_no_form_set(self):
        self.assertRaises(NotImplementedError, lambda: self.app.get('/test1/'))

    def test_jinja2_renderer_get_form(self):
        r = self.app.get('/test/', headers={'Accept': 'text/html'}, expect_errors=True)
        self.assertIn('textarea', r.body)
        self.assertIn('field', r.body)
        self.assertIn('required_field', r.body)

    def test_json_renderer_get_form(self):
        r = self.app.get('/test/', headers={'Accept': 'application/json'}, expect_errors=True)
        data = json.loads(r.body)
        self.assertIn('form', data)
        self.assertIn('is_valid', data['form'])
        self.assertIn('errors', data['form'])
        self.assertIn('data', data['form'])
        self.assertEqual(False, data['form']['is_valid'])
        self.assertEqual(None, data['form']['data']['field'])
        self.assertEqual(None, data['form']['data']['required_field'])
        self.assertNotEqual({}, data['form']['errors'])

    def test_json_renderer_get_post_invalid_data(self):
        post_data = {
            'field': 'ww'
        }
        r = self.app.post_json('/test/', post_data, headers={'Accept': 'application/json'}, expect_errors=True)
        data = json.loads(r.body)
        self.assertNotEqual({}, data['form']['errors'])

    def test_json_renderer_post_valid_data_use_json_body(self):
        post_data = {
            'field': 'ww',
            'required_field': 'ss'
        }
        r = self.app.post_json('/test/', post_data, headers={'Accept': 'application/json'}, expect_errors=True)
        self.assertEqual(r.body, "OK")

    def test_json_renderer_post_valid_data_use_POST(self):
        post_data = {
            'field': 'ww',
            'required_field': 'ss'
        }
        r = self.app.post('/test/', post_data, expect_errors=True)
        self.assertEqual(r.body, "OK")