from pyramid.httpexceptions import HTTPError


class ExportResource(object):
    template = None
    export_factory = None

    def __init__(self, request):
        self.request = request

    def get_queryset(self):
        return None

    def filter_queryset(self, qs):
        return qs

    def run_exporter(self):
        if not self.template:
            raise HTTPError

        qs = self.get_queryset()
        qs = qs if qs is not None else self.export_factory.model.query
        qs = self.filter_queryset(qs)
        return self.export_factory(qs).get_export_data()

    def pdf(self, **kwargs):
        data = self.run_exporter()
        context = data
        context.update({'template': self.template})
        return context

    def csv(self, **kwargs):
        data = self.run_exporter()
        context = data
        return context