from seth.classy.rest import mixins
from seth.classy.base import QuerySetMixin
from seth.classy.rest.base import RestResource


class GenericApiView(QuerySetMixin,
                     mixins.BaseSchemaMixin,
                     RestResource):
    pass


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
        return self.modify(**kwargs)


class PatchAndUpdateApiView(mixins.PatchResourceMixin,
                            mixins.UpdateResourceMixin,
                            GenericApiView):

    allowed_methods = ['PATCH', 'PUT']

    def patch(self, **kwargs):
        return self.modify(**kwargs)

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
        return self.modify(**kwargs)

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
