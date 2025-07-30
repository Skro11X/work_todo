from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary)


class Role(Base):
    pass  # todo нужно потом реализовать этот класс мб придется сделать другую доменную модель
