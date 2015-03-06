# -*- coding: utf-8 -*-

from __future__ import absolute_import
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from seth.db.mixins import BaseModelMixin
from seth.db.managers import BaseManager


Base = declarative_base(cls=BaseModelMixin)


class SampleModel(Base):
    int_col = sa.Column(sa.Integer)
    dec_col = sa.Column(sa.Numeric)
    str_col = sa.Column(sa.String)
    bool_col = sa.Column(sa.Boolean)
    float_col = sa.Column(sa.Float)


class PredefinedManager(BaseManager):

    def non_existant(self):
        return 1


class PredefinedModel(Base):
    json_included = ['sth']

    @declared_attr
    def manager(cls):
        return PredefinedManager(model_class=cls)

    @property
    def sth(self):
        return u"sth"
