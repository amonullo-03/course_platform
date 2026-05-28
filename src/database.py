from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

DATABASE_URL = settings.DATABASE_URL

# Создаем асинхронный движок (Engine)
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику асинхронных сессий
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Главная функция-зависимость (Dependency Injection). 
# Она открывает сессию для каждого запроса и закрывает её после ответа.
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
