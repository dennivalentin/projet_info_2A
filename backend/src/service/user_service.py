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

    @log
    def make_admin(self, user_id: int) -> bool:
        """change the role from "user" to "admin"
        Args:
          user_ind (int): The id of the user to promote
        
        Returns:
           bool: True if the change was succesful
        """
        user = UserDao().find_by_id(user_id)
        if user is None:
            raise ValueError("The user could not be found")
        
        new_user = User(user_id=user.user_id, username=user.username, email=user.email, password_hash=user.password_hash, creation_date=user.creation_date, role="admin")

        return UserDao().update(new_user)
    
    @log
    def delete_account(self, user_id:int) -> bool:
        """ delete a user accout 
          Args:
            user_id (int): The id of the user to delete
        
          Returns:
            bool: True if the supression was succesful.
        """

        user = UserDao().find_by_id(user_id)
        if user is None:
            raise ValueError("The user could not be found")

        return UserDao().delete(user.user_id)