from typing import Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class File(Base):
    filename: Mapped[str] = mapped_column(Text)
    filepath: Mapped[str] = mapped_column(Text)
    mimetype: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    size: Mapped[Optional[int]] = mapped_column(nullable=True, default=0)

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))

    task: Mapped["Task"] = relationship("Task", back_populates="files")
