class BaseAuthenticationPolicy(object):

    def authenticate(self, request):
        raise NotImplementedError


class HeaderAuthenticationPolicy(BaseAuthenticationPolicy):
    header_name = 'Api-Auth'
    header_secret = 'Secret'

    def authenticate(self, request):
        header = request.headers.get(self.header_name, '')
        return header == self.header_secret


class SecretTokenAuthenticationPolicy(BaseAuthenticationPolicy):
    param_name = 'token'
    param_secret = 'secret'

    def authenticate(self, request):
        param = request.params.get(self.param_name, '')
        return param == self.param_secret