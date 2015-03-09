import json
from collections import defaultdict


class BasicPubSubManager(object):

    def __init__(self):
        self.channels = defaultdict(set)

    def subscribe(self, channels, subscriber):
        if isinstance(channels, (list, tuple)):
            for channel in channels:
                self.channels[channel].add(subscriber)
        else:
            self.channels[channels].add(subscriber)

    def unsubscribe(self, channel, subscriber):
        try:
            self.channels[channel].remove(subscriber)
        except (KeyError, ValueError):
            pass

    def publish(self, channel, message):
        subscribers = self.channels.get(channel, [])
        message = json.dumps(message)
        if subscribers:
            for s in subscribers:
                if not s.session.is_closed:
                    s.broadcast(subscribers, message)
                    break