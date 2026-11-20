from business_object.connection import Connection
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class ConnectionDao(metaclass=Singleton):
    """Class containing methods to access the connection history in the database."""

    @log
    def create(self, user_id: int, access_token: str | None = None) -> Connection:
        """Records a login of a user (the date is set by the database).

        Args:
            user_id (int): The id of the user who logged in.
            access_token (str, optional): The authentication token.

        Returns:
            Connection: The recorded connection.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO connection (user_id, access_token) VALUES (%(user_id)s, %(token)s) RETURNING *;",
                        {"user_id": user_id, "token": access_token},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        return self._map_row_to_connection(res)

    @log
    def find_by_user(self, user_id: int) -> list[Connection]:
        """Find the connection history of a user.

        Args:
            user_id (int): The id of the user to look for.
        Returns:
            list[Connection]: The connections of the user, latest first (empty if none).
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                               "
                        "  FROM connection                      "
                        " WHERE user_id = %(user_id)s           "
                        " ORDER BY connection_date DESC;        ",
                        {"user_id": user_id},
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        connections = []
        for row in res:
            connections.append(self._map_row_to_connection(row))
        return connections

    def _map_row_to_connection(self, row: dict) -> Connection:
        """Builds a Connection from a row of the connection table."""
        return Connection(
            connection_id=row["connection_id"],
            user_id=row["user_id"],
            date=row["connection_date"],
        )
