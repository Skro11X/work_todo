from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi import File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.files.utils import save_upload_file
from app.tasks.schemas import (
    FileCreate,
    FilePublic,
    TaskCreate,
    TaskFilter,
    TaskPublic,
    TaskStatusUpdate,
    TaskUpdate,
)

router = APIRouter()

MOCK_TASK_PUBLIC = TaskPublic(
    id=1,
    title="Биба",
    description="Боба",
    project="VistaFuns",
    organisation="boobs",
    status="new",
    created_at="2007-01-01",
    updated_at="2007-01-01",
    files=[
        FilePublic(
            id=1,
            filename="pipyao.txt",
            mimetype="text/plain",
        )
    ],
)


@router.post("/", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_new_task(task_in: TaskCreate, session: AsyncSession = Depends(get_session)):
    """Создает новую задачу"""
    task = MOCK_TASK_PUBLIC
    if not task:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось создать задачу"
        )
    return task


@router.get("/{task_id}", response_model=TaskPublic)
async def get_task_by_id(task_id: int, session: AsyncSession = Depends(get_session)):
    """Возвращает задачу по ID"""
    task = MOCK_TASK_PUBLIC
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task


@router.patch("/{task_id}", response_model=TaskPublic)
async def update_existing_task(
    task_id: int, task_update: TaskUpdate, session: AsyncSession = Depends(get_session)
):
    """Обновляет существующую задачу"""
    task = MOCK_TASK_PUBLIC
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task


@router.patch("/{task_id}/status", response_model=TaskPublic)
async def update_task_status(
    task_id: int, status_update: TaskStatusUpdate, session: AsyncSession = Depends(get_session)
):
    """Обновляет только статус задачи"""

    task = MOCK_TASK_PUBLIC

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_task(task_id: int, session: AsyncSession = Depends(get_session)):
    """Удаляет задачу по ID"""
    deleted = True
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return


@router.get("/", response_model=List[TaskPublic])
async def search_tasks(
    session: AsyncSession = Depends(get_session), filters: TaskFilter = Depends(), limit: int = 100
):
    """Возвращает список задач с возможностью фильтрации и поиска"""
    tasks = [MOCK_TASK_PUBLIC]
    return tasks


@router.post("/{task_id}/files/", response_model=FilePublic, status_code=status.HTTP_201_CREATED)
async def upload_file_to_task(
    task_id: int, file: UploadFile = FastAPIFile(...), session: AsyncSession = Depends(get_session)
):
    """Загружает файл и прикрепляет его к задаче"""
    task = "Получил задачу с ID {task_id}"
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    try:
        saved_filepath = await save_upload_file(file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save file: {e}"
        )

    file_data_for_db = FileCreate(
        filename=file.filename,
        mimetype=file.content_type,
        task_id=task_id,
        filepath=str(saved_filepath),
    )
    db_file = FilePublic(
        id=1,
        filename=file_data_for_db.filename,
        mimetype=file_data_for_db.mimetype,
    )

    return db_file
