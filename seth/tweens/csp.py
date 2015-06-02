def parse_setting(name, settings, default=None):
    return settings.get(name) if settings.get(name, None) else default


def build_csp_policy(settings):
    config = {
        'default-src': parse_setting('csp.default_src', settings, ["'self'"]),
        'script-src': parse_setting('csp.script_src', settings),
        'object-src': parse_setting('csp.object_src', settings),
        'style-src': parse_setting('csp.style_src', settings),
        'img-src': parse_setting('csp.img_src', settings),
        'media-src': parse_setting('csp.media_src', settings),
        'frame-src': parse_setting('csp.frame_src', settings),
        'font-src': parse_setting('csp.font_src', settings),
        'connect-src': parse_setting('csp.connect_src', settings),
        'sandbox': parse_setting('csp.sandbox', settings),
    }

    policy = [
        '{0} {1}'.format(k, ' '.join(v))
        for (k, v)
        in config.iteritems() if v
    ]
    if settings.get('csp.report_uri', None):
        policy.append('report-uri {0}'.format(settings.get('csp.report_uri')))

    return '; '.join(policy)


def csp_tween_factory(handler, registry):

    def csp_tween(request):
        settings, response = registry.settings, request.response

        csp_headers = ['Content-Security-Policy', 'X-WebKit-CSP']

        prefixes = settings.get('csp.exclude_prefixes', ('/admin',))

        if request.path.startswith(prefixes):
            return handler(request)

        if response.headers.get(csp_headers[0], None) is None:
            policy = build_csp_policy(settings)
            for HEADER in csp_headers:
                response.headers[HEADER] = policy

        return handler(request)

    return csp_tween