from sockjs.tornado import SockJSRouter

from seth.pusher.ws import views


class SethSockJSRouter(SockJSRouter):

    def __init__(self, connection, prefix='',
                 user_settings=dict(), io_loop=None, **kwargs):
        super(SethSockJSRouter, self).__init__(connection, prefix,
                                               user_settings, io_loop)
        self.application = kwargs.get('application_instance', None)


def get_ws_handlers(application_instance):
    return SethSockJSRouter(
        connection=views.SethSocketHandler,
        prefix='/connect',
        application_instance=application_instance
    ).urls
