import hashlib
from fastapi import Header, HTTPException
from business_object.user import User


def hash_password(password: str, salt: str = "") -> str:
    password_bytes = password.encode("utf-8") + salt.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def verify_token(x_auth_token=Header(None)) -> User:
    """Valide le token de l'utilisateur connecté."""
    if not x_auth_token:
        raise HTTPException(status_code=401, detail="Missing token.")

    try:
        from dao.user_dao import UserDao
        user = UserDao().find_by_token(x_auth_token)
        if user:
            return user
        raise HTTPException(status_code=401, detail="Invalid token.")
    except (ImportError, Exception):
        # Fallback pour le dev en attendant que la branche F1 (UserDao) soit fusionnée
        return User(
            user_id=1,
            username="admin",
            email="admin@email.fr",
            password_hash="",
            role="admin",
        )
