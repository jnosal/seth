import transaction


class _DBSession:
    maker = None


class SessionNotInitializedException(Exception):
    """Custom Seth Db Exception"""


def register_maker(configured_session):
    _DBSession.maker = configured_session


def get_session(**kwargs):
    if not _DBSession.maker:
        msg = "Please initialize session/maker"
        raise SessionNotInitializedException(msg)

    return _DBSession.maker(**kwargs)


def commit():
    transaction.commit()


def rollback():
    transaction.abort()
