import unittest


class SettingsDatabaseUrlTestCase(unittest.TestCase):
    def test_default_database_url_points_to_local_sqlite_meta_database(self):
        from app.config import Settings

        settings = Settings(_env_file=None)

        self.assertEqual(
            settings.DATABASE_URL,
            "sqlite+aiosqlite:///./dblens_meta.db",
        )

    def test_sync_database_url_uses_pymysql_for_same_meta_database(self):
        from app.config import Settings, sync_database_url

        settings = Settings(
            DATABASE_URL="mysql+aiomysql://dblens:secret@db-host:3306/dblens?charset=utf8mb4",
            _env_file=None,
        )

        self.assertEqual(
            sync_database_url(settings.DATABASE_URL),
            "mysql+pymysql://dblens:secret@db-host:3306/dblens?charset=utf8mb4",
        )


if __name__ == "__main__":
    unittest.main()
