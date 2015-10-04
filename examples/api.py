from pyramid.config import Configurator
from wsgiref.simple_server import make_server

import sqlalchemy as sa
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative.api import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from marshmallow import Schema, fields

from seth import db
from seth import filtering
from seth.classy.rest import generics
from seth.db.base import TimeStampedModel


Base = declarative_base(cls=TimeStampedModel)


# Basic model definition
class SuperModel(Base):
    string_column = sa.Column(sa.String(512))


# Define model filter
class SuperModelFilters(filtering.FilterFactory):
    model = SuperModel
    string_column = filtering.CharFilter()


# Basic schema definition - TimeStampedModel predefines four fields:
# id, is_deleted, created_at, updated_at
class SuperModelSchema(Schema):
    id = fields.Integer()
    is_deleted = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    string_column = fields.String()


# Sample Model Api View
class SampleModelApiView(generics.ListReadOnlyApiView):
    schema = SuperModelSchema
    filter_class = SuperModelFilters
    paginate = True

    def get_queryset(self, *args, **kwargs):
        return SuperModel.query


# Sample Model Api View without pagination
class SampleModelNoPaginateApiView(generics.ListReadOnlyApiView):
    schema = SuperModelSchema
    filter_class = SuperModelFilters
    paginate = False

    def get_queryset(self, *args, **kwargs):
        return SuperModel.query


# Basic api view using GenericApiView base class
class SampleApiView(generics.GenericApiView):

    def get(self, **kwargs):
        return {'hey': 'ho'}


if __name__ == '__main__':
    config = Configurator()
    # predefine in memory sqlalchemy database
    settings = {
        'sqlalchemy.url': 'sqlite://'
    }

    engine = engine_from_config(settings, prefix='sqlalchemy.')
    maker = scoped_session(sessionmaker(
        extension=ZopeTransactionExtension()
    ))
    maker.configure(bind=engine)
    # register maker for seth db
    db.register_maker(maker=maker)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    # create two blank models
    session = db.get_session()
    session.add(SuperModel(**{'string_column': 'a'}))
    session.add(SuperModel(**{'string_column': 'b'}))
    db.commit()

    # add seth and register resources
    config.include('seth')
    config.register_resource(SampleApiView, '/test/')
    config.register_resource(SampleModelApiView, '/test_pager/')
    config.register_resource(SampleModelNoPaginateApiView, '/test_no_pager/')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()