from fastapi import Depends, UploadFile, APIRouter, HTTPException, File, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.tasks.repository import TaskRepository
from app.files.schemas import FilePublic, FileCreate
from app.files.utils import save_upload_file
from app.files.repository import FileRepository


router = APIRouter()


@router.post(
    "/{task_id}",
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

    task = await task_repo.get_by_id(task_id)
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
        file_id = await file_repo.create(file_data_dict)
        created_file = await file_repo.get_by_id(file_id)
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


@router.get("/{file_id}")
async def download_file(
    file_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Скачивает файл по его ID"""
    file_repo = FileRepository(session)

    file_record = await file_repo.get_by_id(file_id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден"
        )

    return FileResponse(
        path=file_record.filepath,
        filename=file_record.filename,
        media_type=file_record.mimetype or "application/octet-stream",
    )
