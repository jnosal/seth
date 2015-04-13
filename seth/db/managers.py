from pyramid.httpexceptions import HTTPNotFound

from seth import db
from seth.paginator import paginate


class BaseManager(object):
    """ Proxy manager for all models created as subclasses of
    `*seth.db.mixins.PlainModelMixin`. Provides basic crud interface
    and couple of utility functions

    For example:

    .. code-block:: python

        MyModel.manager.get_all(1, 2, 3)
        MyModel.manager.first()
        MyModel.manager.create(**{})
        MyModel.manager.find(id=3)

    """
    def __init__(self, model_class, **kwargs):
        self.model_class = model_class

    @property
    def query(self):
        """ Provides shortcut to sqlalchemy's `*session.query` function
        from manager.

        For example:

        .. code-block:: python

            MyModel.manager.query

        or

        .. code-block:: python

            MyModel.query

        """
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
        """ Saves model instance.
        Before actual saving it runs `*_isinstance` function.
        """
        self._isinstance(model)
        db.get_session().add(model)
        return model

    def new(self, **kwargs):
        """ Returns new model instance initialized with data
        found in `*kwargs`
        """
        return self.model_class(**self._preprocess_params(kwargs))

    def create(self, **kwargs):
        """ Returns new model instance initialized with data
        found in `*kwargs` and saves it in database.
        """
        return self.save(self.new(**kwargs))

    def all(self):
        """ Returns all models from database.
        """
        return self.model_class.query.all()

    def get(self, id):
        """ Returns model instance based on primary key or `*None`
        """
        return self.model_class.query.get(id)

    def get_all(self, *ids):
        """ Returns all model instances that much primary keys provided

        For example:

        .. code-block:: python

            models = MyModel.manager.get_all(1, 2, 3)

        """
        return self.model_class.query.filter(self.model_class.id.in_(ids)).all()

    def get_or_404(self, **kwargs):
        """ Returns model instance that matches `*kwargs` or raises `*HTTPNotFound`
        """

        obj = self.model_class.query.filter_by(**kwargs).first()
        if not obj:
            raise HTTPNotFound(detail=u"Object doest not exist")
        return obj

    def get_or_create(self, **kwargs):
        """ Returns model instance that matches `*kwargs` or creates it
        if it does not exist.

        For example:

        .. code-block:: python

            obj, created = MyModel.manager.get_or_created(id=1)

        """
        obj = self.model_class.query.filter_by(**kwargs).first()
        if obj:
            return obj, False
        else:
            return self.create(**kwargs), True

    def find(self, **kwargs):
        """ Returns model instances that match `*kwargs`.
        """

        return self.model_class.query.filter_by(**kwargs)

    def first(self, **kwargs):
        """ Returns first model instance that matches `*kwargs`.
        """

        return self.find(**kwargs).first()

    def update(self, model, **kwargs):
        self._isinstance(model)
        for k, v in self._preprocess_params(kwargs).items():
            setattr(model, k, v)
        self.save(model)
        return model

    def delete(self, model):
        """ Deletes model instance performing verification first.
        """

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