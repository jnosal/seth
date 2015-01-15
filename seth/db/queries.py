from sqlalchemy.orm.query import Query


class DeletionFilterQuery(Query):

    def __new__(cls, *args, **kwargs):
        if args and hasattr(args[0][0], "is_deleted"):
            return Query(*args, **kwargs).filter_by(is_deleted=False)
        else:
            return object.__new__(cls)