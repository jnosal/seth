from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr
from seth.db.managers import BaseManager


class BaseModelMixin(object):

    __table_args__ = {}

    @declared_attr
    def manager(cls):
        return BaseManager(model_class=cls)

    @declared_attr
    def __tablename__(cls):
        name = cls.__name__.lower()
        return "{0}s".format(name) if not name.endswith('s') else name

    @declared_attr
    def id(self):
        return Column(Integer, autoincrement=True, primary_key=True)

    @declared_attr
    def created_at(self):
        return Column(DateTime, default=datetime.now, nullable=False)

    @declared_attr
    def updated_at(self):
        return Column(DateTime, onupdate=datetime.now, nullable=True)

    @declared_attr
    def is_deleted(self):
        return Column(Boolean, default=False)

    def __json__(self, request=None):
        pass