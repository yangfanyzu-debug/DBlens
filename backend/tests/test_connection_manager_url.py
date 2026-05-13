import unittest
from unittest.mock import patch

from sqlalchemy.engine import make_url


class ConnectionManagerUrlTestCase(unittest.TestCase):
    def test_saved_mysql_connection_url_preserves_at_sign_in_password(self):
        from app.models.connection import Connection
        from app.services import connection_manager

        conn = Connection(
            id="conn-1",
            name="demo",
            db_type="mysql",
            host="192.168.0.140",
            port=3306,
            username="app_user",
            password_enc="encrypted",
            database="dblens",
        )

        with patch.object(connection_manager.crypto, "decrypt", return_value="Qzmp@2018"):
            parsed = make_url(connection_manager._build_url(conn))

        self.assertEqual(parsed.username, "app_user")
        self.assertEqual(parsed.password, "Qzmp@2018")
        self.assertEqual(parsed.host, "192.168.0.140")

    def test_saved_doris_connection_uses_mysql_driver(self):
        from app.models.connection import Connection
        from app.services import connection_manager

        conn = Connection(
            id="conn-1",
            name="demo",
            db_type="doris",
            host="192.168.0.140",
            port=9030,
            username="app_user",
            password_enc="encrypted",
            database="warehouse",
        )

        with patch.object(connection_manager.crypto, "decrypt", return_value="Qzmp@2018"):
            parsed = make_url(connection_manager._build_url(conn))

        self.assertEqual(parsed.drivername, "mysql+pymysql")
        self.assertEqual(parsed.username, "app_user")
        self.assertEqual(parsed.password, "Qzmp@2018")
        self.assertEqual(parsed.host, "192.168.0.140")
        self.assertEqual(parsed.port, 9030)

    def test_form_mysql_connection_url_preserves_at_sign_in_password(self):
        from app.services import connection_manager

        captured = {}

        class FakeConnection:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def execute(self, _statement):
                return None

        class FakeEngine:
            def connect(self):
                return FakeConnection()

            def dispose(self):
                return None

        def fake_create_engine(url, *args, **kwargs):
            captured["url"] = url
            return FakeEngine()

        data = {
            "db_type": "mysql",
            "host": "192.168.0.140",
            "port": 3306,
            "username": "app_user",
            "password": "Qzmp@2018",
            "database": "dblens",
        }

        with patch.object(connection_manager, "create_engine", side_effect=fake_create_engine):
            success, _message, _latency = connection_manager.test_connection_from_form(data)

        self.assertTrue(success)
        parsed = make_url(captured["url"])
        self.assertEqual(parsed.username, "app_user")
        self.assertEqual(parsed.password, "Qzmp@2018")
        self.assertEqual(parsed.host, "192.168.0.140")

    def test_form_doris_connection_uses_mysql_driver_and_default_port(self):
        from app.services import connection_manager

        captured = {}

        class FakeConnection:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def execute(self, _statement):
                return None

        class FakeEngine:
            def connect(self):
                return FakeConnection()

            def dispose(self):
                return None

        def fake_create_engine(url, *args, **kwargs):
            captured["url"] = url
            return FakeEngine()

        data = {
            "db_type": "doris",
            "host": "192.168.0.140",
            "username": "app_user",
            "password": "Qzmp@2018",
            "database": "warehouse",
        }

        with patch.object(connection_manager, "create_engine", side_effect=fake_create_engine):
            success, _message, _latency = connection_manager.test_connection_from_form(data)

        self.assertTrue(success)
        parsed = make_url(captured["url"])
        self.assertEqual(parsed.drivername, "mysql+pymysql")
        self.assertEqual(parsed.username, "app_user")
        self.assertEqual(parsed.password, "Qzmp@2018")
        self.assertEqual(parsed.host, "192.168.0.140")
        self.assertEqual(parsed.port, 9030)


if __name__ == "__main__":
    unittest.main()
