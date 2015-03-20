# -*- coding: utf-8 -*-

from __future__ import absolute_import, division
import os
import unittest
from pkg_resources import resource_filename

from mock import Mock
from pyramid import testing
from sqlalchemy import engine_from_config
from paste.deploy.loadwsgi import appconfig
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from seth import db
from seth.tests.base import ExtendedTestApp
from seth.tests.models import Base
here = os.path.dirname(__file__)


def get_settings():
    return appconfig('config:' + resource_filename(__name__, 'test.ini'))


class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(get_settings(), prefix='sqlalchemy.')
        maker = scoped_session(sessionmaker(
            extension=ZopeTransactionExtension()
        ))
        maker.configure(bind=cls.engine)
        db.register_maker(maker)
        Base.metadata.bind = cls.engine
        Base.metadata.create_all(cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        self.connection = self.engine.connect()
        self.trans = self.connection.begin()
        self.config = testing.setUp()
        self.session = db.get_session()

    def tearDown(self):
        testing.tearDown()
        self.session.close()
        self.trans.rollback()
        db.rollback()
        self.connection.close()


class UnitTestBase(BaseTestCase):

    def get_csrf_request(self, post=None, request_method='GET', params=None):
        csrf = 'abc'

        post = post if post else {}
        params = params if params else {}

        if not 'csrf_token' in post.keys():
            post.update({
                'csrf_token': csrf
            })

        request = testing.DummyRequest(params=params, post=post)

        request.session = Mock()
        csrf_token = Mock()
        csrf_token.return_value = csrf

        request.session.get_csrf_token = csrf_token
        request.method = request_method

        return request


class IntegrationTestBase(BaseTestCase):

    def main(self, global_config, **settings):
        config = global_config
        config.add_settings(**get_settings())
        app = config.make_wsgi_app()
        return app

    def extend_app_configuration(self, config):
        pass

    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        self.extend_app_configuration(self.config)
        app = self.main(self.config, **get_settings())
        self.app = ExtendedTestApp(app)