from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Cookie

from app.database import get_session
from app.users.repository import UserRepository, User
from app.users.utils.token import get_data_from_token


async def get_token_from_cookie(user_access_token: str = Cookie(...)):
    return get_data_from_token(user_access_token)


async def get_user_by_token(
    user: str = Depends(get_token_from_cookie),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Зависимость, которая достаёт пользователя из БД."""
    user_rep = UserRepository(session)

    user = await user_rep.get_by_username(user["username"])

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
