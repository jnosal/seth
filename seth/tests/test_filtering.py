from seth.tests import UnitTestBase
from seth.tests.models import SampleModel
from seth.filtering import FilterFactory, IntegerFilter


class BaseFilterTestCase(UnitTestBase):

    def freq(self, params):
        return self.get_csrf_request(request_method='GET', params=params)


class FilteringTestCase(BaseFilterTestCase):

    def test_assertion_error_is_raised_when_no_model_is_set(self):
        self.assertRaises(AssertionError, lambda: type('SuperSth', (FilterFactory,), {})(None))

    def test_empty_filter_factory_class(self):

        class EmptyModelFilters(FilterFactory):
            model = SampleModel

        qs = SampleModel.query
        empty_factory = EmptyModelFilters(qs=qs)
        self.assertEqual(empty_factory.filters, {})
        self.assertEqual(
            empty_factory.apply(self.get_csrf_request()),
            qs
        )

    def test_filter_factory_param_does_not_exist_on_model(self):

        class SimpleFactory(FilterFactory):
            model = SampleModel
            s = IntegerFilter()

        qs = SampleModel.query
        factory = SimpleFactory(qs=qs)
        self.assertEqual(qs, factory.apply(self.freq({'s': 1})))

    def test_filter_factory_name_is_same_as_field_on_model(self):

        class SimpleFactory(FilterFactory):
            model = SampleModel
            int_col = IntegerFilter()

        qs = SampleModel.query
        factory = SimpleFactory(qs=qs)
        self.assertIn('int_col', factory.filters)
        self.assertNotEqual(qs, factory.apply(self.freq({'int_col': 1})))

    def test_filter_factory_predefined_name(self):

        class SimpleFactory(FilterFactory):
            model = SampleModel
            k = IntegerFilter(name='int_col')

        qs = SampleModel.query
        factory = SimpleFactory(qs=qs)
        self.assertIn('int_col', factory.filters)
        self.assertNotEqual(qs, factory.apply(self.freq({'int_col': 1})))


class IntegerFilterTestCase(BaseFilterTestCase):

    def get_factory(self, qs):
        class SimpleFactory(FilterFactory):
            model = SampleModel
            int_col = IntegerFilter()

        return SimpleFactory(qs=qs)

    def test_value_is_empty(self):
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        self.assertEqual(factory.apply(self.freq({})), qs)

    def test_value_cannot_be_cast_to_integer(self):
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        self.assertEqual(factory.apply(self.freq({'int_col': 'asdasd'})), qs)

    def test_find_models(self):
        SampleModel.manager.create(int_col=1)
        SampleModel.manager.create(int_col=1)
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        filtered_qs = factory.apply(self.freq({'int_col': 1}))
        self.assertEqual(filtered_qs.count(), 2)

        filtered_qs = factory.apply(self.freq({'int_col': 666}))
        self.assertEqual(filtered_qs.count(), 0)


