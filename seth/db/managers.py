from seth import db
from seth.paginator import paginate


class BaseManager(object):

    def __init__(self, model_class, **kwargs):
        self.model_class = model_class

    @property
    def query(self):
        return db.get_session().query(self.model_class)

    def _isinstance(self, model, raise_error=True):
        rv = isinstance(model, self.model_class)
        if not rv and raise_error:
            raise ValueError('%s is not of type %s' % (model, self.model_class))
        return rv

    def _preprocess_params(self, kwargs):
        banned_params = []

        for param in banned_params:
            kwargs.pop(param, None)

        return kwargs

    def save(self, model):
        self._isinstance(model)
        db.get_session().add(model)
        return model

    def all(self):
        return self.model_class.query.all()

    def get(self, id):
        return self.model_class.query.get(id)

    def get_all(self, *ids):
        return self.model_class.query.filter(self.model_class.id.in_(ids)).all()

    def find(self, **kwargs):
        return self.model_class.query.filter_by(**kwargs)

    def first(self, **kwargs):
        return self.find(**kwargs).first()

    def get_or_404(self, id):
        return self.model_class.query.get_or_404(id)

    def new(self, **kwargs):
        return self.model_class(**self._preprocess_params(kwargs))

    def create(self, **kwargs):
        return self.save(self.new(**kwargs))

    def update(self, model, **kwargs):
        self._isinstance(model)
        for k, v in self._preprocess_params(kwargs).items():
            setattr(model, k, v)
        self.save(model)
        return model

    def delete(self, model):
        self._isinstance(model)
        db.get_session().delete(model)

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