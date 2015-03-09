from seth.pusher.api import views


def get_api_handlers(application_instance):
    urls = []
    if application_instance.debug:
        urls += [
            (r'/debug/', views.OverallDebugHandler),
            (r'/debug/channels/(?P<channel>.+)/', views.ChannelDebugHandler),
        ]
    return urls