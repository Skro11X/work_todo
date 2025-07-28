from typing import List, Optional

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.files.models import File


class FileRepository:
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    async def create_file(self, file_data_dict: dict) -> int:
        """Создает новый файл в БД и возвращает его ID"""
        stmt = insert(File).values(**file_data_dict).returning(File.id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar()

    async def get_file_by_id(self, file_id: int) -> Optional[File]:
        """Получает файл по ID"""
        stmt = select(File).where(File.id == file_id)
        result = await self._session.execute(stmt)
        return result.scalar()

    async def get_files_by_task_id(self, task_id: int) -> List[File]:
        """Получает все файлы для конкретной задачи"""
        stmt = select(File).where(File.task_id == task_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_file_by_id(self, file_id: int) -> bool:
        """Удаляет файл по ID"""
        stmt = delete(File).where(File.id == file_id)
        operation_result = await self._session.execute(stmt)
        await self._session.commit()
        return operation_result.rowcount > 0
