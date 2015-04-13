def secure_headers_tween_factory(handler, registry):

    def secure_headers_tween(request):
        response = request.response
        secure_headers = {
            'X-XSS-Protection': '1; mode=block',
            'X-Content-Type-Options': 'nosniff'
        }

        for header in secure_headers:
            if response.headers.get(header, None) is None:
                response.headers[header] = secure_headers[header]
        return handler(request)

    return secure_headers_tween