# -*- coding: utf-8 -*-

from __future__ import absolute_import, division
import os
import unittest
from pkg_resources import resource_filename

from mock import Mock
from webtest import TestApp
from sqlalchemy import engine_from_config
from pyramid import testing
from paste.deploy.loadwsgi import appconfig
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from seth import db
from seth.tests.models import Base
here = os.path.dirname(__file__)
settings = appconfig('config:' + resource_filename(__name__, 'test.ini'))


class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        # maker = scoped_session(sessionmaker(
        #     extension=ZopeTransactionExtension(),
        #     query_cls=DeletionFilterQuery
        # ))
        maker = sessionmaker(
            extension=ZopeTransactionExtension()
        )
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

    def get_csrf_request(self, post=None, request_method='GET'):
        csrf = 'abc'

        if not post:
            post = {}

        if not 'csrf_token' in post.keys():
            post.update({
                'csrf_token': csrf
            })

        request = testing.DummyRequest(post)

        request.session = Mock()
        csrf_token = Mock()
        csrf_token.return_value = csrf

        request.session.get_csrf_token = csrf_token
        request.method = request_method

        return request


class IntegrationTestBase(BaseTestCase):

    def main(self, global_config, **settings):
        config = global_config
        config.add_settings(settings)
        config.include('seth')
        app = config.make_wsgi_app()
        return app

    def extend_app_configuration(self, config):
        pass

    def setUp(self):
        super(IntegrationTestBase, self).setUp()
        self.extend_app_configuration(self.config)
        app = self.main(self.config, **settings)
        self.app = TestApp(app)