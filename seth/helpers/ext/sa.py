import time
import logging
import traceback

from sqlalchemy import event

logger = logging.getLogger('seth')


def setup_query_listener(engine, threshold):
    logger.info("QueryListener Started ...")

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement,
                              parameters, context, executemany):
        context._query_start_time = time.time()

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement,
                             parameters, context, executemany):
        total = int(1000 * (time.time() - context._query_start_time))
        statement = ' '.join(statement.split())

        if total >= threshold and statement.startswith('SELECT'):
            logger.warning("[%s ms] Completed query: %s" % (str(total), statement))
            # Log stack trace, but remove the uninteresting parts.
            tb = ''.join([line for line in traceback.format_stack() if 'b4b' in
                          line][:-1])
            params = (total, parameters,)
            logger.warning('Slow Query. Time: %s, parameters: %s' % params)