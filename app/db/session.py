from functools import wraps
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.utils import async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def connection(self, commit: bool = True):
    """
    Декоратор для управления сессией с возможностью настройки уровня изоляции и коммита.
    Параметры:
    - `commit`: если `True`, выполняется коммит после вызова метода.
    """

    def decorator(method):
        @wraps(method)
        async def wrapper(*args, **kwargs):
            async with self.session_maker() as session:
                try:
                    result = await method(*args, session=session, **kwargs)
                    if commit:
                        await session.commit()
                    return result
                except Exception as e:
                    await session.rollback()
                    raise
                finally:
                    await session.close()

        return wrapper

    return decorator
