import unittest
from unittest.mock import AsyncMock, patch


class QueryExecutorTestCase(unittest.TestCase):
    def test_mysql_table_not_found_reports_case_sensitive_match(self):
        from app.services import query_executor

        error = "(pymysql.err.ProgrammingError) (1146, \"Table 'ry-cloud.SKILLS' doesn't exist\")"

        class FakeDialect:
            name = "mysql"

        class FakeResult:
            returns_rows = False
            rowcount = 0

            def __init__(self, rows=None, scalar_value=None):
                self._rows = rows or []
                self._scalar_value = scalar_value

            def scalar(self):
                return self._scalar_value

            def fetchall(self):
                return self._rows

        class FakeConnection:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def execute(self, statement, params=None):
                sql = str(statement)
                if "CONNECTION_ID" in sql:
                    return FakeResult(scalar_value=123)
                if "information_schema.TABLES" in sql:
                    return FakeResult(rows=[("skills",)])
                if "SELECT * FROM SKILLS" in sql:
                    raise RuntimeError(error)
                return FakeResult()

            def commit(self):
                pass

        class FakeEngine:
            dialect = FakeDialect()

            def connect(self):
                return FakeConnection()

        with patch("app.services.query_executor.ensure_engine", return_value=FakeEngine()):
            result = query_executor._run_query_sync("conn-1", "ry-cloud", "SELECT * FROM SKILLS", "query-1")

        self.assertEqual(result["status"], "error")
        self.assertIn("case-sensitive", result["error"])
        self.assertIn("SKILLS", result["error"])
        self.assertIn("skills", result["error"])


class QueryKillTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_kill_query_terminates_mysql_thread_and_notifies_client(self):
        from app.services import query_executor

        executed = []

        class FakeConnection:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def exec_driver_sql(self, sql):
                executed.append(sql)

        class FakeEngine:
            def connect(self):
                return FakeConnection()

        query_executor._running["query-1"] = (FakeEngine(), 123)
        try:
            with patch.object(query_executor.ws_manager, "send", new=AsyncMock()) as send:
                await query_executor.kill_query("query-1")

            self.assertEqual(executed, ["KILL QUERY 123"])
            self.assertEqual(send.await_args.args[1]["status"], "killed")
        finally:
            query_executor._running.pop("query-1", None)
            query_executor._killed.discard("query-1")


if __name__ == "__main__":
    unittest.main()
