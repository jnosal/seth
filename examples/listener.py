import logging

import sqlalchemy as sa
from wsgiref.simple_server import make_server
from pyramid.config import Configurator

from sqlalchemy import engine_from_config
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative.api import declarative_base

from seth import db
from seth.db.base import Model
from seth.classy.rest import generics


Base = declarative_base(cls=Model)


# Basic model definition
class SuperModel(Base):
    string_column = sa.Column(sa.String(512))

    def __repr__(self):
        return u"SuperModel {0}".format(self.id)


class SampleResource(generics.GenericApiView):

    def get(self):
        print SuperModel.query.count()
        SuperModel.query.all()
        return {}


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    config = Configurator()
    settings = {
        'sqlalchemy.url': 'sqlite://'
    }

    engine = engine_from_config(settings, prefix='sqlalchemy.')
    maker = scoped_session(sessionmaker(
        extension=ZopeTransactionExtension()
    ))
    maker.configure(bind=engine)
    db.register_maker(maker=maker)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    # create two blank models
    session = db.get_session()
    for i in range(10000):
        SuperModel.manager.create()
    db.commit()

    config.include('seth')
    config.register_query_listener(engine, 0)
    config.register_resource(SampleResource, '/test/')

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()
