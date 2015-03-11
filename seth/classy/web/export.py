from pyramid.response import Response
from pyramid.httpexceptions import HTTPError, HTTPOk


class ExportResource(object):
    template = None
    export_factory = None
    filter_class = None

    def __init__(self, request):
        self.request = request

    def get_queryset(self):
        return None

    def filter_queryset(self, qs):
        if self.filter_class:
            filter_instance = self.filter_class(qs)
            return filter_instance.apply(self.request)

        return qs

    def run_exporter(self):
        if not self.template:
            raise HTTPError

        qs = self.get_queryset()
        # if no queryset is predefined export
        qs = qs if qs is not None else self.export_factory.model.query
        # filters queryset - has request access so it can be used to filer
        # or optionaly filter_class can be specified
        qs = self.filter_queryset(qs)
        return self.export_factory(qs).get_export_data()

    def get(self, **kwargs):
        msg = "Go to /csv/ or /pdf/ to view export"
        return Response(msg, status=HTTPOk.code)

    def pdf(self, **kwargs):
        data = self.run_exporter()
        context = data
        context.update({'template': self.template})
        return context

    def csv(self, **kwargs):
        data = self.run_exporter()
        context = data
        return context