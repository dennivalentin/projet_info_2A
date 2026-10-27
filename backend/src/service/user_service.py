import hmac

from business_object.user import User
from dao.connection_dao import ConnectionDao
from dao.user_dao import UserDao
from utils.log_utils import log
from utils.security import hash_password

class UserService:
    """Buisness logic related to user accounts"""

    @log
    def create_account(self, username: str, email:str, password: str) -> User:
        """creates a new account with the 'user' role

        Args:
           username (str): The chosen username
           email (str): The email adress
           password (str): The plain password
        
        Returns:
           A user

        """
        if UserDao().find_by_username(username):
            raise ValueError("The username is already used")
        elif UserDao().find_by_email(email):
            raise ValueError("The email is already used")

        new_user = User(user_id=None, username=username, email=email,
        password_hash=hash_password(password, username), creation_date=None, role="user")

        if not UserDao().create(new_user):
            raise ValueError("Account creation failed")
        
        return UserDao().find_by_username(username)

    @log
    def login(self, username: str, password: str) -> User | None:
        """Authenticates a user and records the connection.

        Args:
            username (str): The username.
            password (str): The plain password.

        Returns:
            User | None: The authenticated user, or None if the username is unknown
                or the password is wrong.
        """
        user = UserDao().find_by_username(username)
        if user is None:
            return None

        if not hmac.compare_digest(user.password_hash, hash_password(password, username)):
            return None

        ConnectionDao().create(user.user_id)
        return user

    