from seth.pusher import utils


class PubSubMixin(object):

    def get_subscriber(self):
        raise NotImplementedError

    def get_publisher(self):
        raise NotImplementedError

    def get_subscribers(self, channel=None):
        raise NotImplementedError

    def get_subscriber_count(self, channel=None):
        raise NotImplementedError

    def add_subscriber(self, channel, subscriber):
        self.subscriber.subscribe(['all', channel], subscriber)

    def remove_subscriber(self, channel, subscriber):
        self.subscriber.unsubscribe(channel, subscriber)
        self.subscriber.unsubscribe('all', subscriber)

    def broadcast(self, message, channel=None, sender=None):
        channel = 'all' if channel is None else channel
        self.publisher.publish(channel, message)


class RedisPubSubMixin(PubSubMixin):
    redis_host = 'localhost'
    redis_port = 6379
    redis_password = None
    redis_selected_db = None

    def get_subscribers(self, channel=None):
        if not channel:
            return dict(
                (channel, [i.dispatcher.subscriber_id for i in c])
                for channel, c
                in self.subscriber.subscribers.iteritems()
            )

        if channel in self.subscriber.subscribers:
            return {
                channel: [
                    i.dispatcher.subscriber_id
                    for i
                    in self.subscriber.subscribers[channel]
                ]
            }

        return {
            channel: []
        }

    def get_subscriber_count(self, channel=None):
        if not channel:
            return sum(
                len(i.keys()) for i in self.subscriber.subscribers.values()
            )

        if channel in self.subscriber.subscribers:
            return len(self.subscriber.subscribers[channel])

        return 0

    def is_subscribed_to_channel(self, subscriber, channel):
        if channel in self.subscriber.subscribers:
            return subscriber in self.subscriber.subscribers[channel]
        return False

    def get_subscriber(self, **kwargs):
        import tornadoredis
        import tornadoredis.pubsub

        client = tornadoredis.Client(
            host=self.redis_host, port=self.redis_port,
            password=self.redis_password, selected_db=self.redis_selected_db
        )
        return tornadoredis.pubsub.SockJSSubscriber(client)

    def get_publisher(self, **kwargs):
        import redis
        return redis.Redis(
            host=self.redis_host, port=self.redis_port,
            password=self.redis_password, db=self.redis_selected_db
        )


class InMemoryPubSubMixin(PubSubMixin):

    _instance = None

    @property
    def pub_sub(self):
        if not self._instance:
            self._instance = utils.BasicPubSubManager()
        return self._instance

    def get_subscribers(self, channel=None):
        if not channel:
            return dict(
                (channel, [i.dispatcher.subscriber_id for i in c])
                for channel, c
                in self.pub_sub.channels.iteritems()
            )

        if channel in self.pub_sub.channels:
            return {
                channel: [
                    i.dispatcher.subscriber_id
                    for i
                    in self.pub_sub.channels[channel]
                ]
            }

        return {
            channel: []
        }

    def get_subscriber_count(self, channel=None):
        if not channel:
            return sum(len(i) for i in self.pub_sub.channels.itervalues())

        if channel in self.pub_sub.channels:
            return len(self.pub_sub.channels[channel])

        return 0

    def get_subscriber(self, **kwargs):
        return self.pub_sub

    def get_publisher(self, **kwargs):
        return self.pub_sub