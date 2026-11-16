"""Re-creates a database schema from the SQL files of the data folder."""

import os
from pathlib import Path

from psycopg2 import sql

from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)

TEST_SCHEMA = "project_test_dao"


class ResetDatabase(metaclass=Singleton):
    """Drops and re-creates a schema, then fills it with seed data.

    Used by the DAO unit tests, which run on their own schema
    (project_test_dao) so that they never touch the application data.
    """

    def __init__(self):
        """Locates the data folder at the root of the repository."""
        self.data_path = Path(__file__).resolve().parents[3] / "data"

    @log
    def run(self, test_dao: bool = False) -> bool:
        """Re-creates the schema and loads the seed data.

        Args:
            test_dao: True to reset the test schema with pop_db_test.sql,
                False to reset the application schema with pop_db.sql.

        Returns:
            True when the schema has been re-created.
        """
        app_schema = os.environ.get("POSTGRES_SCHEMA", "project")
        schema = TEST_SCHEMA if test_dao else app_schema
        pop_file = "pop_db_test.sql" if test_dao else "pop_db.sql"

        init_db = (self.data_path / "init_db.sql").read_text(encoding="utf-8")
        pop_db = (self.data_path / pop_file).read_text(encoding="utf-8")

        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                # init_db.sql has no schema prefix: the search_path decides where
                # the tables go, so it is set explicitly to the schema being reset
                cursor.execute(
                    sql.SQL(
                        "DROP SCHEMA IF EXISTS {s} CASCADE; CREATE SCHEMA {s}; SET search_path TO {s};"
                    ).format(s=sql.Identifier(schema))
                )
                cursor.execute(init_db)
                cursor.execute(pop_db)
                # Back to the schema the application is configured to use
                cursor.execute(
                    sql.SQL("SET search_path TO {s};").format(s=sql.Identifier(app_schema))
                )

        logger.info(f"Schema {schema} re-created with {pop_file}")
        return True


if __name__ == "__main__":
    ResetDatabase().run(test_dao=True)
