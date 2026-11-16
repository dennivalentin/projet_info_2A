"""Generates a random secret key for JWT_SECRET_KEY in the .env file.

Usage (from the repository root): python key_generator_for_.env.py
"""

import secrets
import string


def generate_secret_key(length: int = 64) -> str:
    """Returns a random key of `length` letters, generated with the secrets module."""
    alphabet = string.ascii_letters
    return "".join(secrets.choice(alphabet) for _ in range(length))


if __name__ == "__main__":
    print(generate_secret_key(64))
