from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
logger = get_logger(__name__)

class FavouriteDao(metaclass=Singleton):
    """Class containing methods to access Favourites in the database."""

    @log
    def create(self, neo_id, user_id) -> bool:
        """Associate a neo to an user
        Parameters
        ----------
            neo_id : Neo that the user wants to mark as favourite
            user_id : user with that favourite
        Returns
        -------
            True if creation is successful, False otherwise
        """
        res = None
        date_now = datetime.now()

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO favourite(user_id, neo_id, date_added) VALUES "
                        "(%(user_id)s, %(neo_id)s, %(date_now)s) "
                        "ON CONFLICT (user_id, neo_id) DO NOTHING "
                        "RETURNING neo_id;",
                        {
                            "neo_id": neo_id,
                            "user_id": user_id,
                            "date_now": date_now,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            created = True

        return created
    
    @log
    def delete(self, neo_id, user_id) -> bool:
        """Delete a favourite
        Parameters
        ----------
            neo_id : Neo that the user wants to mark as favourite
            user_id : user with that favourite
        Returns
        -------
            True if deleting is successful, False otherwise
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM favourite                               "
                        " WHERE user_id = %(user_id)s and neo_id = %(neo_id)s                 ",
                        {"user_id": user_id, "neo_id": neo_id},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return res > 0
    
    @log
    def find_favourite_by_user(self, user_id : int) -> list[int]:
        """List all favourite by user
        Returns:
            list[Neo] sorted by username
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT neo_id                               "
                        "  FROM favourite                           "
                        "WHERE user_id = %(user_id)s",
                        {
                            "user_id": user_id
                        }
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        return [row["neo_id"] for row in res]
