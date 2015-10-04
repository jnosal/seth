from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr

from seth.decorators import classproperty
from seth.db.managers import BaseManager


class Model(object):

    json_included = []
    json_excluded = []
    __table_args__ = {}

    def _get_attrs_to_include(self):
        return self.json_included

    @declared_attr
    def manager(cls):
        # manager is a class that can have some additional methods
        # apart from just those provided by sqlalchemy interface
        return BaseManager(model_class=cls)

    @classproperty
    def query(cls):
        # proxy to sqlalchemy session.query
        return cls.manager.query

    @declared_attr
    def __tablename__(cls):
        name = cls.__name__.lower()
        return "{0}s".format(name) if not name.endswith('s') else name

    @declared_attr
    def id(self):
        return Column(Integer, autoincrement=True, primary_key=True)

    def __json__(self, request=None):
        data = {}
        for el, val in vars(self).iteritems():
            if not el.startswith('_') and not el in self.json_excluded:

                if isinstance(val, Model):
                    data[el] = val.__json__()
                else:
                    data[el] = val

        for key in self._get_attrs_to_include():
            if hasattr(self, key):
                data[key] = getattr(self, key)
        return data

    def to_dict(self):
        return self.__json__(request=None)


class TimeStampedModel(Model):

    @declared_attr
    def created_at(self):
        return Column(DateTime, default=datetime.now, nullable=False)

    @declared_attr
    def updated_at(self):
        return Column(DateTime, onupdate=datetime.now, nullable=True)

    @declared_attr
    def is_deleted(self):
        return Column(Boolean, default=False)