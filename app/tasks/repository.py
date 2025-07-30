from typing import List, Optional

from sqlalchemy import and_, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.tasks.models import Task
from app.tasks.schemas import TaskCreate, TaskFilter, TaskUpdate


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    async def create_new_task(self, task: TaskCreate) -> int:
        stmt = (
            insert(Task)
            .values(**task.model_dump(exclude_unset=True))
            .returning(Task.id)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar()

    async def get_task_by_id(self, task_id: int) -> Task:
        stmt = select(Task).options(selectinload(Task.files)).where(Task.id == task_id)
        result = await self._session.execute(stmt)
        return result.scalar()

    async def list_all(self) -> List[Task]:
        stmt = select(Task).options(selectinload(Task.files))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_all_with_filtres(
        self, filters: TaskFilter = TaskFilter()
    ) -> List[Task]:
        filters_dict = filters.model_dump(exclude_unset=True, exclude_none=True)
        conditions = []
        for key in filters_dict:
            if key == "create_gt":
                conditions.append(Task.created_at > filters_dict[key])
            elif key == "create_lt":
                conditions.append(Task.created_at < filters_dict[key])
            elif key in ["status", "project", "organisation"]:
                conditions.append(getattr(Task, key) == filters_dict[key])
            else:
                conditions.append(getattr(Task, key).like(f"%{filters_dict[key]}%"))

        stmt = select(Task).options(selectinload(Task.files)).where(and_(*conditions))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update_by_id(
        self, task_id: int, update_fields: TaskUpdate
    ) -> Optional[bool]:
        task = await self._session.get(Task, task_id)
        if not task:
            return None
        update_dict = update_fields.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_dict.items():
            if hasattr(task, key):
                setattr(task, key, value)
        await self._session.commit()
        return True

    async def delete_by_id(self, task_id: int) -> bool:
        stmt = delete(Task).where(Task.id == task_id)
        operation_result = await self._session.execute(stmt)
        await self._session.commit()
        return operation_result.rowcount > 0
