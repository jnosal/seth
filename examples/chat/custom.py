import logging

from seth.pusher.applications import DefaultSethApplication
from seth.pusher import mixins


class Batman(DefaultSethApplication,
             mixins.InMemoryPubSubMixin):

    def __init__(self, **kwargs):
        super(Batman, self).__init__(**kwargs)
        logging.critical("I'm Batman. BEHOLD")