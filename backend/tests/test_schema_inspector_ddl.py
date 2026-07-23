import importlib
import sys
import types
import unittest
from unittest.mock import patch


def load_schema_inspector():
    connection_manager = types.ModuleType("app.services.connection_manager")
    connection_manager.get_engine = lambda _conn_id: None
    sys.modules.pop("app.services.schema_inspector", None)
    with patch.dict(sys.modules, {"app.services.connection_manager": connection_manager}):
        return importlib.import_module("app.services.schema_inspector")


class TableDdlTestCase(unittest.TestCase):
    def test_mysql_returns_native_create_table_statement(self):
        schema_inspector = load_schema_inspector()

        with patch.object(
            schema_inspector,
            "_exec",
            return_value=[("categories", "CREATE TABLE `categories` (`id` bigint NOT NULL)")],
        ) as execute:
            ddl = schema_inspector.get_table_ddl("conn-1", "mysql", "ry-cloud", "categories")

        self.assertEqual(ddl, "CREATE TABLE `categories` (`id` bigint NOT NULL);")
        self.assertIn("SHOW CREATE TABLE `ry-cloud`.`categories`", execute.call_args.args[1])

    def test_sqlite_returns_stored_schema_statement(self):
        schema_inspector = load_schema_inspector()

        with patch.object(
            schema_inspector,
            "_exec",
            return_value=[("CREATE TABLE categories (id INTEGER PRIMARY KEY)",)],
        ):
            ddl = schema_inspector.get_table_ddl("conn-1", "sqlite", "main", "categories")

        self.assertEqual(ddl, "CREATE TABLE categories (id INTEGER PRIMARY KEY);")

    def test_postgresql_builds_table_statement_from_catalog_metadata(self):
        schema_inspector = load_schema_inspector()

        with patch.object(
            schema_inspector,
            "_exec",
            side_effect=[
                [
                    ("id", "bigint", True, "nextval('categories_id_seq'::regclass)"),
                    ("label", "character varying(100)", False, None),
                ],
                [("categories_pkey", "PRIMARY KEY (id)")],
                [("CREATE INDEX categories_label_idx ON public.categories USING btree (label)",)],
            ],
        ):
            ddl = schema_inspector.get_table_ddl("conn-1", "postgresql", "main", "categories")

        self.assertIn('CREATE TABLE "public"."categories"', ddl)
        self.assertIn('"id" bigint DEFAULT nextval', ddl)
        self.assertIn('CONSTRAINT "categories_pkey" PRIMARY KEY (id)', ddl)
        self.assertIn("CREATE INDEX categories_label_idx", ddl)


if __name__ == "__main__":
    unittest.main()
