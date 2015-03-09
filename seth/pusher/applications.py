from tornado.web import Application


class SethPusherApplication(Application):

    def __init__(self, **kwargs):
        handlers = []
        super(SethPusherApplication, self).__init__(handlers, **kwargs)