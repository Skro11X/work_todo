from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.db.connections import CONNECTIONS, TEST_DB

async_engine = create_async_engine(url=TEST_DB)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                # Явно не открываем транзакции, так как они уже есть в контексте
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                raise e  # Поднимаем исключение дальше
            finally:
                await session.close()  # Закрываем сессию
    return wrapper


# class Base(AsyncAttrs, DeclarativeBase):
#     __abstract__ = True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     created_at: Mapped[datetime] = mapped_column(server_default=func.now())
#     updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
#
#     @declared_attr.directive
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower() + 's'