from typing import List, Optional

from sqlalchemy import delete, insert, select, Result
from sqlalchemy.ext.asyncio import AsyncSession

# from sqlalchemy.orm import selectinload

from app.users.models import User
from app.users.shemas import UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    async def create(self, user: dict) -> int:
        stmt = insert(User).values(**user).returning(User.id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar()

    async def get(self, id: str) -> User:
        stmt = select(User).where(User.id == id)
        result = await self._session.execute(stmt)
        return result.scalar()

    async def get_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        result = await self._session.execute(stmt)
        return result.scalar()

    async def update_by_username(
        self, username: str, update_fields: UserUpdate
    ) -> Optional[bool]:
        stmt = select(User).where(User.id == username)
        result: Result = await self._session.execute(stmt)
        user = result.fetchone()
        if not user:
            return None
        update_dict = update_fields.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self._session.commit()
        return True

    async def delete_by_id(self, task_id: int) -> bool:
        stmt = delete(User).where(User.id == task_id)
        operation_result = await self._session.execute(stmt)
        await self._session.commit()
        return operation_result.rowcount > 0
