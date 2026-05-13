import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class DeploymentArtifactsTestCase(unittest.TestCase):
    def test_mysql_init_script_matches_current_doris_schema(self):
        source = (REPO_ROOT / "sql" / "init_dblens_mysql.sql").read_text(encoding="utf-8")

        self.assertIn("db_type ENUM('mysql', 'postgresql', 'sqlite', 'doris')", source)
        self.assertIn("INSERT INTO alembic_version (version_num) VALUES ('0003')", source)

    def test_dblensctl_restart_does_not_exit_before_starting(self):
        source = (REPO_ROOT / "backend" / "dblensctl.sh").read_text(encoding="utf-8")

        self.assertIn("restart_app()", source)
        self.assertIn("restart) restart_app ;;", source)


if __name__ == "__main__":
    unittest.main()
