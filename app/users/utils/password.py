import bcrypt


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    password_bytes: bytes = password.encode()
    return bcrypt.hashpw(password_bytes, salt)


def check_password(password: str, hashed_password: bytes) -> bool:
    password = password.encode('utf-8')
    return bcrypt.checkpw(password=password, hashed_password=hashed_password)
