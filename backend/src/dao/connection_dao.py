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
