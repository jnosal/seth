import logging

from seth.pusher.applications import DefaultSethApplication
from seth.pusher import mixins


class Batman(DefaultSethApplication,
             mixins.InMemoryPubSubMixin):

    def __init__(self, **kwargs):
        super(Batman, self).__init__(**kwargs)
        logging.critical("I'm Batman. BEHOLD")

    def add_subscriber(self, channel, subscriber):
        logging.critical("Batman has intercepted your subscribtion !")
        super(Batman, self).add_subscriber(channel, subscriber)

    def remove_subscriber(self, channel, subscriber):
        logging.critical("Batman has intercepted your unsubscribtion !")
        super(Batman, self).add_subscriber(channel, subscriber)

    def broadcast(self, message, channel=None, sender=None):
        logging.critical("Batman has intercepted broadcast message !")
        super(Batman, self).broadcast(message, channel, sender)