from seth import db
from seth.paginator import paginate


class BaseManager(object):

    def __init__(self, model_class, **kwargs):
        self.model_class = model_class
        self._qs = None

    def get_query(self):
        if not self._qs:
            session = db.get_session()
            return session.query(self.model_class)
        return self._qs

    def from_query(self, query):
        self._qs = query
        return self

    def clear_query(self):
        self._qs = None
        return self

    def filter_query(self, qs, filters):
        filters = filters if filters else []
        for f in filters:
            qs = qs.filter(f)
        return qs

    def load(self, filters=None):
        qs = self.get_query()
        qs = self.filter_query(qs, filters)
        return qs.all()

    def count(self, filters=None):
        qs = self.get_query()
        qs = self.filter_query(qs, filters)
        return qs.count()

    def paginate(self, filters=None, page=1, per_page=20, **kwargs):
        qs = self.get_query()
        qs = self.filter_query(qs, filters)
        return paginate(qs, page, per_page, **kwargs)