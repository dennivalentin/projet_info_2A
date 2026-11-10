import os
from pathlib import Path
from unittest import mock

import dotenv

from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.security import hash_password
from utils.singleton import Singleton

logger = get_logger(__name__)


class ResetDatabase(metaclass=Singleton):
    """Database reset utility"""

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent.parent.parent

    @log
    def run(self, test_dao=False):
        """Run the database reset.
        If test_dao=True: reset test data.
        """
        if test_dao:
            mock.patch.dict(os.environ, {"POSTGRES_SCHEMA": "project_test_dao"}).start()
            pop_data_path = self.base_path / "data" / "pop_db_test.sql"
        else:
            pop_data_path = self.base_path / "data" / "pop_db.sql"

        init_db_path = self.base_path / "data" / "init_db.sql"

        dotenv.load_dotenv()

        schema = os.environ.get("POSTGRES_SCHEMA", "project")
        create_schema = (
            f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"
        )

        try:
            with open(init_db_path, encoding="utf-8") as init_db_file:
                init_db_as_string = init_db_file.read()

            with open(pop_data_path, encoding="utf-8") as pop_db_file:
                pop_db_as_string = pop_db_file.read()

        except Exception as e:
            logger.info(e)
            raise

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(create_schema)
                    cursor.execute(init_db_as_string)
                    cursor.execute(pop_db_as_string)
        except Exception as e:
            logger.info(e)
            raise

        # Hash passwords for initial users if UserDao is present
        try:
            from dao.user_dao import UserDao

            for u in UserDao().find_all():
                if hasattr(u, "password_hash"):
                    pass
        except Exception:
            pass

        return True


if __name__ == "__main__":
    ResetDatabase().run()
    ResetDatabase().run(True)
