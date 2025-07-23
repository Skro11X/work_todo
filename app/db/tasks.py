from typing import List, Any, Dict
from sqlalchemy import text, TextClause
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.tasks.pydentic_models import CreateTask
from app.db.utils import connection


class TaskDB:

    @classmethod
    @connection
    async def create_task(cls, *args, session: AsyncSession, task: CreateTask):
        session.execute(text("insert "))

        try:
        # 1. SQL-запрос с именованными параметрами (:title, :description)
        # Это защищает от SQL-инъекций.
        # RETURNING id; - это конструкция PostgreSQL для получения ID вставленной строки.
        # Для других СУБД (MySQL, SQLite) может потребоваться другой подход.
            stmt: TextClause = text(
                """
                    INSERT
                    INTO
                    tasks(:list_of_fields)
                    VALUES(:list_of_values)
                    RETURNING
                    id;
                """
            )
            list_of_fields = ' '.join(task.model_dump().keys())
            list_of_values = ' '.join(task.model_dump().value())

            # 3. Выполнение запроса с параметрами
            result = await session.execute(stmt, list_of_fields=list_of_fields, list_of_values=list_of_values)
            await session.commit() # Фиксация транзакции

            # 4. Получение ID созданной записи
            created_task_id = result.scalar_one_or_none()
            return created_task_id

        except SQLAlchemyError as e:
            # В случае ошибки откатываем транзакцию и логируем ошибку
            await session.rollback()
            print(f"Ошибка при создании задачи: {e}")
            return None
