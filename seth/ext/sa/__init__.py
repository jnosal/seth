import time
import logging

from sqlalchemy import event
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement,\
    _literal_as_text

logger = logging.getLogger('seth')


def setup_query_listener(engine, threshold):
    logger.info("QueryListener Started ...")

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement,
                              parameters, context, execute_many):
        context._query_start_time = time.time()

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement,
                             parameters, context, execute_many):

        total = int(1000 * (time.time() - context._query_start_time))
        statement = ' '.join(statement.split())

        if total >= threshold and statement.startswith('SELECT'):
            logger.warning("[%s ms] Completed query: %s" % (str(total), statement))
            params = (total, parameters,)
            logger.warning('Slow Query. Time: %s, parameters: %s' % params)


class explain(Executable, ClauseElement):

    def __init__(self, stmt, analyze=False):
        self.statement = _literal_as_text(stmt)
        self.analyze = analyze
        self.inline = getattr(stmt, 'inline', None)


@compiles(explain, 'postgresql')
def pg_explain(element, compiler, **kw):
    text = "EXPLAIN "
    if element.analyze:
        text += "ANALYZE "
    text += compiler.process(element.statement, **kw)
    return text
