import os
import hashlib
import binascii
from .database import get_connection, init_db


class RepositoryUsers:
    """Repository for users and login attempts.

    Provides both low-level APIs used by AuthManager (create/get_by_username/log_login_attempt)
    and convenience helpers (create_user/get_user/verify_password) to support other callers.
    """

    def __init__(self, db_path=None):
        self.db_path = db_path
        init_db(self.db_path)

    # Internal: produce hex-hashed password and hex-encoded salt
    def _hash_password(self, password, salt_hex=None, iterations=100000):
        if salt_hex is None:
            salt = os.urandom(16)
        else:
            salt = binascii.unhexlify(salt_hex)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return binascii.hexlify(pwdhash).decode('utf-8'), binascii.hexlify(salt).decode('utf-8')

    # Low-level create accepting precomputed hash+salt (used by AuthManager)
    def create(self, username, password_hash, salt, role):
        conn = get_connection(self.db_path)
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (username, password_hash, salt, role) VALUES (?,?,?,?)",
                (username, password_hash, salt, role),
            )
        conn.close()

    def get_by_username(self, username):
        conn = get_connection(self.db_path)
        row = conn.execute(
            "SELECT id, username, password_hash, salt, role, created_at FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()
        if not row:
            return None
        keys = ["id", "username", "password_hash", "salt", "role", "created_at"]
        return dict(zip(keys, row))

    def any_users_exist(self):
        conn = get_connection(self.db_path)
        row = conn.execute("SELECT COUNT(1) FROM users").fetchone()
        conn.close()
        return (row[0] or 0) > 0

    def log_login_attempt(self, username, success, reason=None):
        conn = get_connection(self.db_path)
        with conn:
            conn.execute(
                "INSERT INTO login_attempts (username, success, reason) VALUES (?,?,?)",
                (username, 1 if success else 0, reason),
            )
        conn.close()

    # Convenience helpers that work with plaintext passwords
    def create_user(self, username, password, role='user'):
        pwdhash, salt = self._hash_password(password)
        self.create(username, pwdhash, salt, role)

    def get_user(self, username):
        rec = self.get_by_username(username)
        if not rec:
            return None
        return {
            'id': rec['id'],
            'username': rec['username'],
            'password_hash': rec['password_hash'],
            'salt': rec['salt'],
            'role': rec['role'],
        }

    def verify_password(self, username, password):
        user = self.get_user(username)
        if not user:
            return False
        pwdhash, _ = self._hash_password(password, salt_hex=user['salt'])
        return pwdhash == user['password_hash']

