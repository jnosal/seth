import re


def mobile_device_tween_factory(handler, registry):
    def mobile_tween(request):
        is_mobile = False
        user_agents_test_match = (
            "w3c ", "acs-", "alav", "alca", "amoi", "audi",
            "avan", "benq", "bird", "blac", "blaz", "brew",
            "cell", "cldc", "cmd-", "dang", "doco", "eric",
            "hipt", "inno", "ipaq", "java", "jigs", "kddi",
            "keji", "leno", "lg-c", "lg-d", "lg-g", "lge-",
            "maui", "maxo", "midp", "mits", "mmef", "mobi",
            "mot-", "moto", "mwbp", "nec-", "newt", "noki",
            "xda", "palm", "pana", "pant", "phil", "play",
            "port", "prox", "qwap", "sage", "sams", "sany",
            "sch-", "sec-", "send", "seri", "sgh-", "shar",
            "sie-", "siem", "smal", "smar", "sony", "sph-",
            "symb", "t-mo", "teli", "tim-", "tosh", "tsm-",
            "upg1", "upsi", "vk-v", "voda", "wap-", "wapa",
            "wapi", "wapp", "wapr", "webc", "winw", "xda-",)
        user_agents_test_search = u"(?:%s)" % u'|'.join((
            'up.browser', 'up.link', 'mmp', 'symbian', 'smartphone', 'midp',
            'wap', 'phone', 'windows ce', 'pda', 'mobile', 'mini', 'palm',
            'netfront', 'opera mobi',
        ))
        user_agents_exception_search = u"(?:%s)" % u'|'.join((
            'ipad',
        ))
        http_accept_regex = re.compile("application/vnd\.wap\.xhtml\+xml", re.IGNORECASE)

        user_agents_test_match = r'^(?:%s)' % '|'.join(user_agents_test_match)
        user_agents_test_match_regex = re.compile(user_agents_test_match, re.IGNORECASE)
        user_agents_test_search_regex = re.compile(user_agents_test_search, re.IGNORECASE)
        user_agents_exception_search_regex = re.compile(user_agents_exception_search, re.IGNORECASE)

        if 'User-Agent' in request.headers:
            ua = request.headers.get('User-Agent', '').lower()
            if user_agents_test_search_regex.search(ua) and \
                not user_agents_exception_search_regex.search(ua):
                is_mobile = True
            else:
                if 'Accept' in request.headers:
                    http_accept = request.headers.get('Accept')
                    if http_accept_regex.search(http_accept):
                        is_mobile = True

            if not is_mobile:
                if user_agents_test_match_regex.match(ua):
                    is_mobile = True
        request.is_mobile = is_mobile
        return handler(request)

    return mobile_tween