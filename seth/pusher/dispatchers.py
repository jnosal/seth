import logging


class DefaultMessageDispatcher(object):
    # Validates messages and delegates them to proper handler
    # functions
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    SUBSCRIBE = 'subscribe'
    UNSUBSCRIBE = 'unsubscribe'

    def __init__(self):
        self.subscriber_id = None
        self.subscribed_to = set()
        self.messages = {
            self.CONNECT: self.handle_connect,
            self.SUBSCRIBE: self.handle_subscribe,
            self.UNSUBSCRIBE: self.handle_unsubscribe
        }
        self.handler = None

    def register_handler(self, handler):
        self.handler = handler

    @property
    def channels(self):
        return [_ for _ in self.subscribed_to]

    @property
    def is_connected(self):
        return self.subscriber_id is not None

    def validate_message(self, msg):
        if not isinstance(msg, dict):
            error = u"Message must be a python dictionary."
            return False, error

        type_ = msg.get('type', None)

        if not type_:
            error = u"Message must have type."
            return False, error

        if not type_ in self.messages.keys():
            error = u"Wrong type: {0}.".format(type_)
            return False, error

        if type_ == self.CONNECT and msg.get('subscriber_id', None) is None:
            error = u"Must provide subscriber_id for connect message."
            return False, error

        if type_ in [self.SUBSCRIBE, self.UNSUBSCRIBE] and msg.get('channel', None) is None:
            error = u"Must provide channel for sub/unsub message."
            return False, error

        return True, None

    def dispatch(self, msg):
        type_ = msg['type']
        logging.debug(u"Handling {0} message.".format(type_))
        self.messages[type_](msg)

    def handle_connect(self, msg):
        if not self.handler:
            raise AttributeError(u"No handler registered.")

        if self.is_connected:
            logging.warning(u"Already connected.")
            return

        subscriber_id = msg['subscriber_id']
        self.subscriber_id = subscriber_id
        self.handler.handle_connect(msg, subscriber_id)

    def handle_subscribe(self, msg):
        if not self.handler:
            raise AttributeError(u"No handler registered.")

        self.subscribed_to.add(msg['channel'])
        self.handler.handle_subscribe(msg)

    def handle_unsubscribe(self, msg):
        if not self.handler:
            raise AttributeError(u"No handler registered.")

        try:
            self.subscribed_to.remove(msg['channel'])
        except KeyError:
            pass

        self.handler.handle_unsubscribe(msg)
