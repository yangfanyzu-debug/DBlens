import unittest
from unittest.mock import patch


class DataServiceChangesTestCase(unittest.TestCase):
    def test_preview_insert_renders_null_and_omits_empty_insert(self):
        from app.services.data_service import preview_changes

        changes = [
            {"op": "insert", "values": {"label": "test", "created_at": None}},
            {"op": "insert", "values": {}},
        ]

        result = preview_changes("conn-1", "mysql", "ry-cloud", "categories", changes)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["sql"],
            "INSERT INTO `categories` (`label`, `created_at`) VALUES ('test', NULL)",
        )
        self.assertNotIn("'None'", result[0]["sql"])

    def test_apply_changes_uses_bound_parameters_for_insert_values(self):
        from app.services import data_service

        executed = []

        class FakeConnection:
            def execute(self, statement, params=None):
                executed.append((str(statement), params))

        class FakeBegin:
            def __enter__(self):
                return FakeConnection()

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakeEngine:
            def begin(self):
                return FakeBegin()

        changes = [{"op": "insert", "values": {"label": "test", "created_at": None}}]

        with patch("app.services.data_service.get_engine", return_value=FakeEngine()):
            data_service.apply_changes("conn-1", "mysql", "ry-cloud", "categories", changes)

        self.assertEqual(
            executed[-1],
            (
                "INSERT INTO `categories` (`label`, `created_at`) VALUES (:v_0_0, :v_0_1)",
                {"v_0_0": "test", "v_0_1": None},
            ),
        )


if __name__ == "__main__":
    unittest.main()
