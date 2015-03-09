import json
import tornado.web


class OverallDebugHandler(tornado.web.RequestHandler):

    def get(self):
        self.set_header('Content-Type', 'application/json')

        count = self.application.get_subscriber_count(channel=None)
        subscribers = self.application.get_subscribers(channel=None)

        text = json.dumps({
            'subscriber_count': count,
            'subscribers': subscribers
        })
        self.write(text)


class ChannelDebugHandler(tornado.web.RequestHandler):

    def get(self, channel):
        self.set_header('Content-Type', 'application/json')

        count = self.application.get_subscriber_count(channel=channel)
        subscribers = self.application.get_subscribers(channel=channel)

        text = json.dumps({
            'subscriber_count': count,
            'subscribers': subscribers
        })
        self.write(text)