from datetime import datetime, timezone, timedelta

from jose import jwt, JWTError

from app.config import settings


def create_tokens(data: dict) -> dict:
    # Текущее время в UTC
    now = datetime.now(timezone.utc)

    # AccessToken - 30 минут
    access_expire = now + timedelta(minutes=30)
    access_payload = data.copy()
    access_payload.update({"exp": int(access_expire.timestamp()), "type": "access"})
    access_token = jwt.encode(
        access_payload,
        settings.JWT.PUBLIC_KEY_PATH,
        algorithm=settings.JWT.ALGORITHM
    )

    # RefreshToken - 7 дней
    refresh_expire = now + timedelta(days=7)
    refresh_payload = data.copy()
    refresh_payload.update({"exp": int(refresh_expire.timestamp()), "type": "refresh"})
    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT.PRIVATE_KEY,
        algorithm=settings.JWT.ALGORITHM
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


def get_data_from_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT.PUBLIC_KEY_PATH,  # или PRIVATE_KEY, зависит от того, чем ты кодировал
            algorithms=[settings.JWT.ALGORITHM]
        )
        return payload
    except JWTError as e:
        # токен недействителен, истёк или подпись неверна
        raise ValueError(f"Invalid token: {e}")
