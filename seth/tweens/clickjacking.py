def clickjacking_tween_factory(handler, registry):

    def clickjacking_tween(request):
        settings, response = registry.settings, request.response
        xframe_header = 'X-Frame-Options'
        if response.headers.get(xframe_header, None) is None:
            option = settings.get('x_frame_options', 'SAMEORIGIN').upper()
            response.headers[xframe_header] = option
        return handler(request)

    return clickjacking_tween