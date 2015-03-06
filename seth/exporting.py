from sqlalchemy.orm.query import Query


class SethExportException(Exception):
    """"""


class Field(object):

    def __init__(self, name, *args, **kwargs):
        self.name = name

    def __call__(self, item):
        value = item[self.name]
        return value if value else u'-'


class NestedField(Field):

    def __init__(self, name, nested, *args, **kwargs):
        super(NestedField, self).__init__(name, *args, **kwargs)
        self.nested = nested

    def __call__(self, item):
        attribute = item.get(self.name, None)
        return attribute.get(self.nested, u'') if attribute else u'-'


class DoubleNestedField(Field):

    def __init__(self, name, nested, dnested, *args, **kwargs):
        super(DoubleNestedField, self).__init__(name, *args, **kwargs)
        self.nested = nested
        self.dnested = dnested

    def __call__(self, item):
        wrapper = item[self.name]
        attribute = wrapper.get(self.nested, u'')
        return attribute.get(self.dnested, u'') if attribute else u'-'


class ExportFactory(object):
    model = None
    title = None
    header = list()
    properties = list()

    def __init__(self, items, *args, **kwargs):
        assert self.model
        if isinstance(items, Query):
            self.items = (i.to_dict() for i in items.all())
        else:
            self.items = (i.to_dict() for i in items)

        self.validate()

    def validate(self):
        if len(self.header) != len(self.properties):
            raise SethExportException(u"Header must match properties length")

        for cell in self.properties:
            if not isinstance(cell, Field):
                raise SethExportException(u"Cell must be instance of Field")

            if not hasattr(self.model, cell.name):
                msg = u"Model {0} does not have property {1}".format(
                    self.model.__name__, cell.name
                )
                raise SethExportException(msg)

    def _cell(self, item):
        for cell in self.properties:
            yield cell(item)

    @property
    def rows(self):
        for item in self.items:
            yield self._cell(item)

    def get_export_data(self):
        return {
            'rows': [[i for i in j] for j in self.rows],
            'title': self.title,
            'header': self.header
        }