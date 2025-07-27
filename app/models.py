import enum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, Enum

from app.db.utils import Base


class Status(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    title: Mapped[str] = mapped_column(Text)
    project: Mapped[str] = mapped_column(Text)
    organisation: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[int] = mapped_column(
        Enum(Status), nullable=False, default=Status.IN_PROGRESS
    )

    files: Mapped[list["File"]] = relationship(
        "File", back_populates="task", cascade="all, delete-orphan"
    )


class File(Base):
    filename: Mapped[str] = mapped_column(Text)
    filepath: Mapped[str] = mapped_column(Text)
    mimetype: Mapped[str] = mapped_column(Text)

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))

    task: Mapped["Task"] = relationship("Task", back_populates="files")
