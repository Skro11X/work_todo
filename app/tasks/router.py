from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.tasks.repository import TaskRepository
from app.tasks.schemas import (
    TaskCreate,
    TaskFilter,
    TaskPublic,
    TaskStatusUpdate,
    TaskUpdate,
)

router = APIRouter()


@router.post("/", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task_in: TaskCreate, session: AsyncSession = Depends(get_session)
):
    """Создает новую задачу"""
    task_repo = TaskRepository(session)
    try:
        task_id = await task_repo.create_new_task(task_in)
        task = await task_repo.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось создать задачу",
            )
        return task
    except ValueError as e:
        logger.error(f"Validation error creating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ошибка валидации: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания задачи: {str(e)}",
        )


@router.get("/{task_id}", response_model=TaskPublic)
async def get_task_by_id(task_id: int, session: AsyncSession = Depends(get_session)):
    """Получает задачу по ID"""
    task_repo = TaskRepository(session)
    task = await task_repo.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
        )
    return task


@router.patch("/{task_id}", response_model=TaskPublic)
async def update_existing_task(
    task_id: int,
    task_update: TaskUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Обновляет существующую задачу"""
    task_repo = TaskRepository(session)

    existing_task = await task_repo.get_task_by_id(task_id)
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
        )

    update_result = await task_repo.update_by_id(task_id, task_update)
    if not update_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить задачу",
        )

    updated_task = await task_repo.get_task_by_id(task_id)
    return updated_task


@router.patch("/{task_id}/status", response_model=TaskPublic)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Обновляет только статус задачи"""
    task_repo = TaskRepository(session)

    existing_task = await task_repo.get_task_by_id(task_id)
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
        )

    task_update = TaskUpdate(status=status_update.status)

    update_result = await task_repo.update_by_id(task_id, task_update)
    if not update_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить статус задачи",
        )

    updated_task = await task_repo.get_task_by_id(task_id)
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_task(
    task_id: int, session: AsyncSession = Depends(get_session)
):
    """Удаляет задачу по ID"""
    task_repo = TaskRepository(session)
    deleted = await task_repo.delete_by_id(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
        )
    return


@router.get("/", response_model=List[TaskPublic])
async def search_tasks(
    session: AsyncSession = Depends(get_session),
    filters: TaskFilter = Depends(),
    limit: int = 100,
):
    """Возвращает список задач с возможностью фильтрации и поиска"""
    task_repo = TaskRepository(session)

    if any(getattr(filters, field) is not None for field in filters.model_fields):
        tasks = await task_repo.list_all_with_filtres(filters)
    else:
        tasks = await task_repo.list_all()

    if limit and len(tasks) > limit:
        tasks = tasks[:limit]

    return tasks
