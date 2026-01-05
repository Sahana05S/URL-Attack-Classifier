import os
import base64
import sqlite3
import hashlib
import hmac
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DB_PATH = Path("data/app.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                salt_b64 TEXT NOT NULL,
                pw_hash_b64 TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()


def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
        dklen=32,
    )


def create_user(name: str, email: str, password: str) -> tuple[bool, str]:
    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return False, "All fields are required."
    if "@" not in email or "." not in email:
        return False, "Enter a valid email."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    salt = os.urandom(16)
    pw_hash = _hash_password(password, salt)

    salt_b64 = base64.b64encode(salt).decode("utf-8")
    pw_hash_b64 = base64.b64encode(pw_hash).decode("utf-8")

    try:
        with _get_conn() as conn:
            conn.execute(
                """
                INSERT INTO users (name, email, salt_b64, pw_hash_b64)
                VALUES (?, ?, ?, ?)
                """,
                (name, email, salt_b64, pw_hash_b64),
            )
            conn.commit()
        return True, "Account created. You can login now."
    except sqlite3.IntegrityError:
        return False, "Email already exists. Try logging in."


@dataclass
class User:
    id: int
    name: str
    email: str


def authenticate(email: str, password: str) -> tuple[bool, str, Optional[User]]:
    email = email.strip().lower()
    if not email or not password:
        return False, "Email and password required.", None

    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if row is None:
        return False, "Invalid credentials.", None

    salt = base64.b64decode(row["salt_b64"])
    expected_hash = base64.b64decode(row["pw_hash_b64"])
    given_hash = _hash_password(password, salt)

    if not hmac.compare_digest(expected_hash, given_hash):
        return False, "Invalid credentials.", None

    user = User(id=row["id"], name=row["name"], email=row["email"])
    return True, "Logged in.", user
