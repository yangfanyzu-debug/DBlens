import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException


class TestConnectionRoutePermissions(unittest.IsolatedAsyncioTestCase):
    def make_admin_user(self):
        from app.schemas.auth import CurrentUser

        return CurrentUser(
            user_id=1,
            username="admin",
            nickname="Admin",
            roles=["admin"],
            permissions=["*:*:*"],
            is_admin=True,
        )

    def test_admin_only_routes_depend_on_require_admin_user(self):
        from app.dependencies.auth import require_admin_user
        from app.main import app

        expected = {
            ("POST", "/api/connections"),
            ("POST", "/api/connections/test-form"),
            ("PUT", "/api/connections/{conn_id}"),
            ("DELETE", "/api/connections/{conn_id}"),
            ("POST", "/api/connections/{conn_id}/test"),
        }

        for method, path in expected:
            route = next(
                route
                for route in app.routes
                if getattr(route, "path", None) == path and method in getattr(route, "methods", set())
            )
            dependency_calls = [dep.call for dep in route.dependant.dependencies]
            self.assertIn(require_admin_user, dependency_calls, msg=f"{method} {path} missing admin dependency")

    def test_authenticated_routes_depend_on_get_current_user(self):
        from app.dependencies.auth import get_current_user
        from app.main import app

        expected = {
            ("GET", "/api/connections"),
            ("GET", "/api/connections/{conn_id}"),
            ("POST", "/api/connections/{conn_id}/connect"),
            ("DELETE", "/api/connections/{conn_id}/disconnect"),
        }

        for method, path in expected:
            route = next(
                route
                for route in app.routes
                if getattr(route, "path", None) == path and method in getattr(route, "methods", set())
            )
            dependency_calls = [dep.call for dep in route.dependant.dependencies]
            self.assertIn(get_current_user, dependency_calls, msg=f"{method} {path} missing auth dependency")

    async def test_require_admin_user_rejects_non_admin(self):
        from app.dependencies.auth import require_admin_user
        from app.schemas.auth import CurrentUser

        current_user = CurrentUser(
            user_id=2,
            username="demo",
            nickname="Demo",
            roles=["common"],
            permissions=["db:lens:use"],
            is_admin=False,
        )

        with self.assertRaises(HTTPException) as exc:
            await require_admin_user(current_user)

        self.assertEqual(exc.exception.status_code, 403)
        self.assertEqual(exc.exception.detail, "Admin permission required")

    async def test_require_admin_user_allows_admin(self):
        from app.dependencies.auth import require_admin_user
        from app.schemas.auth import CurrentUser

        current_user = CurrentUser(
            user_id=1,
            username="admin",
            nickname="Admin",
            roles=["admin"],
            permissions=["*:*:*"],
            is_admin=True,
        )

        result = await require_admin_user(current_user)

        self.assertEqual(result, current_user)

    async def test_create_connection_passes_operator_context(self):
        from app.routers.connections import create_connection
        from app.schemas.connection import ConnectionCreate

        current_user = self.make_admin_user()
        payload = ConnectionCreate(name="demo", db_type="sqlite", database="demo.db")
        db = object()
        expected = object()

        with patch(
            "app.routers.connections.connection_crud.create_connection",
            new=AsyncMock(return_value=expected),
        ) as create_mock:
            result = await create_connection(payload, db, current_user)

        self.assertIs(result, expected)
        _, kwargs = create_mock.await_args
        operator = kwargs["operator"]
        self.assertEqual(operator.user_id, current_user.user_id)
        self.assertEqual(operator.username, current_user.username)
        self.assertEqual(operator.roles, tuple(current_user.roles))
        self.assertTrue(operator.is_admin)

    async def test_update_connection_passes_operator_context(self):
        from app.routers.connections import update_connection
        from app.schemas.connection import ConnectionUpdate

        current_user = self.make_admin_user()
        payload = ConnectionUpdate(name="demo", db_type="sqlite", database="demo.db")
        db = object()
        expected = object()

        with patch(
            "app.routers.connections.connection_crud.update_connection",
            new=AsyncMock(return_value=expected),
        ) as update_mock:
            result = await update_connection("conn-1", payload, db, current_user)

        self.assertIs(result, expected)
        _, kwargs = update_mock.await_args
        operator = kwargs["operator"]
        self.assertEqual(operator.user_id, current_user.user_id)
        self.assertEqual(operator.username, current_user.username)
        self.assertEqual(operator.roles, tuple(current_user.roles))
        self.assertTrue(operator.is_admin)

    async def test_delete_connection_passes_operator_context(self):
        from app.routers.connections import delete_connection

        current_user = self.make_admin_user()
        db = object()

        with patch(
            "app.routers.connections.connection_crud.delete_connection",
            new=AsyncMock(return_value=True),
        ) as delete_mock, patch(
            "app.routers.connections.connection_manager.disconnect",
        ) as disconnect_mock:
            result = await delete_connection("conn-1", db, current_user)

        self.assertEqual(result, {"ok": True})
        _, kwargs = delete_mock.await_args
        operator = kwargs["operator"]
        self.assertEqual(operator.user_id, current_user.user_id)
        self.assertEqual(operator.username, current_user.username)
        self.assertEqual(operator.roles, tuple(current_user.roles))
        self.assertTrue(operator.is_admin)
        disconnect_mock.assert_called_once_with("conn-1")

    async def test_test_connection_passes_operator_context(self):
        from app.routers.connections import test_connection

        current_user = self.make_admin_user()
        db = object()
        conn = object()

        with patch(
            "app.routers.connections.connection_crud.get_connection",
            new=AsyncMock(return_value=conn),
        ), patch(
            "app.routers.connections.connection_manager.test_connection",
            return_value=(True, "ok", 12),
        ) as test_mock:
            result = await test_connection("conn-1", db, current_user)

        self.assertTrue(result.success)
        self.assertEqual(result.message, "ok")
        self.assertEqual(result.latency_ms, 12)
        _, kwargs = test_mock.call_args
        operator = kwargs["operator"]
        self.assertEqual(operator.user_id, current_user.user_id)
        self.assertEqual(operator.username, current_user.username)
        self.assertEqual(operator.roles, tuple(current_user.roles))
        self.assertTrue(operator.is_admin)

    async def test_test_connection_form_passes_operator_context(self):
        from app.routers.connections import test_connection_form
        from app.schemas.connection import ConnectionCreate

        current_user = self.make_admin_user()
        payload = ConnectionCreate(name="demo", db_type="sqlite", database="demo.db")

        with patch(
            "app.routers.connections.connection_manager.test_connection_from_form",
            return_value=(True, "ok", 8),
        ) as test_mock:
            result = await test_connection_form(payload, current_user)

        self.assertTrue(result.success)
        self.assertEqual(result.message, "ok")
        self.assertEqual(result.latency_ms, 8)
        _, kwargs = test_mock.call_args
        operator = kwargs["operator"]
        self.assertEqual(operator.user_id, current_user.user_id)
        self.assertEqual(operator.username, current_user.username)
        self.assertEqual(operator.roles, tuple(current_user.roles))
        self.assertTrue(operator.is_admin)


if __name__ == "__main__":
    unittest.main()
