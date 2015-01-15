# -*- coding: utf-8 -*-

from __future__ import absolute_import
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from seth.db.mixins import BaseModelMixin
from seth.db.managers import BaseManager


Base = declarative_base(cls=BaseModelMixin)


class SampleModel(Base):
    pass


class PredefinedManager(BaseManager):

    def non_existant(self):
        return 1


class PredefinedModel(Base):

    @declared_attr
    def manager(cls):
        return PredefinedManager(model_class=cls)
