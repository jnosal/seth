from seth.classy.web import mixins
from seth.paginator import paginate
from seth.classy.web.base import WebResource


class GenericWebResourceView(mixins.WTFormsSchemaMixin, WebResource):
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


class ProcessFormView(mixins.ContextMixin,
                      mixins.ProcessFormMixin,
                      GenericWebResourceView):

    allowed_methods = ['GET', 'POST']

    def form_is_valid(self, form):
        raise NotImplementedError

    def form_is_invalid(self, form):
        return self.get_context_data(form=form)

    def get(self, **kwargs):
        form = self.get_form(None, None)
        return self.get_context_data(form=form)

    def post(self, **kwargs):
        form_data = self.get_form_data(**kwargs)
        form = self.get_form(form_data=form_data)

        is_valid, errors = self.validate_form(form)
        if is_valid:
            return self.form_is_valid(form=form)
        else:
            return self.form_is_invalid(form=form)