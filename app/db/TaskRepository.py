from typing import List, Optional

from sqlalchemy import text, delete, select, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


from app.models import Task
from app.tasks.schemas import TaskUpdate, TaskCreate


class TaskRepository:

    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    async def create_new_task(self, task: TaskCreate) -> int:
        stmt = insert(Task).values(task.model_dump(exclude_unset=True))
        result = await self._session.execute(stmt)
        return result.fetchone().id

    async def get_task_by_id(self, task_id: int) -> Task:
        stmt = select(Task).where(Task.id == task_id)
        result = await self._session.execute(stmt)
        return result.fetchone()

    async def list_all(self) -> List[Task]:
        stmt = select(Task)
        result = await self._session.execute(stmt)
        return result.fetchall()

    async def update_by_id(
        self, task_id: int, update_fields: TaskUpdate
    ) -> Optional[bool]:
        user = await self._session.get(Task, task_id)
        if not user:
            return None
        update_dict = TaskUpdate.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self._session.commit()
        return True

    async def delete_by_id(self, task_id: int) -> bool:
        stmt = delete(Task).where(Task.id == task_id)
        operation_result = await self._session.execute(stmt)
        return operation_result.rowcount() > 0
