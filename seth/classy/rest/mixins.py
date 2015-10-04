import types

from sqlalchemy.orm.query import Query
from pyramid.httpexceptions import HTTPCreated, HTTPOk

from seth import db
from seth.db import base as db_mixins
from seth.classy.rest.utils import ResponseStatus


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
        # Must return serialized structure.
        # Override if schema is handled differently.
        data = self.prepare_data_to_dump(data)
        results = schema_class.dump(data)
        return results.data

    def load_schema(self, schema_class, data):
        # Must return data, errors tuple.
        # Override if schema is handled differently.
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

        if isinstance(data, db_mixins.Model):
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

        instance = qs.filter_by(**{self.lookup_param: id_}).first()

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

        result = self.dump_schema(schema, instance)
        self.handle_read(instance)
        return {
            'object': result
        }


class CreateResourceMixin(object):

    def handle_creation(self, instance):
        session = db.get_session()
        instance.manager.save(model=instance)
        session.flush()

    def created(self, instance):
        self.request.response.status_int = HTTPCreated.code
        return {
            'status': ResponseStatus.CREATED,
            'object': instance
        }

    def prepare_serialized_data(self, data):
        return data

    def create(self, **kwargs):

        model_class = self.model if self.model else self.get_model()
        schema = self._get_schema(many=False)

        try:
            json_data = self.request.json_body
        except ValueError as e:
            return self.bad_request([str(e)])

        data, errors = self.load_schema(schema, json_data)

        if not errors:
            data = self.prepare_serialized_data(data)
            instance = model_class.manager.new(**data)

            self.handle_creation(instance)
            return self.created(instance)

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
            'items': results
        }


class DeleteResourceMixin(RetrieveResourceMixin):

    def handle_deletion(self, instance):
        session = db.get_session()
        instance.manager.delete(model=instance)
        session.flush()

    def deleted(self, instance):
        self.request.response.status_int = HTTPOk.code
        return {
            'status': ResponseStatus.DELETED,
        }

    def remove(self, **kwargs):
        instance, _ = self.retrieve(with_schema=False)

        if not instance:
            return self.not_found()

        self.handle_deletion(instance)
        return self.deleted(instance)


class PatchResourceMixin(RetrieveResourceMixin):

    def handle_patch(self, instance, data):
        session = db.get_session()
        instance.manager.update(model=instance, **data)
        session.flush()

    def patched(self, instance):
        self.request.response.status_int = HTTPOk.code
        return {
            'status': ResponseStatus.PATCHED,
            'object': instance
        }

    def modify(self, **kwargs):
        instance, schema = self.retrieve()
        if not instance:
            return self.not_found()

        try:
            json_data = self.request.json_body
        except ValueError as e:
            return self.bad_request([str(e)])

        data, errors = self.load_schema(schema, json_data)

        if not errors:
            self.handle_patch(instance, data)
            return self.patched(instance)

        return self.bad_request(errors)


class UpdateResourceMixin(RetrieveResourceMixin):

    def handle_update(self, instance, data):
        session = db.get_session()
        instance.manager.update(model=instance, **data)
        session.flush()

    def updated(self, instance):
        self.request.response.status_int = HTTPOk.code

        return {
            'status': ResponseStatus.UPDATED,
            'object': instance
        }

    def update(self, **kwargs):
        instance, schema = self.retrieve()
        if not instance:
            return self.not_found()

        try:
            json_data = self.request.json_body
        except ValueError as e:
            return self.bad_request([str(e)])

        data, errors = self.load_schema(schema, json_data)

        if not errors:
            self.handle_update(instance, data)
            return self.updated(instance)

        return self.bad_request(errors)
