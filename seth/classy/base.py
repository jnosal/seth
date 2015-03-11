from seth.paginator import paginate


class View(object):
    dispatchable_methods = [
        'GET', 'POST', 'PUT', 'DELETE', 'PATCH',
        'CONNECT', 'TRACE', 'HEAD', 'OPTIONS'
    ]

    def __init__(self, request):
        self.request = request

    def perform_setup(self):
        pass

    @property
    def request_method(self):
        return self.request.method

    def dispatch(self, **kwargs):
        self.perform_setup()

        if self.request_method in self.dispatchable_methods:

            attr = self.request_method.lower()
            response_data = getattr(self, attr)(**kwargs)
            return response_data

        return self.not_allowed()

    def get(self, **kwargs):
        return self.not_allowed()

    def post(self, **kwargs):
        return self.not_allowed()

    def put(self, **kwargs):
        return self.not_allowed()

    def delete(self, **kwargs):
        return self.not_allowed()

    def patch(self, **kwargs):
        return self.not_allowed()

    def head(self, **kwargs):
        return self.not_allowed()

    def options(self, **kwargs):
        return self.not_allowed()

    def trace(self, **kwargs):
        return self.not_allowed()

    def connect(self, **kwargs):
        return self.not_allowed()


class QuerySetMixin(object):
    model = None
    paginate = True
    filter_class = None
    lookup_param = u'id'

    def get_model(self):
        raise NotImplementedError

    def get_queryset(self, *args, **kwargs):
        raise NotImplementedError

    def filter_queryset(self, qs):
        if self.filter_class:
            filter_instance = self.filter_class(qs)
            return filter_instance.apply(self.request)

        return qs

    def paginate_queryset(self, qs):
        settings = self.request.registry.settings

        page_param = settings.get('pagination.page_param_name', 'page')
        default_page = settings.get('pagination.default_page', 1)
        per_page_param = settings.get('pagination.per_page_param_name', 'per_page')
        default_per_page = settings.get('pagination.default_per_page', 20)

        try:
            page = int(self.request.params.get(page_param, default_page))
        except ValueError:
            page = default_page

        try:
            per_page = int(self.request.params.get(per_page_param, default_per_page))
        except ValueError:
            per_page = default_per_page

        return paginate(qs, page, per_page)