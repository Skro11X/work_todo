from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# -- File Schemas --


class FileBase(BaseModel):
    filename: str = Field(..., description="Имя файла")
    mimetype: str = Field(..., description="(image/jpeg', 'application/pdf')")

    task_id: int = Field(..., description="ID задачи, к которой прикреплен файл")


class FileCreate(FileBase):
    filepath: str = Field(..., description="Путь к файлу на сервере")


class FilePublic(BaseModel):
    id: int
    filename: str
    mimetype: str

    model_config = ConfigDict(from_attributes=True)


# -- Task Schemas --


class ETaskStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskBase(BaseModel):
    title: str = Field(min_length=3, max_length=40, description="Заголовок задачи")
    description: str = Field(max_length=2_000, description="Описание задачи")
    project: str = Field(min_length=3, max_length=63, description="Проект")
    organisation: str = Field(min_length=3, max_length=255, description="Организация")

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    status: ETaskStatus = Field(default=ETaskStatus.NEW, description="Статус задачи")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=40, description="Заголовок задачи")
    description: Optional[str] = Field(None, max_length=2000, description="Описание задачи")
    project: Optional[str] = Field(None, min_length=3, max_length=63, description="Проект")
    organisation: Optional[str] = Field(
        None, min_length=3, max_length=255, description="Организация (ЛПУ)"
    )
    status: Optional[ETaskStatus] = Field(None, description="Статус задачи")


class TaskStatusUpdate(BaseModel):
    status: ETaskStatus


class TaskFilter(BaseModel):
    title: Optional[str] = Field(None, max_length=40, description="Поиск по части заголовка")
    description: Optional[str] = Field(None, max_length=2000, description="Поиск по части описания")
    project: Optional[str] = Field(None, description="Фильтр по проекту")
    organisation: Optional[str] = Field(None, max_length=255, description="Фильтр по организации (ЛПУ)")
    status: Optional[ETaskStatus] = Field(None, description="Фильтр по статусу")

    create_gt: datetime | None = Field(description="позже чем", default=None)
    create_lt: datetime | None = Field(description="раньше чем", default=None)


class TaskPublic(TaskBase):
    id: int
    status: ETaskStatus
    created_at: datetime
    updated_at: datetime

    files: list[FilePublic] = []

    model_config = ConfigDict(from_attributes=True)
