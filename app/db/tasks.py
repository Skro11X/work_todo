from typing import List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.utils import connection
from app.tasks.schemas import CreateTask, FilterTask, Task


class TaskDB:
    @classmethod
    @connection
    async def create_task(cls, *, session: AsyncSession, task: CreateTask):
        params = task.model_dump()
        params["status"] = 0
        try:
            stmt = text(
                """
                    INSERT INTO tasks (title, project, organisation, description, status)
                    VALUES (:title, :project, :organisation, :description, :status)
                    RETURNING id;
                """
            )
            result = await session.execute(stmt, params)
            await session.commit()
            created_task_id = result.scalar_one()
            return created_task_id

        except SQLAlchemyError as e:
            await session.rollback()
            print(f"Ошибка при создании задачи: {e}")
            return None

    @classmethod
    @connection
    async def get_list_of_tasks(cls, *, session: AsyncSession, task: FilterTask) -> List[Task]:
        where_conditions = list()
        active_filtres = dict()
        base_query = """SELECT * FROM tasks"""

        for key in active_filtres.keys():
            where_conditions.append(f"{key} regexp :{key}")

        if task.create_lt:
            where_conditions.append("create_datetime < :create_lt")
            active_filtres["create_lt"] = task.create_lt
        if task.create_gt:
            where_conditions.append("create_datetime > :create_gt")
            active_filtres["create_gt"] = task.create_gt

        active_filtres.update(task.model_dump(exclude_none=True))

        where_substr = ""
        if where_conditions:
            where_substr = "WHERE " + " AND ".join(where_conditions)

        try:
            stmt = text(f"{base_query} {where_substr}")
            result = await session.execute(stmt, active_filtres)
            # list_of_tasks = [Task(**row) for row in result.mappings().all()]
            list_of_tasks = [Task(**row._mapping) for row in result.fetchall()]
            return list_of_tasks

        except SQLAlchemyError as e:
            await session.rollback()
            print(f"Ошибка при создании задачи: {e}")
            return None
