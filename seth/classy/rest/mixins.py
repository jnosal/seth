import types

from sqlalchemy.orm.query import Query
from pyramid.httpexceptions import HTTPCreated, HTTPOk

from seth import db
from seth.db import mixins as db_mixins


class BaseSchemaMixin(object):
    schema = None

    def get_schema_class(self, *args, **kwargs):
        raise NotImplementedError

    def _get_schema(self, many):
        if self.schema:
            return self.schema(many=many)
        else:
            return self.get_schema_class()(many=many)

    def prepare_data_to_dump(self, data):
        # Use to prepare data before it gets serialized
        return data

    def prepare_data_to_load(self, data):
        # Use to prepare data before it gets deserialized / loaded
        return data

    def dump_schema(self, schema_class, data):
        # Must return serialized structure
        # override if schema is handled differently
        data = self.prepare_data_to_dump(data)
        results = schema_class.dump(data)
        return results.data

    def load_schema(self, schema_class, data):
        # Must return data, errors tuple
        # override if schema is handled differently
        data = self.prepare_data_to_load(data)
        return schema_class.load(data)


class ColanderSchemaMixin(BaseSchemaMixin):

    def _get_schema(self, many):
        if self.schema:
            return self.schema()
        else:
            return self.get_schema_class()()

    def prepare_data_to_dump(self, data):
        if isinstance(data, types.GeneratorType):
            data = [_ for _ in data]

        if isinstance(data, Query):
            data = [model.to_dict() for model in data.all()]

        if isinstance(data, db_mixins.PlainModelMixin):
            data = data.to_dict()

        return data

    def dump_schema(self, schema_class, data):
        data = self.prepare_data_to_dump(data)
        results = schema_class.serialize(data)
        return results

    def load_schema(self, schema_class, data):
        import colander
        data = self.prepare_data_to_load(data)
        try:
            deserialized = schema_class.deserialize(data)
        except colander.Invalid, e:
            errors = e.asdict()
            return None, errors
        return deserialized, {}


class RetrieveResourceMixin(object):

    def retrieve(self, with_schema=True):
        qs = self.get_queryset()
        id_ = self.request.matchdict[self.lookup_param]
        instance = qs.get(id_)

        if with_schema:
            schema = self._get_schema(many=False)
            return instance, schema

        return instance, None


class ReadResourceMixin(RetrieveResourceMixin):

    def handle_read(self, instance):
        return instance

    def read(self, **kwargs):
        instance, schema = self.retrieve()
        if not instance:
            return self.not_found()

        results = self.dump_schema(schema, instance)
        self.handle_read(instance)
        return {
            'object': results
        }


class CreateResourceMixin(object):

    def handle_creation(self, instance):
        session = db.get_session()
        session.add(instance)
        session.flush()
        return instance

    def created(self):
        self.request.response.status_int = HTTPCreated.code
        return {
            'status': 'Created'
        }

    def prepare_serialized_data(self, data):
        return data

    def create(self, **kwargs):

        model_class = self.model if self.model else self.get_model()
        schema = self._get_schema(many=False)
        data, errors = self.load_schema(schema, self.request.json_body)

        if not errors:
            data = self.prepare_serialized_data(data)
            instance = model_class(**data)

            self.handle_creation(instance)
            return self.created()

        return self.bad_request(errors)


class ListResourceMixin(object):

    def list(self, **kwargs):
        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        schema = self._get_schema(many=True)

        if self.paginate:
            pagination = self.paginate_queryset(qs)
            results = self.dump_schema(schema, pagination.items)
            next_ = pagination.next_num if pagination.has_next else None
            previous_ = pagination.prev_num if pagination.has_prev else None

            return {
                'items': results,
                'extra': {},
                'meta': {
                    'total_entries': pagination.total,
                    'total_pages': pagination.pages,
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'previous': previous_,
                    'next': next_
                }
            }

        results = self.dump_schema(schema, qs)
        return {
            'results': results
        }


class DeleteResourceMixin(RetrieveResourceMixin):

    def handle_deletion(self, instance):
        session = db.get_session()
        session.delete(instance)
        session.flush()
        return instance

    def deleted(self):
        self.request.response.status_int = HTTPOk.code
        return {
            'status': 'Deleted'
        }

    def remove(self, **kwargs):
        instance, _ = self.retrieve(with_schema=False)

        if not instance:
            return self.not_found()

        self.handle_deletion(instance)
        return self.deleted()


class PatchResourceMixin(RetrieveResourceMixin):

    def handle_patch(self, instance, data):
        session = db.get_session()
        for name, value in data.iteritems():
            setattr(instance, name, value)

        session.flush()
        return instance

    def patched(self):
        self.request.response.status_int = HTTPOk.code
        return {
            'status': 'Patched'
        }

    def modify(self, **kwargs):
        instance, schema = self.retrieve()
        if not instance:
            return self.not_found()

        data, errors = self.load_schema(schema, self.request.json_body)
        if not errors:
            self.handle_patch(instance, data)
            return self.patched()

        return self.bad_request(errors)


class UpdateResourceMixin(RetrieveResourceMixin):

    def handle_update(self, instance, data):
        session = db.get_session()
        for name, value in data.iteritems():
            setattr(instance, name, value)

        session.flush()
        return instance

    def updated(self):
        self.request.response.status_int = HTTPOk.code
        return {
            'status': 'Updated'
        }

    def update(self, **kwargs):
        instance, schema = self.retrieve()
        if not instance:
            return self.not_found()

        data, errors = self.load_schema(schema, self.request.json_body)
        if not errors:
            self.handle_update(instance, data)
            return self.updated()

        return self.bad_request(errors)
