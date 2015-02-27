from seth.classy import mixins
from seth.paginator import paginate
from seth.classy.base import RestResource


class GenericApiView(mixins.BaseSchemaMixin, RestResource):
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


class ListReadOnlyApiView(mixins.ListResourceMixin,
                          GenericApiView):

    allowed_methods = ['GET']

    def get(self, **kwargs):
        return self.list(**kwargs)


class DetailApiView(mixins.ReadResourceMixin,
                    GenericApiView):

    allowed_methods = ['GET']

    def get(self, **kwargs):
        return self.read(**kwargs)


class CreateApiView(mixins.CreateResourceMixin,
                    GenericApiView):

    allowed_methods = ['POST']

    def post(self, **kwargs):
        return self.create(**kwargs)


class ListCreateApiView(mixins.CreateResourceMixin,
                        mixins.ListResourceMixin,
                        GenericApiView):

    allowed_methods = ['GET', 'POST']

    def get(self, **kwargs):
        return self.list(**kwargs)

    def post(self, **kwargs):
        return self.create(**kwargs)


class UpdateApiView(mixins.UpdateResourceMixin,
                    GenericApiView):

    allowed_methods = ['PUT']

    def put(self, **kwargs):
        return self.update(**kwargs)


class PatchApiView(mixins.PatchResourceMixin,
                   GenericApiView):

    allowed_methods = ['PATCH']

    def patch(self, **kwargs):
        return self.patch(**kwargs)


class PatchAndUpdateApiView(mixins.PatchResourceMixin,
                            mixins.UpdateResourceMixin,
                            GenericApiView):

    allowed_methods = ['PATCH', 'PUT']

    def patch(self, **kwargs):
        return self.patch(**kwargs)

    def put(self, **kwargs):
        return self.update(**kwargs)


class RetrieveUpdateApiView(mixins.ReadResourceMixin,
                            mixins.PatchResourceMixin,
                            mixins.UpdateResourceMixin,
                            GenericApiView):

    allowed_methods = ['GET', 'PATCH', 'PUT']

    def get(self, **kwargs):
        return self.read(**kwargs)

    def patch(self, **kwargs):
        return self.patch(**kwargs)

    def put(self, **kwargs):
        return self.update(**kwargs)


class DestroyDetailApiView(mixins.ReadResourceMixin,
                           mixins.DeleteResourceMixin,
                           GenericApiView):

    allowed_methods = ['GET', 'DELETE']

    def get(self, **kwargs):
        return self.read(**kwargs)

    def delete(self, **kwargs):
        return self.remove(**kwargs)
