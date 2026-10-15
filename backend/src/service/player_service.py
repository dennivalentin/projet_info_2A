import secrets

from business_object.player import Player
from dao.player_dao import PlayerDao
from utils.log_utils import log
from utils.security import hash_password


class PlayerService:
    """Service that handles business logic related to players (creation, search, etc.)."""

    @log
    def create(self, username, password, elo, email, pokemon_fan) -> Player:
        """Creates a new player in the system.
        Args:
            username (str)
            password (str) will be hashed before storage
            elo (int)
            email (str)
            pokemon_fan (bool)
        Returns:
            Player object created or None if creation failed.
        """
        new_player = Player(
            username=username,
            password=hash_password(password, username),
            elo=elo,
            email=email,
            pokemon_fan=pokemon_fan,
        )
        return new_player if PlayerDao().create(new_player) else None

    @log
    def find_all(self) -> list[Player]:
        """Retrieves all players from the database.
        Returns:
            list[Player]"""
        return PlayerDao().find_all()

    @log
    def find_by_id(self, id_player: int) -> Player:
        """Finds a specific player by their unique id.
        Args:
            id_player (int)
        Returns:
            Player object if found, otherwise None.
        """
        return PlayerDao().find_by_id(id_player)

    @log
    def update(self, player) -> Player:
        """Updates an existing player's information.
        Args:
            Player object containing updated information.
        Returns:
            The updated Player object, or None if the update failed.
        """
        return player if PlayerDao().update(player) else None

    @log
    def delete(self, user) -> bool:
        """Delete a user account.
        Args:
            User object to be deleted.
        Returns:
            True if deletion was successful, False otherwise.
        """
        return UserDao().delete(user)

    @log
    def login(self, username, password):
        user = UserDao().find_by_username(username) 
        if user is None:
            return None
        if not hmac.compare_digest(user.password_hash, hash_password(password, username)): #compare les deux chaines en temps constant pour une meilleure sécurité 
            return None                                
        ConnectionDao().create(user.user_id)
        return user


    @log
    def username_already_used(self, username: str) -> bool:
        """Check if a username is already used.
        Args:
            username (str)
        Returns:
            True if the username already exists in the database.
        """
        players = PlayerDao().find_all()
        return username in [p.username for p in players]
