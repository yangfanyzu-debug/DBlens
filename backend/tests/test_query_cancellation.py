import threading
import unittest
from unittest.mock import MagicMock

from sqlalchemy.pool import QueuePool
from app.services import query_executor as qe


class QueryCancellationTests(unittest.TestCase):
    def tearDown(self):
        qe._running.clear()
        qe._killed.clear()

    def test_cancel_works_with_exhausted_business_pool(self):
        connections = []

        def connect():
            connection = MagicMock()
            connections.append(connection)
            return connection

        pool = QueuePool(connect, pool_size=1, max_overflow=0, timeout=0.01)
        engine = MagicMock(pool=pool)
        busy = pool.connect()
        state = qe.RunningQuery(engine, 123)
        qe._running['q'] = state
        try:
            qe._kill_mysql_query('q', state, threading.Event())
            self.assertEqual(len(connections), 2)
            connections[1].cursor.return_value.execute.assert_called_once_with('KILL QUERY 123')
            connections[0].cursor.assert_not_called()
        finally:
            busy.close()
            pool.dispose()

    def test_cancel_abandoned_during_connect_never_sends_kill(self):
        abandoned = threading.Event()
        engine = MagicMock()
        control = MagicMock()

        def delayed_connect():
            abandoned.set()
            return control

        engine.pool.recreate.return_value.connect.side_effect = delayed_connect
        state = qe.RunningQuery(engine, 123)
        qe._running['q'] = state
        qe._kill_mysql_query('q', state, abandoned)
        control.cursor.assert_not_called()
        control.close.assert_called_once()
        engine.pool.recreate.return_value.dispose.assert_called_once()

    def test_finished_or_replaced_query_is_not_cancelled(self):
        for replaced in (False, True):
            engine = MagicMock()
            state = qe.RunningQuery(engine, 123)
            if replaced:
                qe._running['q'] = qe.RunningQuery(engine, 123)
            else:
                state.active = False
                qe._running['q'] = state
            qe._kill_mysql_query('q', state, threading.Event())
            engine.pool.recreate.return_value.connect.return_value.cursor.assert_not_called()

    def test_registry_is_cleared_before_business_connection_is_returned(self):
        engine = MagicMock()
        engine.dialect.name = 'mysql'
        engine.connect.return_value.__enter__.return_value.execute.return_value.scalar.return_value = 123
        observed = []
        engine.connect.return_value.__exit__.side_effect = lambda *args: observed.append('q' in qe._running)
        with qe._query_connection(engine, 'q'):
            self.assertTrue(qe._running['q'].active)
        self.assertEqual(observed, [False])

    def test_cancelled_connection_is_discarded_before_pool_return(self):
        engine = MagicMock()
        engine.dialect.name = 'mysql'
        conn = engine.connect.return_value.__enter__.return_value
        conn.execute.return_value.scalar.return_value = 123
        with qe._query_connection(engine, 'q'):
            qe._kill_mysql_query('q', qe._running['q'], threading.Event())
        conn.invalidate.assert_called_once()
        conn.execution_options.assert_not_called()
        self.assertNotIn('q', qe._running)
