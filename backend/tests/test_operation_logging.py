import unittest
from unittest.mock import AsyncMock, patch


class FakeAsyncSession:
    def __init__(self, fail_commit: bool = False):
        self.fail_commit = fail_commit
        self.added = []

    def add(self, item):
        self.added.append(item)

    async def commit(self):
        if self.fail_commit:
            raise RuntimeError("log write failed")

    async def rollback(self):
        pass


def make_operator():
    from app.schemas.operator import OperatorContext

    return OperatorContext(
        user_id=7,
        username="alice",
        roles=("admin", "dba"),
        is_admin=True,
    )


class OperationLoggingServiceTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_record_operation_writes_operator_and_truncates_sql(self):
        from app.services.operation_logger import record_operation

        db = FakeAsyncSession()
        ok = await record_operation(
            db,
            operator=make_operator(),
            action="query.execute",
            resource_type="query",
            resource_id="query-1",
            conn_id="conn-1",
            db_name="ry-cloud",
            sql_text="x" * 5000,
            detail={"statement_count": 1},
            status="success",
            duration_ms=12,
        )

        self.assertTrue(ok)
        self.assertEqual(len(db.added), 1)
        log = db.added[0]
        self.assertEqual(log.user_id, 7)
        self.assertEqual(log.username, "alice")
        self.assertEqual(log.roles, "admin,dba")
        self.assertEqual(log.action, "query.execute")
        self.assertEqual(log.resource_type, "query")
        self.assertEqual(log.resource_id, "query-1")
        self.assertEqual(log.conn_id, "conn-1")
        self.assertEqual(log.db_name, "ry-cloud")
        self.assertEqual(log.status, "success")
        self.assertEqual(log.duration_ms, 12)
        self.assertEqual(len(log.sql_text), 4000)
        self.assertIn("statement_count", log.detail)

    async def test_record_operation_failure_is_swallowed(self):
        from app.services.operation_logger import record_operation

        ok = await record_operation(
            FakeAsyncSession(fail_commit=True),
            operator=make_operator(),
            action="connection.create",
            resource_type="connection",
            status="success",
        )

        self.assertFalse(ok)


class OperationLoggingRouteTestCase(unittest.IsolatedAsyncioTestCase):
    def make_current_user(self):
        from app.schemas.auth import CurrentUser

        return CurrentUser(
            user_id=7,
            username="alice",
            nickname="Alice",
            roles=["admin"],
            permissions=["*:*:*"],
            is_admin=True,
        )

    async def test_query_execute_passes_operator_to_background_task(self):
        from app.routers.query import execute_query
        from app.schemas.query import QueryExecuteRequest

        class BackgroundTasksStub:
            def __init__(self):
                self.task = None

            def add_task(self, fn, *args):
                self.task = (fn, args)

        bg = BackgroundTasksStub()
        req = QueryExecuteRequest(conn_id="conn-1", database="ry-cloud", sql="SELECT 1", query_id="query-1")

        result = await execute_query(req, bg, self.make_current_user())

        self.assertEqual(result, {"query_id": "query-1", "status": "running"})
        _, args = bg.task
        operator = args[-1]
        self.assertEqual(operator.user_id, 7)
        self.assertEqual(operator.username, "alice")

    async def test_apply_changes_records_table_operation(self):
        from app.routers.data import ChangeItem, ChangesRequest, apply_changes

        current_user = self.make_current_user()
        req = ChangesRequest(changes=[ChangeItem(op="update", pk_col="id", pk_val="1", values={"name": "demo"})])
        db = object()

        with patch("app.routers.data._db_type", return_value="mysql"), patch(
            "app.routers.data.data_service.apply_changes"
        ), patch("app.routers.data.operation_logger.record_operation", new=AsyncMock(return_value=True)) as log_mock:
            result = await apply_changes("conn-1", "ry-cloud", "sys_user", req, db, current_user)

        self.assertEqual(result, {"ok": True})
        _, kwargs = log_mock.await_args
        self.assertEqual(kwargs["operator"].user_id, 7)
        self.assertEqual(kwargs["action"], "data.apply_changes")
        self.assertEqual(kwargs["resource_type"], "table")
        self.assertEqual(kwargs["conn_id"], "conn-1")
        self.assertEqual(kwargs["db_name"], "ry-cloud")
        self.assertEqual(kwargs["table_name"], "sys_user")
        self.assertIn("change_count", kwargs["detail"])

    async def test_create_connection_records_operation(self):
        from app.routers.connections import create_connection
        from app.schemas.connection import ConnectionCreate

        current_user = self.make_current_user()
        payload = ConnectionCreate(name="demo", db_type="sqlite", database="demo.db")
        db = object()
        conn = type("ConnectionStub", (), {"id": "conn-1", "name": "demo", "db_type": "sqlite", "database": "demo.db"})()

        with patch(
            "app.routers.connections.connection_crud.create_connection",
            new=AsyncMock(return_value=conn),
        ), patch("app.routers.connections.operation_logger.record_operation", new=AsyncMock(return_value=True)) as log_mock:
            result = await create_connection(payload, db, current_user)

        self.assertIs(result, conn)
        _, kwargs = log_mock.await_args
        self.assertEqual(kwargs["operator"].user_id, 7)
        self.assertEqual(kwargs["action"], "connection.create")
        self.assertEqual(kwargs["resource_type"], "connection")
        self.assertEqual(kwargs["resource_id"], "conn-1")
        self.assertEqual(kwargs["detail"]["name"], "demo")

    async def test_kill_query_records_operation(self):
        from app.routers.query import kill_query

        current_user = self.make_current_user()
        db = object()

        with patch("app.routers.query.query_executor.kill_query", new=AsyncMock()), patch(
            "app.routers.query.operation_logger.record_operation", new=AsyncMock(return_value=True)
        ) as log_mock:
            result = await kill_query("query-1", db, current_user)

        self.assertEqual(result, {"ok": True})
        _, kwargs = log_mock.await_args
        self.assertEqual(kwargs["operator"].user_id, 7)
        self.assertEqual(kwargs["action"], "query.kill")
        self.assertEqual(kwargs["resource_type"], "query")
        self.assertEqual(kwargs["resource_id"], "query-1")


if __name__ == "__main__":
    unittest.main()
