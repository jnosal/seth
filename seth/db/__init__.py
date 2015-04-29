import transaction


class Meta:
    maker = None


class SessionNotInitializedException(Exception):
    """Custom Seth Db Exception"""


def register_maker(maker):
    Meta.maker = maker


def get_session(**kwargs):
    if not Meta.maker:
        msg = "Please initialize session/maker"
        raise SessionNotInitializedException(msg)

    return Meta.maker(**kwargs)


def commit():
    transaction.commit()


def rollback():
    transaction.abort()
