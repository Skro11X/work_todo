from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class FileBase(BaseModel):
    filename: str = Field(..., description="Имя файла")
    mimetype: str = Field(..., description="(image/jpeg', 'application/pdf')")


class FileCreate(BaseModel):
    filename: str = Field(..., description="Имя файла")
    mimetype: Optional[str] = Field(None, description="MIME тип файла")
    filepath: str = Field(..., description="Путь к файлу на сервере")
    size: Optional[int] = Field(None, description="Размер файла в байтах")


class FilePublic(BaseModel):
    id: int
    filename: str
    mimetype: Optional[str] = None
    size: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
