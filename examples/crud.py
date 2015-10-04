import sqlalchemy as sa

from pyramid.config import Configurator

from sqlalchemy import engine_from_config
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative.api import declarative_base

from seth import db
from seth.db.base import Model


Base = declarative_base(cls=Model)


# Basic model definition
class SuperModel(Base):
    string_column = sa.Column(sa.String(512))

    def __repr__(self):
        return u"SuperModel {0}".format(self.id)


if __name__ == '__main__':
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
    session.add(SuperModel(**{'string_column': 'a'}))
    session.add(SuperModel(**{'string_column': 'b'}))
    db.commit()

    config.include('seth')
    app = config.make_wsgi_app()

    print "Querying using manager"
    print SuperModel.manager.all()

    print "Querying using query proxy"
    print SuperModel.query.all()

    print "Filtering using manager"
    print SuperModel.manager.find(string_column='a').all()

    print "Using get or create - returns (obj, created)"
    print SuperModel.manager.get_or_create(id=55)

    print "Replying same operation - return (obj, created)"
    print SuperModel.manager.get_or_create(id=55)

    print "Creating model"
    print "Before: {0}".format(SuperModel.query.count())
    SuperModel.manager.create(**{})
    print "After: {0}".format(SuperModel.query.count())

    print "Paginating"
    pagination = SuperModel.manager.paginate()
    print "Pagination - json repr"
    print pagination.__json__()
