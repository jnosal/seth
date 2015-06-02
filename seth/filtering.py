import decimal
import datetime


class LookupParam(object):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get_lookup(self):
        if self.name in ['like', 'ilike']:
            return u'%{0}%'.format(self.value)
        return self.value


class Filter(object):
    lookup = ''

    def __init__(self, name=None, required=False, lookup=None, **kw):
        self.name = name
        self.required = required
        self.lookup = lookup if lookup else self.lookup
        assert self.lookup

    def prepare_value(self, value):
        return value

    def filter(self, model, qs, param, value):
        if value in [(), [], {}, '', None]:
            return qs

        # value we are filtering against
        value = self.prepare_value(value)

        # Get sqlalchemy InstrumentedAttribute
        column = getattr(model, param)

        # Get column attribute to filter against
        # most of the time its just value
        lookup_value = LookupParam(self.lookup, value).get_lookup()

        filter_ = getattr(column, self.lookup)(lookup_value)
        return qs.filter(filter_)


class BooleanFilter(Filter):
    lookup = '__eq__'

    def prepare_value(self, value):
        if isinstance(value, bool):
            return value

        value_map = {
            'true': True,
            'false': False,
        }
        if isinstance(value, (unicode, str)) and value.lower() in value_map:
            return value_map.get(value.lower(), bool(value))

        raise AttributeError


class IntegerFilter(Filter):
    lookup = '__eq__'

    def prepare_value(self, value):
        return int(value)


class FloatFilter(Filter):
    lookup = '__eq__'

    def prepare_value(self, value):
        return float(value)


class DecimalFilter(Filter):
    lookup = '__eq__'

    def prepare_value(self, value):
        return decimal.Decimal(value)


class CharFilter(Filter):
    lookup = 'like'


class BaseDateTimeFilter(Filter):
    lookup = '__eq__'
    date_fmt = None

    def __init__(self, name=None, required=False, lookup=None, **kw):
        super(BaseDateTimeFilter, self).__init__(name, required, lookup, **kw)
        assert self.date_fmt


class DateTimeFilter(BaseDateTimeFilter):
    date_fmt = '%Y-%m-%d %H:%M:%S'

    def prepare_value(self, value):
        if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            return value

        return datetime.datetime.strptime(value, self.date_fmt)


class DateFilter(BaseDateTimeFilter):
    date_fmt = '%Y-%m-%d'

    def prepare_value(self, value):
        if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            return value

        return datetime.datetime.strptime(value, self.date_fmt).date()


class TimeFilter(BaseDateTimeFilter):
    date_fmt = '%H:%M:%S'

    def prepare_value(self, value):
        if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            return value

        return datetime.datetime.strptime(value, self.date_fmt).time()


class FilterFactoryMeta(type):
    """
        Creates filters attribute on FilterFactory class which represents
        param <-> filter map
    """
    def __new__(cls, name, bases, attrs):
        new_attrs = attrs.copy()
        new_attrs['filters'] = {}

        for (el, val) in attrs.iteritems():
            if isinstance(val, Filter):
                filter_name = val.name if val.name else el
                new_attrs['filters'][filter_name] = val

        return super(FilterFactoryMeta, cls).__new__(cls, name, bases, new_attrs)


class BaseFilterFactory(object):
    model = None

    def __init__(self, qs, *args, **kwargs):
        assert self.model
        self.qs = qs

    def get_sort_by_and_order(self, request):
        sort_by = request.params.get('sort_by', '')
        sort_by = sort_by.split(',', 1)[0]

        if not sort_by in self.filters:
            sort_by = ''

        order = request.params.get('order', 'asc')
        if not order in ['asc', 'desc']:
            order = None

        return sort_by, order 

    def process_sort_by_and_order(self, qs, request, sort_by, order):
        return qs.order_by("%s %s" % (sort_by, order))

    def apply(self, request, *args, **kwargs):
        qs = self.qs

        if not self.filters:
            return qs

        for (name, field) in self.filters.iteritems():
            value = request.params.get(name, None)
            qs = field.filter(self.model, qs, name, value)

        sort_by, order = self.get_sort_by_and_order(request)
        if sort_by and order:
            qs = self.process_sort_by_and_order(qs, request, sort_by, order)

        return qs


class FilterFactory(BaseFilterFactory):
    __metaclass__ = FilterFactoryMeta