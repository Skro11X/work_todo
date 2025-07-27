import enum
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.utils import Base


class Status(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    title: Mapped[str] = mapped_column(Text)
    project: Mapped[str] = mapped_column(Text)
    organisation: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[Status] = mapped_column(
        Enum(Status), nullable=False, default=Status.NEW
    )

    files: Mapped[list["File"]] = relationship(
        "File", back_populates="task", cascade="all, delete-orphan"
    )


class File(Base):
    filename: Mapped[str] = mapped_column(Text)
    filepath: Mapped[str] = mapped_column(Text)
    mimetype: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    size: Mapped[Optional[int]] = mapped_column(nullable=True, default=0)

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))

    task: Mapped["Task"] = relationship("Task", back_populates="files")
