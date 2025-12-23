import hashlib
import re
import secrets

from src.Model.abstract_user import AbstractUser


class PasswordService:
    """
    Service dedicated to the secure creation, hashing, and verification
    of passwords using manual salting (SHA-256).
    """

    COMMON_PASSWORDS = {"password", "12345678", "qwerty", "azerty", "admin", "motdepasse"}
    MIN_LENGTH = 8
    MIN_SCORE = 4

    def __init__(self):
        pass

    def create_salt(self) -> str:
        """
        Creates a secure, random salt string.
        (Using 32 bytes/64 hex characters.)
        """
        return secrets.token_hex(32)

    def hash_password(self, password: str, salt: str) -> str:
        """
        Hashes a plain text password combined with a salt using SHA-256.
        The salt parameter is mandatory for secure hashing.
        """
        if not salt:
            raise ValueError("Salt must be provided for secure hashing.")

        return hashlib.sha256((password + salt).encode()).hexdigest()

    def check_password_strength(self, password: str):
        """
        Validates minimum strength rules for a password.
        Raises an exception if rules are not met.
        """

        if len(password) < self.MIN_LENGTH:
            raise ValueError(f"The password must be at least {self.MIN_LENGTH} characters long.")

        if password.lower() in self.COMMON_PASSWORDS:
            raise ValueError("The password is one of the most commonly used passwords and is prohibited.")

        score = 0
        if re.search(r"[A-Z]", password):
            score += 1
        if re.search(r"[a-z]", password):
            score += 1
        if re.search(r"\d", password):
            score += 1
        if re.search(r"[^a-zA-Z0-9\s]", password):
            score += 1

        if score < self.MIN_SCORE:
            raise ValueError(
                f"Your password must have all character types "
                f"(capital letter, lower letter, digit and special). You actually have {score}/4 of them."
            )
        return True

    def set_password(self, user: AbstractUser, password: str):
        """
        Generates a new salt, hashes the password, and sets
        the private attributes _hash_password and _salt on the user.
        """
        self.check_password_strength(password)
        salt = self.create_salt()
        hashed = self.hash_password(password, salt)
        user._salt = salt
        user._hash_password = hashed

    def verify_password(self, user: AbstractUser, password: str) -> bool:
        """
        Verifies if a given password matches the user's stored hash.
        """
        if not hasattr(user, "_hash_password") or not hasattr(user, "_salt"):
            raise ValueError("User object is missing password or salt attributes.")

        hashed_input = self.hash_password(password, user._salt)
        return hashed_input == user._hash_password
