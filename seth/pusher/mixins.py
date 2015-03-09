import json
import tornado.websocket


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
        message = json.dumps(message)
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
            return sum(self.subscriber.subscriber_count.values())

        if channel in self.subscriber.subscriber_count:
            return self.subscriber.subscriber_count[channel]

        return 0

    def get_subscriber(self, **kwargs):
        import tornadoredis
        import tornadoredis.pubsub

        class DefaultRedisSubscriber(tornadoredis.pubsub.BaseSubscriber):

            def on_message(self, msg):
                if msg and msg.kind == 'message':
                    subscribers = list(self.subscribers[msg.channel].keys())
                    for subscriber in subscribers:
                        try:
                            subscriber.send(msg.body)
                        except tornado.websocket.WebSocketClosedError:
                            self.unsubscribe(msg.channel, subscriber)

                super(DefaultRedisSubscriber, self).on_message(msg)

        client = tornadoredis.Client(
            host=self.redis_host, port=self.redis_port,
            password=self.redis_password, selected_db=self.redis_selected_db
        )
        return DefaultRedisSubscriber(client)

    def get_publisher(self, **kwargs):
        import redis
        return redis.Redis(
            host=self.redis_host, port=self.redis_port,
            password=self.redis_password, db=self.redis_selected_db
        )


class InMemoryPubSubMixin(PubSubMixin):

    def get_subscriber(self, **kwargs):
        pass

    def get_publisher(self, **kwargs):
        pass