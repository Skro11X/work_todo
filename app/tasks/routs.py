from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.file_repository import FileRepository
from app.db.session import get_session
from app.db.task_repository import TaskRepository
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
async def get_task_by_id(
    task_id: int, session: AsyncSession = Depends(get_session)
):
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


@router.post(
    "/{task_id}/files/",
    response_model=FilePublic,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file_to_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    file: UploadFile = File(..., description="Файл для загрузки"),
):
    """Загружает файл и прикрепляет его к задаче"""
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не был получен или имя файла пустое",
        )

    task_repo = TaskRepository(session)
    file_repo = FileRepository(session)

    task = await task_repo.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
        )

    file_size = 0
    if hasattr(file, "size") and file.size:
        file_size = file.size
    else:
        contents = await file.read()
        file_size = len(contents)
        await file.seek(0)

    try:
        saved_filepath = await save_upload_file(file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сохранения файла: {str(e)}",
        )

    file_data_for_db = FileCreate(
        filename=file.filename or "unknown",
        mimetype=file.content_type or "application/octet-stream",
        filepath=str(saved_filepath),
        size=file_size,
    )

    try:
        file_data_dict = file_data_for_db.model_dump()
        file_data_dict["task_id"] = task_id
        file_id = await file_repo.create_file(file_data_dict)
        created_file = await file_repo.get_file_by_id(file_id)
        if not created_file:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось создать запись файла",
            )
        return created_file
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания записи файла: {str(e)}",
        )


@router.get("/files/{file_id}")
async def download_file(
    file_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Скачивает файл по его ID"""
    file_repo = FileRepository(session)

    file_record = await file_repo.get_file_by_id(file_id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден"
        )

    return FileResponse(
        path=file_record.filepath,
        filename=file_record.filename,
        media_type=file_record.mimetype or "application/octet-stream",
    )
