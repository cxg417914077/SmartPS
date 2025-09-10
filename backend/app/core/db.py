from typing import AsyncGenerator
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from backend.app.core.config import settings


DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI)
engine = create_async_engine(DATABASE_URL)


AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() ->  AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
