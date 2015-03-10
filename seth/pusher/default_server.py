import sys
import time
import signal
import logging
import importlib

from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import define, parse_command_line, options
from seth.pusher import applications

define('debug', default=False, type=bool, help=u'Run in debug mode')
define('port', default=8080, type=int, help=u'Server port to bind to')
define('host', default='127.0.0.1', type=str, help=u'Server host')
define('app', default='', type=str, help=u'Pusher application to run')


def shutdown(server_instance):
    ioloop_instance = IOLoop.instance()
    logging.info(u'Stopping Seth pusher server gracefully.')
    server_instance.stop()

    def finalize():
        ioloop_instance.stop()
        logging.info(u'Seth pusher server stopped.')

    ioloop_instance.add_timeout(time.time() + 1.5, finalize)


def main():
    parse_command_line()

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug(u"DEBUG MODE is ON")

    if options.app:
        try:
            components = options.app.split('.')
            module_name = ".".join(components[:-1])
            logging.info(u"Importing {0}".format(module_name))
            module = importlib.import_module(module_name)
            ApplicationClass = getattr(module, components[-1])
        except AttributeError:
            logging.error(u"Problem loading application from path")
            sys.exit(1)
    else:
        ApplicationClass = applications.SethPusherInMemoryApplication

    logging.info(u"Application Class: {0}".format(ApplicationClass.__name__))

    application = ApplicationClass(**options.as_dict())

    server = HTTPServer(application)
    server.listen(options.port, options.host)

    shutdown_handler = lambda sig, frame: shutdown(server)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logging.info(u"Starting Seth pusher server on {0}:{1}.".format(
        options.host, options.port
    ))
    IOLoop.instance().start()