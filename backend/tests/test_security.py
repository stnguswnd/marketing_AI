from app.core.security import hash_password, verify_password


def test_hash_password_round_trip():
    password_hash = hash_password("12345678")

    assert password_hash.startswith("pbkdf2_sha256$")
    assert verify_password("12345678", password_hash) is True
    assert verify_password("wrong-password", password_hash) is False
