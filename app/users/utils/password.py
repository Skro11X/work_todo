import bcrypt


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    password_bytes: bytes = password.encode()
    return bcrypt.hashpw(password_bytes, salt)


def check_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)
