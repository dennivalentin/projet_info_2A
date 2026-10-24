from business_object.connection import Connection
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class ConnectionDao(metaclass=Singleton):
    """Class containing methods to access the connection history in the database."""

    @log
    def create(self, user_id: int) -> Connection:
        """Records a login of a user (the date is set by the database).

        Args:
            user_id (int): The id of the user who logged in.

        Returns:
            Connection: The recorded connection.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO connection (user_id) VALUES (%(user_id)s) RETURNING *;",
                        {"user_id": user_id},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        return Connection(
            connection_id=res["connection_id"],
            user_id=res["user_id"],
            connection_date=res["connection_date"],
        )

    @log
    def find_by_user(self, user_id: int) -> list[Connection]:
        """Find the connection history of a user.

        Args:
            user_id (int): The id of the user to look for.
        Returns:
            list[Connection]: The connections of the user (empty if none).
        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                               "
                        "  FROM connection                      "
                        " WHERE user_id = %(user_id)s;          ",
                        {"user_id": user_id},
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        connection = []

        for row in res:
            connection.append(
                Connection(
                    user_id=row["user_id"],
                    connection_id=row["connection_id"],
                    connection_date=row["connection_date"],
                )
            )

        return connection