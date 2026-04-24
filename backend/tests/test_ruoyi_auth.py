import unittest
from unittest.mock import patch
from fastapi import HTTPException


class TestRuoYiAuth(unittest.IsolatedAsyncioTestCase):
    async def test_map_admin_user_from_ruoyi_payload(self):
        payload = {
            "user": {"userId": 1, "userName": "admin", "nickName": "Admin"},
            "roles": ["admin"],
            "permissions": ["*:*:*"],
        }

        from app.services.ruoyi_auth import map_ruoyi_user

        user = map_ruoyi_user(payload)

        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.username, "admin")
        self.assertEqual(user.nickname, "Admin")
        self.assertEqual(user.roles, ["admin"])
        self.assertEqual(user.permissions, ["*:*:*"])
        self.assertTrue(user.is_admin)

    async def test_map_normal_user_from_ruoyi_payload(self):
        payload = {
            "user": {"userId": 2, "userName": "demo", "nickName": "Demo"},
            "roles": ["common"],
            "permissions": ["db:lens:use"],
        }

        from app.services.ruoyi_auth import map_ruoyi_user

        user = map_ruoyi_user(payload)

        self.assertEqual(user.user_id, 2)
        self.assertEqual(user.username, "demo")
        self.assertEqual(user.nickname, "Demo")
        self.assertEqual(user.roles, ["common"])
        self.assertEqual(user.permissions, ["db:lens:use"])
        self.assertFalse(user.is_admin)

    async def test_fetch_current_user_forwards_authorization_header(self):
        import json
        from app.services.ruoyi_auth import fetch_current_user

        payload = {
            "code": 200,
            "user": {"userId": 9, "userName": "demo", "nickName": "Demo"},
            "roles": ["common"],
            "permissions": ["db:lens:use"],
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps(payload).encode("utf-8")

        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.get_header("Authorization")
            captured["timeout"] = timeout
            return FakeResponse()

        with patch("app.services.ruoyi_auth.urlopen", new=fake_urlopen):
            user = await fetch_current_user("Bearer token-123")

        self.assertEqual(user.user_id, 9)
        self.assertEqual(
            captured["url"],
            "http://192.168.0.140/prod-api/system/user/getInfo",
        )
        self.assertEqual(captured["authorization"], "Bearer token-123")
        self.assertEqual(captured["timeout"], 10)


class TestAuthEndpoint(unittest.TestCase):
    def test_auth_router_is_registered_on_app(self):
        from app.main import app

        auth_route = next(
            (route for route in app.routes if getattr(route, "path", None) == "/api/auth/me"),
            None,
        )

        self.assertIsNotNone(auth_route)
        self.assertIn("GET", auth_route.methods)


class TestAuthDependency(unittest.IsolatedAsyncioTestCase):
    async def test_get_current_user_requires_authorization_header(self):
        from app.dependencies.auth import get_current_user

        with self.assertRaises(HTTPException) as exc:
            await get_current_user(None)

        self.assertEqual(exc.exception.status_code, 401)
        self.assertEqual(exc.exception.detail, "RuoYi token missing")

    async def test_get_current_user_forwards_authorization_header(self):
        from app.dependencies.auth import get_current_user
        from app.schemas.auth import CurrentUser

        mocked_user = CurrentUser(
            user_id=1,
            username="admin",
            nickname="Admin",
            roles=["admin"],
            permissions=["*:*:*"],
            is_admin=True,
        )

        with patch(
            "app.dependencies.auth.fetch_current_user",
            autospec=True,
            return_value=mocked_user,
        ) as fetch_current_user:
            user = await get_current_user("Bearer token-123")

        self.assertEqual(user, mocked_user)
        fetch_current_user.assert_awaited_once_with("Bearer token-123")

    async def test_me_returns_normalized_current_user(self):
        from app.routers.auth import read_current_user
        from app.schemas.auth import CurrentUser

        mocked_user = CurrentUser(
            user_id=1,
            username="admin",
            nickname="Admin",
            roles=["admin"],
            permissions=["*:*:*"],
            is_admin=True,
        )

        response = await read_current_user(mocked_user)

        self.assertEqual(response.model_dump(), {"user": mocked_user.model_dump()})


if __name__ == "__main__":
    unittest.main()
