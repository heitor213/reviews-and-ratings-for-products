"""Подсистема аутентификации: SHA-256 + соль, роли."""

import hashlib
import os
import binascii
from dataclasses import dataclass
from src.db.database import db


SALT_SIZE = 16


def hash_password(password: str, salt: bytes | None = None) -> str:
    if salt is None:
        salt = os.urandom(SALT_SIZE)
    digest = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()
    return f"{binascii.hexlify(salt).decode()}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, _ = stored.split("$", 1)
        salt = binascii.unhexlify(salt_hex)
        return hash_password(password, salt) == stored
    except (ValueError, TypeError):
        return False


@dataclass
class CurrentUser:
    id: int
    login: str
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def authenticate(login: str, password: str) -> CurrentUser | None:
    row = db.fetch_one(
        """
        SELECT u.id, u.login, u.password_hash, r.name AS role
        FROM users u JOIN roles r ON r.id = u.role_id
        WHERE u.login = ?
        """,
        (login,),
    )
    if not row or not verify_password(password, row["password_hash"]):
        return None
    return CurrentUser(id=row["id"], login=row["login"], role=row["role"])


def log_action(user_id: int, action_type: str, entity_type: str, entity_id: int | None):
    db.execute(
        "INSERT INTO action_log(user_id, action_type, entity_type, entity_id) VALUES (?,?,?,?)",
        (user_id, action_type, entity_type, entity_id),
    )