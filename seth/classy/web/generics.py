from seth.classy.base import QuerySetMixin
from seth.classy.web import mixins
from seth.classy.web.base import WebResource


class GenericWebResourceView(QuerySetMixin,
                             mixins.WTFormsSchemaMixin,
                             WebResource):
    pass


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