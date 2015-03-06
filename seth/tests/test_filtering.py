from datetime import datetime, timedelta

from seth import filtering
from seth.tests import UnitTestBase
from seth.tests.models import SampleModel


class BaseFilterTestCase(UnitTestBase):

    def freq(self, params):
        return self.get_csrf_request(request_method='GET', params=params)


class FilteringTestCase(BaseFilterTestCase):

    def test_assertion_error_is_raised_when_no_model_is_set(self):
        self.assertRaises(AssertionError, lambda: type('SuperSth', (filtering.FilterFactory,), {})(None))

    def test_empty_filter_factory_class(self):

        class EmptyModelFilters(filtering.FilterFactory):
            model = SampleModel

        qs = SampleModel.query
        empty_factory = EmptyModelFilters(qs=qs)
        self.assertEqual(empty_factory.filters, {})
        self.assertEqual(
            empty_factory.apply(self.get_csrf_request()),
            qs
        )

    def test_filter_factory_param_does_not_exist_on_model(self):

        class SimpleFactory(filtering.FilterFactory):
            model = SampleModel
            s = filtering.IntegerFilter()

        qs = SampleModel.query
        factory = SimpleFactory(qs=qs)
        self.assertRaises(AttributeError, lambda: factory.apply(self.freq({'s': 1})))

    def test_filter_factory_name_is_same_as_field_on_model(self):

        class SimpleFactory(filtering.FilterFactory):
            model = SampleModel
            int_col = filtering.IntegerFilter()

        qs = SampleModel.query
        factory = SimpleFactory(qs=qs)
        self.assertIn('int_col', factory.filters)
        self.assertNotEqual(qs, factory.apply(self.freq({'int_col': 1})))

    def test_filter_factory_predefined_name(self):

        class SimpleFactory(filtering.FilterFactory):
            model = SampleModel
            k = filtering.IntegerFilter(name='int_col')

        qs = SampleModel.query
        factory = SimpleFactory(qs=qs)
        self.assertIn('int_col', factory.filters)
        self.assertNotEqual(qs, factory.apply(self.freq({'int_col': 1})))


class IntegerFilterTestCase(BaseFilterTestCase):

    def get_factory(self, qs):
        class SimpleFactory(filtering.FilterFactory):
            model = SampleModel
            int_col = filtering.IntegerFilter()

        return SimpleFactory(qs=qs)

    def test_value_is_empty(self):
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        self.assertEqual(factory.apply(self.freq({})), qs)

    def test_value_cannot_be_cast_to_integer(self):
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        self.assertRaises(ValueError, lambda: factory.apply(self.freq({'int_col': 'asdasd'})))

    def test_find_models(self):
        SampleModel.manager.create(int_col=1)
        SampleModel.manager.create(int_col=1)
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        filtered_qs = factory.apply(self.freq({'int_col': 1}))
        self.assertEqual(filtered_qs.count(), 2)

        filtered_qs = factory.apply(self.freq({'int_col': 666}))
        self.assertEqual(filtered_qs.count(), 0)


class BooleanFilterTestCase(BaseFilterTestCase):

    def get_factory(self, qs):
        class SimpleFactory(filtering.FilterFactory):
            model = SampleModel
            bool_col = filtering.BooleanFilter()

        return SimpleFactory(qs=qs)

    def test_value_is_empty(self):
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        self.assertEqual(factory.apply(self.freq({})), qs)

    def test_find_models(self):
        SampleModel.manager.create(bool_col=True)
        SampleModel.manager.create(bool_col=False)
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)

        filtered_qs = factory.apply(self.freq({'bool_col': None}))
        self.assertEqual(filtered_qs.count(), 2)

        filtered_qs = factory.apply(self.freq({'bool_col': ''}))
        self.assertEqual(filtered_qs.count(), 2)

        filtered_qs = factory.apply(self.freq({'bool_col': 'true'}))
        self.assertEqual(filtered_qs.count(), 1)

        filtered_qs = factory.apply(self.freq({'bool_col': 'True'}))
        self.assertEqual(filtered_qs.count(), 1)

        filtered_qs = factory.apply(self.freq({'bool_col': True}))
        self.assertEqual(filtered_qs.count(), 1)

        filtered_qs = factory.apply(self.freq({'bool_col': 'false'}))
        self.assertEqual(filtered_qs.count(), 1)

        filtered_qs = factory.apply(self.freq({'bool_col': 'False'}))
        self.assertEqual(filtered_qs.count(), 1)

        self.assertRaises(AttributeError, lambda: factory.apply(self.freq({'bool_col': '@@@'})))
        self.assertRaises(AttributeError, lambda: factory.apply(self.freq({'bool_col': 1})))
        self.assertRaises(AttributeError, lambda: factory.apply(self.freq({'bool_col': 0})))


class CharFilterTestCase(BaseFilterTestCase):

    def get_factory(self, qs):
        class SimpleFactory(filtering.FilterFactory):
            model = SampleModel
            str_col = filtering.CharFilter()

        return SimpleFactory(qs=qs)

    def test_value_is_empty(self):
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        self.assertEqual(factory.apply(self.freq({})), qs)

    def test_find_models(self):
        SampleModel.manager.create(str_col='a')
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        filtered_qs = factory.apply(self.freq({'str_col': 'a'}))
        self.assertEqual(filtered_qs.count(), 1)

        filtered_qs = factory.apply(self.freq({'str_col': 666}))
        self.assertEqual(filtered_qs.count(), 0)

    def test_like_lookup(self):
        SampleModel.manager.create(str_col='AbcD Wsad132')
        qs = SampleModel.query

        class SimpleLikeFactory(filtering.FilterFactory):
            model = SampleModel
            str_col = filtering.CharFilter(lookup='like')

        factory = SimpleLikeFactory(qs=qs)
        self.assertEqual(factory.apply(self.freq({'str_col': '1234'})).count(), 0)
        self.assertEqual(factory.apply(self.freq({'str_col': 'AB'})).count(), 1)
        self.assertEqual(factory.apply(self.freq({'str_col': 'CD'})).count(), 1)
        self.assertEqual(factory.apply(self.freq({'str_col': 'aBCd'})).count(), 1)

    def test_ilike_lookup(self):
        SampleModel.manager.create(str_col='AbcD Wsad132')
        qs = SampleModel.query

        class SimpleIlikeFactory(filtering.FilterFactory):
            model = SampleModel
            str_col = filtering.CharFilter(lookup='ilike')

        factory = SimpleIlikeFactory(qs=qs)
        self.assertEqual(factory.apply(self.freq({'str_col': '1234'})).count(), 0)
        self.assertEqual(factory.apply(self.freq({'str_col': 'AB'})).count(), 1)
        self.assertEqual(factory.apply(self.freq({'str_col': 'CD'})).count(), 1)
        self.assertEqual(factory.apply(self.freq({'str_col': 'aBCd'})).count(), 1)

    def test_contains_lookup(self):
        SampleModel.manager.create(str_col='AbcD Wsad132')
        qs = SampleModel.query

        class SimpleLikeFactory(filtering.FilterFactory):
            model = SampleModel
            str_col = filtering.CharFilter(lookup='contains')

        factory = SimpleLikeFactory(qs=qs)
        self.assertEqual(factory.apply(self.freq({'str_col': 'AAD'})).count(), 0)
        self.assertEqual(factory.apply(self.freq({'str_col': '1234'})).count(), 0)
        self.assertEqual(factory.apply(self.freq({'str_col': ' Wsad'})).count(), 1)


class DateTimeFilterTestCase(BaseFilterTestCase):

    def test_lt_lookup(self):
        now = datetime.now()
        SampleModel.manager.create(created_at=now)
        qs = SampleModel.query

        class SimpleDateTimeFactory(filtering.FilterFactory):
            model = SampleModel
            created_at = filtering.DateTimeFilter(lookup='__lt__')

        factory = SimpleDateTimeFactory(qs=qs)
        data = now
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 0)
        data = now + timedelta(seconds=10)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 1)
        data = now - timedelta(seconds=10)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 0)

    def test_lt_lookup_with_string(self):
        now = datetime.now()
        fmt = '%Y-%m-%d %H:%M:%S'
        SampleModel.manager.create(created_at=now)
        qs = SampleModel.query

        class SimpleDateTimeFactory(filtering.FilterFactory):
            model = SampleModel
            created_at = filtering.DateTimeFilter(lookup='__lt__')

        factory = SimpleDateTimeFactory(qs=qs)
        data = (now + timedelta(seconds=10)).strftime(fmt)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 1)
        data = (now - timedelta(seconds=10)).strftime(fmt)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 0)

    def test_eq_lookup(self):
        now = datetime.now()
        SampleModel.manager.create(created_at=now)
        qs = SampleModel.query

        class SimpleDateTimeFactory(filtering.FilterFactory):
            model = SampleModel
            created_at = filtering.DateTimeFilter(lookup='__eq__')

        factory = SimpleDateTimeFactory(qs=qs)
        data = now
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 1)
        data = now + timedelta(seconds=10)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 0)
        data = now - timedelta(seconds=10)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 0)

    def test_gt_lookup(self):
        now = datetime.now()
        SampleModel.manager.create(created_at=now)
        qs = SampleModel.query

        class SimpleDateTimeFactory(filtering.FilterFactory):
            model = SampleModel
            created_at = filtering.DateTimeFilter(lookup='__gt__')

        factory = SimpleDateTimeFactory(qs=qs)
        data = now
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 0)
        data = now - timedelta(seconds=10)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 1)
        data = now + timedelta(seconds=10)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 0)

    def test_gt_lookup_with_string(self):
        now = datetime.now()
        fmt = '%Y-%m-%d %H:%M:%S'
        SampleModel.manager.create(created_at=now)
        qs = SampleModel.query

        class SimpleDateTimeFactory(filtering.FilterFactory):
            model = SampleModel
            created_at = filtering.DateTimeFilter(lookup='__gt__')

        factory = SimpleDateTimeFactory(qs=qs)
        data = (now - timedelta(seconds=10)).strftime(fmt)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 1)
        data = (now + timedelta(seconds=10)).strftime(fmt)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 0)

    def test_gte_lookup(self):
        now = datetime.now()
        SampleModel.manager.create(created_at=now)
        qs = SampleModel.query

        class SimpleDateTimeFactory(filtering.FilterFactory):
            model = SampleModel
            created_at = filtering.DateTimeFilter(lookup='__ge__')

        factory = SimpleDateTimeFactory(qs=qs)
        data = now
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 1)
        data = now + timedelta(seconds=10)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 0)
        data = now - timedelta(seconds=10)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 1)

    def test_lte_lookup(self):
        now = datetime.now()
        SampleModel.manager.create(created_at=now)
        qs = SampleModel.query

        class SimpleDateTimeFactory(filtering.FilterFactory):
            model = SampleModel
            created_at = filtering.DateTimeFilter(lookup='__le__')

        factory = SimpleDateTimeFactory(qs=qs)
        data = now
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 1)
        data = now + timedelta(seconds=10)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 1)
        data = now - timedelta(seconds=10)
        self.assertEqual(factory.apply(self.freq({'created_at': data})).count(), 0)


class ComplexFilterTestCase(BaseFilterTestCase):

    def test_filter_against_three_attributes(self):
        now = datetime.now()
        SampleModel.manager.create(created_at=now, int_col=5, str_col='test')
        qs = SampleModel.query

        class ComplexFilterFactory(filtering.FilterFactory):
            model = SampleModel
            created_at = filtering.DateTimeFilter(lookup='__lt__')
            int_col = filtering.IntegerFilter()
            str_col = filtering.CharFilter(lookup='ilike')

        factory = ComplexFilterFactory(qs=qs)
        filter_data = {
            'created_at': (now + timedelta(seconds=10)).strftime('%Y-%m-%d %H:%M:%S')
        }
        self.assertEqual(factory.apply(self.freq(filter_data)).count(), 1)
        filter_data = {
            'created_at': (now + timedelta(seconds=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'int_col': 5
        }
        self.assertEqual(factory.apply(self.freq(filter_data)).count(), 1)
        filter_data = {
            'created_at': (now + timedelta(seconds=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'int_col': 6
        }
        self.assertEqual(factory.apply(self.freq(filter_data)).count(), 0)
        filter_data = {
            'created_at': (now + timedelta(seconds=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'int_col': 5,
            'str_col': 'test'
        }
        self.assertEqual(factory.apply(self.freq(filter_data)).count(), 1)
        filter_data = {
            'created_at': (now + timedelta(seconds=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'int_col': 5,
            'str_col': 'TEST'
        }
        self.assertEqual(factory.apply(self.freq(filter_data)).count(), 1)
        filter_data = {
            'created_at': (now + timedelta(seconds=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'int_col': 5,
            'str_col': 'testasudgasygdua'
        }
        self.assertEqual(factory.apply(self.freq(filter_data)).count(), 0)


class SortAndOrderTestCase(BaseFilterTestCase):

    def prepare_test(self):
        SampleModel.manager.create(int_col=7)
        SampleModel.manager.create(int_col=5)

        qs = SampleModel.query

        class ComplexFilterFactory(filtering.FilterFactory):
            model = SampleModel
            int_col = filtering.IntegerFilter(lookup='__ge__')

        return ComplexFilterFactory(qs=qs)

    def test_no_sort_applied(self):
        factory = self.prepare_test()
        filter_data = {
            'int_col': 5
        }
        qs = factory.apply(self.freq(filter_data))
        self.assertEqual(qs.count(), 2)
        self.assertEqual(qs.all()[0].int_col, 7)
        self.assertEqual(qs.all()[1].int_col, 5)

    def test_sort_ascending_order(self):
        factory = self.prepare_test()
        filter_data = {
            'int_col': 5,
            'sort_by': 'int_col',
            'order': 'asc'
        }
        qs = factory.apply(self.freq(filter_data))
        self.assertEqual(qs.count(), 2)
        self.assertEqual(qs.all()[0].int_col, 5)
        self.assertEqual(qs.all()[1].int_col, 7)

    def test_sort_specified_but_order_should_be_asc_by_default(self):
        factory = self.prepare_test()
        filter_data = {
            'int_col': 5,
            'sort_by': 'int_col'
        }
        qs = factory.apply(self.freq(filter_data))
        self.assertEqual(qs.count(), 2)
        self.assertEqual(qs.all()[0].int_col, 5)
        self.assertEqual(qs.all()[1].int_col, 7)

    def test_descending_order_sort(self):
        factory = self.prepare_test()
        filter_data = {
            'int_col': 5,
            'sort_by': 'int_col',
            'order': 'desc'
        }
        qs = factory.apply(self.freq(filter_data))
        self.assertEqual(qs.count(), 2)
        self.assertEqual(qs.all()[0].int_col, 7)
        self.assertEqual(qs.all()[1].int_col, 5)

    def test_order_does_not_make_sense_default_to_none(self):
        factory = self.prepare_test()
        filter_data = {
            'int_col': 5,
            'sort_by': 'int_col',
            'order': 'asuydasygdasyugd'
        }
        qs = factory.apply(self.freq(filter_data))
        self.assertEqual(qs.count(), 2)


class FloatAndDecimalFilterTestCase(BaseFilterTestCase):

    def get_factory(self, qs):
        class SimpleFactory(filtering.FilterFactory):
            model = SampleModel
            float_col = filtering.FloatFilter()
            dec_col = filtering.DecimalFilter()

        return SimpleFactory(qs=qs)

    def test_value_is_empty(self):
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        self.assertEqual(factory.apply(self.freq({})), qs)

    def test_find_models(self):
        SampleModel.manager.create(float_col=1.0, dec_col=5.0)
        SampleModel.manager.create(float_col=2.0, dec_col=6.0)
        qs = SampleModel.query
        factory = self.get_factory(qs=qs)
        filtered_qs = factory.apply(self.freq({'float_col': 1.0}))
        self.assertEqual(filtered_qs.count(), 1)

        filtered_qs = factory.apply(self.freq({'dec_col': 6.0}))
        self.assertEqual(filtered_qs.count(), 1)