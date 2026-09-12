import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from app.services import query_executor


class QueryLimitsTest(unittest.TestCase):
    def test_mysql_caps_each_statement_and_restores_session_limit(self):
        engine = MagicMock()
        engine.dialect.name = "mysql"
        conn = engine.connect.return_value.__enter__.return_value
        conn.execute.return_value.scalar.return_value = 9000
        runner = conn.execution_options.return_value
        server_limit = 9000
        returned_rows = []

        def execute(statement):
            nonlocal server_limit
            sql = str(statement)
            result = MagicMock()
            if sql.startswith('SET SESSION sql_select_limit'):
                server_limit = int(sql.rsplit('=', 1)[1])
                return result
            self.assertEqual(server_limit, 501)
            result.returns_rows = True
            result.keys.return_value = ['n']
            result.fetchmany.return_value = [(n,) for n in range(min(server_limit, 10000))]
            result.close.side_effect = lambda: returned_rows.append(server_limit)
            return result

        runner.execute.side_effect = execute
        with patch.object(query_executor, 'ensure_engine', return_value=engine):
            response = query_executor._run_query_sync('test', '', 'SELECT n FROM huge; SELECT n FROM huge', 'limited')
        self.assertEqual(response['status'], 'success')
        self.assertEqual(returned_rows, [501, 501])
        self.assertEqual(server_limit, 9000)
        self.assertTrue(all(stmt['truncated'] for stmt in response['statements']))

    def test_mysql_uses_streaming_and_bounded_fetch(self):
        engine = MagicMock()
        engine.dialect.name = "mysql"
        conn = engine.connect.return_value.__enter__.return_value
        result = conn.execution_options.return_value.execute.return_value
        result.returns_rows = True
        result.keys.return_value = ["id"]
        result.fetchmany.return_value = [(i,) for i in range(501)]
        with patch.object(query_executor, "ensure_engine", return_value=engine):
            response = query_executor._run_query_sync("test", "", "SELECT * FROM large_table", "stream-test")
        self.assertEqual(response["status"], "success")
        conn.execution_options.assert_any_call(stream_results=True, max_row_buffer=501)
        result.fetchmany.assert_called_once_with(501)
        result.fetchall.assert_not_called()
        result.close.assert_called_once()

    def test_result_limit_and_exact_boundary(self):
        engine = create_engine("sqlite://")
        try:
            with patch.object(query_executor, "ensure_engine", return_value=engine):
                for count in (499, 500, 501, 10000):
                    sql = f"WITH RECURSIVE numbers(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM numbers WHERE n < {count}) SELECT n FROM numbers"
                    result = query_executor._run_query_sync("test", "", sql, "limit-test")
                    self.assertEqual(result["status"], "success")
                    statement = result["statements"][0]
                    self.assertEqual(len(statement["rows"]), min(count, 500))
                    self.assertEqual(statement["truncated"], count > 500)
        finally:
            engine.dispose()

    def test_expired_query_does_not_execute_write(self):
        from threading import Event
        engine = create_engine("sqlite://")
        expired = Event()
        expired.set()
        try:
            with patch.object(query_executor, "ensure_engine", return_value=engine):
                result = query_executor._run_query_sync("test", "", "CREATE TABLE unwanted(id INT)", "expired", expired)
            self.assertEqual(result["status"], "error")
            with engine.connect() as conn:
                self.assertEqual(conn.exec_driver_sql("SELECT count(*) FROM sqlite_master WHERE name='unwanted'").scalar(), 0)
        finally:
            engine.dispose()
