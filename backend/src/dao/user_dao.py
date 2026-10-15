from business_object.user import User.py
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class UserDao(metaclass=Singleton):
    """Class containing methods to access users in the database."""

    @log
    def create(self, user: User) -> bool:
        """Create a user in the database.

        Args:
            user (User): The user to create.

        Returns:
            bool: True if the user was inserted, False otherwise.
        """
        nb_affected_rows = 0

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO "user" (username, password_hash, email, role)      '
                        "VALUES (%(username)s, %(password_hash)s, %(email)s, %(role)s); ",
                        {
                            "username": user.username,
                            "password_hash": user.password_hash,
                            "email": user.email,
                            "role": user.role,
                        },
                    )
                    nb_affected_rows = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return nb_affected_rows == 1

    @log
def find_by_id(self, user_id: int) -> User:
    """Find a user by their id.
    Args:
        user_id (int): The ID of the user to find
    Returns:
        User matching the given id
    """
    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT *                            "
                    '  FROM "user" '
                    " WHERE user_id = %(user_id)s;       ",
                    {"user_id": user_id},
                )
                res = cursor.fetchone()
    except Exception as e:
        logger.error(e)
        raise

    user = None
    if res:
        user = User(
            user_id=res["user_id"],
            username=res["username"],
            email=res["email"],
            password_hash=res["password_hash"],
            creation_date=res["creation_date"],
            role=res["role"],
        )

    return user


    @log
    def find_all(self) -> list[User]:
        """List all users in the database.
        Returns:
            list[User] sorted by username
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                                "
                        '  FROM "user"                           '
                        " ORDER BY username;                     "
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        users_list = []

        if res:
            for row in res:
                user = User(
                    user_id=row["user_id"],
                    username=row["username"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    creation_date=row["creation_date"],
                    role=row["role"],
                )

                users_list.append(user)

        return users_list

    @log
    def update(self, user: User) -> bool:
        """Update a user in the database.
        Args:
            user (User): User to be updated 
        Returns:
            True if update is successful, False otherwise
        """
        nb_affected_rows = 0

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'UPDATE "user"                                '
                        "   SET username = %(username)s,              "
                        "       email = %(email)s,                    "
                        "       password_hash = %(password_hash)s,    "
                        "       role = %(role)s                       "
                        " WHERE user_id = %(user_id)s;                ",
                        {
                            "username": user.username,
                            "email": user.email,
                            "password_hash": user.password_hash,
                            "role": user.role,
                            "user_id": user.user_id,
                        },
                    )
                    nb_affected_rows = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return nb_affected_rows == 1

    @log
    def delete(self, user_id: int) -> bool:
        """Delete a user from the database.
        Args:
            user_id (int): The id of the user to delete.

        Returns:
            True if the user was successfully deleted, False otherwise
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'DELETE FROM "user"                               '
                        " WHERE user_id = %(user_id)s                    ",
                        {"user_id": user_id},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return res > 0

    @log
    def find_by_username(self, username: str) -> User:
        """Find a user by their username.

        Args:
            username (str): The username to look for.
        Returns:
            User matching the given username, or None if not found.
        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                               "
                        '  FROM "user"                          '
                        " WHERE username = %(username)s;        ",
                        {"username": username},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        user = None

        if res:
            user = User(
                user_id=res["user_id"],
                username=res["username"],
                email=res["email"],
                password_hash=res["password_hash"],
                creation_date=res["creation_date"],
                role=res["role"],
            )

        return user

    @log
    def find_by_token(self, access_token: str) -> User:
        """Find the user owning an active connection token.

        Args:
            access_token (str): The token to search for.
        Returns:
            User object if the token is valid, otherwise None.
        """
        if not access_token:
            return None

        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'SELECT u.*                                          '
                        '  FROM "user" u                                    '
                        "  JOIN connection c ON c.user_id = u.user_id       "
                        " WHERE c.access_token = %(token)s;                 ",
                        {"token": access_token},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(f"Error finding user by token: {e}")
            raise

        user = None
        if res:
            user = User(
                user_id=res["user_id"],
                username=res["username"],
                email=res["email"],
                password_hash=res["password_hash"],
                creation_date=res["creation_date"],
                role=res["role"],
            )

        return user
