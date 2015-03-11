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
        return None

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