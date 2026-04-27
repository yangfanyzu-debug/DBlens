import unittest

from fastapi import HTTPException


class TestConnectionRoutePermissions(unittest.IsolatedAsyncioTestCase):
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


if __name__ == "__main__":
    unittest.main()
