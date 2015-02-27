from seth import db
from seth.paginator import paginate


class BaseManager(object):

    def __init__(self, model_class, **kwargs):
        self.model_class = model_class

    @property
    def query(self):
        return db.get_session().query(self.model_class)

    def filter_query(self, qs=None, filters=None):
        if not qs:
            qs = self.query

        filters = filters if filters else []
        for f in filters:
            qs = qs.filter(f)
        return qs

    def paginate(self, filters=None, page=1, per_page=20, **kwargs):
        qs = self.filter_query(self.query, filters)
        return paginate(qs, page, per_page, **kwargs)