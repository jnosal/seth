import json
import logging

from sockjs.tornado import SockJSConnection


class SethSocketHandler(SockJSConnection):

    @property
    def application(self):
        return self.session.server.application

    def check_origin(self, origin):
        allowed = super(SethSocketHandler, self).check_origin(origin)
        return True

    def on_open(self, request):
        logging.debug(u"New connection opened.")
        self.dispatcher = self.application.get_dispatcher()
        self.dispatcher.register_handler(self)

    def on_message(self, raw_msg):
        try:
            message = json.loads(raw_msg)
        except ValueError:
            logging.error(u"Could not dispatch {0}".format(raw_msg))
            return

        logging.debug(u"Got message: {0}".format(
            message
        ))

        is_valid, error = self.dispatcher.validate_message(message)
        if not is_valid:
            logging.error(error)
            return

        self.dispatcher.dispatch(message)

    def on_close(self):
        logging.debug(u"Closing connection.")

        for channel in self.dispatcher.channels:
            self.application.remove_subscriber(channel, self)

        if self.dispatcher.subscriber_id:
            subscriber_id = self.dispatcher.subscriber_id
            message = {
                'body': u'User: {0} disconnected.'.format(subscriber_id),
                'target_id': subscriber_id,
                'type': self.dispatcher.DISCONNECT
            }
            self.application.broadcast(message=message, channel=None)

    def close(self, code=3000, message=""):
        self.session.close(code, message)

    def handle_connect(self, source_msg, subscriber_id):
        message = {
            'body': u"User: {0} connected.".format(subscriber_id),
            'target_id': subscriber_id,
            'type': self.dispatcher.CONNECT
        }
        self.application.broadcast(message=message, channel=None)

    def handle_subscribe(self, source_msg):
        channel = source_msg['channel']
        subscriber_id = self.dispatcher.subscriber_id

        self.application.add_subscriber(channel, self)
        message = {
            'body': u'User: {0} subscribed to {1}'.format(
                subscriber_id, channel
            ),
            'target_id': subscriber_id,
            'type': self.dispatcher.SUBSCRIBE
        }
        self.application.broadcast(message=message, channel=channel)

    def handle_unsubscribe(self, source_msg):
        channel = source_msg['channel']
        subscriber_id = self.dispatcher.subscriber_id

        self.application.remove_subscriber(channel, self)
        message = {
            'body': u'User: {0} unsubscribed from {1}'.format(
                subscriber_id, channel
            ),
            'target_id': subscriber_id,
            'type': self.dispatcher.UNSUBSCRIBE
        }
        self.application.broadcast(message=message, channel=channel)

