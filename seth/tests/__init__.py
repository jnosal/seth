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
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from seth.tests.models import Base


here = os.path.dirname(__file__)
settings = appconfig('config:' + resource_filename(__name__, 'test.ini'))

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.Session = sessionmaker()

    def setUp(self):
        self.config = testing.setUp()

        self.connection = connection = self.engine.connect()

        # begin a non-ORM transaction
        self.trans = connection.begin()

        # bind an individual Session to the connection
        self.session = self.Session(bind=connection)

        Base.metadata.bind = connection

    def tearDown(self):
        testing.tearDown()
        self.trans.rollback()
        self.session.close()
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


class IntegrationTestBase(unittest.TestCase):

    def main(self, global_config, **settings):
        config = global_config
        config.add_settings(settings)

        app = config.make_wsgi_app()
        return app

    def setUp(self):
        self.engine = engine_from_config(settings, prefix='sqlalchemy.')
        config = testing.setUp()
        app = self.main(config, **settings)

        self.app = TestApp(app)
        self.connection = connection = self.engine.connect()

        self.session.configure(bind=connection)
        self.trans = connection.begin()

        Base.metadata.bind = connection

    def tearDown(self):
        testing.tearDown()
        self.trans.rollback()
        self.session.close()