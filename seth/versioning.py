class BaseVersioningPolicy(object):
    default_version = None

    def get_allowed_version(self):
        # allowed is default plus those specified in the list
        return []

    def get_default_version(self, request):
        if self.default_version:
            return self.default_version

        settings = request.registry.settings
        default_version = settings.get('seth.default_api_version', '1.0')
        return default_version

    def get_version_info(self, request, *args, **kwargs):
        # Must be predefined
        raise NotImplementedError

    def is_allowed(self, request, version):
        allowed = self.get_allowed_version()
        if not allowed:
            return True

        default = self.get_default_version(request)
        return True if (version == default or version in allowed) else False


class CheckQueryParamsVersioningPolicy(BaseVersioningPolicy):

    def get_version_info(self, request, *args, **kwargs):
        return request.params.get('version', '')


class CheckHeaderVersioningPolicy(BaseVersioningPolicy):
    header_name = 'Api-Version'

    def get_version_info(self, request, *args, **kwargs):
        return request.headers.get(self.header_name, '')