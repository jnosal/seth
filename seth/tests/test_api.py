import json
from decimal import Decimal
from datetime import datetime

from pyramid.renderers import JSONP

from seth.classy import generics
from seth.tests.models import SampleModel
from seth.classy.base import RestResource
from seth.tests import IntegrationTestBase, UnitTestBase
from seth.tests.schemas import SampleModelSchema, SampleModelRequiredSchema


class BasicResourceTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class SampleResource(RestResource):
            pass

        config.resource_path(SampleResource, '/test')

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


class DefaultResourceTestCase(UnitTestBase):

    def test_default_resource_settings(self):

        class DefaultResource(RestResource):
            pass

        view = DefaultResource(self.get_csrf_request())

        self.assertEqual(view.get_authenticators(), ())
        self.assertEqual(view.get_view_name(), 'DefaultResource')
        self.assertEqual(view.get_view_description(), u'')
        self.assertEqual(view.get_allowed_methods(), [])
        self.assertEqual(view.request_method, 'GET')
        json_data = view.not_allowed()
        self.assertIn('method', json_data)
        self.assertIn('error', json_data)
        json_data = view.not_authorized()
        self.assertIn('error', json_data)
        self.assertEqual(view.not_allowed(), view.head())
        self.assertEqual(view.not_allowed(), view.trace())
        self.assertEqual(view.not_allowed(), view.connect())


class BasicResourceWithNotJsonRendererTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')
        config.add_renderer('jsonp', JSONP(param_name='callback'))

        class SampleResource(RestResource):
            pass

        config.resource_path(SampleResource, '/test', renderer='jsonp')

    def test_get_method_is_not_allowed_with_jsonp(self):
        r = self.app.get('/test?callback=callback', expect_errors=True)
        self.assertEqual(r.status_int, 405)
        self.assertIn('callback', r.body)


class JsonAdapterTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class GenericResource(generics.GenericApiView):

            def get(self, **kwargs):
                return {'something': Decimal("3.0"), 'something_else': datetime.now()}


        config.resource_path(GenericResource, '/test')

    def test_decimal_and_datetme_are_serialized_properly(self):
        r = self.app.get('/test')
        self.assertEqual(r.status_int, 200)


class GenericApiViewTestCase(UnitTestBase):

    def test_default_generic_api_view_setup(self):

        class GenericResource(generics.GenericApiView):
            pass

        view = GenericResource(self.get_csrf_request())

        self.assertRaises(NotImplementedError, lambda: view.get_model())
        self.assertRaises(NotImplementedError, lambda: view.get_queryset())
        self.assertEqual(view.lookup_param, u'id')
        self.assertEqual(view.filter_class, None)


class BasicListResourceTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class SampleListResource(generics.ListReadOnlyApiView):
            schema = SampleModelSchema
            paginate = False

            def get_queryset(self, *args, **kwargs):
                return SampleModel.query

        config.resource_path(SampleListResource, '/test_list')

        class SampleListPaginatedResource(generics.ListReadOnlyApiView):
            schema = SampleModelSchema
            paginate = True

            def get_queryset(self, *args, **kwargs):
                return SampleModel.query

        config.resource_path(SampleListPaginatedResource, '/test_paginated_list')

        class NoQuerysetResource(generics.ListReadOnlyApiView):
            schema = SampleModelSchema

        config.resource_path(NoQuerysetResource, '/no_query')

        class NoSchemaResource(generics.ListReadOnlyApiView):
            def get_queryset(self, *args, **kwargs):
                return SampleModel.query

        config.resource_path(NoSchemaResource, '/no_schema')

    def test_get_list_no_model_exists(self):
        r = self.app.get('/test_list', expect_errors=True)
        data = json.loads(r.body)
        self.assertIn('results', data)
        self.assertEqual(data['results'], [])

    def test_get_list_db_is_not_empty(self):
        self.session.add(SampleModel(int_col=1, dec_col=3))
        self.session.flush()
        r = self.app.get('/test_list', expect_errors=True)
        data = json.loads(r.body)
        self.assertEqual(len(data['results']), 1)

    def test_get_paginated_list_no_model_exists(self):
        r = self.app.get('/test_paginated_list', expect_errors=True)
        data = json.loads(r.body)
        self.assertEqual(len(data['items']), 0)

    def test_get_paginated_list_db_is_not_empty(self):
        self.session.add(SampleModel(int_col=1, dec_col=3))
        self.session.flush()
        r = self.app.get('/test_paginated_list', expect_errors=True)
        data = json.loads(r.body)
        self.assertEqual(len(data['items']), 1)

    def test_page_is_default_when_page_param_is_not_an_integer(self):
        r = self.app.get('/test_paginated_list?page=adasdasdasd', expect_errors=True)
        data = json.loads(r.body)
        self.assertEqual(data['meta']['page'], 1)

    def test_per_page_is_default_when_per_page_param_is_not_an_integer(self):
        r = self.app.get('/test_paginated_list?per_page=adasdasdasd', expect_errors=True)
        data = json.loads(r.body)
        self.assertEqual(data['meta']['per_page'], 20)

    def test_no_queryset_on_resource_class(self):
        # NotImplemented is raised because get_queryset is not defined
        self.assertRaises(NotImplementedError, lambda: self.app.get('/no_query', expect_errors=True))

    def test_no_schema_set_on_resource_class(self):
        # NotImplemented is raised because marshmallow schema is not set
        self.assertRaises(NotImplementedError, lambda: self.app.get('/no_schema', expect_errors=True))


class BaseDetailResourceTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class SampleDetailResource(generics.DetailApiView):
            schema = SampleModelSchema
            paginate = False

            def get_queryset(self, *args, **kwargs):
                return SampleModel.query

        config.resource_path(SampleDetailResource, '/test_detail/{id}')

    def test_get_list_non_existang_id(self):
        r = self.app.get('/test_detail/126361287361278', expect_errors=True)
        self.assertEqual(r.status_int, 404)

    def test_get_model(self):
        instance = SampleModel(int_col=1, dec_col=3)
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        r = self.app.get('/test_detail/{0}'.format(instance.id), expect_errors=True)
        self.assertEqual(r.status_int, 200)
        print r.body


class BaseCreateResourceTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class SampleCreateResource(generics.CreateApiView):
            schema = SampleModelRequiredSchema
            model = SampleModel

        config.resource_path(SampleCreateResource, '/test_create/')

    def test_create_not_all_data(self):
        r = self.app.post_json('/test_create/', {}, expect_errors=True)
        self.assertEqual(r.status_int, 400)
        self.assertEqual(SampleModel.query.count(), 0)

    def test_create_data_is_valid(self):
        data = {
            'int_col': 1,
            'dec_col': 2
        }
        r = self.app.post_json('/test_create/', data, expect_errors=True)
        self.assertEqual(r.status_int, 201)
        json_data = json.loads(r.body)
        self.assertIn('status', json_data)
        self.assertEqual(json_data['status'], 'Created')
        self.assertEqual(SampleModel.query.count(), 1)

    def test_get_method_is_not_allowed(self):
        r = self.app.get('/test_create/', expect_errors=True)
        self.assertEqual(r.status_int, 405)


class BaseListCreateApiViewTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class SampleCreateResource(generics.ListCreateApiView):
            schema = SampleModelRequiredSchema
            model = SampleModel
            paginate = False

            def get_queryset(self, *args, **kwargs):
                return SampleModel.query

        config.resource_path(SampleCreateResource, '/test_create/')

    def test_create_data_is_valid_and_get_list_later(self):
        data = {
            'int_col': 1,
            'dec_col': 2
        }
        r = self.app.post_json('/test_create/', data, expect_errors=True)
        self.assertEqual(r.status_int, 201)
        r = self.app.post_json('/test_create/', data, expect_errors=True)
        self.assertEqual(r.status_int, 201)
        self.assertEqual(SampleModel.query.count(), 2)

        r = self.app.get('/test_create/')
        json_data = json.loads(r.body)
        self.assertIn('results', json_data)
        self.assertEqual(len(json_data['results']), 2)


class BaseDestroyDetailApiViewTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class SampleDestroyResource(generics.DestroyDetailApiView):
            schema = SampleModelRequiredSchema
            model = SampleModel

            def get_queryset(self, *args, **kwargs):
                return SampleModel.query

        config.resource_path(SampleDestroyResource, '/test_delete/{id}')

    def test_destroy_object_does_not_exist(self):
        r = self.app.delete('/test_delete/123123', expect_errors=True)
        self.assertEqual(r.status_int, 404)

    def test_get_model_is_successful(self):
        instance = SampleModel(int_col=1, dec_col=3)
        self.session.add(instance)
        self.session.flush()
        r = self.app.get('/test_delete/{0}'.format(instance.id), expect_errors=True)
        self.assertEqual(r.status_int, 200)
        json_data = json.loads(r.body)
        self.assertIn('object', json_data)

    def test_delete_model_is_succesfull(self):
        instance = SampleModel(int_col=1, dec_col=3)
        self.session.add(instance)
        self.session.flush()
        r = self.app.delete('/test_delete/{0}'.format(instance.id), expect_errors=True)
        self.assertEqual(r.status_int, 200)
        json_data = json.loads(r.body)
        self.assertIn('status', json_data)
        self.assertEqual(json_data['status'], 'Deleted')


class BasePatchViewTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class SamplePatchResource(generics.PatchApiView):
            schema = SampleModelRequiredSchema
            model = SampleModel

            def get_queryset(self, *args, **kwargs):
                return SampleModel.query

        config.resource_path(SamplePatchResource, '/test_simple_patch/{id}')

    def test_patch_model_does_not_exist(self):
        r = self.app.patch_json('/test_simple_patch/12312', {}, expect_errors=True)
        self.assertEqual(r.status_int, 404)

    def test_patch_model_schema_is_not_valid(self):
        instance = SampleModel(int_col=1, dec_col=3)
        self.session.add(instance)
        self.session.flush()
        r = self.app.patch_json('/test_simple_patch/{0}'.format(instance.id), {}, expect_errors=True)
        self.assertEqual(r.status_int, 400)
        json_data = json.loads(r.body)
        self.assertIn('errors', json_data)

    def test_simple_patch_is_succesful(self):
        instance = SampleModel(int_col=1, dec_col=3)
        self.session.add(instance)
        self.session.flush()
        before = SampleModel.query.get(instance.id)
        self.assertEqual(before.int_col, 1)
        self.assertEqual(before.dec_col, Decimal('3.0'))
        schema_data = {
            'int_col': 4,
            'dec_col': 5
        }
        r = self.app.patch_json('/test_simple_patch/{0}'.format(instance.id), schema_data, expect_errors=True)
        self.assertEqual(r.status_int, 200)
        json_data = json.loads(r.body)
        self.assertEqual(json_data['status'], 'Patched')
        after = SampleModel.query.get(instance.id)
        self.assertEqual(after.int_col, 4)
        self.assertEqual(after.dec_col, Decimal('5.0'))


class BaseUpdateViewTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class SampleUpdateResource(generics.UpdateApiView):
            schema = SampleModelRequiredSchema
            model = SampleModel

            def get_queryset(self, *args, **kwargs):
                return SampleModel.query

        config.resource_path(SampleUpdateResource, '/test_simple_update/{id}')

    def test_update_model_does_not_exist(self):
        r = self.app.put_json('/test_simple_update/12312', {}, expect_errors=True)
        self.assertEqual(r.status_int, 404)

    def test_simple_update_is_succesful(self):
        instance = SampleModel(int_col=1, dec_col=3)
        self.session.add(instance)
        self.session.flush()
        before = SampleModel.query.get(instance.id)
        self.assertEqual(before.int_col, 1)
        self.assertEqual(before.dec_col, Decimal('3.0'))
        schema_data = {
            'int_col': 4,
            'dec_col': 5
        }
        r = self.app.put_json('/test_simple_update/{0}'.format(instance.id), schema_data, expect_errors=True)
        self.assertEqual(r.status_int, 200)
        json_data = json.loads(r.body)
        self.assertEqual(json_data['status'], 'Updated')
        after = SampleModel.query.get(instance.id)
        self.assertEqual(after.int_col, 4)
        self.assertEqual(after.dec_col, Decimal('5.0'))


class BasePatchAndPutApiViewTestCase(IntegrationTestBase):

    def extend_app_configuration(self, config):
        config.include('seth')

        class SamplePatchAndUpdateResource(generics.PatchAndUpdateApiView):
            schema = SampleModelRequiredSchema
            model = SampleModel

            def get_queryset(self, *args, **kwargs):
                return SampleModel.query

        config.resource_path(SamplePatchAndUpdateResource, '/test_update/{id}')

    def test_get_returns_method_not_allowed(self):
        r = self.app.delete('/test_update/123123', expect_errors=True)
        self.assertEqual(r.status_int, 405)

    def test_update_model_does_not_exist(self):
        r = self.app.put('/test_update/12312', {}, expect_errors=True)
        self.assertEqual(r.status_int, 404)

    def test_update_model_schema_is_not_valid(self):
        instance = SampleModel(int_col=1, dec_col=3)
        self.session.add(instance)
        self.session.flush()
        r = self.app.put_json('/test_update/{0}'.format(instance.id), {}, expect_errors=True)
        self.assertEqual(r.status_int, 400)
        json_data = json.loads(r.body)
        self.assertIn('errors', json_data)

    def test_update_model_is_succesful(self):
        instance = SampleModel(int_col=1, dec_col=3)
        self.session.add(instance)
        self.session.flush()
        before = SampleModel.query.get(instance.id)
        self.assertEqual(before.int_col, 1)
        self.assertEqual(before.dec_col, Decimal('3.0'))
        schema_data = {
            'int_col': 4,
            'dec_col': 5
        }
        r = self.app.put_json('/test_update/{0}'.format(instance.id), schema_data, expect_errors=True)
        self.assertEqual(r.status_int, 200)
        json_data = json.loads(r.body)
        self.assertEqual(json_data['status'], 'Updated')
        after = SampleModel.query.get(instance.id)
        self.assertEqual(after.int_col, 4)
        self.assertEqual(after.dec_col, Decimal('5.0'))