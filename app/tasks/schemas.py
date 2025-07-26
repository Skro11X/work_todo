from pydantic import BaseModel, computed_field, Field, ConfigDict
from typing_extensions import Annotated
from datetime import datetime


class ChangeStatus(BaseModel):
    id: int


class Task(BaseModel):
    title: str = Field(min_length=3, max_length=40, description="Заголовок задачи")
    description: str = Field(min_length=3, max_length=255, description="Описание задачи")

    model_config = ConfigDict(from_attributes=True)


class CreateTask(Task):
    project: str = Field(min_length=3, max_length=63, description="Заголовок задачи")
    organisation: str = Field(min_length=3, max_length=255, description="Описание задачи")


class FilterTask(BaseModel):
    title: str | None = Field(max_length=40, description="Заголовок задачи", default=None)
    description: str | None = Field(max_length=255, description="Описание задачи", default=None)
    project: str | None = Field(description="Заголовок задачи", default=None)
    organisation: str | None = Field(max_length=255, description="Описание задачи", default=None)
    create_gt: datetime | None = Field(description="позже чем", default=None, exclude=True)
    create_lt: datetime | None = Field(description="раньше чем", default=None, exclude=True)

class ChangeTask(Task):
    id: int