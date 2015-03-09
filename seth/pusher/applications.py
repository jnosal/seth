from tornado.web import Application

from seth.pusher.api.urls import get_api_handlers
from seth.pusher.ws.urls import get_ws_handlers
from seth.pusher import mixins
from seth.pusher import dispatchers


class DefaultSethApplication(Application):

    def get_dispatcher(self):
        return dispatchers.DefaultMessageDispatcher()

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', False)
        handlers = get_api_handlers(self) + get_ws_handlers(self)
        self.subscriber = self.get_subscriber(**kwargs)
        self.publisher = self.get_publisher(**kwargs)
        super(DefaultSethApplication, self).__init__(handlers, **kwargs)


class SethPusherOnRedisApplication(DefaultSethApplication,
                                   mixins.RedisPubSubMixin):
    pass


class SethPusherInMemoryApplication(DefaultSethApplication,
                                    mixins.InMemoryPubSubMixin):
    pass