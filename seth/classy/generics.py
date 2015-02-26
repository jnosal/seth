from seth import db
from seth.paginator import paginate
from seth.classy.base import RestResource, BaseSchemaMixin


class ListReadOnlyApiView(BaseSchemaMixin, RestResource):

    paginate = True
    filter_class = None

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

    def get(self):
        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        schema = self._get_schema(many=True)

        if self.paginate:
            pagination = self.paginate_queryset(qs)
            results = self.dump_schema(schema, pagination.items)
            return {
                'items': results,
                'extra': {},
                'meta': {
                    'total_entries': pagination.total,
                    'total_pages': pagination.pages,
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'previous': pagination.prev_num if pagination.has_prev else None,
                    'next': pagination.next_num if pagination.has_next else None
                }
            }

        results = self.dump_schema(schema, qs)
        return {
            'results': results
        }


class DetailApiReadOnlyView(BaseSchemaMixin, RestResource):

    def get_queryset(self, *args, **kwargs):
        raise NotImplementedError

    def get_id_param(self):
        return u'id'

    def get(self, **kwargs):
        qs = self.get_queryset()
        schema = self._get_schema(many=False)
        id_ = self.request.matchdict[self.get_id_param()]

        obj = qs.get(id_)
        if not obj:
            return self.not_found()

        results = self.dump_schema(schema, obj)
        return {
            'object': results
        }


class CreateView(BaseSchemaMixin, RestResource):
    model = None

    def get_model(self):
        raise NotImplementedError

    def handle_creation(self, instance):
        pass

    def preprocess_serialized_data(self, data):
        return data

    def post(self):

        model_class = self.model if self.model else self.get_model()
        schema = self._get_schema(many=False)
        data, errors = self.load_schema(schema, self.request.json_body)

        if not errors:
            data = self.preprocess_serialized_data(data)
            instance = model_class(**data)
            session = db.get_session()
            session.add(instance)
            session.flush()
            self.handle_creation(instance)
            return self.created()

        return self.bad_request(errors)