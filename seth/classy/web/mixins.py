from webob import multidict


class BaseFormSchemaMixin(object):
    form = None

    def get_form(self, form_data=None, obj=None, **kwargs):
        kwargs.update(self.get_extra_args())
        prefix = self.get_prefix()
        if self.form:
            return self.form(form_data, obj, prefix=prefix, **kwargs)
        else:
            return self.get_form_class()(
                form_data, obj, prefix=prefix **kwargs
            )

    def get_form_class(self):
        raise NotImplementedError

    def get_prefix(self):
        return ''

    def get_extra_args(self):
        return {}

    def validate_form(self, form, **kwargs):
        raise NotImplementedError


class WTFormsSchemaMixin(BaseFormSchemaMixin):

    def validate_form(self, form, **kwargs):
        is_valid = form.validate()
        return is_valid, form.errors


class ContextMixin(object):

    def get_context_data(self, **kwargs):
        return kwargs


class ProcessFormMixin(object):

    def get_form_data(self, **kwargs):
        try:
            return multidict.MultiDict(self.request.json_body)
        except ValueError:
            return self.request.POST