from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Final


PBKDF2_ITERATIONS: Final[int] = 600_000
PBKDF2_ALGORITHM: Final[str] = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS)
    return f"{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt}${derived.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    algorithm, iterations, salt, expected = password_hash.split("$", 3)
    if algorithm != PBKDF2_ALGORITHM:
        return False
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations))
    return hmac.compare_digest(derived.hex(), expected)
