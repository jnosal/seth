# -*- coding: utf-8 -*-

from __future__ import absolute_import
from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.scan()
    return config.make_wsgi_app()